import sys
import numpy as np
from collections import OrderedDict

import bokeh.plotting as bk
from bokeh.models.glyphs import Patches, Line, Circle
from bokeh.models import (
    GMapPlot, Range1d, ColumnDataSource, LinearAxis,
    HoverTool, PanTool, WheelZoomTool, BoxSelectTool, ResetTool, PreviewSaveTool,
    BoxSelectionOverlay, GMapOptions,
    NumeralTickFormatter, PrintfTickFormatter)
from bokeh.resources import CDN
from bokeh.embed import components, autoload_static, autoload_server

####################################
####################################
# Preparation of the data:
####################################
####################################

# Reads data from Boroughs-pop.dat and stores in dict:
boroughsnames = []
boroughs_data = {}
population = [] ; area = [] ; density = []
with open('data/Boroughs-pop.dat', 'r') as f:
    for row in f:
        bname = row.split()[0]
	boroughsnames.append(bname)
	boroughs_data[bname] = [float(x) for x in row.split()[1:]]
	population.append(boroughs_data[bname][0])
	area.append(boroughs_data[bname][1])
	density.append(boroughs_data[bname][2])
maxpop = np.amax(boroughs_data.values(), axis=0)[0]
minpop = np.amin(boroughs_data.values(), axis=0)[0]
maxdens = np.amax(boroughs_data.values(), axis=0)[2]
mindens = np.amin(boroughs_data.values(), axis=0)[2]
filenames = ["data/"+name+".dat" for name in boroughsnames]


# Sets color depending on density:
colors = ["#fee5d9", "#fcbba1", "#fc9272", "#fb6a4a", "#ef3b2c", "#cb181d", "#99000d"] # reds
numcolors = len(colors)
boroughs_colors = []
popstep = (maxpop-minpop)/(numcolors-1)
densstep = (maxdens-mindens)/(numcolors-1)
for bname in boroughsnames:
    try:
        #popnorm = boroughs_data[bname][0] - minpop
        #idx = int(popnorm/popstep)
	densnorm = boroughs_data[bname][2] - mindens
	idx = int(densnorm/densstep)
	boroughs_colors.append(colors[idx])
    except KeyError:
        boroughs_colors.append("black")


# Reads the coordinates of each borough to draw the map:
listofcoords = []
for i in xrange(len(boroughsnames)):
    coords = np.genfromtxt(filenames[i])[:,:2]
    listofcoords.append(coords)
boroughs_xs = [coord[:,0].tolist() for coord in listofcoords]
boroughs_ys = [coord[:,1].tolist() for coord in listofcoords]


####################################
####################################
# Figure:
####################################
####################################

bk.output_file("Berlin_dens_gmap.html",  mode="cdn") # title="Berlin population")

source = bk.ColumnDataSource(data=dict( boroughsnames=boroughsnames,
					population=population, area=area, density=density))

p = GMapPlot(title="", # False, # "Berlin population",
#	     x_axis_label='Longitude', y_axis_label='Latitude',
             plot_width=570, plot_height=500,
	     x_range = Range1d(), y_range = Range1d(),
#	     border_fill = '#130f30',
             map_options=GMapOptions(lat=52.521123, lng=13.407478, zoom=10))
#             tools="pan,wheel_zoom,box_zoom,reset,hover,save")
p.map_options.map_type="satellite" # satellite, roadmap, terrain or hybrid

source_patches = bk.ColumnDataSource(data=dict( boroughs_xs=boroughs_xs, boroughs_ys=boroughs_ys,
                                                boroughs_colors=boroughs_colors,
						boroughsnames=boroughsnames,
                                        	population=population, area=area, density=density))
patches = Patches(xs="boroughs_xs", ys="boroughs_ys", fill_color="boroughs_colors",
                  fill_alpha=0.5, line_color="black", line_width=0.5)
patches_glyph = p.add_glyph(source_patches, patches)

p.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool(), HoverTool(), 
	    ResetTool(), PreviewSaveTool())

#xaxis = LinearAxis(axis_label="lat", major_tick_in=0, formatter=NumeralTickFormatter(format="0.000"))
#p.add_layout(xaxis, 'below')
#yaxis = LinearAxis(axis_label="lon", major_tick_in=0, formatter=PrintfTickFormatter(format="%.3f"))
#p.add_layout(yaxis, 'left')

hover = p.select(dict(type=HoverTool))
#hover.snap_to_data = False	# not supported in new bokeh versions
hover.tooltips = OrderedDict([
    ("Borough", "@boroughsnames"),
    ("Density (pop/km2)", "@density"),
#    ("Population", "@population"),
    ("Area (km2)", "@area"),
#    ("(long,lat)", "($x, $y)"),
])

bk.show(p)

