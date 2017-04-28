#!/usr/bin/env python
import random
import math
import hashlib
import logging


"""
A quick Monte Carlo Tree Search implementation.  For more details on MCTS see See http://pubs.doc.ic.ac.uk/survey-mcts-methods/survey-mcts-methods.pdf
"""


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('mcts')

class Node():
    def __init__(self, state, parent=None):
        self.visits=0
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
        re=0
        if self.visits:
            re=float(self.reward)/self.visits
        s="Node; move: %s; children: %d; visits: %d; reward: %f(%f)"%(self.state, len(self.tried),self.visits,self.reward, re)
        return s
        

class MonteCarloRunner(object):
    def __init__(self, monte):
        self.monte=monte

    def run(self, rootNode, maxMoves, maxIters):
        node=rootNode
        for l in range(maxMoves):
            node=self.monte.search(maxIters/(l+1), node)
            print("Move: %i, children: %i" % (l, node.noChildren))
            for i,c in enumerate(node.tried):
                logger.warning("%s %s" % (i,c))

            print("Best Child: %s" % node.state)
            if node.state.terminal():
                print("End of game!")
                return (True, node)
        print("No winner")
        return (False, node)
            
class MonteCarloSearch(object):
    def __init__(self, banditStrategy, maxDepth=1000, debugIter=100):
        self.banditStrategy=banditStrategy
        self.debugIterations=debugIter
        self.maxDepth=maxDepth
        #MCTS scalar.  Larger scalar will increase exploitation, smaller will increase exploration. 
        self.scalar=1/math.sqrt(2.0)
      
    def search(self,budget,root):
        """Find best move for the current move"""
        for iter in range(budget):
            if iter%self.debugIterations==(self.debugIterations-1):
                logger.info("simulation: %d"%iter)
                logger.info(root)
            front=self.expandNodeUntilLeaf(root, self.maxDepth)
            self.updateNodes(front,front.state.reward())
        return self.banditStrategy(root,0)

    def expandNodeUntilLeaf(self,node, depth):
        """Iterate down the tree until the the leaf (fully expanded)"""
        while node.state.terminal()==False and depth>0:
            if node.fullyVisited()==False:    
                node=node.getUnvisitedChild()
            else:
                node=self.banditStrategy(node,self.scalar)
            depth-=1
        return node

    def updateNodes(self, node,reward):
        """Update nodes from the leaf to the root"""
        while node!=None:
            node.update(reward)
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

