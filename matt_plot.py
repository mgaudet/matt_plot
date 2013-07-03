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

from matplotlib import rc
import matplotlib.pyplot as plt
import shlex 
import sarge
import os.path
import shutil

#configs: This should likely be set in a decor file; FIXME
rc('text',usetex=True)
rc('font',family='serif', size=26)
rc('lines',linewidth=4)

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
    plt.figlegend(*ax.get_legend_handles_labels(), loc='upper left')
    figure.savefig(filename, format="pdf")
    crop(filename)

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
        
        <label> <new_label> <line_colour> <line_width> <marker_size> <marker> 

    Everything past the new label is optional.
    """
    global prefix
    decor = {}
    keys = ["olabel", "label", "color", "lw" , "ms", "marker"] 
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
        decor[name] = decor_elem
    return decor

def plot(X,Y, **kwargs): 
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
        plt.plot(X,Y,**decor)
    else:
        #Should really memoize this... but I dont see it being a huge issue
        with open(kwargs["decor_file"]) as f: 
            decor = process_decor_file(f) 
        
        label = kwargs["label"]
        try: 
            l_decor = decor[label]
            merge_kwargs(l_decor,kwargs) 
            print "DECOR: Plotting with l_decor: %s" % (l_decor) 
        except KeyError: #No decor declared for this label
            l_decor = {}
            merge_kwargs(l_decor,kwargs) 
            print "DECOR: Plotting with l_decor: %s (no decor for label)" % (l_decor) 
        
        plt.plot(X,Y, **l_decor)

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

