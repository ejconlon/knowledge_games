#!/usr/bin/env python

import base
import parse
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
    PAWN = "p"
    ROOK = "R"
    KNIGHT = "N"
    BISHOP = "B"
    QUEEN = "Q"
    KING = "K"
    PIECE_ABBRS = [PAWN, ROOK, KNIGHT, BISHOP, QUEEN, KING]
    PIECE_CLASSES = {} # filled below class definitions
    COLS = "abcdefgh"
    ROWS = "12345678"

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
        raise Exception("OVERRIDE")
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return '<piece abbr="%s" color="%s" moved="%s" />' % \
                (self.abbr, self.color, self.moved)

class Pawn(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = ChessConstants.PAWN
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
        self.abbr = ChessConstants.ROOK
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
        self.abbr = ChessConstants.KNIGHT
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
        self.abbr = ChessConstants.BISHOP
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
        self.abbr = ChessConstants.QUEEN
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
        self.abbr = ChessConstants.KING
    def is_valid_move(self, move, grid):
        delta = grid.delta(move)
        jumps = [abs(x) for x in delta.values()]
        jumps.sort()
        log.debug("KING JUMPS", jumps)
        # WHITE LISTING
        if (False):
            # CASTLE
            log.debug("Castling", move, grid)
            return True
        elif (jumps[0] == 0 or jumps[0] == 1) and jumps[1] == 1:
            log.debug("King moving max 2 taxi-cab", move, grid)
            return True
        return False

# Circular dependency but whatever
ChessConstants.PIECE_CLASSES = {
    ChessConstants.PAWN: Pawn,
    ChessConstants.ROOK: Rook,
    ChessConstants.KNIGHT: Knight,
    ChessConstants.BISHOP: Bishop,
    ChessConstants.QUEEN: Queen,
    ChessConstants.KING: King
}

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
        return (move.start_col in ChessConstants.COLS and
                move.start_row in ChessConstants.ROWS and
                move.end_col   in ChessConstants.COLS and
                move.end_row   in ChessConstants.ROWS)
    def clear_path(self, move):
        log.debug("is clear path?", move)
        return True # TODO
    def matching(self, who, piece_abbr, piece_col, piece_row, end_col, end_row):
        log.debug("MATCHING", who, piece_abbr, piece_col, piece_row)
        start_col = None
        start_row = None
        moving_piece = None
        for col in ChessConstants.COLS:
            if piece_col is not None and col != piece_col:
                continue
            for row in ChessConstants.ROWS:
                if piece_row is not None and row != piece_row:
                    break
                piece = self.get(col=col, row=row)
                if piece is None:
                    continue
                elif piece.color != who:
                    continue
                elif piece.abbr != piece_abbr:
                    continue
                elif not piece.is_valid_move(ChessMove(col, row, end_col, end_row), self):
                    continue
                else:
                    start_col = col
                    start_row = row
                    moving_piece = piece
                    break
            if moving_piece is not None:
                break
        log.debug("Found", moving_piece, start_col, start_row)
        return moving_piece, start_col, start_row

    @classmethod
    def empty(cls):
        array = [[None for i in xrange(8)] for j in xrange(8)]
        grid = ChessGrid(array)
        for col in ChessConstants.COLS:
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
        for row in reversed(ChessConstants.ROWS):
            t += " "+row+"|"
            for col in ChessConstants.COLS:
                s = "  "
                p = self.get(row, col)
                if p is not None:
                    s = p.color+p.abbr
                t += s+"|"
            t += "\n"
            t +="---------------------------\n"
        return t[:-1]
    def disambiguate(self, who, token, grid):
        log.debug("DISAMBIGUATING", who, token, grid)
        check=False
        mate=False
        if token[-1] == "+":
            check = True
            token = token[:-1]
        elif token[-1] == "#":
            mate = True
            token = token[:-1]
        end_col = token[-2]
        end_row = token[-1]
        token = token[:-2]
        piece_col = None
        piece_row = None
        piece_abbr = None
        if len(token) > 0:
            piece_abbr = token[0]
            if piece_abbr.upper() != piece_abbr:
                # is a pawn col
                piece_abbr = "p"
                piece_col = token[0]
            token = token[1:]
        else:
            piece_abbr = "p"
        if len(token) > 0:
            piece_col = token[0]
            if piece_col == "x":
                piece_col = None
            token = token[1:]
        if len(token) > 0:
            piece_row = token[0]
            if piece_row == "x":
                piece_row = None
            token = token[1:]

        moving_piece, start_col, start_row = grid.matching(who, piece_abbr, piece_col, piece_row, end_col, end_row)

        assert start_col is not None
        assert start_row is not None
        assert moving_piece is not None
        move = ChessMove(start_col, start_row, end_col, end_row)
        log.debug("Found move", move)
        return move


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
        start_col = raw_input("Choose start col (a-h): ")
        start_row = raw_input("Choose start row (1-8): ")
        end_col = raw_input("Choose end col (a-h): ")
        end_row = raw_input("Choose end row (1-8): ")
        return ChessMove(start_col, start_row, end_col, end_row)

class ChessPGNMoveParser(parse.BasePGNMoveParser):

    def parse_moves(self, grid):
        token_iter = iter(self.tokens)
        first = token_iter.next()
        log.debug("FIRST", first)

        first_parts = first.split('.')
        if len(first_parts) > 0 and len(first_parts[-1]) > 0:
            first = first_parts[-1]
        else:
            first = None
            assert token_iter.next() == "..."

        second = None
        while True:
            try:
                token = token_iter.next()
                if token == "{":
                    token_iter, comment_tokens = parse.until(token_iter, "}")
                elif token == "(":
                    token_iter, comment_tokens = parse.until(token_iter, ")")
                else:
                    second = token
                    log.debug("SECOND", second)
                    break
            except StopIteration:
                break

        if second is not None:
            if parse.is_game_result(second):
                second = None

        if first is not None:
            grid = yield grid.disambiguate(ChessConstants.WHITE, first, grid)
        if second is not None:
            yield grid.disambiguate(ChessConstants.BLACK, second, grid)



if __name__ == "__main__":
    import sys
    mode = sys.argv[1]
    if mode == "play":
        board = ChessBoard.empty()
        agents = [ChessPlayerAgent(color) for color in ChessConstants.COLORS]
        final_board, moves, winner = base.play(agents, board)
    elif mode == "read":
        filename = sys.argv[2]
        with open(filename, 'r') as f:
            chars = f.read()
        game_chars = parse.split_games(chars)
        for chars in game_chars:
            print "NEW GAME"
            tokens = parse.tokenize(chars)
            game_parser = parse.PGNGameParser(tokens, ChessPGNMoveParser)
            game = game_parser.game
            board = ChessBoard.empty()
            print board
            turn = 0
            for move_parser in game.move_parsers:
                it = move_parser.parse_moves(board.grid)
                first = True
                while True:
                    try:
                        if first:
                            move = it.next()
                            first = False
                        else:
                            move = it.send(board.grid)
                        board = board.result(ChessConstants.COLORS[turn], move)
                        print board
                        turn = (turn + 1) % 2
                    except StopIteration:
                        break
                r = raw_input("ok?")

