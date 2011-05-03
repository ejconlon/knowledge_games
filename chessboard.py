#!/usr/bin/env python

import base
import copy
import parse
import random

class PMap(object):
    @staticmethod
    def empty():
        return PMap(None, None)
    def __init__(self, k, v, l=None, r=None):
        self.k = k
        self.v = v
        self.l = l
        self.r = r
    def set(self, k, v):
        if k is None:
            raise KeyError("Cannot set null key")
        if self.k is None or k == self.k:
            return PMap(k, v, self.l, self.r)
        elif k < self.k:
            if self.l is None:
                return PMap(self.k, self.v, PMap(k,v), self.r)
            else:
                return PMap(self.k, self.v, self.l.set(k, v), self.r)
        else:
            if self.r is None:
                return PMap(self.k, self.v, self.l, PMap(k,v))
            else:
                return PMap(self.k, self.v, self.l, self.r.set(k, v))
    def get(self, k, default_lambda=None):
        if k is None:
            raise KeyError("Cannot get null key")
        if self.k is None:
            if default_lambda is not None:
                return default_lambda()
            else:
                raise KeyError(str(k)+" not found")
        elif k == self.k:
            return self.v
        elif k < self.k:
            if self.l is None:
                if default_lambda is not None:
                    return default_lambda()
                else:
                    raise KeyError(str(k)+" not found")
            else:
                return self.l.get(k, default_lambda)
        else:
            if self.r is None:
                if default_lambda is not None:
                    return default_lambda()
                else:
                    raise KeyError(str(k)+" not found")
            else:
                return self.r.get(k, default_lambda)
    def sorted_keys(self):
        if self.k is None:
            raise KeyError("Cannot rebalance null tree")
        if self.l is not None:
            keys = self.l.sorted_keys()
        else:
            keys = []
        keys.append(self.k)
        if self.r is not None:
            keys.extend(self.r.sorted_keys())
        return keys

    def rebalance(self):
        keys = self.sorted_keys()
        random.shuffle(keys)
        m = PMap.empty()
        for k in keys:
            m = m.set(k, self.get(k))
        return m



class LogicException(Exception): pass
class StalemateException(base.WinnerException): pass
class MatedException(base.WinnerException): pass

log = base.LogWrapper("chess")
#th = base.logging.FileHandler('/tmp/chess.log')
#log.wrap.addHandler(th)
log.wrap.setLevel(base.logging.DEBUG)
log.enabled = False

class ChessConstants:
    TURNS_WO_CAP_LIMIT = 50
    TURNS_REP_LIMIT = 3
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
    PROMOTABLES = [ROOK, KNIGHT, BISHOP, QUEEN]
    VALUE = {PAWN: 1, ROOK: 5, KNIGHT: 3, BISHOP: 3, QUEEN: 9, KING: 100}
    COLS = "abcdefgh"
    ROWS = "12345678"
    KING_SIDE_CASTLE="O-O"
    QUEEN_SIDE_CASTLE="O-O-O"

def sgn(num):
    if num == 0: return 0
    elif num > 0: return 1
    else: return -1

class Piece(object):
    __slots__ = ['color','moved','abbr', 'last_moved_on', 'last_move_delta', 'proxy_bishop', 'proxy_rook']
    def __init__(self, color):
        self.color = color
        self.moved = False
        self.abbr = None
        self.last_moved_on = None
        self.last_move_delta = None
    def translate_move(self, move, grid):
        raise Exception("OVERRIDE")
    def get_moves(self, row, col, grid):
        raise Exception("OVERRIDE")
    def enpassantable(self, cur_turn):
        return False
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return '<piece abbr="%s" color="%s" moved="%s" />' % \
                (self.abbr, self.color, self.moved)

