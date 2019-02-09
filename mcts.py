# This is a very simple implementation of the UCT Monte Carlo Tree Search algorithm in Python 3.6
# The function UCT(rootstate, itermax, verbose = False) is towards the bottom of the code.
# It aims to have the clearest and simplest possible code, and for the sake of clarity, the code
# is orders of magnitude less efficient than it could be made, particularly by using a
# state.GetRandomMove() or state.DoRandomRollout() function.
#
# Example GameState classes for Nim, OXO and Othello are included to give some idea of how you
# can write your own GameState use UCT in your 2-player game. Change the game to be played in
# the UCTPlayGame() function at the bottom of the code.
#
# Written by Peter Cowling, Ed Powley, Daniel Whitehouse (University of York, UK) September 2012.
#
# Licence is granted to freely use and distribute for any sensible/legal purpose so long as this comment
# remains in any distributed code.
#
# For more information about Monte Carlo Tree Search check out our web site at www.mcts.ai

from math import *
from abc import abstractmethod
import random


class GameState:
    """ A state of the game, i.e. the game board. These are the only functions which are
        absolutely necessary to implement UCT in any 2-player complete information deterministic
        zero-sum game, although they can be enhanced and made quicker, for example by using a
        GetRandomMove() function to generate a random move during rollout.
        By convention the players are numbered 1 and 2.
    """

    def __init__(self):
        self.player_just_moved = 2  # At the root pretend the player just moved is player 2 - player 1 has the first move

    @abstractmethod
    def clone(self):
        """ Create a deep clone of this game state.
        """
        st = GameState()
        st.player_just_moved = self.player_just_moved
        return st

    @abstractmethod
    def do_move(self, move):
        """ Update a state by carrying out the given move.
            Must update playerJustMoved.
        """
        self.player_just_moved = 3 - self.player_just_moved

    @abstractmethod
    def get_moves(self):
        """ Get all possible moves from this state.
        """

    @abstractmethod
    def get_result(self, playerjm):
        """ Get the game result from the viewpoint of playerjm.
        """

    def __repr__(self):
        """ Don't need this - but good style.
        """
        pass


class OXOState(GameState):
    """ A state of the OXOgame(圈圈叉叉), i.e. the game board.
        Squares in the board are in this arrangement
        012
        345
        678
        where 0 = empty, 1 = player 1 (X), 2 = player 2 (O)
    """

    def __init__(self):
        super(OXOState, self).__init__()
        self.player_just_moved = 2  # At the root pretend the player just moved is p2 - p1 has the first move
        self.board = [0, 0, 0, 0, 0, 0, 0, 0, 0]  # 0 = empty, 1 = player 1, 2 = player 2

    def clone(self):
        """ Create a deep clone of this game state.
        """
        st = OXOState()
        st.player_just_moved = self.player_just_moved
        st.board = self.board[:]
        return st

    def do_move(self, move):
        """ Update a state by carrying out the given move.
            Must update playerToMove.
        """
        assert move >= 0 and move <= 8 and move == int(move) and self.board[move] == 0
        self.player_just_moved = 3 - self.player_just_moved
        self.board[move] = self.player_just_moved

    def get_moves(self):
        """ Get all possible moves from this state.
        """
        return [i for i in range(9) if self.board[i] == 0]

    def get_result(self, playerjm):
        """ Get the game result from the viewpoint of playerjm.
        """
        for (x, y, z) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if self.board[x] == self.board[y] == self.board[z]:
                if self.board[x] == playerjm:
                    return 1.0
                else:
                    return 0.0
        if not self.get_moves():
            return 0.5  # draw
        assert False  # Should not be possible to get here

    def __repr__(self):
        s = ""
        for i in range(9):
            s += ".XO"[self.board[i]]
            if i % 3 == 2:
                s += "\n"
        return s


