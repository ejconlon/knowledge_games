#!/usr/bin/env python

class SatMat(object):
	@staticmethod
	def from_sentence_tokens(sentence_tokens, labels):
		tokstr = "".join(sentence_tokens)
		disjunctions = tokstr.split("&")
		grid = []
		for d in disjunctions:
			terms = d[1:-1].split("|")
			assert len(terms) <= len(labels)
			row = ["*" for i in xrange(len(labels))]
			for t in terms:
				val = "1"
				if t[0] == "~":
					val = "0"
					t = t[1:]
				pos = labels.index(t)
				row[pos] = val
			grid.append(row)
		return SatMat(grid)

	def __init__(self, grid):
		self.grid = grid

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

"""
def is_cnf_simple(tokens):
	token_iter = iter(tokens)
	in_paren = True
	op_stack = []
	while True:
		try:
			t = token_iter.next()
			if t == "(":
				if in_paren:
					return False
				else:
					in_paren = True
			elif t == ")":
				if not in_paren:
					return False
				else:
					in_paren = False
			elif t in "~&|"
		except StopIteration:
			return not in_paren
"""

def test():
	example_mat_string = "0 0 *\n* 1 1\n* 1 0\n1 * 0"

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

if __name__ == "__main__":
	test()
