
from chessboard import *
import unittest

class TestChessboard(unittest.TestCase):
    def test_not_move_through_pawns(self):
        board = ChessBoard.empty()
        # assert we can't move bishop
        move = ChessMove(start_row="8", start_col="f", end_row="6", end_col="h")
        assert not board.grid.clear_path(move)
        # assert we can't move rook
        move = ChessMove(start_row="8", start_col="h", end_row="6", end_col="h")
        assert not board.grid.clear_path(move)