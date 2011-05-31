#!/usr/bin/env python
from copy import deepcopy

class Stash(object):
    def __init__(self):
        self.stash = []
    def put(self, obj):
        self.stash.append(obj)
class NoOpStash(object):
    def put(self, obj): pass

class SatMat(object):
    @staticmethod
    def from_sentence_tokens(sentence_tokens, labels):
        tokstr = "".join(sentence_tokens)
        disjunctions = tokstr.split("&")
        grid = []
        for d in disjunctions:
            if d[0] == "(" and d[-1] == ")": d = d[1:-1]
            if "(" in d or ")" in d or "&" in d:
                raise Exception("INVALID DISJUNCTION: "+d)
            terms = d.split("|")
            assert len(terms) <= len(labels)
            row = ["*" for i in xrange(len(labels))]
            for t in terms:
                val = "1"
                if t[0] == "~":
                    val = "0"
                    t = t[1:]
                pos = labels.index(t)
                if row[pos] != "*":
                    raise Exception("DUPLICATE VAR: "+terms)
                row[pos] = val
            grid.append(row)
        return SatMat(grid)

    @staticmethod
    def from_mat_string(mat_string):
        lines = [l.strip() for l in mat_string.split("\n")]
        grid = []
        for line in lines:
            grid.append(line.split(" "))
        if len(grid) > 0:
            n = len(grid[0])
            for i in xrange(1, len(grid)):
                assert len(grid[i]) == n
        return SatMat(grid)

    @staticmethod
    def from_dimacs(dimacs):
        rows = [l.split(" ") for l in dimacs.split("\n")]
        nvars = 0
        for row in rows:
            if row[-1] != "0":
                raise Exception("No 0: "+row)
            for elt in row[:-1]:
                i = abs(int(elt))
                if i > nvars: nvars = i
        grid = []
        for row in rows:
            grow = ["*" for i in xrange(nvars)]
            for elt in row[:-1]:
                i = int(elt)
                if i > 0:
                    grow[i-1] = "1"
                else:
                    grow[abs(i)-1] = "0"
            grid.append(grow)
        return SatMat(grid)

    def __init__(self, grid):
        self.grid = grid
    def __eq__(self, other):
        return self.grid == other.grid

    def has_stars(self):
        for row in self.grid:
            for t in row:
                if t == "*":
                    return True
        return False

    def has_unique_rows(self):
        for i in xrange(1, len(self.grid)):
            row = self.grid[i]
            if row in self.grid[:i-1]:
                return False
        return True

    def to_equiv_mat(self):
        h = []
        for row in self.grid:
            stars = []
            for i in xrange(len(row)):
                if row[i] == "*":
                    stars.append(i)
            if len(stars) == 0:
                if row not in h:
                    h.append(row)
            else:
                rows = self._gen_rows(stars, row)
                for row in rows:
                    if row not in h:
                        h.append(row)
        return SatMat(h)

    def _gen_rows(self, stars, row):
        rows = []
        pos = stars[0]
        row0 = [r for r in row]
        row0[pos] = "0"
        row1 = [r for r in row]
        row1[pos] = "1"
        if len(stars) == 1:
            yield row0
            yield row1
        else:
            for r in self._gen_rows(stars[1:], row0):
                yield r
            for r in self._gen_rows(stars[1:], row1):
                yield r

    def to_sentence_tokens(self, labels):
        t = []
        for i in xrange(len(self.grid)):
            t.append("(")
            for j in xrange(len(self.grid[i])):
                s = self.grid[i][j]
                if s == "*":
                    continue
                if s == "0":
                    t.append("~")
                t.append(labels[j])
                t.append("|")
            if t[-1] == "|":
                t = t[:-1]
            t.append(")")
            t.append("&")
        if t[-1] == "&":
            t = t[:-1]
        return t

    def to_dimacs(self):
        s = ""
        for row in self.grid:
            for i in xrange(len(row)):
                t = row[i]
                v = str(i+1)
                if t == "0":
                    v = "-"+v
                if t != "*":
                    s += v+" "
            s += "0\n"
        if len(s) > 0:
            s = s[:-1]
        return s

    def sat_by_counting(self):
        if self.has_stars() or not self.has_unique_rows():
            raise Exception("Need to operate on equiv mat")
        if len(self.grid) == 0:
            return
        nvars = len(self.grid[0])
        if len(self.grid) == int(2**nvars):
            return
        else:
            poss = self._gen_rows([i for i in xrange(nvars)], ["*" for i in xrange(nvars)])
            for row in poss:
                if row not in self.grid:
                    yield self.row_not(row)

    def row_not(self, row):
        r = [x for x in row]
        for i in xrange(len(r)):
            if r[i] == "0":
                r[i] = "1"
            elif r[i] == "1":
                r[i] = "0"
        return r

    def is_sat_by_counting(self):
        return len(list(self.sat_by_counting())) != 0

    def is_sat_by_davis_putnam(self, stash=NoOpStash(), labels=None, ass=None):
        if ass is None: ass = []
        stash.put(self.grid)
        for row in self.grid:
            # if empty clause return false
            if len(row) == 0:
                stash.put("EMPTY CLAUSE (ret False)")
                return False
            all_stars = True
            for t in row:
                if t != "*":
                    all_stars = False
            # clause of all stars return false
            if all_stars:
                stash.put("ALL STARS (ret False)")
                return False
        # if no clauses return false
        if len(self.grid) == 0:
            stash.put("NO CLAUSES (ret True)")
            return True
        # now recurse with assignment
        for val in "10":
            sub = self._assign_and_filter(val)
            labelsp = None
            lstr = ""
            if labels is not None:
                lstr = " to "+labels[0]
                labelsp = labels[1:]
            stash.put("ASSIGNING "+val+lstr)
            assp = ass+[val]
            if sub.is_sat_by_davis_putnam(stash, labelsp, assp):
                stash.put("SATISFYING ASSIGNMENT: "+str(assp))
                return True
        return False

    def _assign_and_filter(self, val):
        if len(self.grid) == 0 or len(self.grid[0]) == 0:
            raise Exception("Invalid grid")
        grid2 = []
        for row in self.grid:
            if row[0] == val:
                continue
            rowp = [x for x in row[1:]]
            grid2.append(rowp)
        return SatMat(grid2)


    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "\n".join(" ".join(row) for row in self.grid)


