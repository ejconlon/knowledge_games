#!/usr/bin/env python

from base import *
from chessboard import *
import random
rand = random.Random()

class RandomHeuristic(base.Heuristic):
    def evaluate(self, who, board):
        other = ChessConstants.BLACK if who == ChessConstants.WHITE else ChessConstants.WHITE
        if ChessBoard._is_mated(0, who, board):
            return base.HVal.neg_inf()
        elif ChessBoard._is_mated(0, other, board):
            return base.HVal.pos_inf()
        else:
            return base.HVal(rand.random())

def random(depth1, depth2, npieces):
    while True:
        board = ChessBoard.empty()
        random_agents = [ChessRandomAgent(color) for color in ChessConstants.COLORS]
        agents_1 = [ChessMinMaxSearchAgent(ChessConstants.WHITE, ChessConstants.BLACK, heuristic=ChessHeuristic(), max_depth=depth1),
                    ChessMinMaxSearchAgent(ChessConstants.BLACK, ChessConstants.WHITE, heuristic=RandomHeuristic(), max_depth=depth2)]
        agents_2 = [ChessMinMaxSearchAgent(ChessConstants.WHITE, ChessConstants.BLACK, heuristic=RandomHeuristic(), max_depth=depth2),
                    ChessMinMaxSearchAgent(ChessConstants.BLACK, ChessConstants.WHITE, heuristic=ChessHeuristic(), max_depth=depth1)]

        print "*"*20+" RANDOM TO N PIECES"
        half_board, half_moves, half_winner = play(random_agents, board, stop_at_n_pieces(npieces))
        if half_winner is not None:
            continue
        print "*"*20+" PLAY FIRST SIDE"
        tup1 = play(agents_1, half_board)
        pgn1 = parse.write_game("Chess1", agents_1, tup1[1], tup1[2])
        print "*"*20+" PLAY SECOND SIDE"
        tup2 = play(agents_2, half_board)
        pgn2 = parse.write_game("Chess2", agents_2, tup2[1], tup2[2])
        return (tup1, tup2, pgn1, pgn2) 

def stop_at_n_pieces(npieces):
    return (lambda board: board.white_nlost+board.black_nlost >= npieces)

def play(agents, board, stop_condition=lambda board: False):
    print "welcome"
    moves = []
    turn = 0
    winner = None

    while winner is None and not stop_condition(board):
        agent = agents[turn]
        print "It's "+str(agent)+"'s turn"
        print board
        try:
            move = agent.get_move(board)
        except WinnerException, e:
            winner = e.winner
            break
        trans_moves = board.translate_move(agent.name, move)
        if len(trans_moves) == 0:
            print "Invalid move"
        else:
            turn = (turn + 1) % 2
            agents[turn].send_move(move, board)
            moves.append(move)
            for trans_move in trans_moves:
                print "Moving: "+str(trans_move)
                board = board.result(agent.name, trans_move)
            winner = board.who_won()

    print ""

    print board
    if winner == "draw":
        print "DRAW"
    else:
        print str(winner)+" won!"

    return board, moves, winner

def aggregate(ntimes, depth1, depth2, npieces, filename = None):
    file = None
    if filename is not None:
        file = open(filename, "a")
    games = [random(depth1, depth2, npieces) for i in xrange(ntimes)]
    a1_points = 0
    a2_points = 0
    for tup4 in games:
        whos = (tup4[0][2], tup4[1][2])
        if whos[0] == ChessConstants.WHITE:
            a1_points += 1
        elif whos[0] == ChessConstants.BLACK:
            a2_points += 1
        if whos[1] == ChessConstants.WHITE:
            a2_points += 1
        elif whos[1] == ChessConstants.BLACK:
            a1_points += 1
        if file is not None:
            file.write(tup4[2])
            file.write(tup4[3])

    if file is not None:
        file.close()

    print "a1_points", a1_points
    print "a2_points", a2_points


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print "test.py ngames depth1 depth2 npieces filename"
        sys.exit(-1)
    ntimes = int(sys.argv[1])
    depth1 = int(sys.argv[2])
    depth2 = int(sys.argv[3])
    npieces = int(sys.argv[4])
    if len(sys.argv) >= 6:
        filename = sys.argv[5]
    else:
        filename = None
    aggregate(ntimes, depth1, depth2, npieces, filename)
    
