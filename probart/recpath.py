#!/usr/bin/env python3
"""WIP: Recursive path generation."""

import math
import random

import cairo
import numpy as np


class FractalPath:
    """Base class for recursive path generation."""

    def __init__(self, start_x, start_y, angular_momentum,
                 velocity, color, cairo_context, depth=0):
        """Create path."""
        self._x = start_x
        self._y = start_y
        self._v = velocity
        self._rho = angular_momentum
        self._color = color
        self._points_right = []
        self._points_center = []
        self._points_left = []
        self._dt = 0.2
        self._ctx = cairo_context
        self._depth = depth
        self._subpaths = []

    def _update_pos(self):
        """Update current center point."""
        # TODO: process rho change by ``Momemtum`` class
        for i in range(len(self._rho) - 1):
            self._rho[i] += self._rho[i + 1] * self._dt
        # TODO: get vx/vy with ``polar2vec`` helper
        r, phi = self._v, self._rho[0]
        vx = r * math.cos(phi)
        vy = -r * math.sin(phi)

        self._x += vx
        self._y += vy

    def _generate(self):
        """Generate a path using angular momentum."""
        for i in range(300):
            self._points_center.append((self._x, self._y))
            self._points_left.append((self._x + 1, self._y + 1))
            self._points_right.append((self._x - 1, self._y - 1))

            if random.random() < 0.01 and self._depth < 7:
                new_rho = self._rho[:]
                new_rho[-1] = -new_rho[-1]
                subpath = FractalPath(self._x, self._y, new_rho, self._v / 1.1,
                                      self._color, self._ctx, self._depth + 1)
                self._subpaths.append(subpath)

            self._update_pos()

    def draw(self):
        """Draw the whole path."""
        self._generate()
        points = self._points_left + self._points_right[::-1]
        if not points:
            return

        self._ctx.set_source_rgba(*self._color)
        self._ctx.move_to(*points[0])
        for point in points[1:]:
            self._ctx.line_to(*point)
        self._ctx.fill()

        for subpath in self._subpaths:
            subpath.draw()


if __name__ == "__main__":
    WIDTH, HEIGHT = 1024, 1024
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    pat = cairo.SolidPattern(0, 0, 0, 1)
    # pat = cairo.SolidPattern(1, 0.9, 0.8, 1)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source(pat)
    ctx.fill()

    momentum = [
        (random.random() - 0.5) * 1,
        (random.random() - 0.5) * 0.1,
        (random.random() - 0.5) * 0.01,
        0.001,
    ]
    print(momentum)
    color = (1, 0.7, 0, 0.3)
    # color = (0, 0, 0, 0.3)
    path = FractalPath(320, 540, momentum, 2, color, ctx)
    path.draw()
    surface.write_to_png("test.png")