def tokenize(chars):
    char_iter = iter(chars)
    current = ""
    while True:
        try:
            c = char_iter.next()
            if c in " \t\n":
                if len(current) > 0: yield current
                current = ""
            elif c in "()&|~":
                if len(current) > 0: yield current
                current = ""
                yield c
            else:
                current += c
        except StopIteration:
            if len(current) > 0: yield current
            return

subtable = {'*': {}, '1': {}, '0': {}}
subtable['*']['1'] = "0p"
subtable['*']['0'] = "1p"
subtable['*']['*'] = "*"
subtable['1']['*'] = "1"
subtable['0']['*'] = "0"
subtable['1']['1'] = "1"
subtable['0']['0'] = "0"
def sub(c1, c2):
    assert len(c1) == len(c2)
    if c1 == c2:
        return []
    try:
        t = [subtable[c1[i]][c2[i]] for i in xrange(len(c1))]
        print "t?", t
        return expand(t)
    except KeyError:
        return None

def suball(s, c2):
    res = []
    for row in s:
        rows = sub(row, c2)
        if rows is not None:
            res.extend(rows)
        else:
            res.append(row)
    return res

def interleave(c1, c2):
    assert len(c1) == len(c2)
    r = []
    for i in xrange(len(c1)):
        yield c1[i]
        yield c2[i]

