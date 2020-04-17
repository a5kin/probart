#!/usr/bin/python3

__author__ = "Andrey Zamaraev (a5kin)"

import math
import random

import cairo
import numpy as np


class EntropyCanvas:

    def __init__(self, width, height, color):
        """Create canvas."""
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        self.ctx = cairo.Context(self.surface)
        self.ctx.scale(width, height)
        self._background(color)

    def _background(self, color):
        """Create canvas background."""
        pat = cairo.SolidPattern(*color)
        self.ctx.rectangle(0, 0, 1, 1)
        self.ctx.set_source(pat)
        self.ctx.fill()

    def _shift(self, x, y, deviation):
        """Return deviated value."""
        x_d = x + random.gauss(0.5, 0.2) * deviation * 2 - deviation / 2
        y_d = y + random.gauss(0.5, 0.2) * deviation * 2 - deviation / 2
        return x_d, y_d

    def _distort(self, path, deviation):
        """Distort given path."""
        interpolated_path = []
        for p1, p2 in zip(path[:-1], path[1:]):
            segment_len = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            num_subsegments = max(1, segment_len // 0.01)
            segment = np.linspace(p1, p2, num_subsegments)
            interpolated_path += segment.tolist()
        interpolated_path.append(path[-1])

        res_path = []
        for x, y in interpolated_path:
            x, y = self._shift(x, y, deviation)
            res_path.append((x, y))
        res_path[0] = res_path[0]
        res_path[-1] = res_path[-1]

        return res_path

    def line(self, path, color, width, dev, subdev):
        """Draw humanized line."""
        if path[0] != path[-1]:
            dpath = [self._shift(x, y, dev) for x, y in path]
        else:
            dpath = [self._shift(x, y, dev) for x, y in path[:-1]]
            dpath += [dpath[0]]

        for p1, p2 in zip(dpath[:-1], dpath[1:]):
            subpath = self._distort((p1, p2), deviation=subdev)
            self.ctx.move_to(*subpath[0])
            for x, y in subpath[1:]:
                self.ctx.line_to(x, y)

        self.ctx.set_source_rgba(*color)
        self.ctx.set_line_width(width)
        self.ctx.stroke()

    def multiline(self, path, color1, color2, num_clones, width,
                  dev=0.01, subdev=0.001):
        """Draw line several times with variations."""
        colors = np.linspace(color1, color2, num_clones).tolist()
        for color in colors:
            self.line(path, color, width, dev, subdev)

    def save_to(self, filename):
        """Save result to a file."""
        self.surface.write_to_png(filename)
