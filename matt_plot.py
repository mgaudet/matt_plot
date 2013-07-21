"""
matt_plot.py: A utility belt for matplotlib

    The idea behind matt_plot is twofold. 
    
    First, there are a bunch of things I *always* end up doing to my plotting
    code, things that can at times be obtuse, or foggy in my mind. So why not
    package all of my historic knowledge in here. 

    Second, I would like to separate presentation from implementation as much
    as possible, so matt_plot is built around the notion of a "decor" file;
    This is fed as a kwarg to the matt_plot functions, and provides data-driven
    styling. For me, it's most important to be able to remap labels; generally
    from development names to publication names. Currently remapping the
    following is supported in a decor file: 

    - Label
    - colour
    - line width
    - marker size
    - maker

    Adding more should be easy. 

    Decor File format: 

    Each line is a mapping: 
        
        <input label> <new_label> <line_colour> <line_width> <marker_size> <marker> 

    A mapping element can be elided by specifying "None" as the value, and all 
    except the new label are optional. 

    Multi-word values can be specified by wrapping the value in quotes
"""
import os.path
import sarge
import shlex 
import shutil

from matplotlib import rc
import matplotlib.pyplot as plt
import numpy as np

#configs: This should likely be set in a decor file; FIXME
rc('text',usetex=True)
rc('font',family='serif', size=26)

rc('axes',titlesize=26*.7)
rc('axes',labelsize=26*.7)
rc('axes',edgecolor='#BDBDBD')

rc('lines',linewidth=3)

fs = (5,5)

"""
Implmentation notes

- Need a way to set the upcoming number of plots to support colour interpolation

"""

prefix = "" 

def set_prefix(labels): 
    """
    The stateful prefix is used to help ease label parsing; 
    
    Any label is stripped of its prefix before being looked up
    """
    global prefix
    prefix = os.path.commonprefix(list(labels))

def merge_kwargs(decor,kwargs): 
    """
    Merges real function kwargs with decor kwargs: Decor kwargs win, 
    
    - Also strips the "decor_file" kwarg
    """
    for k in kwargs.keys(): 
        if k in decor: 
            continue
        else: 
            if k != "decor_file": 
                decor[k] = kwargs[k]
            else:
                pass

def clean_decors(decors, blacklist):
    """ Delete non-sensical, blacklisted, decor elements from decor set """ 
    for decor in decors:
        for k in blacklist:
            if k in decors[decor]: 
                del decors[decor][k]

def crop(filename): 
   """ Call PDFCrop on a file, and replace it with its cropped version """
   r = sarge.capture_stdout("pdfcrop %s" % (filename))
   if r.returncode  > 0: 
       print "PDFCrop error, return code %d\n\t%s" % (r.returncode, r.stdout.text)
   else: 
       shutil.move(filename.replace(".pdf","-crop.pdf"), filename)

def legend(filename, **kwargs): 
    """ Manufacture legend, and save; Is always cropped """ 
    ax = plt.gca()
    figure = plt.figure(figsize=(200,200))
    print ax.get_legend_handles_labels()
    print len(ax.get_legend_handles_labels()[0])
    r = plt.figlegend(*ax.get_legend_handles_labels(), loc='upper left', ncol=len(ax.get_legend_handles_labels()[0]) )
    figure.savefig(filename, format="pdf")
    crop(filename)
    return r 

def figure(**kwargs):
    """ Create a matt_plot figure, which has a default size and labels """ 
    decor = {"figsize" : fs} 
    merge_kwargs(decor,kwargs)
    fig = plt.figure(**decor)
    plt.xlabel("TBD")
    plt.ylabel("DO FILL IN")
    return fig

def process_decor_file(f):
    """
    Process a file into a decor dictionary; 

    Each line is a mapping: 
        
        <label> <new_label> <line_colour> <line_width> <marker_size> <marker> <hatching>

    Everything past the new label is optional.
    """
    global prefix
    decor = {}
    keys = ["olabel", "label", "color", "lw" , "ms", "marker", "hatch"] 
    for l in f: 
        elems = shlex.split(l,comments=True)
        if len(elems) < 2: 
            continue
        decor_elem = {} 
        for k,v in zip(keys,elems): 
            try: 
                decor_elem[k] = int(v)
            except ValueError: 
                if v == "None":
                    continue
                decor_elem[k] = v

        name = decor_elem["olabel"]
        try: 
            if prefix in name:
                name = name[len(prefix):]
        except TypeError:
            pass
        del decor_elem["olabel"]
        #Be insensitive to _ - distinction
        decor[name] = decor_elem
        decor[name.replace("-","_")] = decor_elem
        decor[name.replace("_","-")] = decor_elem
    return decor

def plot(X,Y, **kwargs): 
    return doplot(X,Y,plt.plot, **kwargs) 

def errorbar(X,Y, **kwargs):
    return doplot(X, Y, plt.errorbar, **kwargs)

