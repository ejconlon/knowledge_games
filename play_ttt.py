#!/usr/bin/env python

class Move(object):
	def __init__(self, sym, row, col):
		self.sym = sym
		self.row = row
		self.col = col
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return "<move sym=\""+str(self.sym)+"\" row=\""+str(self.row)+"\" col=\""+str(self.col)+"\" />"

class Board(object):
	def __init__(self, previous=None):
		if previous is not None:
			self.grid = [[previous.grid[i][j] for j in xrange(len(previous.grid[i]))] for i in xrange(len(previous.grid))]
		else:
			self.grid = [[None for j in xrange(3)] for i in xrange(3)]
	def do_move(self, move):
		self.grid[move.row][move.col] = move.sym
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

		return None	

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
	for move in moves:
		board = Board(prev) 
		board.do_move(move)
		yield board
		prev = board

def play():
	print "welcome"
	moves = []
	board = Board()
	players = ["X", "O"]
	turn = 0
	winner = None

	while winner is None:
		cur = players[turn]
		print "It's "+cur+"'s turn"
		print board
		row = int(raw_input("Choose row (1-3): "))
		col = int(raw_input("Choose col (1-3): "))
		move = Move(cur, row-1, col-1)
		if not board.is_valid_move(move):
			print "Invalid move"
		else:
			moves.append(move)
			board.do_move(move)
			turn = (turn + 1) % 2
			winner = board.who_won()

	print ""

	print board
	print winner+" won!"
	return moves 

if __name__ == "__main__":
	moves = play()
	print moves
	for board in board_iterator(moves):
		print board
		print ""


