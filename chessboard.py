#!/usr/bin/env python

import base

class Piece(object):
    def __init__(self, color):
        self.color = color
        self.moved = False
        self.abbr = None

class Pawn(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = "p"
class Rook(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = "R"
class Knight(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = "N"
class Bishop(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = "B"
class Queen(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = "Q"
class King(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = "K"

class ChessGrid(object):
    def __init__(self, array):
        self.array = array
    def get(self, row, col):
        arow = 8 - int(row)
        acol = "abcdefgh".index(col)
        return self.array[arow][acol]
    def set(self, row, col, piece):
        arow = 8 - int(row)
        acol = "abcdefgh".index(col)
        self.array[arow][acol] = piece
    @classmethod
    def empty(cls):
        array = [[None for i in xrange(8)] for j in xrange(8)]
        grid = ChessGrid(array)
        black = "B"
        white = "W"
        for col in "abcdefgh":
            grid.set("7", col, Pawn(black))
            grid.set("2", col, Pawn(white))
        for col in "ah":
            grid.set("8", col, Rook(black))
            grid.set("1", col, Rook(white))
        for col in "bg":
            grid.set("8", col, Knight(black))
            grid.set("1", col, Knight(white))
        for col in "cf":
            grid.set("8", col, Bishop(black))
            grid.set("1", col, Bishop(white))
        for col in "d":
            grid.set("8", col, Queen(black))
            grid.set("1", col, Queen(white))
        for col in "e":
            grid.set("8", col, King(black))
            grid.set("1", col, King(white))
        return grid

class ChessBoard(base.Board):
    @classmethod
    def empty(cls):
        return ChessBoard(ChessGrid.empty())
    def __str__(self):
        t = ""
        for row in "12345678":
            for col in "abcdefgh":
                s = "  "
                p = self.grid.get(row, col)
                if p is not None:
                    s = p.color+p.abbr
                t += s+"|"
            t = t[:-1]+"\n"
        return t[:-1]

if __name__ == "__main__":
    board = ChessBoard.empty()
    print board

