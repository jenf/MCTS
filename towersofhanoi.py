#!/usr/bin/env python
import hashlib
import random
import logging
import argparse
from mcts import Node, MonteCarloSearch, BESTCHILD, MonteCarloRunner


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('State')


class Move():
    def __init__(self, src, dst):
        self.src=src
        self.dst=dst

    def apply(self, state):
        if len(state[self.src])==0:
            return False
        item=state[self.src][-1]
        if len(state[self.dst]) > 0 and state[self.dst][-1]>item:
            return False
        state[self.src]=state[self.src][:]
        state[self.dst]=state[self.dst][:]
        state[self.src].pop()
        state[self.dst].append(item)
        return True

    def __repr__(self):
        return "Move(%i, %i)" % (self.src, self.dst)

    def __hash__(self):
        return hash(repr(self))
        
        
class Hanoi():
    """
    Can a MCTS play towers of hanoi?
    """

    discs=3
    NUM_TURNS=30

    def __init__(self, state=None, moves=[]):
        if state==None:
            state=[[1,2,3],[],[]]
        self.state=state
        self.moves=moves

    def getMoves(self):
        states=[]
        for x in range(0,len(self.state)):
            for y in range(0, len(self.state)):
                if x!=y:
                    mv=Move(x,y)
                    state=self.state[:]
                    if mv.apply(state):
#                        print x,y, state
                        states.append(Hanoi(state, self.moves+[mv]))
        return states

    def terminal(self):
        if len(self.state[-1]) == self.discs:
            return True
        return False

    def reward(self):
        r=0
        for x in self.state[-1]:
            r+=x
        return r

    def __hash__(self):
        return int(hashlib.md5(str(self.moves)).hexdigest(),16)

    def __eq__(self,other):
        if hash(self)==hash(other):
            return True
        return False

    def __repr__(self):
        s="State: %s; Moves: %s Terminal: %s"%(self.state,self.moves, self.terminal())
        return s
    
if __name__=="__main__":
    random.seed(0)
    parser = argparse.ArgumentParser(description='MCTS research code')
    parser.add_argument('--num_sims', action="store", required=True, type=int)
    parser.add_argument('--levels', action="store", required=True, type=int)
    args=parser.parse_args()
    monte=MonteCarloSearch(BESTCHILD, 20)
    
    current_node=Node(Hanoi())
    runner=MonteCarloRunner(monte)
    runner.run(current_node, args.levels, args.num_sims)
    
