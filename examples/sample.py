#!/usr/bin/env python

from sys import path
from os.path import abspath
path.append(abspath("../.."))  # If not yet installed

from math import pi, e

from grapher import GraphImage, FunctionImage


### GRAPH 1 ###

graph = GraphImage("test.png", 1000, 1000)  # Filename, width, height

graph.xbounds = (-5, 5)  # Bounds of graph
graph.ybounds = (-5, 5)
graph.grid = True  # Show grid

inverse_f = graph.add(FunctionImage("a/x", (150, 25, 0)))  # Function, color

graph.gvars["a"] = 1  # Set a custom variable

graph.draw()

# Shade area under 1/x from 1 to e
graph.shade_between(inverse_f, endpoints=(1, e), color=(50, 0, 200))

### GRAPH 2 ###

graph2 = GraphImage("test2.png", 2000, 2000)

graph2.xbounds = (-2 * pi, 2 * pi)
graph2.ybounds = (-2, 2)
graph2.tick, graph2.tickprec = 10, 10E-3
graph2.xscl = pi/6  # Set x-tick scale

sin = FunctionImage("sin(x)", (200, 0, 0), restrict=[None, [pi]])
cos = FunctionImage("cos(x)", (0, 0, 200), restrict=[[-pi], None])
tan = FunctionImage(sin / cos, (0, 150, 50), pthick=4)

sin, cos, tan = graph2.add(sin, cos, tan)  # Add all three to graph

graph2.draw()
