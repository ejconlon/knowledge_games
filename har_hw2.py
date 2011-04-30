#!/usr/bin/env python

from sat import *

class Problem(object):
    def __init__(self, name=""):
        self.name = name
    def __enter__(self):
        print "*** START "+self.name
    def __exit__(self, a, b, c):
        print "*** END "+self.name+"\n"

with Problem("2.5.b") as X:
    matstr = "\n".join([
    "* * * 1 *",
    "0 * * * *",
    "* * 0 * *",
    "* 0 * * *",
    "* * * * 1"
    ])
    mat = SatMat.from_mat_string(matstr)
    print mat
    print ""
    print mat.to_equiv_mat()
    for x in mat.to_equiv_mat().sat_by_counting():
        print x

with Problem("2.5.c") as X:
    matstr = "\n".join([
    "0 * * 1 *",
    "1 * * 0 *"
    ])
    mat = SatMat.from_mat_string(matstr)
    print mat
    print ""
    print mat.to_equiv_mat()
    for x in mat.to_equiv_mat().sat_by_counting():
        print x