class Pawn(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = ChessConstants.PAWN
    def enpassantable(self, cur_turn):
        if self.last_moved_on == cur_turn-1:
            return abs(self.last_move_delta['col']) == 2
        return False
    def translate_move(self, move, grid):
        # TODO EN PASSANT
        delta = grid.delta(move)
        target_piece = grid.get_end(move)
        if abs(delta['col']) > 1:
            log.warn("Pawn cannot move more than 1 column", move, grid)
            return []
        elif sgn(delta['row']) != ChessConstants.PAWN_DIRECTION[self.color]:
            log.warn("Must move forward", move, grid)
            return []
        elif delta['col'] != 0 and target_piece is None:
            log.warn("Cannot move to adjacent column w/o capture", move, grid)
            return []
        elif delta['col'] == 0 and target_piece is not None:
            log.warn("Cannot capture piece in same column", move, grid)
            return []
        elif abs(delta['row']) > 2:
            log.warn("Can never move more than two", move, grid)
            return []
        elif abs(delta['row']) == 2 and self.moved:
            log.warn("Can only move 2 on first move", move, grid)
            return []
        return [move]
    def get_moves(self, row, col, grid):
        arow, acol = grid._arow_acol(row, col)
        direction = -1 if self.color == ChessConstants.WHITE else 1
        # check forward move 1
        if True: # for new namespace
            forward_arow, forward_acol = arow + direction, acol
            forward_row, forward_col = grid._row_col(forward_arow, forward_acol)
            if grid.get(forward_row, forward_col) is None: # must not cap
                promotion = '?' if grid.would_promote(self.color, forward_row) else None
                yield ChessMove(self.abbr, start_row=row, start_col=col, end_row=forward_row, end_col=forward_col, promotion=promotion)
        # check opening move 2
        if not self.moved:
            double_arow, double_acol = arow + 2*direction, acol
            double_row, double_col = grid._row_col(double_arow, double_acol)
            if grid.get(double_row, double_col) is None: # must not cap
                yield ChessMove(self.abbr, start_row=row, start_col=col, end_row=double_row, end_col=double_col)
        # check attack left, right
        for side in [-1, 1]:
            left_arow, left_acol = arow + direction, acol + side
            if left_acol >= 0 and left_acol < 8:
                left_row, left_col = grid._row_col(left_arow, left_acol)
                target = grid.get(left_row, left_col)
                if target is not None and target.color != self.color: # must cap
                    promotion = '?' if grid.would_promote(self.color, left_row) else None
                    yield ChessMove(self.abbr, start_row=row, start_col=col, end_row=left_row, end_col=left_col, promotion=promotion,
                                    capture=target.abbr)


class Rook(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = ChessConstants.ROOK
    def translate_move(self, move, grid):
        delta = grid.delta(move)
        if abs(delta['col']) != 0 and abs(delta['row']) != 0:
            log.warn("Can only move in one file", move, grid)
            return []
        elif not grid.clear_path(move):
            log.warn("Not clear path", move, grid)
            return []
        return [move]
    def get_moves(self, row, col, grid):
        arow, acol = grid._arow_acol(row, col)
        for arowp in xrange(8):
            rowp, colp = grid._row_col(arowp, acol)
            target = grid.get(rowp, colp)
            if target is None:
                move = ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp)
                if grid.clear_path(move): yield move
            elif target.color != self.color:
                move = ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp, capture=target.abbr)
                if grid.clear_path(move): yield move
        for acolp in xrange(8):
            rowp, colp = grid._row_col(arow, acolp)
            target = grid.get(rowp, colp)
            if target is None:
                move = ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp)
                if grid.clear_path(move): yield move
            elif target.color != self.color:
                move = ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp, capture=target.abbr)
                if grid.clear_path(move): yield move

