#!/usr/bin/env python

import base
import copy
import logging

class LogWrapper(object):
	def __init__(self, name):
		self.wrap = logging.getLogger(name)
	def debug(self, *args): self.log(logging.DEBUG, *args)
	def info(self, *args): self.log(logging.INFO, *args)
	def warn(self, *args): self.log(logging.WARN, *args)
	def error(self, *args): self.log(logging.ERROR, *args)
	def log(self, level, *args):
		for arg in args:
			self.wrap.log(level, arg)

log = LogWrapper("chess")
th = logging.FileHandler('/tmp/chess.log')
log.wrap.addHandler(th)
log.wrap.setLevel(logging.DEBUG)

class ChessConstants:
	WHITE = "W"
	BLACK = "B"
	COLORS = [WHITE, BLACK]
	PAWN_DIRECTION = {WHITE: -1, BLACK: 1}

def sgn(num):
	if num == 0: return 0
	elif num > 0: return 1
	else: return -1

class Piece(object):
	def __init__(self, color):
		self.color = color
		self.moved = False
		self.abbr = None
	def is_valid_move(self, move, grid):
		#raise Exception("OVERRIDE")
		log.warn("need to overrride piece is_valid_move")
		return True # TODO
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return '<piece abbr="%s" color="%s" moved="%s" />' % \
				(self.abbr, self.color, self.moved)

class Pawn(Piece):
	def __init__(self, color):
		Piece.__init__(self, color)
		self.abbr = "p"
	def is_valid_move(self, move, grid):
		delta = grid.delta(move)
		target_piece = grid.get_end(move)
		if abs(delta['col']) > 1:
			log.warn("Pawn cannot move more than 1 column", move, grid)
			return False
		elif sgn(delta['row']) != ChessConstants.PAWN_DIRECTION[self.color]:
			log.warn("Must move forward", move, grid)
			return False
		elif delta['col'] != 0 and target_piece is None:
			log.warn("Cannot move to adjacent column w/o capture", move, grid)
			return False
		elif delta['col'] == 0 and target_piece is not None:
			log.warn("Cannot capture piece in same column", move, grid)
			return False
		elif abs(delta['row']) > 2:
			log.warn("Can never move more than two", move, grid)
			return False
		elif abs(delta['row']) == 2 and self.moved:
			log.warn("Can only move 2 on first move", move, grid)
			return False
		return True

class Rook(Piece):
	def __init__(self, color):
		Piece.__init__(self, color)
		self.abbr = "R"
	def is_valid_move(self, move, grid):
		delta = grid.delta(move)
		if abs(delta['col']) != 0 and abs(delta['row']) != 0:
			log.warn("Can only move in one file", move, grid)
			return False
		elif not grid.clear_path(move):
			log.warn("Not clear path", move, grid)
			return False
		return True

class Knight(Piece):
	def __init__(self, color):
		Piece.__init__(self, color)
		self.abbr = "N"
	def is_valid_move(self, move, grid):
		delta = grid.delta(move)
		jumps = [abs(x) for x in delta.values()]
		jumps.sort()
		if jumps[0] != 1 or jumps[1] != 2:
			log.warn("Must move taxi-cab distance of 3 by (1,2)", move, grid)
			return False
		return True

class Bishop(Piece):
	def __init__(self, color):
		Piece.__init__(self, color)
		self.abbr = "B"
	def is_valid_move(self, move, grid):
		delta = grid.delta(move)
		if abs(delta['row']) != abs(delta['col']):
			log.warn("Must move diagonally", move, grid)
			return False
		elif not grid.clear_path(move):
			log.warn("Not clear path", move, grid)
			return False
		return True

class Queen(Piece):
	def __init__(self, color):
		Piece.__init__(self, color)
		self.abbr = "Q"
	def is_valid_move(self, move, grid):
		delta = grid.delta(move)
		if not grid.clear_path(move):
			log.warn("Not clear path", move, grid)
			return False

		# WHITE LISTING
		if abs(delta['row']) == abs(delta['col']):
			log.debug("Moving Queen like Bishop")
			return True 
		elif abs(delta['row']) == 0 or abs(delta['col']) == 0:
			log.debug("Moving Queen like Rook")
			return True
		return False 

class King(Piece):
	def __init__(self, color):
		Piece.__init__(self, color)
		self.abbr = "K"
	def is_valid_move(self, move, grid):
		jumps = [abs(x) for x in delta.values()]
		jumps.sort()
		# WHITE LISTING
		if (False):
			# CASTLE
			log.debug("Castling", move, grid)
			return True
		elif (jumps[0] == 0 or jumps[0] == 1) and jumps[1] != 1:
			log.debug("King moving max 2 taxi-cab", move, grid)
			return True	
		return False 

class ChessMove(base.Move):
	def __init__(self, start_col, start_row, end_col, end_row):
		self.start_col = start_col
		self.start_row = start_row
		self.end_col = end_col
		self.end_row = end_row
	def __str__(self):
		return '<move start="%s%s" end="%s%s" />' % \
				(self.start_col, self.start_row, self.end_col, self.end_row)

