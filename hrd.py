# -*- coding: utf-8 -*-
import copy
import heapq

class Frontier(object):

    def __init__(self):
        """Initialize frontier list
        """
        self.frontier_index = 0  # the number of items ever added to the frontier
        self.frontierpq = []  # the frontier priority queue

    def empty(self):
        return self.frontierpq == []

    def add(self, node, value):
        """Add a node and its value to the frontier/priority queue"""
        self.frontier_index += 1
        heapq.heappush(self.frontierpq,(value,node)) #add (value,  node) nto our heap (self.frontierpq)

    def pop(self):
        """Remove and result in the node with lowest value
        """
        (_,node) = heapq.heappop(self.frontierpq)
        return node 

    def __str__(self):
        return str([(str(n),",".join(v.state)) for (n,v) in self.frontierpq])

            
            
class Node:
    def __init__(self, g, parent=None):
        '''g is level
        h is distance heuristic
        f = g+h'''
        self.state = []
        self.parent = parent

        self.g = 0
        self.h = 0
        self.f = 0
        
    def read(self, file_path):
        file = open(file_path)
        data = file.read()
        puzzle = data.split("\n")
        while '' in puzzle:
            puzzle.remove('')
        file.close()
        
        '''Change numbering 
        using 2 to denote horizontal 1x2 pieces, 
        3 to denote vertical 1x2 pieces, and 
        4 to denote the single pieces'''
        orig = puzzle.copy()
        to_pr = puzzle.copy()

        for i in range(len(to_pr)): #every row
            if any(item in orig[i] for item in ["2", "3", "4", "5", "6"]):
                for j in range(4): #every col
                     #if down same number & (2-6), change to 3
                    if (i+1 <5) and orig[i][j] == orig[i+1][j] and not(orig[i][j] in ['1','7','0']): #this row vs lower row
                        to_pr[i] = to_pr[i][:j] + "3" + to_pr[i][j+1:]
                        to_pr[i+1] = to_pr[i+1][:j] + "3" + to_pr[i+1][j+1:]
                
                    #if right same number & (2-6), change to 2
                    if (j+1 <4) and (orig[i][j] == orig[i][j+1]) and not(orig[i][j] in ['1','7','0']): #this col vs next col
                        to_pr[i] = to_pr[i][:j] + "2" + to_pr[i][j+1:]
                        to_pr[i] = to_pr[i][:j+1] + "2" + to_pr[i][j+2:]
                        
            #Change 7 to 1 for singles
            if "7" in to_pr[i]:
                to_pr[i] = to_pr[i].replace("7","4")
        
        self.state = to_pr
        
    def __str__(self):
        return '\n'.join(self.state)
    
    # defining less than for purposes of heap queue
    def __lt__(self, other):
        return self.f < other.f
    
    # defining greater than for purposes of heap queue
    def __gt__(self, other):
        return self.f > other.f
      
    # tests whether a state is a goal state
    def is_goal(self):
        return self.state[3][1] == '1' and self.state[4][1] == '1' and self.state[3][2] == '1' and self.state[4][2] == '1'
    
    # takes a state and returns a list of its successor states. 
    def get_successors(self):
        #Generate successor states by moving blank space
        blank = self.find('blank') #[(x1,y1),(x2,y2)]
        x1,y1 = blank[0]
        x2,y2 = blank[1]
        
        #Diagonal to blanks [1leftup,1rightup,1rightdown,1leftdown,2leftup,2rightup,2rightdown,2leftdown]
        diag = [(x1-1,y1-1),(x1+1,y1-1),(x1+1,y1+1),(x1-1,y1+1),(x2-1,y2-1),(x2+1,y2-1),(x2+1,y2+1),(x2-1,y2+1)]
        
        moves_from = dict()
        for i in range(0,4):
            moves_from[i] = (x1,y1)
            moves_from[i+4] = (x2,y2)
            
        n_list = self.neighbors(blank)
        moves_to_1 = self.moves_to(1)
        moves_to_2 = self.moves_to(2)

        [fu, fd, fl, fr, su, sd, sl, sr] = n_list
        left_rights = [fl,fr,sl,sr]
        up_downs = [fu,fd,su,sd]
        
        children = []
            
        for i in range(len(n_list)):
            if n_list[i] ==None:
                continue
            
            #If neighbor is 4 (singles), move 1 tile
            if n_list[i] == "4":
                puzzle = self.action(self.state, moves_from[i], moves_to_1[i])
                child_node = Node(self.g+1, self)
                child_node.state = puzzle
                children.append(child_node)
                
            #If right or left neighbor is 2, blank move 2 tiles
            if n_list[i] == '2' and i in [2,3,6,7]:
                puzzle = self.action(self.state, moves_from[i], moves_to_2[i])
                child_node = Node(self.g+1, self)
                child_node.state = puzzle
                children.append(child_node)
                
            #If above or below neighbor is 3, blank moves 2 tiles
            if n_list[i] == '3' and i in [0,1,4,5]:
                puzzle = self.action(self.state, moves_from[i], moves_to_2[i])
                child_node = Node(self.g+1, self)
                child_node.state = puzzle
                children.append(child_node)
        
        #Cases when two blanks are beside each other
        
        #If right or left neighbor is blank AND above or below is 2, both blanks move 1 tile
        if "0" in left_rights and ((fu == su) or (fd ==sd)) and (("2" in up_downs) or ("1" in up_downs)):
            
            #Check if the tile 1 or 2 is on the above or below (up or down)
            concerned_tile = {} #dictionary
            if fu == su and (fu == "2" or fu =="1"):
                #Check first tile top left and second tile top right diagonals to see if the adjacent tile (to the blanks) is one tile
                #Diagonal to blanks [1leftup,1rightup,1rightdown,1leftdown,2leftup,2rightup,2rightdown,2leftdown]
                (x1_d,y1_d) = diag[0]
                (x2_d,y2_d) = diag[5]
                if x1 == 0 or x2 == 3 or fu =="1":
                    concerned_tile.update({"up":fu})
                elif (self.state[y1_d][x1_d] != self.state[y2_d][x2_d]) or (self.state[y1_d][x1_d] != fu and self.state[y2_d][x2_d] != su):
                    concerned_tile.update({"up":fu})
                    
            if fd == sd and (fd == "2" or fd =="1"):
                #Check first tile bottom left and second tile bottom right diagonals to see if the adjacent tile (to the blanks)
                (x1_d,y1_d) = diag[3]
                (x2_d,y2_d) = diag[6]
                if x1 == 0 or x2 == 3 or fd == "1": #If two blank coordinates are at most left or most right
                    concerned_tile.update({"down":fd})
                elif (self.state[y1_d][x1_d] != self.state[y2_d][x2_d])  or (self.state[y1_d][x1_d] != fd and self.state[y2_d][x2_d] != sd):
                    concerned_tile.update({"down":fd})
            
            #For each concerned tile,
            for key, value in concerned_tile.items(): #key is up or down, value is 1 or 32
                if value == "2":
                    tile = 1
                if value == "1":
                    tile = 2

                #first blank tile is always the left blank tile
                if key == "up":
                    child_node = Node(self.g +1, self)
                    child_node.state = self.action(self.state, (x1, y1), (x1, y1-tile), (x2, y2), (x2, y2-tile))  #move up
                if key == "down":
                    child_node = Node(self.g +1, self)
                    child_node.state = self.action(self.state, (x1, y1), (x1, y1+tile), (x2, y2), (x2, y2+tile))  #move down
                children.append(child_node)
            
        #If above or below neighbor is blank AND right or left is 3, both blanks move 1 tile
        if "0" in up_downs and ((fl == sl) or (fr ==sr)) and (("3" in left_rights) or ("1" in left_rights)):
            #Check if the tile 1 or 3 is on the left or right
            concerned_tile = {} #dictionary
            if fl == sl and (fl == "3" or fl =="1"):
                #Check first tile top left and second tile bottom left diagonals to see if the adjacent tile (to the blanks) is one tile
                #Diagonal to blanks [1leftup,1rightup,1rightdown,1leftdown,2leftup,2rightup,2rightdown,2leftdown]
                (x1_d,y1_d) = diag[0]
                (x2_d,y2_d) = diag[7]
                if y1 == 0 or y2 == 4 or fl =="1":
                    concerned_tile.update({"left":fl})
                elif (self.state[y1_d][x1_d] != self.state[y2_d][x2_d])  or (self.state[y1_d][x1_d] != fl and self.state[y2_d][x2_d] != sl):
                    concerned_tile.update({"left":fl})
            if fr == sr and (fr == "3" or fr == "1"):
                #Check first tile top right and second tile bottom right diagonals to see if the adjacent tile (to the blanks)
                (x1_d,y1_d) = diag[1]
                (x2_d,y2_d) = diag[6]
                if y1 == 0 or y2 == 4 or fr =="1":
                    concerned_tile.update({"right":fr})
                elif(self.state[y1_d][x1_d] != self.state[y2_d][x2_d])  or (self.state[y1_d][x1_d] != fr and self.state[y2_d][x2_d] != sr):
                    concerned_tile.update({"right":fr})
            
            #For each concerned tile,
            for key, value in concerned_tile.items(): #key is left or right, value is 1 or 3
                if value == "3":
                    tile = 1 #no of tiles the blank space has to move
                if value == "1":
                    tile = 2

                #first blank tile is always the left blank tile
                if key == "left":
                    child_node = Node(self.g +1, self)
                    child_node.state = self.action(self.state, (x1, y1), (x1-tile, y1), (x2, y2), (x2-tile, y2)) #move left
                if key == "right":
                    child_node = Node(self.g +1, self)
                    child_node.state = self.action(self.state, (x1, y1), (x1+tile, y1), (x2, y2), (x2+tile, y2)) #move right
                children.append(child_node)
            
        return children

    def action(self, puzzle, move1_from, move1_to, move2_from=None, move2_to=None):
        '''Moves blank spaces'''
        #switch
        new_puzzle = copy.deepcopy(puzzle)
        (x1, y1) = move1_from
        (x1_a, y1_a) = move1_to
        
        new_puzzle[y1] = new_puzzle[y1][:x1] + puzzle[y1_a][x1_a] + new_puzzle[y1][x1+1:]
        new_puzzle[y1_a] = new_puzzle[y1_a][:x1_a] + puzzle[y1][x1] + new_puzzle[y1_a][x1_a+1:]
        
        if move2_from is not None:
            x2, y2 = move2_from
            x2_a,y2_a = move2_to
            
            new_puzzle[y2] = new_puzzle[y2][:x2] + puzzle[y2_a][x2_a] + new_puzzle[y2][x2+1:]
            new_puzzle[y2_a] = new_puzzle[y2_a][:x2_a] + puzzle[y2][x2] + new_puzzle[y2_a][x2_a+1:]
            
        return new_puzzle

    def find(self,blank_or_cao):
        '''To find the blank space or top-left coordinate of 2x2 puzzle piece'''
        found_one=False
        for i in range(5):
            for j in range(4):
                if blank_or_cao == 'blank':
                    if self.state[i][j] == '0':
                        if found_one == False:
                            x1=j
                            y1=i
                            found_one =True
                        else:
                            x2=j
                            y2=i
                            return [(x1,y1),(x2,y2)]
                if blank_or_cao == 'cao':
                    if self.state[i][j] == '1':
                        x1=j
                        y1=i
                        return (x1,y1)

    def neighbors(self, blank):
        '''Lists all neighbords of blank tiles'''
        [(x1,y1),(x2,y2)] = blank
        neighbors = []

        for each_blank in blank:
            x,y = each_blank
            # the 4 direction [up,down,left,right] respectively.
            moves = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
            for i in moves:
                x_a, y_a = i
                if x_a >= 0 and x_a < 4 and y_a >= 0 and y_a < 5:
                    neighbors.append(self.state[y_a][x_a])
                else:
                    neighbors.append(None)
        return neighbors #[first_up, first_down, fist_left, first_right, second_up, second_down, second_lef, second_right]
    
    def moves_to(self, tile):
        ''' # of tile(s) "dictionary" for blank spaces'''
        blank = self.find('blank') #[(x1,y1),(x2,y2)]
        x1,y1 = blank[0]
        x2,y2 = blank[1]
        dictionary = {0:(x1, y1-tile), 1:(x1, y1+tile), 2:(x1-tile,y1), 3:(x1+tile,y1), 4:(x2,y2-tile), 5:(x2, y2+tile), 6:(x2-tile, y2), 7:(x2+tile,y2)}
        return dictionary
    
    def cost(self):
        cost = 0
        curr = self.deepcopy()
        while curr.parent is not None:
            cost +=1
            curr = curr.parent
        return cost
    
    def calc_h(self, h_type):
        if self.is_goal():
            return 0
        
        if h_type == 'Manhattan':
            (x1,y1) = self.find("cao")
            (x2,y2) = (1,3)
            return abs(x1-x2) + abs(y1-y2)
        
        if h_type == 'Advanced':
            (x,y) = self.find('cao')
            neighbors = self.neighbors((x,y), 'cao') #[topleft, topright, righttop, rightbottom, bottomleft, bottomright, lefttop, leftbottom]
            
            add_steps = 0
            
            def below():
                steps=0
                belownb = [neighbors[4], neighbors[5]]
                for each in belownb:
                    
                    if each == '4' or each == '3':
                        steps += 1

                            
                    elif each == '2':
                        if x==0 or x==2:
                            if belownb[0] == belownb[1]:
                                return 2
                            steps += 1
                        elif x==1: 
                            diag = [self.state[y+2][x-1], self.state[y+2][x+2]] #bottomleft diag, bottomright diag
                            if (diag[0] == '2' and diag[0] == diag[1]) or (('2' in diag) and (belownb[0]!=belownb[1])):
                                #this means that the row below caocao has 2 1x2 
                                return 6
                            else:
                                return 3 #if same, break
                return steps
            
            def side(): #only called when x=0 or 2
                
                steps=0    

                if x == 0:#check right side
                    sidenb = [neighbors[2], neighbors[3]]
                    side = 'r'
                elif x == 2:
                    sidenb = [neighbors[6], neighbors[7]]
                    side = 'l'
                for each in sidenb:
                    if sidenb[0] == '2' and (y==0 or y==4):
                        steps +=2
                    if each != '0':
                        steps+=1
                return steps
            
            #Special case: if y=3, only consider left OR right (non-None)
            if y==3:
                add_steps += side()
            
            #If x=1, only consider bottom neighbors
            elif x==1:
                add_steps +=below()
            
            #If x=0, only consider right and bottom neighbors
            #If x=2, only consider left and bottom neighbors
            elif x==0 or x==2:
                add_steps +=below()
                add_steps +=side()
                
            return abs(x1-x2) + abs(y1-y2) + add_steps