def doplot(X,Y,function, **kwargs): 
    """
    If a 'decor_file' kwarg is provided to mattplot, then 
    decor parameters are read from that file, and used. 

        A decor parmeter file maps labels to: 
            - new labels
            - line colours
            - line widths
            - marker sizes
    """ 
    if ("decor_file" not in kwargs) or ("label" not in kwargs) \
        or (kwargs["decor_file"] is None):
        decor = {}
        merge_kwargs(decor, kwargs)  #Strips out decor_file key if exists
        print "DECOR: Plotting with decor: %s" % (decor) 
        return function(X,Y,**decor)
    else:
        #Should really memoize this... but I dont see it being a huge issue
        with open(kwargs["decor_file"]) as f: 
            decor = process_decor_file(f) 
            clean_decors(decor, ["hatch"])
        
        label = kwargs["label"]
        try: 
            l_decor = decor[label]
            merge_kwargs(l_decor,kwargs) 
            print "DECOR: Plotting with l_decor: %s" % (l_decor) 
        except KeyError: #No decor declared for this label
            l_decor = {}
            merge_kwargs(l_decor,kwargs) 
            print "DECOR: Plotting with l_decor: %s (no decor for label)" % (l_decor) 
        
        return function(X,Y, **l_decor)

def savefig(filename, **kwargs): 
   """ tighten layout, save figure, crop """ 
   plt.tight_layout()
   plt.savefig(filename, **kwargs)
   crop(filename)
       

def print_decorfile_sample(params_exist):
    """ Dump a sample decor file for the set """ 
    print "# Sample decor file for this set" 
    prefix = os.path.commonprefix(list(params_exist))
    max_strlen = max(map(lambda x: len(x), params_exist))
    format_str = "{0: <%d}" % (max_strlen)
    print "#%s\tnew_label\tcolor\tlw\tms\tmarker" % (format_str.format("olabel"))
    for p in sorted(params_exist): 
        print "%s\t\"NEW_NAME\"" % (format_str.format(p[len(prefix):]).replace("_","-"))


def check_data(data):
    l = None
    for d in data:
        if l is not None:
            assert len(d) == l, "Bad dimensions"
        else: 
            l = len(d) 
    assert l is not None
    return l 

def map_decor_labels(labs, decor):
    out = []
    for l in labs:
        rep = l.replace("_","-")
        if rep in decor:
            out.append(decor[rep]["label"])
        else:
            print "Didn't find {} in decor".format(rep)
            out.append(rep)
    return out

def fix_labels(labs, decor=None): 
    if decor is None:
        return map(lambda x: x.replace("_","-"), labs)
    else:
        print "mapping decor"
        return map_decor_labels(labs, decor)


def grouped_barplot(data, unsafe_labels, ticklabels, **kwargs): 
    """
    data is a list of data sets to plot as grouped bars
    - Sum of bar widths for each group apparently needs to sum to 1
    """
    if "decor_file" in kwargs and kwargs["decor_file"] is not None: 
        with open(kwargs["decor_file"]) as f:
            decors = process_decor_file(f)
        print "DECOR FILE: {}".format(decors)
        labels = fix_labels(unsafe_labels,decors)
        clean_decors(decors,["ms", "marker","lw"])
    else:
        decors = {} 
        labels = fix_labels(unsafe_labels)
    print "Decors: {}".format(decors)
    N = check_data(data)
    assert len(labels) == len(data), "Label dimensions bad %s %s" % (len(labels), len(data)) 
    assert len(ticklabels) == N, "Tick label dims bad" 
    gap = 0.2 
    width = float(1 - gap) / N 

    #fig = plt.figure()
    #ax = fig.add_subplot(111)
    ax = plt.gca()

    ind = np.arange(N)
    
    rectangles = []
    
    for i,d in enumerate(data):
        olabel = unsafe_labels[i].replace("_","-")
        print olabel
        if olabel in decors:
            decor = decors[olabel]
        else:
            if len(data) > 1: 
                decor = { "color" : plt.get_cmap('jet')(float(i)/(len(data)-1)) }
            else:
                decor = {}

        r =  ax.bar(ind + i*width, d, width, linewidth=0, edgecolor='#2D2D2D', **decor  )
        rectangles.append(r)

    # ax.legend( tuple(rectangles), tuple(labels)  )
    locs, ticks = plt.xticks()
    plt.xticks(locs, ticklabels)
    
    #White lines -- Turns out, these don't work at the figure sizes 
    #I am working with. 
    # ax.grid(axis = 'y', color ='white', linestyle='-', linewidth=2)


def remove_axes(axis): 
    axis.spines['top'].set_visible(False)
    axis.spines['right'].set_visible(False)
    axis.tick_params(axis='both', direction='out')
    axis.get_xaxis().tick_bottom()   # only needed ticks
    axis.get_yaxis().tick_left()

def setAxLinesBW(ax):
    """
    Take each Line2D in the axes, ax, and convert the line style to be 
    suitable for black and white viewing.

    Modified from http://stackoverflow.com/questions/7358118/matplotlib-black-white-colormap-with-dashes-dots-etc
    """
    MARKERSIZE = 3

    COLORMAP = {
        'b': {'marker': None, 'dash': (None,None)},
        'g': {'marker': None, 'dash': [5,5]},
        'r': {'marker': None, 'dash': [5,3,1,3]},
        'c': {'marker': None, 'dash': [1,3]},
        'm': {'marker': None, 'dash': [5,2,5,2,5,10]},
        'y': {'marker': None, 'dash': [5,3,1,2,1,10]},
        'k': {'marker': 'o', 'dash': (None,None)} #[1,2,1,10]}
        }

    for i,line in enumerate(ax.get_lines()):
        origColor = line.get_color()
        line.set_color('black')
        line.set_dashes(COLORMAP[origColor]['dash'])
        line.set_marker(COLORMAP[origColor]['marker'])
        line.set_markersize(MARKERSIZE)