class ChessGrid(object):
	def __init__(self, array):
		self.array = array
	def _arow_acol(self, row, col):
		arow = 8 - int(row)
		acol = "abcdefgh".index(col)
		return arow, acol
	def get(self, row, col):
		arow, acol = self._arow_acol(row, col)
		return self.array[arow][acol]
	def get_start(self, move):
		return self.get(col=move.start_col, row=move.start_row)
	def get_end(self, move):
		return self.get(col=move.end_col, row=move.end_row)
	def set(self, row, col, piece):
		arow, acol = self._arow_acol(row, col)
		self.array[arow][acol] = piece
	def set_start(self, move, piece):
		self.set(col=move.start_col, row=move.start_row, piece=piece)
	def set_end(self, move, piece):
		self.set(col=move.end_col, row=move.end_row, piece=piece)
	def delta(self, move):
		arow_start, acol_start = self._arow_acol(row=move.start_row, col=move.start_col)
		arow_end, acol_end = self._arow_acol(row=move.end_row, col=move.end_col)
		return {'row': (arow_end-arow_start), 'col': (acol_end-acol_start)}
	def makes_sense(self, move):
		return (move.start_col in "abcdefgh" and
				move.start_row in "12345678" and
				move.end_col   in "abcdefgh" and
				move.end_row   in "12345678")
	def clear_path(self, move):
		return True # TODO
	@classmethod
	def empty(cls):
		array = [[None for i in xrange(8)] for j in xrange(8)]
		grid = ChessGrid(array)
		for col in "abcdefgh":
			grid.set("7", col, Pawn(ChessConstants.BLACK))
			grid.set("2", col, Pawn(ChessConstants.WHITE))
		for col in "ah":
			grid.set("8", col, Rook(ChessConstants.BLACK))
			grid.set("1", col, Rook(ChessConstants.WHITE))
		for col in "bg":
			grid.set("8", col, Knight(ChessConstants.BLACK))
			grid.set("1", col, Knight(ChessConstants.WHITE))
		for col in "cf":
			grid.set("8", col, Bishop(ChessConstants.BLACK))
			grid.set("1", col, Bishop(ChessConstants.WHITE))
		for col in "d":
			grid.set("8", col, Queen(ChessConstants.BLACK))
			grid.set("1", col, Queen(ChessConstants.WHITE))
		for col in "e":
			grid.set("8", col, King(ChessConstants.BLACK))
			grid.set("1", col, King(ChessConstants.WHITE))
		return grid
	def copy(self):
		array = [[x for x in self.array[j]] for j in xrange(len(self.array))]
		return ChessGrid(array)
	def __str__(self):
		t = "  | a| b| c| d| e| f| g| h|\n"
		t +="---------------------------\n"
		for row in "87654321":
			t += " "+row+"|"
			for col in "abcdefgh":
				s = "  "
				p = self.get(row, col)
				if p is not None:
					s = p.color+p.abbr
				t += s+"|"
			t += "\n"
			t +="---------------------------\n"
		return t[:-1]


class ChessBoard(base.Board):
	def __init__(self, grid):
		self.grid = grid
		self.lost = {ChessConstants.WHITE: [],
				ChessConstants.BLACK: []}

	@classmethod
	def empty(cls):
		return ChessBoard(ChessGrid.empty())

	def __str__(self):
		whitelost = "".join(piece.abbr for piece in self.lost[ChessConstants.WHITE])
		blacklost = "".join(piece.abbr for piece in self.lost[ChessConstants.BLACK])
		s = "LOST: W [%s] B [%s]\n" % (whitelost, blacklost)
		s += str(self.grid)
		return s

	def who_won(self):
		return None # TODO

	def is_valid_move(self, who, move):
		if not self.grid.makes_sense(move):
			log.warn("Does not make sense", move)
			return False
		moving_piece = self.grid.get_start(move)
		target_piece = self.grid.get_end(move)
		if moving_piece is None:
			log.warn("No piece to move", move, self.grid)
			return False
		elif moving_piece.color != who:
			log.warn("Not right color", who, moving_piece, move)
			return False
		elif moving_piece == target_piece:
			log.warn("Cannot no-op", who, moving_piece, move)
			return False
		elif target_piece is not None and moving_piece.color == target_piece.color:
			log.warn("Cannot capture own piece", who, moving_piece, target_piece, move)
			return False
		else:
			return moving_piece.is_valid_move(move, self.grid)

	def valid_moves(self):
		return [] # TODO

	def result(self, who, move):
		log.info(move, who)
		board = copy.deepcopy(self)
		moving_piece = copy.deepcopy(board.grid.get_start(move))
		target_piece = board.grid.get_end(move)
		board.grid.set_start(move, None)
		if target_piece is not None:
			log.info("Losing piece", target_piece)
			board.lost[target_piece.color].append(target_piece)
		board.grid.set_end(move, moving_piece)
		moving_piece.moved = True
		return board


class ChessPlayerAgent(base.Agent):
	def send_move(self, move, result):
		pass

	def get_move(self, board):
		start_col = raw_input("Choose start col (a-g): ")
		start_row = raw_input("Choose start row (1-8): ")
		end_col = raw_input("Choose end col (a-g): ")
		end_row = raw_input("Choose end row (1-8): ")
		return ChessMove(start_col, start_row, end_col, end_row)


if __name__ == "__main__":
	board = ChessBoard.empty()
	agents = [ChessPlayerAgent(color) for color in ChessConstants.COLORS]
	final_board, moves, winner = base.play(agents, board)


