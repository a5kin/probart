#!/usr/bin/env python3
"""WIP: Recursive path generation."""

import math
import random

import cairo
import numpy as np
from matplotlib.path import Path

from utils import polar2vec


class FractalPath:
    """Base class for recursive path generation."""

    def __init__(self, start_x, start_y, angular_momentum,
                 velocity, color, cairo_context, paths, depth=0):
        """Create path."""
        self._x, self._y = start_x, start_y
        self._v = velocity
        self._rho = angular_momentum
        self._color = color
        self._points_right = []
        self._points_center = []
        self._points_left = []
        self._angles = []
        self._dt = 0.2
        self._margin = 30
        self._ctx = cairo_context
        self._depth = depth
        self._subpaths = []
        self._global_paths = paths

    def _move_by(self, r, phi):
        """Calculate new point moved by raduis/angle."""
        vx, vy = polar2vec(r, phi)
        return self._x + vx, self._y + vy

    def _update_momentum(self):
        """Update momentum state."""
        # TODO: process rho change by ``Momentum`` class
        for i in range(len(self._rho) - 1):
            self._rho[i] += self._rho[i + 1] * self._dt

    def _dead_end(self):
        """Test if current direction will intersect known paths."""
        start_x, start_y = self._move_by(0.001, self._rho[0])
        end_x, end_y = self._move_by(self._v * 10, self._rho[0])
        test_path = Path([(start_x, start_y), (end_x, end_y)])

        for i, path in enumerate(self._global_paths):
            if path.intersects_path(test_path, filled=i > 0):
                # print("Global intersect:", path)
                return True

        cur_path = Path(self._points_center)
        if cur_path.intersects_path(test_path, filled=False):
            # print("Current intersect:", cur_path)
            return True

        return False

    def _generate_sides(self):
        """Generate reft/right paths."""
        total_points = len(self._points_center)
        r_left, r_right = 1, 1
        path_data = zip(self._points_center, self._angles)
        for i, ((x, y), phi) in enumerate(path_data):
            r_left = math.sin(math.pi * i / total_points) ** 3
            r_left = 1 + r_left * 4
            r_right = math.sin(math.pi * i / total_points) ** 3
            r_right = 1 + r_right * 4
            self._x, self._y = x, y
            x_left, y_left = self._move_by(r_left, phi + math.pi / 2)
            x_right, y_right = self._move_by(r_right, phi - math.pi / 2)
            self._points_left.append((x_left, y_left))
            self._points_right.append((x_right, y_right))

        # delete path if it's intersecting with any other
        test_path = Path(self._points_left + self._points_right[::-1])
        for i, path in enumerate(self._global_paths):
            if path.intersects_path(test_path, filled=i > 0):
                self._points_left = []
                self._points_right = []
                break

    def _generate(self):
        """Generate a path using angular momentum."""
        while 1:
            self._points_center.append((self._x, self._y))
            self._angles.append(self._rho[0])

            self._update_momentum()
            if self._dead_end():
                break

            if random.random() < 0.08 and self._depth < 123333:
                new_rho = self._rho[:]
                new_rho[-1] = new_rho[-1] * random.choice([-1, 1])
                new_rho[-2] = new_rho[-2] * random.choice([-1, 1])
                new_rho[-3] = new_rho[-3] * random.choice([-1, 1])
                new_r = self._margin + 10 * random.random()
                new_phi = new_rho[0] + math.pi / 2 * [1, -1][new_rho[0] > 0]
                new_x, new_y = self._move_by(new_r, new_phi)
                if 0 < new_x < 1024 and 0 < new_y < 1024:
                    subpath = FractalPath(
                        new_x, new_y, new_rho, self._v,  # / 1.1,
                        self._color, self._ctx, self._global_paths,
                        self._depth + 1
                    )
                    self._subpaths.append(subpath)

            # Update current center point
            self._x, self._y = self._move_by(self._v, self._rho[0])

        self._generate_sides()

    def draw(self):
        """Draw the whole path."""
        self._generate()
        points = self._points_left + self._points_right[::-1]
        if len(points) < 23:
            return

        self._global_paths.append(Path(points))

        color = list(self._color[:3]) + [min(1, len(points) / 200)]
        self._ctx.set_source_rgba(*color)
        self._ctx.move_to(*points[0])
        for point in points[1:]:
            self._ctx.line_to(*point)
        self._ctx.fill()

        for subpath in self._subpaths:
            subpath.draw()


if __name__ == "__main__":
    WIDTH, HEIGHT = 1024, 1024
    MAIN_COLOR = (1, 0.7, 0, 0.3)
    # MAIN_COLOR = (0, 0, 0, 0.3)
    BACKGROUND_COLOR = (0, 0, 0, 1)
    # BACKGROUND_COLOR = (1, 0.9, 0.8, 1)

    # init canvas
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # fill background
    pat = cairo.SolidPattern(*BACKGROUND_COLOR)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source(pat)
    ctx.fill()

    # init paths collection
    border = Path([(0, 0), (WIDTH, 0), (WIDTH, HEIGHT), (0, HEIGHT), (0, 0)])
    paths = [border]

    r, phi = 0, 0
    for i in range(235):
        r += 2.2
        phi += 0.19

        # build start momentum
        momentum = [
            (random.random() - 0.5) * math.pi * 2,
            # phi + math.pi / 2,
            (random.random() - 0.5) * 0.1,
            (random.random() - 0.5) * 0.01,
            0.001,
        ]
        start_x = random.random() * WIDTH
        start_y = random.random() * HEIGHT
        # start_x, start_y = polar2vec(r, phi)
        # start_x += 512
        # start_y += 512

        # generate whole pattern
        path = FractalPath(start_x, start_y, momentum, 2,
                           MAIN_COLOR, ctx, paths)
        path.draw()

    surface.write_to_png("test.png")
