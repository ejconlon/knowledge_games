#!/usr/bin/env python

class Move(object):
	def __init__(self, row, col):
		self.row = row
		self.col = col
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return "<move row=\""+str(self.row)+"\" col=\""+str(self.col)+"\" />"
	def to_pgn(self):
		cchar = "abc"[self.col]
		rchar = str(3-self.row)	
		return cchar+rchar
	@staticmethod
	def from_pgn(self, pgn):
		cchar, rchar = pgn[0], pgn[1]
		col = "abc".index(cchar)	
		row = 3 - int(rchar) 
		return Move(row, col)

class Board(object):
	def __init__(self, previous=None):
		if previous is not None:
			self.grid = [[previous.grid[i][j] for j in xrange(len(previous.grid[i]))] for i in xrange(len(previous.grid))]
		else:
			self.grid = [[None for j in xrange(3)] for i in xrange(3)]
	def do_move(self, who, move):
		self.grid[move.row][move.col] = who
	def is_valid_row_col(self, row, col):
		return row >= 0 and row < 3 and col >= 0 and col < 3 and self.grid[row][col] is None
	def is_valid_move(self, move):
		return self.is_valid_row_col(move.row, move.col)
	def who_won(self):
		# CHECK ROWS 
		for i in xrange(3):
			s = self.grid[i][0]
			if s is None:
				continue
			found = True
			for j in xrange(1,3):
				if self.grid[i][j] != s:
					found = False
					break
			if found: return s

		# CHECK COLS 
		for i in xrange(3):
			s = self.grid[0][i]
			if s is None:
				continue
			found = True
			for j in xrange(1,3):
				if self.grid[j][i] != s:
					found = False
					break
			if found: return s

		# CHECK DIAGONALS
		s = self.grid[1][1]
		if s is not None:
			if (s == self.grid[0][0] and s == self.grid[2][2]) or \
			   (s == self.grid[0][2] and s == self.grid[2][0]):
				return s

		# CHECK FOR DRAW
		for i in xrange(3):
			for j in xrange(3):
				if self.grid[i][j] is None:
					return None

		return "draw"

	def __repr__(self):
		return self.__str__()
	def __str__(self):
		t = ""
		for i in xrange(3):
			for j in xrange(3):
				s = self.grid[i][j]
				if s is None:
					s = " "
				t += s+"|"	
			t = t[:-1]+"\n"
		return t[:-1]

def board_iterator(moves):
	prev = Board()
	yield prev
	whos = ["X", "O"]
	turn = 0
	for move in moves:
		board = Board(prev) 
		board.do_move(whos[turn], move)
		yield board
		prev = board
		turn = (turn + 1) % 2

class Agent(object):
	def __init__(self, name):
		self.name = name
	def get_move(self, board):
		raise Exception("Override me")
	def __str__(self):
		return self.name

class PlayerAgent(Agent):
	def get_move(self, board):
		row = int(raw_input("Choose row (1-3): "))
		col = int(raw_input("Choose col (1-3): "))
		return Move(row-1, col-1)

import random
class RandomAgent(Agent):
	def get_move(self, board):
		valid = False
		move = None
		while not valid:
			row = random.randint(0,2)
			col = random.randint(0,2)
			move = Move(row, col)
			valid = board.is_valid_move(move)
		return move

def play(agents):
	print "welcome"
	moves = []
	board = Board()
	turn = 0
	winner = None

	while winner is None:
		agent = agents[turn]
		print "It's "+str(agent)+"'s turn"
		print board
		move = agent.get_move(board)
		if not board.is_valid_move(move):
			print "Invalid move"
		else:
			moves.append(move)
			board.do_move(agent.name, move)
			turn = (turn + 1) % 2
			winner = board.who_won()

	print ""

	print board
	if winner == "draw":
		print "DRAW"
	else:
		print winner+" won!"

	return moves, winner 

def pairs(moves):
	last = None
	for move in moves:
		if last is None:
			last = move
		else:
			yield (last, move)
			last = None
	if last is not None:
		yield (last, None)

def format_meta(meta):
	s = ""
	for k, v in meta:
		s += '[%s "%s"]\n' % (k, v)
	return s

def format_pair(pair, turn):
	s = "%d." % turn
	a, b = pair
	s += a.to_pgn() + " "
	if b is not None:
		s += b.to_pgn()
	return s

def write_game(agents, moves, winner):
	meta = []
	meta.append(("Event", ""))
	meta.append(("Game", "TicTacToe"))
	meta.append(("White", agents[0].name))
	meta.append(("Black", agents[1].name))
	result = None
	if winner == "draw":
		result = "1/2-1/2"
	elif winner == agents[0].name:
		result = "1-0"
	else:
		result = "0-1"
	meta.append(("Result", result))

	out = ""
	turn = 0
	for pair in pairs(moves):
		turn += 1
		out += format_pair(pair, turn)+"\n"

	return "\n".join([format_meta(meta), out, ""])

if __name__ == "__main__":
	import sys
	n = int(sys.argv[1])
	f = None
	if len(sys.argv) > 2:
		fn = sys.argv[2]
		f = open(fn, "a")

	for i in xrange(n):
		agents = [RandomAgent("X"), RandomAgent("O")]
		moves, winner = play(agents)
		print moves
		for board in board_iterator(moves):
			print board
			print ""
		pgn = write_game(agents, moves, winner)
		print pgn
		if f is not None:
			f.write(pgn)

	if f is not None:
		f.close()


