#!/usr/bin/env python

from sat import *

class Problem(object):
    def __init__(self, name=""):
        self.name = name
    def __enter__(self):
        print "*** START "+self.name
    def __exit__(self, a, b, c):
        print "*** END "+self.name+"\n"

with Problem("3.1.1") as X:
    print sub(['*','*','*'], ['1', '*', '1'])
    print sub(['1','0','*'], ['0', '1', '*'])
    print sub(['*','*','*'], ['1', '*', '*'])

with Problem("3.2.1") as X:
    g = [
        ['*', '*', '1', '1'],
        ['0', '*', '*', '*'],
        ['0', '1', '*', '*'],
        ['0', '1', '1', '*'],
        ['1', '*', '0', '*']
    ]
    s = [['*', '*', '*', '*']]
    for row in g:
        s = suball(s, row)
        print s
    print s

    sm = SatMat(g).to_equiv_mat()
    print list(sm.sat_by_counting())

with Problem("3.3.5") as X:
    g = [
        ['*', '*', '1', '*', '0'],
        ['1', '1', '*', '*', '*']
    ]

    print sub(g[0], g[1])
    """
    s = [['*', '*', '*', '*','*']]
    for row in g:
        s = suball(s, row)
        print s
    print s

    sm = SatMat(g).to_equiv_mat()
    print list(sm.sat_by_counting())
    """

with Problem("3.4") as X:
    g = [
        ['1', '*', '*', '1'],
        ['0', '1', '*', '*'],
        ['1', '*', '0', '*'],
        ['*', '*', '0', '1']
    ]
    s = [['*', '*', '*', '*']]
    for row in g:
        s = suball(s, row)
        print s
    print s

    sm = SatMat(g).to_equiv_mat()
    print list(sm.sat_by_counting())

with Problem('3.5.5') as X:
    print sub(['*', '0', '*', '1'], ['0', '*', '1', '1'])
    print sub(['1','*', '*', ], ['1','1','0'])
    print sub(['*', '1', '*', '1'], ['1', '*', '1', '*'])

with Problem("3.6") as X:
    g = [
        ['0', '*', '1'],
        ['*', '1', '0'],
        ['*', '0', '0'],
        ['1', '*', '1']
    ]
    s = [['*', '*', '*']]
    for row in g:
        s = suball(s, row)
        print s
    print s

    sm = SatMat(g).to_equiv_mat()
    print list(sm.sat_by_counting())