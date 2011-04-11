#!/usr/bin/env python

import base

class TTTMove(base.Move):
    def __init__(self, row, col):
        self.row = row
        self.col = col
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
        return TTTMove(row, col)

class TTTBoard(base.Board):
    def result(self, who, move):
        grid = [[i for i in self.grid[j]] for j in xrange(len(self.grid))]
        grid[move.row][move.col] = who
        return TTTBoard(grid)
    def is_valid_row_col(self, row, col):
        return row >= 0 and row < 3 and col >= 0 and col < 3 and self.grid[row][col] is None
    def is_valid_move(self, who, move):
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

    @classmethod
    def empty(cls):
        grid = [[None for i in xrange(3)] for j in xrange(3)]
        return TTTBoard(grid)


def board_iterator(moves, board):
    yield board
    whos = ["X", "O"]
    turn = 0
    for move in moves:
        board = board.result(whos[turn], move)
        yield board
        turn = (turn + 1) % 2

class PlayerAgent(base.Agent):
    def get_move(self, board):
        row = int(raw_input("Choose row (1-3): "))
        col = int(raw_input("Choose col (1-3): "))
        return TTTMove(row-1, col-1)
    def send_move(self, move, board): pass

import random
class RandomAgent(base.Agent):
    def get_move(self, board):
        valid = False
        move = None
        while not valid:
            row = random.randint(0,2)
            col = random.randint(0,2)
            move = TTTMove(row, col)
            valid = board.is_valid_move(self.name, move)
        return move
    def send_move(self, move, board): pass

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
        final_board, moves, winner = base.play(agents, TTTBoard.empty())
        print moves
        for board in board_iterator(moves, TTTBoard.empty()):
            print board
            print ""
        pgn = write_game(agents, moves, winner)
        print pgn
        if f is not None:
            f.write(pgn)

    if f is not None:
        f.close()


