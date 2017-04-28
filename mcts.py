#!/usr/bin/env python
import random
import math
import hashlib
import logging
import argparse


"""
A quick Monte Carlo Tree Search implementation.  For more details on MCTS see See http://pubs.doc.ic.ac.uk/survey-mcts-methods/survey-mcts-methods.pdf
"""


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('MyLogger')


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
    

class Node():
    def __init__(self, state, parent=None):
        self.visits=1
        self.reward=0.0 
        self.state=state
        self.noChildren=-1
        self.untried=[]
        self.tried=[]
        self.parent=parent

    def getUnvisitedChild(self):
        if self.noChildren==-1:
            self.untried=self.state.getMoves()
            self.noChildren=len(self.untried)
        choice=random.choice(self.untried)
        child=Node(choice, self)
        self.tried.append(child)
        self.untried.remove(choice)
        return child

    def update(self,reward):
        self.reward+=reward
        self.visits+=1

    def fullyVisited(self):
        if len(self.tried)==self.noChildren:
            return True
        return False

    def __repr__(self):
        s="Node; children: %d; visits: %d; reward: %f"%(len(self.tried),self.visits,self.reward)
        return s
        


class MonteCarloSearch(object):
    def __init__(self, banditStrategy, debugIter=100):
        self.banditStrategy=banditStrategy
        self.debugIterations=debugIter
        #MCTS scalar.  Larger scalar will increase exploitation, smaller will increase exploration. 
        self.scalar=1/math.sqrt(2.0)
      
    def search(self,budget,root):
        """Find best move for the current move"""
        for iter in range(budget):
            if iter%self.debugIterations==(self.debugIterations-1):
                logger.info("simulation: %d"%iter)
                logger.info(root)
            front=self.expandNodeUntilLeaf(root)
            self.updateNodes(front,front.state.reward())
        return self.banditStrategy(root,0)

    def expandNodeUntilLeaf(self,node):
        """Iterate down the tree until the the leaf (fully expanded)"""
        while node.state.terminal()==False:
            if node.fullyVisited()==False:    
                node=node.getUnvisitedChild()
            else:
                node=self.banditStrategy(node,self.scalar)
        return node

    def updateNodes(self, node,reward):
        """Update nodes from the leaf to the root"""
        while node!=None:
            node.visits+=1
            node.reward+=reward
            node=node.parent
        return


#current this uses the most vanilla MCTS formula it is worth experimenting with THRESHOLD ASCENT (TAGS)
def BESTCHILD(node,scalar):
    bestscore=0.0
    bestchildren=[]
    for c in node.tried:
        exploit=c.reward/c.visits
        explore=math.sqrt(math.log(2*node.visits)/float(c.visits))  
        score=exploit+scalar*explore
        if score==bestscore:
            bestchildren.append(c)
        if score>bestscore:
            bestchildren=[c]
            bestscore=score
    if len(bestchildren)==0:
        logger.warn("OOPS: no best child found, probably fatal")
    return random.choice(bestchildren)

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
            
    
