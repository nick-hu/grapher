#!/usr/bin/env python

import math
from decimal import Decimal
import ast
from itertools import product


class Function(object):

    """Function base class for evaluating and manipulating functions.

    The function can be evaluated by "calling" func_inst(x_value)."""

    def __init__(self, fstr, restrict=None):

        """Constructs a function from an expression string which is
        parsed for validity to ensure safe evaluation using value(...) .

        A restriction can be specified with a list in interval notation:
        [n] denotes a closed endpoint, whereas n denotes an open endpoint.
        For example, [a, [b]] represents {x | a < x <= b}."""

        self.fstr = fstr.replace("^", "**")

        whitelist = (ast.Expression, ast.Call, ast.Name, ast.Load,
                     ast.UnaryOp, ast.BinOp, ast.BitXor, ast.operator,
                     ast.unaryop, ast.cmpop, ast.Num, ast.Module, ast.Expr)

        tree = ast.parse(fstr)
        valid = all(isinstance(node, whitelist) for node in ast.walk(tree))
        if not valid:
            raise SyntaxError("invalid mathematical expression")

        self.restrict = restrict

    def __str__(self):
        return self.fstr

    def __repr__(self):
        return "<Function {0}>".format(self.fstr)

    def __call__(self, x, gvars={}):
        return self.value(x, gvars)

    def __add__(self, other):
        return self.combine_func(other, "+")

    def __sub__(self, other):
        return self.combine_func(other, "-")

    def __mul__(self, other):
        return self.combine_func(other, "*")

    def __div__(self, other):
        return self.combine_func(other, "/")

    def __and__(self, other):
        return self.compose_func(other)

    def checktype(f1, f2, op):

        """Check if two objects are the same type (for combining
        functions)."""

        types = [repr(type(f).__name__) for f in (f1, f2)]

        if types[0] != types[1]:
            msg = "unsupported operand type(s) for"
            err = "{0} {1}: {2} and {3}".format(msg, op, *types)
            raise TypeError(err)

    def combine_func(f1, f2, op):

        """Returns a new Function combining two functions.

        The new function's string is the concatenation of f1 and f2's
        strings with op. The two functions must both be Function or
        FunctionImage instances.
        If the parents are FunctionImage instances, a string will be
        returned for use with the FunctionImage constructor."""

        f1.checktype(f2, op)

        fstr = "({0}) {1} ({2})".format(f1.fstr, op, f2.fstr)
        if isinstance(f1, FunctionImage):
            return fstr
        return Function(fstr)

    def compose_func(f1, f2):

        """Returns a new Function equivalent to f1@f2(x).

        The new function's string is f1's string with f2 substituted
        for x by string replacement. The two functions must both be
        Function or FunctionImage instances.
        If the parents are FunctionImage instances, a string will be
        returned for use with the FunctionImage constructor."""

        f1.checktype(f2, "&")

        fstr = f1.fstr.replace("x", "({0})".format(f2.fstr))
        if isinstance(f1, FunctionImage):
            return fstr
        return Function(fstr)

    def value(self, x, gvars={}):

        """Evaluate a function at x using the gvars variable dictionary.

        The function has access to all functions in the math module,
        the abs function, and the constants pi and e.
        Evaluation occurs within this namespace and without built-ins."""

        if self.restrict:
            left, right = self.restrict
            if left is not None:
                if isinstance(left, list):  # left-closed
                    if x < left[0]:
                        return
                elif x <= left:  # left-open
                    return
            if right is not None:
                if isinstance(right, list):  # right-closed
                    if x > right[0]:
                        return
                elif x >= right:  # right-open
                    return

        gvars = ((var, Decimal(str(val))) for var, val in gvars.iteritems())
        namespace = [(n, o) for n, o in vars(math).iteritems() if callable(o)]
        namespace = dict(namespace)
        namespace.update({"x": Decimal(str(x)), "pi": Decimal(str(math.pi)),
                          "e": Decimal(str(math.e)), "abs": abs})
        namespace.update(gvars)

        try:
            return float(eval(self.fstr, {"__builtins__": None}, namespace))
        except ValueError:
            pass
        except ZeroDivisionError:
            pass


class FunctionImage(Function):

    """Function image class which can be used with GraphImage class.

    The function can be evaluated by "calling" func_inst(x_value)."""

    def __init__(self, fstr, pcolor=(0, 0, 0), pthick=2, show=True,
                 eq="=", restrict=None):

        """Construct a FunctionImage instance for use with the
        GraphImage class.

        pcolor is an RGB color tuple, pthick is the point thickness,
        eq is the optional inequality as a string, and show
        controls whether or not the function is displayed.

        A restriction can be specified with a list in interval notation:
        [n] denotes a closed endpoint, whereas n denotes an open endpoint.
        For example, [a, [b]] represents {x | a < x <= b}."""

        super(self.__class__, self).__init__(fstr, restrict)

        self.pcolor, self.pthick = pcolor, pthick
        self.eq, self.show = eq, show

    def __repr__(self):
        return "<FunctionImage {0}>".format(self.fstr)


class Points(object):

    """Class for a container-like group of points.

    The points can be evaluated by "calling" points_inst(x_value).
    Points support dictionary-style assignment."""

    def __init__(self, plist):

        """Builds an internal point dictionary from a list of 2-tuples."""

        points = {}
        for point in plist:
            if point[0] not in points:
                points[point[0]] = []
            points[point[0]].append(point[1])

        self.points = points

    def __repr__(self):
        return "<Points ({0} x-values)>".format(len(self.points))

    def __len__(self):
        return len(self.points)

    def __getitem__(self, x):
        return self.points[x]

    def __setitem__(self, x, y):
        self.points[x] = y

    def __delitem__(self, x):
        del self.points[x]

    def __call__(self, x, *_):
        return self.value(x)

    def value(self, x):
        """Return a list of y-values for a specified x-value."""
        if x in self.points:
            return self.points[x]


class PointsImage(Points):

    """Points image class which can be used with GraphImage class.

    The points can be evaluated by "calling" points_inst(x_value).
    Points support dictionary-style assignment."""

    def __init__(self, plist, pcolor=(0, 0, 0), pthick=2, show=True):

        """Construct a PointsImage instance for use with the
        GraphImage class.

        pcolor is an RGB color tuple, pthick is the point thickness,
        and show controls whether or not the points are displayed."""

        super(self.__class__, self).__init__(plist)

        self.pcolor, self.pthick, self.show = pcolor, pthick, show

    def __repr__(self):
        return "<PointsImage ({0} x-values)>".format(len(self.points))
