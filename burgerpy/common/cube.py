# -*- coding: utf-8 -*-
import itertools
import numpy as np
import random


class Cube(object):
    points = [
        (-1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (1.0, 1.0, -1.0),
        (1.0, -1.0, -1.0),
        (-1.0, -1.0, 1.0),
        (-1.0, 1.0, 1.0),
        (1.0, 1.0, 1.0),
        (1.0, -1.0, 1.0),
    ]

    lines = [
        (1, 2),
        (0, 1),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (0, 4),
        (1, 5),
        (2, 6),
        (3, 7)
    ]

    def rotate(self, x_angle, y_angle):
        x_mat = Transformations.rotate_x_axis(x_angle)
        y_mat = Transformations.rotate_y_axis(y_angle)
        trans = np.dot(x_mat, y_mat)

        self.points = map(lambda x: np.dot(trans, x), self.points)

    def draw_line(self, frame, line, v='#'):
        p0 = self.points[line[0]]
        p1 = self.points[line[1]]
        x0, y0 = frame.scale(*p0)
        x1, y1 = frame.scale(*p1)

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else - 1
        sy = 1 if y0 < y1 else - 1
        err = dx - dy

        for vb in itertools.cycle(v):
            frame.putpixel(x0, y0, vb)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw(self, frame, v):
        map(lambda line: self.draw_line(frame, line, v), self.lines)


class Frame(object):
    def __init__(self, W=40, H=25):
        self.w = W
        self.h = H
        self.buf = []
        for i in xrange(H):
            self.buf.append([' '] * W)

    def __iter__(self):
        self.i = 0
        return self

    def scale(self, x, y, _):
        px = int((x*0.7 + 1.0)/2 * self.w)
        py = int((y*0.4 + 1.0)/2 * self.h)

        return (px, py)

    def putpixel(self, x, y, v):
        if x >= self.w or y >= self.h:
            return None

        self.buf[y][x] = v

    def flush(self):
        return
        for i in xrange(self.w):
            for j in xrange(self.h):
                self.buf[i][j] = 0.0

    def next(self):
        if self.i == self.h:
            raise StopIteration()
        line = ''

        for j in xrange(self.w):
            line += self.buf[self.i][j]

        self.i += 1

        if line.strip() == '':
            return self.next()

        return line


class Transformations(object):
    @staticmethod
    def rotate_x_axis(angle):
        return np.array([
            [1.0, 0.0, 0.0],
            [0.0, np.cos(angle), -np.cos(angle)],
            [0.0, np.sin(angle), np.cos(angle)]
        ])

    @staticmethod
    def rotate_y_axis(angle):
        return np.array([
            [np.cos(angle), 0.0, np.sin(angle)],
            [0.0, 1.0, 0.0],
            [-np.sin(angle), 0.0, np.cos(angle)]
        ])


class Renderer(object):
    def get(self, v):
        f = Frame()
        c = Cube()
        x = random.uniform(.0, 1.0)
        y = random.uniform(.0, 1.0)
        c.rotate(x, y)
        c.draw(f, v)

        return f


if __name__ == "__main__":
    r = Renderer()
    r.run()