class Node:
    """ A node in the game tree. Note wins is always from the viewpoint of playerJustMoved.
        Crashes if state not specified.
    """

    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parent_node = parent  # "None" for the root node
        self.child_nodes = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_moves()  # future child nodes
        self.player_just_moved = state.player_just_moved  # the only part of the state that the Node needs later

    def uct_select_child(self):
        """ Use the UCB1 formula to select a child node. Often a constant UCTK is applied so we have
            lambda c: c.wins/c.visits + UCTK * sqrt(2*log(self.visits)/c.visits to vary the amount of
            exploration versus exploitation.
        """
        s = sorted(self.child_nodes, key=lambda c: c.wins / c.visits + sqrt(2 * log(self.visits) / c.visits))[-1]
        return s

    def add_child(self, m, s):
        """ Remove m from untriedMoves and add a new child node for this move.
            Return the added child node
        """
        n = Node(move=m, parent=self, state=s)
        self.untried_moves.remove(m)
        self.child_nodes.append(n)
        return n

    def update(self, result):
        """ Update this node - one additional visit and result additional wins. result must be from the viewpoint of playerJustmoved.
        """
        self.visits += 1
        self.wins += result

    def __repr__(self):
        return "[M:" + str(self.move) + " W/V:" + str(self.wins) + "/" + str(self.visits) + " U:" + str(
            self.untried_moves) + "]"

    def tree_to_string(self, indent):
        s = self.indent_string(indent) + str(self)
        for c in self.child_nodes:
            s += c.tree_to_string(indent + 1)
        return s

    def indent_string(self, indent):
        s = "\n"
        for i in range(1, indent + 1):
            s += "| "
        return s

    def children_to_string(self):
        s = ""
        for c in self.child_nodes:
            s += str(c) + "\n"
        return s


def UCT(rootstate, itermax, verbose=False):
    """ Conduct a UCT search for itermax iterations starting from rootstate.
        Return the best move from the rootstate.
        Assumes 2 alternating players (player 1 starts), with game results in the range [0.0, 1.0]."""

    rootnode = Node(state=rootstate)

    for i in range(itermax):
        node = rootnode
        state = rootstate.clone()

        # Select
        while node.untried_moves == [] and node.child_nodes != []:  # node is fully expanded and non-terminal
            node = node.uct_select_child()
            state.do_move(node.move)

        # Expand
        if node.untried_moves:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untried_moves)
            state.do_move(m)
            node = node.add_child(m, state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        while state.get_moves():  # while state is non-terminal
            state.do_move(random.choice(state.get_moves()))

        # Backpropagate
        while node:  # backpropagate from the expanded node and work back to the root node
            node.update(state.get_result(
                node.player_just_moved))  # state is terminal. Update node with result from POV of node.playerJustMoved
            node = node.parent_node

    # Output some information about the tree - can be omitted
    if verbose:
        print(rootnode.tree_to_string(0))
    else:
        print(rootnode.children_to_string())

    return sorted(rootnode.child_nodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


def UCTPlayGame():
    """ Play a sample game between two UCT players where each player gets a different number
        of UCT iterations (= simulations = tree nodes).
    """
    # state = OthelloState(4) # uncomment to play Othello on a square board of the given size
    # state = OXOState() # uncomment to play OXO

    # 這邊可以選要玩啥遊戲
    state = OXOState()  # uncomment to play Nim with the given number of starting chips
    while (state.get_moves() != []):
        print(str(state))
        if state.player_just_moved == 1:
            m = UCT(rootstate=state, itermax=1000, verbose=False)  # play with values for itermax and verbose = True
        else:
            m = UCT(rootstate=state, itermax=100, verbose=False)
        print("Best Move: " + str(m))
        state.do_move(m)
    if state.get_result(state.player_just_moved) == 1.0:
        print("Player " + str(state.player_just_moved) + " wins!")
    elif state.get_result(state.player_just_moved) == 0.0:
        print("Player " + str(3 - state.player_just_moved) + " wins!")
    else:
        print("Nobody wins!")


if __name__ == "__main__":
    """ Play a single game to the end using UCT for both players. 
    """
    UCTPlayGame()
