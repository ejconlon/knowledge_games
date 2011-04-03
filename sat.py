#!/usr/bin/env python

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

	def __init__(self, grid):
		self.grid = grid

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

	def sat_by_counting(self):
		if self.has_stars() or not self.has_unique_rows():
			raise Exception("Need to operate on equiv mat")
		if len(self.grid) == 0:
			return None
		nvars = len(self.grid[0])
		if len(self.grid) == int(2**nvars):
			return None
		else:
			poss = self._gen_rows([i for i in xrange(nvars)], ["*" for i in xrange(nvars)])
			for row in poss:
				if row not in self.grid:
					return row
	
	def is_sat_by_counting(self):
		return self.sat_by_counting() is not None

	def is_sat_by_davis_putnam(self):
		for row in self.grid:
			# if empty clause return false
			if len(row) == 0:
				return False
			all_stars = True
			for t in row:
				if t != "*":
					all_stars = False
			# clause of all stars return false
			if all_stars:
				return False
		# if no clauses return false
		if len(self.grid) == 0:
			return True

		# now recurse with assignment
		if self._assign_and_filter("1").is_sat_by_davis_putnam():
			return True
		elif self._assign_and_filter("0").is_sat_by_davis_putnam():
			return True
		else:
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


def test():
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
	assert sat == ["1", "0", "1"]
	assert mat.is_sat_by_davis_putnam()

	non_sat_mat_string = "0 0 *\n* 1 1\n1 1 *\n* 1 0\n1 0 *"
	nsmat = SatMat.from_mat_string(non_sat_mat_string)
	print nsmat
	assert not nsmat.to_equiv_mat().is_sat_by_counting()
	assert not nsmat.is_sat_by_davis_putnam()

if __name__ == "__main__":
	test()