class Knight(Piece):
    DELTAS = [(1,2),(-1,2),(1,-2),(-1,-2),
              (2,1),(2,-1),(-2,1),(-2,-1)]

    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = ChessConstants.KNIGHT
    def translate_move(self, move, grid):
        delta = grid.delta(move)
        jumps = [abs(x) for x in delta.values()]
        jumps.sort()
        if jumps[0] != 1 or jumps[1] != 2:
            log.warn("Must move taxi-cab distance of 3 by (1,2)", move, grid)
            return []
        return [move]
    def get_moves(self, row, col, grid):
        arow, acol = grid._arow_acol(row, col)
        for delta in Knight.DELTAS:
            arowp, acolp = arow + delta[0], acol + delta[1]
            if arowp >= 0 and arowp < 8 and acolp >= 0 and acolp < 8:
                rowp, colp = grid._row_col(arowp, acolp)
                target = grid.get(rowp, colp)
                if target is None:
                    yield ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp)
                elif target.color != self.color:
                    yield ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp, capture=target.abbr)

class Bishop(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = ChessConstants.BISHOP
    def translate_move(self, move, grid):
        delta = grid.delta(move)
        if abs(delta['row']) != abs(delta['col']):
            log.warn("Must move diagonally", move, grid)
            return []
        elif not grid.clear_path(move):
            log.warn("Not clear path", move, grid)
            return []
        return [move]
    def get_moves(self, row, col, grid):
        arow, acol = grid._arow_acol(row, col)
        for inc in range(-7, 0) + range(1, 8):
            arowp, acolp = arow + inc, acol + inc
            if arowp >= 0 and arowp < 8 and acolp >= 0 and acolp < 8:
                rowp, colp = grid._row_col(arowp, acolp)
                target = grid.get(rowp, colp)
                if target is None:
                    move = ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp)
                    if grid.clear_path(move): yield move
                elif target.color != self.color:
                    move = ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp, capture=target.abbr)
                    if grid.clear_path(move): yield move

class Queen(Piece):
    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = ChessConstants.QUEEN
        self.proxy_bishop = Bishop(color)
        self.proxy_rook = Rook(color)
    def translate_move(self, move, grid):
        delta = grid.delta(move)
        if not grid.clear_path(move):
            log.warn("Not clear path", move, grid)
            return []

        # WHITE LISTING
        if abs(delta['row']) == abs(delta['col']):
            log.debug("Moving Queen like Bishop")
            return [move]
        elif abs(delta['row']) == 0 or abs(delta['col']) == 0:
            log.debug("Moving Queen like Rook")
            return [move]
        return []
    def get_moves(self, row, col, grid):
        for move in self.proxy_rook.get_moves(row, col, grid):
            move.abbr = self.abbr
            yield move
        for move in self.proxy_bishop.get_moves(row, col, grid):
            move.abbr = self.abbr
            yield move

class King(Piece):
    DELTAS = [(0,1),(0,-1),(1,0),(-1,0),
              (1,1),(1,-1),(-1,1),(-1,-1)]

    def __init__(self, color):
        Piece.__init__(self, color)
        self.abbr = ChessConstants.KING
    def _get_rook(self, delta, grid):
        if self.color == ChessConstants.WHITE:
            if sgn(delta['col']) > 0:
                # king castle
                return grid.get(col='h', row='1'), 'h', '1'
            else:
                return grid.get(col='a', row='1'), 'a', '1'
        else:
            if sgn(delta['col']) > 0:
                return grid.get(col='h', row='8'), 'h', '8'
            else:
                return grid.get(col='a', row='8'), 'a', '8'
    def translate_move(self, move, grid):
        delta = grid.delta(move)
        jumps = [abs(x) for x in delta.values()]
        jumps.sort()
        log.debug("KING JUMPS", jumps)
        # WHITE LISTING
        if delta['row'] == 0 and abs(delta['col']) == 2\
            and not self.moved:
            log.debug("Castling?", move, grid)
            # castle - check for rook movement
            rook, rook_col, rook_row = self._get_rook(delta, grid)
            if rook is None or rook.moved:
                log.debug("king rook gone or moved")
                return []
            else:
                arow, acol = grid._arow_acol(move.start_row, move.start_col)
                acol += sgn(delta['col'])
                end_row, end_col = grid._row_col(arow, acol)
                rook_move = ChessMove(self.abbr, rook_col, rook_row, end_col, end_row)
                return [move, rook_move]
        elif (jumps[0] == 0 or jumps[0] == 1) and jumps[1] == 1:
            log.debug("King moving max 2 taxi-cab", move, grid)
            return [move]
        return []
    def get_moves(self, row, col, grid):
        arow, acol = grid._arow_acol(row, col)
        for delta in King.DELTAS:
            arowp, acolp = arow + delta[0], acol + delta[1]
            if arowp >= 0 and arowp < 8 and acolp >= 0 and acolp < 8:
                rowp, colp = grid._row_col(arowp, acolp)
                target = grid.get(rowp, colp)
                if target is None:
                    yield ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp)
                elif target.color != self.color:
                    yield ChessMove(self.abbr, start_row=row, start_col=col, end_row=rowp, end_col=colp, capture=target.abbr)

