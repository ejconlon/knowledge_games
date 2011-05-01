
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

class Move(object):
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        raise Exception("SUBCLASS")

class Board(object):
    def __init__(self, grid):
        self.grid = grid
    def result(self, who, move):
        raise Exception("SUBCLASS")
    def translate_move(self, who, move):
        raise Exception("SUBCLASS")
    def who_won(self):
        raise Exception("SUBCLASS")
    def valid_moves(self, who):
        raise Exception("SUBCLASS")
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        raise Exception("SUBCLASS")

class Agent(object):
    def __init__(self, name):
        self.name = name
    def get_move(self, board):
        raise Exception("SUBCLASS")
    def send_move(self, move, result):
        #raise Exception("SUBCLASS")
        pass
    def __str__(self):
        return self.name

# need extended real numbers for heuristic values
# i.e. R U {+inf, -inf}
# +inf = certain victory, -inf = certain defeat
class HVal(object):
    POS_INF = "inf"
    NEG_INF = "-inf"

    def __init__(self, val):
        self.val = val
    @staticmethod
    def pos_inf():
        return HVal(HVal.POS_INF)
    @staticmethod
    def neg_inf():
        return HVal(HVal.NEG_INF)

    def __cmp__(self, other):
        if self.val == HVal.POS_INF:
            if other.val == HVal.POS_INF:
                return 0
            else:
                return 1
        elif self.val == HVal.NEG_INF:
            if other.val == HVal.NEG_INF:
                return 0
            else:
                return -1
        elif other.val == HVal.POS_INF:
            return -1
        elif other.val == HVal.NEG_INF:
            return 1
        else:
            return self.val.__cmp__(other.val)

    def __neg__(self):
        if self.val == HVal.POS_INF:
            return HVal.neg_inf()
        elif self.val == HVal.NEG_INF:
            return HVal.pos_inf()
        else:
            return HVal(self.val.__neg__())

class Heuristic(object):
    def evaluate(self, who, board):
        raise Exception("SUBCLASS")
        # and return an HVal

class WinnerException(Exception):
    def __init__(self, winner):
        Exception.__init__(self, "Winner: "+winner)
        self.winner = winner

def play(agents, board):
    print "welcome"
    moves = []
    turn = 0
    winner = None

    while winner is None:
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
        print winner+" won!"

    return board, moves, winner