def display_sol(end_node, outFile):
    total_cost = -1 #for double checking purposes, -1 for accurate cost
    states = []
    curr = end_node
    
    with open(outFile,'w') as o:
    
        while curr is not None:
            total_cost += 1
            states.append(curr.state)
            curr = curr.parent
        
        o.write("Cost of the solution: "+ str(end_node.g) +"\n")
        
        for i in reversed(states):
            o.write('\n'.join(i))
            o.write('\n\n')
    


def A_Search(file_path, outFile, h_type):
    # Search (Initial State, Successor Function, Goal Test)
    #Initialize node
    curr = Node(0)
    curr.read(file_path)
    curr.g = 0
    curr.h = curr.calc_h(h_type)
    curr.f = curr.g+curr.h
    
    # 2     Frontier = { Initial State }
    frontier = Frontier()
    frontier.add(curr,curr.f)
    
    explored = []
    # 3     While Frontier is not empty do
    while not frontier.empty():
        curr = frontier.pop()
        if curr.is_goal():
            display_sol(curr,outFile)
            return curr 
        if curr.state in explored:
            continue
        explored.append(curr.state)
        successors = curr.get_successors() #list of nodes
        for each_child in successors:
            each_child.g = curr.g+1
            each_child.h = each_child.calc_h(h_type)
            each_child.f = each_child.g+each_child.h
            frontier.add(each_child,each_child.f)
    
    return None

def DFS_Search(file_path, outFile):
    curr = Node(0)
    curr.read(file_path)
    curr.g = 0
    
    # 2     Frontier = { Initial State }
    frontier = []
    frontier.append(curr)
    
    explored = []
    # 3     While Frontier is not empty do
    while frontier:
        curr = frontier.pop()
        if curr.is_goal():
            display_sol(curr,outFile)
            return curr
        if curr.state in explored:
            continue
        explored.append(curr.state)
        successors = curr.get_successors() #list of nodes
        for each_child in successors:
            each_child.g = curr.g+1
            frontier.append(each_child)
    
    return None

import sys
inFile = sys.argv[1]
DFSoutFile = sys.argv[2]
AoutFile = sys.argv[3]

A_Search(inFile, AoutFile,"Manhattan")
DFS_Search(inFile, DFSoutFile)