#!/usr/bin/env python

from sys import path
from os.path import abspath
path.append(abspath("../.."))  # If not yet installed

from pprint import pprint

from grapher import Function


f = Function("log10(x)")

print f(0)
print f(10)

table_of_values = {x: f(x) for x in xrange(11)}
pprint(table_of_values)  # Pretty print
print


g, h = Function("e^x"), Function("2*x")

print (g & h)(0.5)  # Function composition
print (h & g)(0)