class PieceFactory(object):
    PIECE_CLASSES = {
        ChessConstants.PAWN: Pawn,
        ChessConstants.ROOK: Rook,
        ChessConstants.KNIGHT: Knight,
        ChessConstants.BISHOP: Bishop,
        ChessConstants.QUEEN: Queen,
        ChessConstants.KING: King
    }

    @staticmethod
    def new_piece(color, abbr):
        return PieceFactory.PIECE_CLASSES[abbr](color)

class ChessMove(base.Move):
    __slots__ = ['abbr', 'start_col', 'start_row', 'end_col', 'end_row', 'promotion', 'capture']
    def __init__(self, abbr, start_col, start_row, end_col, end_row, promotion=None, capture=None):
        self.abbr = abbr
        self.start_col = start_col
        self.start_row = start_row
        self.end_col = end_col
        self.end_row = end_row
        self.promotion = promotion
        self.capture = capture
    def to_pgn(self):
        abbr = '' if (self.abbr is None or self.abbr == 'p') else self.abbr
        conj = '' if self.capture is None else "x"
        prom = ''
        if self.promotion is not None:
            prom = '='+self.promotion
        return ''.join([abbr, self.start_col, self.start_row, conj, self.end_col, self.end_row, prom])
    def __str__(self):
        s = '<move start="%s%s" end="%s%s"' % \
                (self.start_col, self.start_row, self.end_col, self.end_row)
        if self.promotion is not None:
            s += ' promotion="%s"' % self.promotion
        if self.capture is not None:
            s += ' capture="%s"' % self.capture
        s += " />"
        return s

