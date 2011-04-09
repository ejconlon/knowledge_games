#!/usr/bin/env python

from sat import *

class Problem(object):
    def __init__(self, name=""):
        self.name = name
    def __enter__(self):
        print "*** START "+self.name
    def __exit__(self, a, b, c):
        print "*** END "+self.name+"\n"

with Problem("1.1.1") as X:
    matstr = "1 * *\n* 1 0\n1 1 0\n* 0 0"
    mat = SatMat.from_mat_string(matstr)
    print mat
    print list(mat.to_sentence_tokens(["a", "b", "c"]))

with Problem("1.1.2") as X:
    matstr = "1\n0"
    mat = SatMat.from_mat_string(matstr)
    print mat
    print mat.sat_by_counting()
    print list(mat.to_sentence_tokens(["a", "b", "c"]))

with Problem("1.2.1") as X:
    sen  = "(a|~c)&(b|c)&(d|a|b)&(~a|~d)&(~b|~c)&c"
    mat = SatMat.from_sentence_tokens(tokenize(sen),["a", "b", "c", "d"])
    print mat

with Problem("1.2.2") as X:
    matstr = "0 1 * *\n* 1 * *\n* 0 0 *\n* * 0 1\n1 0 1 0"
    mat = SatMat.from_mat_string(matstr)
    print mat,"\n"
    eqm = mat.to_equiv_mat()
    print eqm
    print list(eqm.sat_by_counting())

with Problem("1.3.1/1.3.2") as X:
    labels = ["a", "b", "c"]
    sen = "(a|b)&(b|c)&(~a|~c)&(~b|~c)&(~a|b|c)"
    mat = SatMat.from_sentence_tokens(tokenize(sen), labels)
    print mat
    print ""
    print mat.to_dimacs()
    print ""
    print list(mat.to_equiv_mat().sat_by_counting())
    stash = Stash()
    print mat.is_sat_by_davis_putnam(stash, labels)
    for s in stash.stash:
        print s

with Problem("1.4.1") as X:
    dimstr = "-22 9 0\n22 -9 0\n22 1 0\n-9 8 0\n-1 8 0\n-8 7 0\n-7 0"
    print dimstr
    labels = [c for c in "abcdefghijklmnopqrstuvwxyz"]
    mat = SatMat.from_dimacs(dimstr)
    print mat
    cnf = mat.to_sentence_tokens(labels)
    print list(cnf)
    print "".join(list(cnf))

with Problem("1.5.2") as X:
    matstr = "0 0 0\n1 1 *\n0 1 *\n1 0 0"
    mat = SatMat.from_mat_string(matstr)
    print list(mat.to_equiv_mat().sat_by_counting())
    print ""
    stash = Stash()
    print mat.is_sat_by_davis_putnam(stash, labels)
    for s in stash.stash:
        print s

with Problem("1.6.1a") as X:
    labels = [x for x in "abc"]
    sen = "(a|~b)&(c|b)&(~a)"
    mat = SatMat.from_sentence_tokens(tokenize(sen), labels)
    print mat
    for x in mat.to_equiv_mat().sat_by_counting():
        print x

with Problem("1.6.1b") as X:
    labels = [x for x in "abcd"]
    sen = "(a|d|~c)&(~b|~d)&(~c)&(a)"
    mat = SatMat.from_sentence_tokens(tokenize(sen), labels)
    print mat
    for x in mat.to_equiv_mat().sat_by_counting():
        print x

with Problem("1.6.1c") as X:
    labels = [x for x in "abc"]
    sen = "(a|~c)&(~a|b)&(~b|~c)&(c)"
    mat = SatMat.from_sentence_tokens(tokenize(sen), labels)
    print mat
    for x in mat.to_equiv_mat().sat_by_counting():
        print x

with Problem("1.7.2") as X:
    matstr = "0 * 0\n1 * *\n0 1 *\n* 0 1"
    mat = SatMat.from_mat_string(matstr)
    print mat
    print ""
    print mat.to_equiv_mat()
    for x in mat.to_equiv_mat().sat_by_counting():
        print x




