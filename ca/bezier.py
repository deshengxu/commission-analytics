#!/usr/bin/env python

# ...

import os
import sys
import csv
import pandas as pd
import numpy as np


def generate_control_points(p0, p3, direction=0):
    x0, y0 = p0
    x3, y3 = p3
    if direction != 0:
        direction = 1

    # direction will be used to control whether curve at x direction (0) or y direction (1)
    x1 = x0 + (direction + 1) * (x3 - x0) / 2.0
    y1 = y0 + direction * (y3 - y0) / 2.0
    x2 = x3 - (direction + 1) * (x3 - x0) / 2.0
    y2 = y3 - direction * (y3 - y0) / 2.0

    np0 = (x0, y0)
    np1 = (x1, y1)
    np2 = (x2, y2)
    np3 = (x3, y3)
    # print(np0,np1,np2,np3)
    return np0, np1, np2, np3


def generate_bezier3(p0, p3, direction=0, steps=100):
    p0, p1, p2, p3 = generate_control_points(p0, p3, direction)
    new_xys = [p0, p1, p2, p3]

    bezier = make_bezier(new_xys)

    ts = [t / (steps * 1.0) for t in range(steps + 1)]
    return (bezier(ts))


def pascal_row(n):
    # This returns the nth row of Pascal's Triangle
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n // 2 + 1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    return result


def make_bezier(xys):
    # xys should be a sequence of 2-tuples (Bezier control points)
    n = len(xys)
    combinations = pascal_row(n - 1)

    def bezier(ts):
        # This uses the generalized formula for bezier curves
        # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
        result = []
        for t in ts:
            tpowers = (t ** i for i in range(n))
            upowers = reversed([(1 - t) ** i for i in range(n)])
            coefs = [c * a * b for c, a, b in zip(combinations, tpowers, upowers)]
            result.append(
                tuple(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in zip(*xys)))
        return result

    return bezier


def main():
    # 1.8, 1.9500000000000002, 2.4, 0.6000000000000001
    # p0 = [1.8, 1.95]
    p0 = [20.0, 20.0]
    # p3 = [ 2.4, 0.6]
    p3 = [200.0, 120.0]
    result = generate_bezier3(p0, p3, 0, 200)
    # print(result)
    print("len of result is:%d" % len(result))


if __name__ == "__main__":
    main()