class ChessGrid(object):
    __slots__ = ['array']
    def __init__(self, array):
        self.array = array
    def _arow_acol(self, row, col):
        # a_rray row, a_rray col - actual indices, ints
        arow = 8 - int(row)
        acol = ChessConstants.COLS.index(col)
        return arow, acol
    def _row_col(self, arow, acol):
        # these are strings
        row = str(8-arow)
        col = ChessConstants.COLS[acol]
        return row, col
    def get(self, row, col):
        arow, acol = self._arow_acol(row, col)
        return self.array.get(arow+8*acol, lambda: None)
    def get_start(self, move):
        return self.get(col=move.start_col, row=move.start_row)
    def get_end(self, move):
        return self.get(col=move.end_col, row=move.end_row)
    def set(self, row, col, piece):
        arow, acol = self._arow_acol(row, col)
        return ChessGrid(self.array.set(arow+8*acol, piece))
    def set_start(self, move, piece):
        return self.set(col=move.start_col, row=move.start_row, piece=piece)
    def set_end(self, move, piece):
        return self.set(col=move.end_col, row=move.end_row, piece=piece)
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
        delta = self.delta(move)
        if delta['row'] == 0:
            arow, acol = self._arow_acol(row=move.start_row, col=move.start_col)
            for i in (sgn(delta['col'])*j for j in xrange(1, abs(delta['col']))):
                row, col = self._row_col(arow, acol+i)
                if self.get(row, col) is not None:
                    log.debug("Found piece at "+row+" "+col)
                    return False
        elif delta['col'] == 0:
            arow, acol = self._arow_acol(row=move.start_row, col=move.start_col)
            for i in (sgn(delta['row'])*j for j in xrange(1, abs(delta['row']))):
                row, col = self._row_col(arow+i, acol)
                if self.get(row, col) is not None:
                    log.debug("Found piece at "+row+" "+col)
                    return False
        else:
            if abs(delta['row']) != abs(delta['col']):
                return False
            arow, acol = self._arow_acol(row=move.start_row, col=move.start_col)
            for i in (j for j in xrange(1, abs(delta['row']))):
                row, col = self._row_col(arow+sgn(delta['row'])*i, acol+sgn(delta['col'])*i)
                if self.get(row, col) is not None:
                    log.debug("Found piece at "+row+" "+col)
                    return False
        return True

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
                    pass
                else:
                    piece = self.get(col=col, row=row)
                    if piece is None:
                        continue
                    elif piece.color != who:
                        continue
                    elif piece.abbr != piece_abbr:
                        continue
                    elif col is not None and \
                        row is not None and \
                        end_col is not None and \
                        end_row is not None and \
                        len(piece.translate_move(ChessMove(piece.abbr, col, row, end_col, end_row), self)) == 0:
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

    def would_promote(self, color, row):
        return (color == ChessConstants.WHITE and row == ChessConstants.ROWS[-1]) or \
               (color == ChessConstants.BLACK and row == ChessConstants.ROWS[0])

    @classmethod
    def empty(cls):
        grid = ChessGrid(PMap.empty())
        for col in ChessConstants.COLS:
            grid = grid.set("7", col, Pawn(ChessConstants.BLACK))
            grid = grid.set("2", col, Pawn(ChessConstants.WHITE))
        for col in "ah":
            grid = grid.set("8", col, Rook(ChessConstants.BLACK))
            grid = grid.set("1", col, Rook(ChessConstants.WHITE))
        for col in "bg":
            grid = grid.set("8", col, Knight(ChessConstants.BLACK))
            grid = grid.set("1", col, Knight(ChessConstants.WHITE))
        for col in "cf":
            grid = grid.set("8", col, Bishop(ChessConstants.BLACK))
            grid = grid.set("1", col, Bishop(ChessConstants.WHITE))
        for col in "d":
            grid = grid.set("8", col, Queen(ChessConstants.BLACK))
            grid = grid.set("1", col, Queen(ChessConstants.WHITE))
        for col in "e":
            grid = grid.set("8", col, King(ChessConstants.BLACK))
            grid = grid.set("1", col, King(ChessConstants.WHITE))
        return ChessGrid(grid.array.rebalance())
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
        orig_token = token
        promotion = None
        log.debug("DISAMBIGUATING", who, token, grid)
        if token == ChessConstants.KING_SIDE_CASTLE or token == ChessConstants.QUEEN_SIDE_CASTLE:
            moving_piece, start_col, start_row = grid.matching(who, "K", None, None, None, None)
            if token == ChessConstants.KING_SIDE_CASTLE:
                end_col = 'g'
            else:
                end_col = 'c'
            end_row = start_row
        else:
            check=False
            mate=False
            if token[-1] == "+":
                check = True
                token = token[:-1]
            elif token[-1] == "#":
                mate = True
                token = token[:-1]
            if "=" in token:
                token, promotion = token.split('=')
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
            if len(token) > 0 and piece_col is None:
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
        move = ChessMove(moving_piece.abbr, start_col, start_row, end_col, end_row, promotion)
        target = grid.get_end(move)
        if target is not None:
            move.capture = target.abbr
        log.debug("Found move", move)
        return move

    def get_piece_tuples(self, color):
        for row in ChessConstants.ROWS:
            for col in ChessConstants.COLS:
                piece = self.get(row, col)
                if piece is not None and piece.color == color:
                    yield piece, row, col


