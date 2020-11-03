#!/usr/bin/env python3
"""WIP: Sierpinski-like pattern generation."""

import math
import random
from collections import deque

import cairo
import tqdm

from utils import polar2vec

COLORS = [
    # (1, 0, 0, 1),
    (1, 1, 0, 1),
    # (0, 1, 0, 1),
    (0, 1, 1, 1),
    # (0, 0, 1, 1),
    (1, 0, 1, 1),
]


class Primitive:
    """Class representing a graphic primitive."""
    CIRCLE_TYPE = 0

    def __init__(self, x, y, radius, color, ptype=CIRCLE_TYPE):
        """Remember the primitive's position and size."""
        self.x, self.y = x, y
        self.radius = radius
        self._color = color
        self._ptype = ptype

    def draw(self, context):
        """Draw a primitive over Cairo context"""
        if self._ptype == self.CIRCLE_TYPE:
            context.set_line_width(0.5)
            context.set_source_rgba(*self._color)
            context.arc(self.x, self.y, max(0.5, self.radius),
                        0, 2 * math.pi)
            # context.stroke()
            context.fill()
            # context.paint()
            return

        raise ValueError("Unknown primitive type: %s" % self._ptype)


class FractalPattern:
    """Base class for recursive patterns generation."""

    def __init__(self, cairo_context, start_x, start_y, start_r,
                 num_points=3, num_iters=10,
                 r_mult=0.5, c_mult=0.5, d_angle=0,
                 fg_color=(1, 1, 1, 1)):
        """Initialize the pattern."""
        self._ctx = cairo_context
        self._num_points = num_points
        self._num_iters = num_iters
        self._r_mult = r_mult
        self._c_mult = c_mult
        self._fg_color = fg_color
        self._rand_shift = 0  # .01
        self._d_angle = d_angle

        self._objects = deque()
        init_primitive = Primitive(start_x, start_y, start_r, self._fg_color)
        self._objects.appendleft(init_primitive)
        self._n_iter = 1

    def iterate(self, need_draw=False):
        """Build next iteration's objects, non-recursive."""
        num_objs = len(self._objects)
        for _ in range(num_objs):
            cur_obj = self._objects.pop()
            if need_draw:
                cur_obj.draw(self._ctx)
            for i in range(self._num_points):
                d_angle = self._n_iter * self._d_angle
                dx, dy = polar2vec(
                    cur_obj.radius * self._c_mult,
                    (i * 2 - 0.5) * math.pi / self._num_points + d_angle,
                )
                new_x, new_y = cur_obj.x + dx, cur_obj.y + dy
                new_r = cur_obj.radius * self._r_mult
                if self._rand_shift > 0:
                    new_x += (random.random() * 2 - 1) * self._rand_shift * new_r
                    new_y += (random.random() * 2 - 1) * self._rand_shift * new_r
                new_obj = Primitive(new_x, new_y, new_r, COLORS[i])
                # new_obj = Primitive(new_x, new_y, new_r, self._fg_color)
                self._objects.appendleft(new_obj)

        self._n_iter += 1


def build_frame(width, height, radius, num_iters, num_points=3,
                r_mult=0.5, c_mult=0.5, d_angle=0,
                bg_color=(0, 0, 0, 1)):
    """Build a frame with given params."""
    # init canvas
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # fill background
    pat = cairo.SolidPattern(*bg_color)
    ctx.rectangle(0, 0, width, height)
    ctx.set_source(pat)
    ctx.fill()
    ctx.set_operator(cairo.Operator.DIFFERENCE)

    # create a pattern and do some iteration
    pattern = FractalPattern(
        ctx, width / 2, height / 2, radius,
        num_points=num_points,
        r_mult=r_mult,
        c_mult=c_mult,
        d_angle=d_angle,
        fg_color=(0, 0, 0, 1)
    )

    for _ in range(num_iters):
        pattern.iterate(need_draw=True)

    return surface


def render_video(width, height, duration, filename,
                 bg_color=(0, 0, 0, 1)):
    """Render a video."""
    import numpy as np
    from moviepy.editor import VideoClip

    def make_frame(frame_num):

        surface = build_frame(
            width, height, height * 0.4,
            num_iters=11,
            num_points=3,
            r_mult=0.5,
            c_mult=0.5,
            d_angle=frame_num * 25 * 2 * math.pi / 300,
            bg_color=bg_color,
        )
        buf = surface.get_data()
        frame_uint32 = np.ndarray(shape=(height, width), dtype=np.uint32, buffer=buf)

        frame = np.zeros(shape=(height, width, 3), dtype=np.uint8)
        frame[:, :, 0] = ((frame_uint32 >> 16) & 0xff).astype(np.uint8)
        frame[:, :, 1] = ((frame_uint32 >> 8) & 0xff).astype(np.uint8)
        frame[:, :, 2] = (frame_uint32 & 0xff).astype(np.uint8)

        return frame

    # render video
    animation = VideoClip(make_frame, duration=duration)
    animation.write_gif(filename, fps=25)


if __name__ == "__main__":
    # WIDTH, HEIGHT = 9933, 9933
    WIDTH, HEIGHT = 1920, 1024
    BACKGROUND_COLOR = (0, 0, 0, 1)
    NUM_FRAMES = 299

    render_video(WIDTH, HEIGHT, NUM_FRAMES / 25,
                 "sierpinoid.gif",
                 BACKGROUND_COLOR)

    # surface.write_to_png("sierpinoid.png")
