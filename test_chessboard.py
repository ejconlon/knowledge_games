
from chessboard import *
import unittest
import random

class TestChessboard(unittest.TestCase):
    def test_not_move_through_pawns(self):
        board = ChessBoard.empty()
        # assert we can't move bishop
        move = ChessMove(start_row="8", start_col="f", end_row="6", end_col="h")
        assert not board.grid.clear_path(move)
        # assert we can't move rook
        move = ChessMove(start_row="8", start_col="h", end_row="6", end_col="h")
        assert not board.grid.clear_path(move)

    def test_pmap(self):
        for i in xrange(100):
            nums = range(100)
            random.shuffle(nums)
            m = PMap.empty()
            for n in nums:
                m = m.set(n, n)
            m_keys = m.sorted_keys()
            assert m_keys == range(100)
            for n in nums:
                assert m.get(n) == n
            m = m.rebalance()
            m_keys = m.sorted_keys()
            assert m_keys == range(100)
            for n in nums:
                assert m.get(n) == n