class ChessBoard(base.Board):
    __slots__ = ['grid', 'white_lost', 'black_lost',
                 'white_nlost', 'black_nlost', 'turns', 'turns_wo_cap', 'seen']
    def __init__(self, grid,
                 white_lost, white_nlost,
                 black_lost, black_nlost,
                 turns, turns_wo_cap, seen):
        self.grid = grid
        self.white_lost = white_lost
        self.white_nlost = white_nlost
        self.black_lost = black_lost
        self.black_nlost = black_nlost
        self.turns = turns
        self.turns_wo_cap = turns_wo_cap
        self.seen = seen

    def copy(self):
        return ChessBoard(grid=self.grid,
                          white_lost=self.white_lost, white_nlost=self.white_nlost,
                          black_lost=self.black_lost, black_nlost=self.black_nlost,
                          turns=self.turns, turns_wo_cap=self.turns_wo_cap, seen=self.seen)

    @classmethod
    def empty(cls):
        grid = ChessGrid.empty()
        white_lost = PMap.empty()
        white_nlost = 0
        black_lost = PMap.empty()
        black_nlost = 0
        turns = 0
        turns_wo_cap = 0
        seen = PMap.empty()
        return ChessBoard(grid=grid,
                          white_lost=white_lost, white_nlost=white_nlost,
                          black_lost=black_lost, black_nlost=black_nlost,
                          turns=turns, turns_wo_cap=turns_wo_cap, seen=seen)

    def __str__(self):
        whitelost = "".join(self.white_lost.get(i) for i in xrange(self.white_nlost))
        blacklost = "".join(self.black_lost.get(i) for i in xrange(self.black_nlost))
        s = ""
        s += "TURNS: %d TWOC: %d SEEN: %d\n" % (self.turns, self.turns_wo_cap, self.get_seen_this())
        s += "LOST: W [%s] B [%s]\n" % (whitelost, blacklost)
        s += str(self.grid)
        return s

    def who_won(self):
        if self.turns_wo_cap >= ChessConstants.TURNS_WO_CAP_LIMIT:
            return "DRAW (EXCEEDED CAPTURE LIMIT)"
        elif self.get_seen_this() >= ChessConstants.TURNS_REP_LIMIT:
            return "DRAW (EXCEEDED REPEAT LIMIT)"
        else:
            return None

    def get_seen_this(self):
        k = str(self.grid)
        return self.seen.get(k, lambda: 0)

    def translate_move(self, who, move):
        if not self.grid.makes_sense(move):
            log.warn("Does not make sense", move)
            return False
        moving_piece = self.grid.get_start(move)
        target_piece = self.grid.get_end(move)
        if moving_piece is None:
            log.warn("No piece to move", move, self.grid)
            return []
        elif moving_piece.color != who:
            log.warn("Not right color", who, moving_piece, move)
            return []
        elif moving_piece == target_piece:
            log.warn("Cannot no-op", who, moving_piece, move)
            return []
        elif target_piece is not None and moving_piece.color == target_piece.color:
            log.warn("Cannot capture own piece", who, moving_piece, target_piece, move)
            return []
        else:
            return moving_piece.translate_move(move, self.grid)

    def valid_moves_init(self, who):
        for piece, row, col in self.grid.get_piece_tuples(who):
            for move in piece.get_moves(row, col, self.grid):
                yield move

    @staticmethod
    def _puts_in_check(depth, color, board, move):
        for trans_move in board.translate_move(color, move):
            board = board.result(color, trans_move)
        return ChessBoard._is_mated(depth+1, color, board)

    #@staticmethod
    #def _puts_in_stalemate(depth, color, board, move):
    #    for trans_move in board.translate_move(color, move):
    #        board = board.result(color, trans_move)
    #    return ChessBoard._is_stalemated(depth+1, color, board)

    #@staticmethod
    #def _is_stalemated(depth, color, board):
    #    other = ChessConstants.BLACK if color == ChessConstants.WHITE else ChessConstants.WHITE
    #    for move in ChessBoard._get_moves(depth+1, other, board):
    #        return False
    #    return True

    @staticmethod
    def _is_mated(depth, color, board):
        other = ChessConstants.BLACK if color == ChessConstants.WHITE else ChessConstants.WHITE
        for move in ChessBoard._get_moves(depth+1, other, board):
            if move.capture == 'K':
                return True
        return False

    #@staticmethod
    #def _filter_not_stalemates(depth, color, board, valid_moves):
    #    stalemated = True
    #    for move in valid_moves:
    #        if not ChessBoard._puts_in_stalemate(depth+1, color, board, move):
    #            stalemated = False
    #            yield move
    #    if stalemated:
    #        other = ChessConstants.BLACK if color == ChessConstants.WHITE else ChessConstants.WHITE
    #        raise StalemateException(other)

    @staticmethod
    def _filter_not_puts_in_check(depth, color, board, valid_moves):
        mated = True
        for move in valid_moves:
            if not ChessBoard._puts_in_check(depth+1, color, board, move):
                mated = False
                yield move
        if mated:
            other = ChessConstants.BLACK if color == ChessConstants.WHITE else ChessConstants.WHITE
            raise MatedException(other) # "other" is winner if "color" is mated

    @staticmethod
    def _assert_valid(color, board, valid_moves):
        for move in valid_moves:
            trans = board.translate_move(color, move)
            if len(trans) == 0:
                raise LogicException("Generated invalid move: "+str(move))
            yield move

    @staticmethod
    def _filter_promotions(valid_moves):
        for move in valid_moves:
            if move.promotion == '?':
                # FORGET IT
                move.promotion = 'Q'
                yield move
                #for abbr in ChessConstants.PROMOTABLES:
                #    movep = copy.deepcopy(move)
                #    movep.promotion = abbr
                #    yield movep
            else:
                yield move

    @staticmethod
    def _get_moves(depth, color, board):
        core = ChessBoard._filter_promotions(
                    board.valid_moves_init(color))
        #core = ChessBoard._filter_not_stalemates(depth, color, board, core)
        if depth < 1:
            core = ChessBoard._filter_not_puts_in_check(depth, color, board, core)
        return core

    def valid_moves(self, who):
        return ChessBoard._get_moves(0, who, self)

    def result(self, who, move):
        log.info(move, who)
        board = self.copy()
        board.turns += 1
        moving_piece = copy.deepcopy(board.grid.get_start(move))
        target_piece = board.grid.get_end(move)
        # pick up the piece
        board.grid = board.grid.set_start(move, None)
        if target_piece is not None: # capture
            log.info("Losing piece", target_piece)
            if target_piece.color == ChessConstants.WHITE:
                board.white_lost = board.white_lost.set(board.white_nlost, target_piece.abbr)
                board.white_nlost += 1
            else:
                board.black_lost = board.black_lost.set(board.black_nlost, target_piece.abbr)
                board.black_nlost += 1
            board.turns_wo_cap = 0 # reset turn_wo_cap counter
        else: # not a capture
            board.turns_wo_cap += 1
        if move.promotion is not None: # replace w/ promoted piece
            moving_piece = PieceFactory.new_piece(who, move.promotion)
        # put down in new location
        board.grid = board.grid.set_end(move, moving_piece)
        # set last move info (used in castling/enpassant/pawn opening rules)
        moving_piece.moved = True
        moving_piece.last_moved_on = board.turns
        moving_piece.last_move_delta = board.grid.delta(move)
        # mark that we've seen this board (for 3x repetition -> draw)
        k = str(board.grid)
        board.seen = board.seen.set(k, board.seen.get(k, lambda: 0)+1)
        return board