def expand(c):
    if c is None:
        return None
    primed = []
    for i in xrange(len(c)):
        if c[i] == "0p" or c[i] == "1p":
            primed.append(i)
    res = []
    pos = {}
    neg = {}
    for x in primed:
        if c[x] == '0p':
            pos[x] = ('0')
            neg[x] = ('1')
        else:
            pos[x] = ('1')
            neg[x] = ('0')
    if len(primed) == 0:
        return [c]
    once = False
    while len(primed) > 1:
        once = True
        idx = primed[0]
        primed = primed[1:]
        c_pos = deepcopy(c)
        for i in xrange(len(c_pos)):
            if i == idx:
                c_pos[i] = pos[i]
            else:
                if c_pos[i] not in '01*':
                    c_pos[i] = '*'
        res.append(c_pos)
        c_pos = None
        c_neg = deepcopy(c)
        for i in xrange(len(c_neg)):
            if i == idx:
                c_neg[i] = neg[i]
            else:
                if c_neg[i] not in '01*':
                    c_neg[i] = pos[i]
        res.append(c_neg)
        c_neg = None
    if not once:
        idx = primed[0]
        primed = primed[1:]
        c_pos = deepcopy(c)
        for i in xrange(len(c_pos)):
            if i == idx:
                c_pos[i] = pos[i]
            else:
                if c_pos[i] not in '01*':
                    c_pos[i] = '*'
        res.append(c_pos)
    return res


def test():
    """
    example_mat_string = "0 0 *\n* 1 1\n* 1 0\n1 * 0"
    equiv_mat_string = "0 0 0\n0 0 1\n0 1 1\n1 1 1\n0 1 0\n1 1 0\n1 0 0"

    example_sen = "(~a | ~b) & (b | c) & (b | ~c) & (a | ~c)"
    example_tokens = "( ~ a | ~ b ) & ( b | c ) & ( b | ~ c ) & ( a | ~ c )".split(" ")

    tokens = list(tokenize(example_sen))
    print tokens
    print example_tokens
    assert tokens == example_tokens
    labels = ["a", "b", "c"]
    mat = SatMat.from_sentence_tokens(tokens, labels)
    print mat
    assert str(mat) == example_mat_string
    mat_tokens = mat.to_sentence_tokens(labels)
    print mat_tokens
    assert mat_tokens == tokens

    assert mat.has_stars()
    assert mat.has_unique_rows()
    equiv = mat.to_equiv_mat()
    print equiv
    assert str(equiv) == equiv_mat_string
    assert not equiv.has_stars()
    assert equiv.has_unique_rows()
    sat = equiv.sat_by_counting()
    print sat
    assert list(sat) == [["0", "1", "0"]]
    stash1 = Stash()
    assert mat.is_sat_by_davis_putnam(stash1, labels)
    for s in stash1.stash: print s

    non_sat_mat_string = "0 0 *\n* 1 1\n1 1 *\n* 1 0\n1 0 *"
    nsmat = SatMat.from_mat_string(non_sat_mat_string)
    print nsmat
    assert not nsmat.to_equiv_mat().is_sat_by_counting()
    stash2 = Stash()
    assert not nsmat.is_sat_by_davis_putnam(stash2, labels)
    for s in stash2.stash: print s

    dt_mat_string = "1 1 0 *\n* 1 1 1\n1 0 * *\n* * 0 0"
    dt_dimacs_string = "1 2 -3 0\n2 3 4 0\n1 -2 0\n-3 -4 0"
    dt_mat = SatMat.from_mat_string(dt_mat_string)
    dt_dimacs = dt_mat.to_dimacs()
    print dt_dimacs
    assert dt_dimacs == dt_dimacs_string
    dt_mat2 = SatMat.from_dimacs(dt_dimacs)
    assert dt_mat == dt_mat2
    """
    assert expand(['1','0']) == [['1','0']]
    s = sub(['1','*','1','*','0'], ['*','1','1','0','*'])
    assert s == expand(['1','0p','1','1p','0'])
    print s
    #assert len(s) == 3


    print "HERE"
    s = sub(['*','*','*'], ['1','*','1'])
    print s
    sm = SatMat(s).to_equiv_mat()
    print sm
    s = suball(s, ['0','1','*'])
    print s
    sm = SatMat(s).to_equiv_mat()
    print sm
    s = suball(s, ['*','0','0'])
    print s
    sm = SatMat(s).to_equiv_mat()
    print sm

    print "THERE"
    g = [ ['1','*','1'], ['0','1','*'], ['*','0','0']]
    print list(SatMat(g).to_equiv_mat().sat_by_counting())

if __name__ == "__main__":
    test()
