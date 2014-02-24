#!/usr/bin/env python

from itertools import product, repeat

import Image
import ImageEnhance

from functions import FunctionImage, PointsImage


class GraphImage(object):

    """Graph image class with curve-drawing methods."""

    def __init__(self, fname=" .png", w=1000, h=1000):
        self.fname = fname

        self.xbounds, self.ybounds = (-20, 20), (-20, 20)
        self.width, self.height = w, h
        self.axesthick, self.drawaxes, self.axescolor = 2, True, (0, 0, 0)
        self.xscl, self.yscl, self.tick = 1, 1, 5
        self.round, self.tickprec = 2, 10E-4
        self.grid, self.backg = False, (255, 255, 255)
        self.shade_opacity = 0.5

        self.gimg = Image.new("RGB", (self.width, self.height), self.backg)
        self.gpix = self.gimg.load()
        self.gimg.save(self.fname)

        self.graphs, self.gvars = {}, {}

    def add(self, *obj):
        """Add object(s) to the GraphImage instance graphs dict.

        The object(s) must have a value function as well as pcolor, pthick,
        and show fields to be considered drawable."""
        for o in obj:
            self.graphs[id(o)] = o
        if len(obj) == 1:
            return obj[0]
        return obj

    def remove(self, *obj):
        """Remove object(s) from the GraphImage instance graphs dict."""
        for o in obj:
            fid = id(o)
            if fid in self.graphs:
                del self.graphs[fid]

    def draw(self):

        """Draw/redraw the image of a GraphImage instance."""

        self.gimg = Image.new("RGB", (self.width, self.height), self.backg)
        self.gpix = self.gimg.load()

        xspan = self.xbounds[1] - self.xbounds[0]
        yspan = self.ybounds[1] - self.ybounds[0]
        self.xstep = self.width // xspan   # x-pixels/unit
        self.ystep = self.height // yspan  # y-pixels/unit

        self.x_axis = FunctionImage("0")
        self.top_axis = FunctionImage(str(self.ybounds[1]))
        self.bot_axis = FunctionImage(str(self.ybounds[0]))

        if self.drawaxes:
            self.draw_axes()
        for fid in self.graphs:
            if self.graphs[fid].show:
                self.draw_func(self.graphs[fid])

    def draw_axes(self):

        """Draw the axes and grid (use draw to redraw the graph)."""

        origx, origy = self.pixel()  # Origin
        w, h = self.width, self.height
        midx, midy = sum(self.xbounds) / 2, sum(self.ybounds) / 2
        axescol, axesth = self.axescolor, self.axesthick

        if 0 <= origy < self.height:
            orig = [(midx, 0)]  # Fake "origin" to draw axis from
            self.graphs["x-axis"] = PointsImage(orig, axescol, [w, axesth])
        if 0 <= origx < self.width:
            orig = [(0, midy)]
            self.graphs["y-axis"] = PointsImage(orig, axescol, [axesth, h])

        x_ticks, y_ticks = [], []
        for xpix in xrange(self.width + 1):
            xcoord = round(self.coord(xpix)[0], self.round)
            if xcoord % self.xscl < self.tickprec:
                x_ticks.append([xcoord, 0])

        for ypix in xrange(self.height + 1):
            ycoord = round(self.coord(y=ypix)[1], self.round)
            if ycoord % self.yscl < self.tickprec:
                y_ticks.append([0, ycoord])

        if self.grid:
            x_ticks = [(point[0], midy) for point in x_ticks]
            y_ticks = [(midx, point[1]) for point in y_ticks]
            tkx, tky = [axesth - 1, h], [w, axesth - 1]
        else:
            tkx, tky = [axesth - 1, self.tick], [self.tick, axesth - 1]

        self.graphs["x-ticks"] = PointsImage(x_ticks, axescol, tkx)
        self.graphs["y-ticks"] = PointsImage(y_ticks, axescol, tky)

        self.gimg.save(self.fname)

    def draw_func(self, fobj):

        """Draws a function on the graph image using image compositing.

        The function must have a value method (Points instances work)."""

        eq = getattr(fobj, "eq", "=")  # Check equality
        curve_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        cpix, fpcolor, pthick = curve_img.load(), fobj.pcolor, fobj.pthick
        if not isinstance(pthick, list):  # Square point
            pthick = [pthick]

        if "=" in eq:
            for px in xrange(self.width - 1):  # Iterate over all columns
                yvals = fobj(round(self.coord(px)[0], self.round), self.gvars)
                if yvals is None:
                    continue
                if not isinstance(yvals, list):  # For single points
                    yvals = [yvals]

                for yval in yvals:
                    py = self.pixel(y=yval)[1]
                    for ppx, ppy in self.pad_point(px, py, *pthick):
                        if ((0 <= ppx < self.width) and
                           (0 <= ppy < self.height)):
                            cpix[ppx, ppy] = fpcolor

            self.gimg = Image.composite(curve_img, self.gimg, curve_img)
            self.gimg.save(self.fname)

        if "<" in eq:
            self.shade_between(fobj, self.bot_axis)
        elif ">" in eq:
            self.shade_between(fobj, self.top_axis)

    def shade_between(self, fobj1, fobj2=None, endpoints=None, color=None):

        """Shade an area between two functions using transparent image
        compositing.

        The first function's point color is used."""

        shade_img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        spix = shade_img.load()
        color = color if color else fobj1.pcolor

        fobj2 = fobj2 if fobj2 else self.x_axis
        if endpoints:
            endpoints = [self.pixel(n)[0] for n in endpoints]
            endpoints = [max(0, min(n, self.width - 1)) for n in endpoints]
        else:
            endpoints = (0, self.width - 1)

        for gx in xrange(*endpoints):
            f1val = fobj1(self.coord(gx)[0], self.gvars)
            f2val = fobj2(self.coord(gx)[0], self.gvars)

            f1pix = self.pixel(y=f1val)[1]  # Pixel of 1st function value
            f2pix = self.pixel(y=f2val)[1]  # Pixel of 2nd function value
            pix = [f1pix, f2pix]
            if None in pix:
                continue

            for gy in xrange(self.height - 1):
                if min(pix) <= gy <= max(pix):
                    spix[gx, gy] = color

        alpha = shade_img.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(self.shade_opacity)
        shade_img.putalpha(alpha)
        self.gimg = Image.composite(shade_img, self.gimg, shade_img)
        self.gimg.save(self.fname)

    def coord(self, x=0, y=0):

        """Calculates Cartesian coordinates of the specified pixel."""

        xcrd = self.xbounds[0] + (float(x) / self.xstep)
        ycrd = self.ybounds[1] - (float(y) / self.ystep)
        return xcrd, ycrd

    def pixel(self, x=0, y=0):

        """Calculates pixel coordinate of specified Cartesian point."""

        if (x is None) or (y is None):
            return (None, None)

        xpix = (x - self.xbounds[0]) * self.xstep
        ypix = (self.ybounds[1] - y) * self.ystep
        return int(round(xpix)), int(round(ypix))

    @staticmethod
    def pad_point(px, py, pxthick, pythick=None):
        """Returns cells to pad a certain point with specified thickness."""
        if pythick is None:
            pythick = pxthick
        try:
            pxspan = xrange(px - pxthick + 1, px + pxthick)
            pyspan = xrange(py - pythick + 1, py + pythick)
        except OverflowError:
            return ()  # Nothing to iterate over!
        return product(pxspan, pyspan)