class ChessPlayerAgent(base.Agent):
    def get_move(self, board):
        start_col = raw_input("Choose start col (a-h): ")
        start_row = raw_input("Choose start row (1-8): ")
        end_col = raw_input("Choose end col (a-h): ")
        end_row = raw_input("Choose end row (1-8): ")
        return ChessMove(None, start_col, start_row, end_col, end_row)

class ChessRandomAgent(base.Agent):
    def get_move(self, board):
        possible = list(board.valid_moves(self.name))
        log.debug("Possible moves", possible)
        return random.choice(possible)

class ChessHeuristic(base.Heuristic):
    def evaluate(self, who, board):
        other = ChessConstants.BLACK if who == ChessConstants.WHITE else ChessConstants.WHITE
        #if ChessBoard._is_stalemated(0, who, board):
        #    return base.HVal(0)
        if ChessBoard._is_mated(0, who, board):
            return base.HVal.neg_inf()
        if ChessBoard._is_mated(0, other, board):
            return base.HVal.pos_inf()

        # count the value of our pieces vs the value of theirs
        our_val = sum((ChessConstants.VALUE[piece.abbr] for piece, row, col in board.grid.get_piece_tuples(who)))
        their_val = sum((ChessConstants.VALUE[piece.abbr] for piece, row, col in board.grid.get_piece_tuples(other)))
        return base.HVal(our_val - their_val)

