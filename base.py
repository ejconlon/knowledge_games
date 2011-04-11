

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
    def is_valid_move(self, who, move):
        raise Exception("SUBCLASS")
    def who_won(self):
        raise Exception("SUBCLASS")
    def valid_moves(self):
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
        raise Exception("SUBCLASS")
    def __str__(self):
        return self.name

def play(agents, board):
    print "welcome"
    moves = []
    turn = 0
    winner = None

    while winner is None:
        agent = agents[turn]
        print "It's "+str(agent)+"'s turn"
        print board
        move = agent.get_move(board)
        if not board.is_valid_move(agent.name, move):
            print "Invalid move"
        else:
            moves.append(move)
            board = board.result(agent.name, move)
            turn = (turn + 1) % 2
            agents[turn].send_move(move, board)
            winner = board.who_won()

    print ""

    print board
    if winner == "draw":
        print "DRAW"
    else:
        print winner+" won!"

    return board, moves, winner