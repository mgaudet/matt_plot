`matt_plot.py`: A utility belt for matplotlib
=========

Plotting utility functions for matplotlib

The idea behind `matt_plot` is twofold. 

First, there are a bunch of things I *always* end up doing to my plotting
code, things that can at times be obtuse, or foggy in my mind. So why not
package all of my historic knowledge in here. 

Second, I would like to separate presentation from implementation as much
as possible, so `matt_plot` is built around the notion of a "decor" file;
This is fed as a kwarg to the `matt_plot` functions, and provides data-driven
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