class ChessMinMaxSearchAgent(base.MinMaxSearchAgent):
    def __init__(self, name, other_name, heuristic, max_depth=-1):
        base.MinMaxSearchAgent.__init__(self, name, other_name, heuristic, max_depth)
    def _valid_moves(self, who, board):
        l = list(board.valid_moves(who))
        random.shuffle(l)
        return l

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


def main(args):
    mode = args[1]
    if mode == "play":
        board = ChessBoard.empty()
        agents = [ChessPlayerAgent(color) for color in ChessConstants.COLORS]
        final_board, moves, winner = base.play(agents, board)
    elif mode == "random":
        f = None
        if len(args) > 2:
            fn = args[2]
            f = open(fn, "a")
        board = ChessBoard.empty()
        #agents = [ChessRandomAgent(color) for color in ChessConstants.COLORS]
        #agents = [base.HeuristicAgent(ChessConstants.WHITE, ChessHeuristic()), ChessRandomAgent(ChessConstants.BLACK)]
        #agents = [ChessMinMaxSearchAgent(ChessConstants.WHITE, ChessConstants.BLACK, heuristic=ChessHeuristic(), max_depth=2), ChessRandomAgent(ChessConstants.BLACK)]
        agents = [ChessMinMaxSearchAgent(ChessConstants.WHITE, ChessConstants.BLACK, heuristic=ChessHeuristic(), max_depth=2),ChessMinMaxSearchAgent(ChessConstants.BLACK, ChessConstants.WHITE, heuristic=ChessHeuristic(), max_depth=2)]

        final_board, moves, winner = base.play(agents, board)
        pgn = parse.write_game("Chess", agents, moves, winner)
        print ""
        print pgn
        if f is not None:
            f.write(pgn)
            f.close()
    elif mode == "manyrandom":
        while True:
            try:
                main(["", "random"])
            except IndexError:
                continue
    elif mode == "read":
        filename = args[2]
        with open(filename, 'r') as f:
            chars = f.read()
        game_chars = parse.split_games(chars)
        for chars in game_chars:
            print "NEW GAME"
            tokens = parse.tokenize(chars)
            game_parser = parse.PGNGameParser(tokens, ChessPGNMoveParser)
            game = game_parser.game
            board = ChessBoard.empty()
            print game
            print board
            turn = 0
            for move_parser in game.move_parsers:
                print move_parser
                it = move_parser.parse_moves(board.grid)
                first = True
                while True:
                    print ""
                    try:
                        if first:
                            move = it.next()
                            first = False
                        else:
                            move = it.send(board.grid)
                        who = ChessConstants.COLORS[turn]
                        print who+"'s turn"
                        #print move
                        trans_moves = board.translate_move(who, move)
                        print trans_moves
                        assert len(trans_moves) > 0
                        for move in trans_moves:
                            board = board.result(who, move)
                            print board
                            #r = raw_input("ok?")
                        turn = (turn + 1) % 2
                    except StopIteration:
                        break


if __name__ == "__main__":
    import sys
    main(sys.argv)
