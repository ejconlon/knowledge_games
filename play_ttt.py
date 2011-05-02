#!/usr/bin/env python

import base
import parse

log = base.LogWrapper("ttt")
th = base.logging.FileHandler('/tmp/chess.log')
log.wrap.addHandler(th)
log.wrap.setLevel(base.logging.DEBUG)
log.enabled = False

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
    def translate_move(self, who, move):
        if self.is_valid_row_col(move.row, move.col):
            return [move]
        else:
            return []
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
    def valid_moves(self, who):
        for rowi in xrange(3):
            for colj in xrange(3):
                if self.is_valid_row_col(rowi, colj):
                    yield TTTMove(rowi, colj)


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

import random
class RandomAgent(base.Agent):
    def get_move(self, board):
        valid = False
        move = None
        while not valid:
            row = random.randint(0,2)
            col = random.randint(0,2)
            move = TTTMove(row, col)
            valid = board.is_valid_row_col(row, col)
        return move

class TTTHeuristic(base.Heuristic):
    def evaluate(self, who, board):
        N = {True: {3: 0, 2: 0, 1: 0},
             False: {3: 0, 2: 0, 1: 0}}

        # fill in N
        for rowi in xrange(3):
            row = board.grid[rowi]
            self._add_runs(N, who, row)

        for colj in xrange(3):
            col = [board.grid[i][colj] for i in xrange(3)]
            self._add_runs(N, who, col)

        if True: # for namespace
            down_diag = [board.grid[i][i] for i in xrange(3)]
            self._add_runs(N, who, down_diag)

        if True: # for namepace
            up_diag = [board.grid[i][2-i] for i in xrange(3)]
            self._add_runs(N, who, up_diag)

        log.debug("WHO "+who, "BOARD "+str(board), "N "+str(N))

        if N[True][3] > 0:
            return base.HVal.pos_inf()
        elif N[False][3] > 0:
            return base.HVal.neg_inf()
        else:
            return base.HVal((2*N[True][2]+N[True][1]) - (2*N[False][2]+N[False][1]))

    def _add_runs(self, N, who, row, curwho=None, curlen=0):
        if len(row) == 0:
            if curwho is not None:
                N[who == curwho][curlen] += 1
        else:
            if curwho is None:
                self._add_runs(N, who, row[1:], row[0], 1)
            elif row[0] == curwho:
                self._add_runs(N, who, row[1:], curwho, curlen+1)
            else:
                N[who == curwho][curlen] += 1
                self._add_runs(N, who, row[1:], row[0], 1)


if __name__ == "__main__":
    import sys
    n = int(sys.argv[1])
    f = None
    if len(sys.argv) > 2:
        fn = sys.argv[2]
        f = open(fn, "a")

    for i in xrange(n):
        agents = [base.MinMaxSearchAgent("X", "O", TTTHeuristic(), 2), RandomAgent("O")]
        #agents = [base.MinMaxSearchAgent("X", "O", TTTHeuristic(), 2), base.HeuristicAgent("O", TTTHeuristic())]
        final_board, moves, winner = base.play(agents, TTTBoard.empty())
        print moves
        for board in board_iterator(moves, TTTBoard.empty()):
            print board
            print ""
        pgn = parse.write_game("TicTacToe", agents, moves, winner)
        print pgn
        if f is not None:
            f.write(pgn)

    if f is not None:
        f.close()


