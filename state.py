#!/usr/bin/env python
import hashlib
import random
import logging
import argparse
from mcts import Node, MonteCarloSearch, BESTCHILD


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('State')


class State():
    """
    The State is just a game where you have NUM_TURNS and at turn i you can make
    a choice from [-2,2,3,-3]*i and this to to an accumulated value.  The goal is for the accumulated value to be as close to 0 as possible.

    The game is not very interesting but it allows one to study MCTS which is.  Some features 
    of the example by design are that moves do not commute and early mistakes are more costly.  

    In particular there are two models of best child that one can use 
    """

    NUM_TURNS = 10  
    GOAL = 0
    MOVES=[2,-2,3,-3]
    MAX_VALUE= (5.0*(NUM_TURNS-1)*NUM_TURNS)/2
    num_moves=len(MOVES)
    def __init__(self, value=0, moves=[], turn=NUM_TURNS):
        self.value=value
        self.turn=turn
        self.moves=moves

    def getMoves(self):
        states=[]
        for x in self.MOVES:
            move=x*self.turn
            states.append(State(self.value+move, self.moves+[move], self.turn-1))
        return states

    def terminal(self):
        if self.turn == 0:
            return True
        return False

    def reward(self):
        r = 1.0-(abs(self.value-self.GOAL)/self.MAX_VALUE)
        return r

    def __hash__(self):
        return int(hashlib.md5(str(self.moves)).hexdigest(),16)

    def __eq__(self,other):
        if hash(self)==hash(other):
            return True
        return False

    def __repr__(self):
        s="Value: %d; Moves: %s"%(self.value,self.moves)
        return s
    
if __name__=="__main__":
    random.seed(0)
    parser = argparse.ArgumentParser(description='MCTS research code')
    parser.add_argument('--num_sims', action="store", required=True, type=int)
    parser.add_argument('--levels', action="store", required=True, type=int, choices=range(State.NUM_TURNS))
    args=parser.parse_args()
    monte=MonteCarloSearch(BESTCHILD)
    
    current_node=Node(State())
    for l in range(args.levels):
        current_node=monte.search(args.num_sims/(l+1),current_node)
        print("level %d"%l)
        print("Num Children: %d"%len(current_node.tried))
        for i,c in enumerate(current_node.tried):
            print(i,c)
        print("Best Child: %s"%current_node.state)
        
        print("--------------------------------")   
            
    
