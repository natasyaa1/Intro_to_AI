# -*- coding: utf-8 -*-
"""
Created on Mon Oct 10 21:42:54 2022

@author: audre
"""
import copy

class Board:
    def __init__(self, state=None, utility=None, parent=None):
        self.state = None
        self.utility = None
        self.parent = parent
        self.black = None
        self.red = None
        self.player_color = None
    
    def assign_player_color(self, color):
        self.player_color = color
    def assign_opp_player_color(self):
        if self.parent.player_color == 'r': self.player_color = 'b'
        elif self.parent.player_color == 'b': self.player_color = 'r'
        
    def read(self, file_path):
        file = open(file_path)
        data = file.read()
        board = data.split("\n")
        while '' in board:
            board.remove('')
        file.close()
        
        self.state = board
    
    def calc_utility(self):
        r = 0 #red piece
        b = 0 #black peice
        R = 0 #red king
        B = 0 #black king
        #if pawn is adjacent to the edge of the board
        middle_sides = [self.state[1][0], self.state[3][0], self.state[5][0], self.state[2][7], self.state[4][7], self.state[6][7]]
        edge_rs = middle_sides.count('r') + middle_sides.count('R')
        edge_bs = middle_sides.count('b') + middle_sides.count('B')
        #Our pieces in our bottom line
        home_rs = self.state[0].count('r') + self.state[0].count('R')
        home_bs = self.state[7].count('b') + self.state[0].count('B')
        #Our pieces in the opposite area
        opp_rs = 0
        opp_bs = 0
        #If player chooses this state as next, will the opposite player's move be a capture move? Player's eaten king will worth more
        will_be_eaten_pawn = 0
        will_be_eaten_king = 0
        #Pieces grouped together tend to be stronger than ones that are separated
        neighboring_rs = 0
        neighboring_bs = 0
        for i in range(8):
            row = self.state[i]
            r += row.count('r')
            b += row.count('b')
            R += row.count('R')
            B += row.count('B')
                
            if i <= 3 and i > 0:
                opp_rs += (row.count('r') + row.count('R'))
            if i >= 4 and i < 7:
                opp_bs += (row.count('b') + row.count('B'))
        
        def check_relationship(from_row, from_col, to_row, to_col):
            if to_row > 7 or to_row < 0 or to_col > 7 or to_col < 0: return 0,0
            if self.state[from_row][from_col] in ['r','R'] and self.state[to_row][to_col] in ['r','R'] : return 1,0
            elif self.state[from_row][from_col] in ['b','B'] and self.state[to_row][to_col] in ['b','B']: return 0,1
            else: return 0,0
        
        def can_be_captured(target_row, target_col, by_row, by_col, player_color):
            if by_row > 7 or by_row < 0 or by_col > 7 or by_col < 0: return 0,0
            if self.player_color == 'r' and  self.state[target_row][target_col] in ['r', 'R'] and ((self.state[by_row][by_col] == 'b' and by_row == target_row-1) or (self.state[by_row][by_col] == 'B')):
                if self.state[target_row][target_col] == 'r': return 1,0 #if this next move is selected, at least one red pawn will be eaten by black player, so negative so that this is not selected as next best move
                elif self.state[target_row][target_col] == 'R': return 0,1
                else: return 0,0
            elif self.player_color == 'b' and  self.state[target_row][target_col] in ['b', 'B'] and ((self.state[by_row][by_col] == 'r' and by_row == target_row+1) or (self.state[by_row][by_col] == 'R')):
                if self.state[target_row][target_col] == 'b': return -1,0
                elif self.state[target_row][target_col] == 'B': return 0,-1
                else: return 0,0
            else: return 0,0
        
        for i in range(8):
            for j in range(8):
                current_piece = self.state[i][j]
                
                r1, b1 = check_relationship(i,j,i-1,j-1)
                r2, b2 = check_relationship(i,j,i-1,j+1)
                r3, b3 = check_relationship(i,j,i+1,j-1)
                r4, b4 = check_relationship(i,j,i+1,j+1)
                
                neighboring_rs += (r1 + r2 + r3 + r4)
                neighboring_bs += (b1 + b2 + b3 + b4)
                
                np1, nk1 = can_be_captured(i,j,i-1,j-1,self.player_color)
                np2, nk2 = can_be_captured(i,j,i-1,j+1,self.player_color)
                np3, nk3 = can_be_captured(i,j,i+1,j-1,self.player_color)
                np4, nk4 = can_be_captured(i,j,i+1,j+1,self.player_color)
                
                will_be_eaten_pawn += (np1+np2+np3+np4)
                will_be_eaten_king += (nk1+nk2+nk3+nk4)
        
        r_possible_moves = get_successors(self, 'r', True)
        b_possible_moves = get_successors(self, 'b', True)
        #P1: Pieces Type Value
        p1 = (R*17.5 + r*5) - (B*17.5 + b*5)
        #P2: Pieces Location Value
        p2 = (opp_rs*2 + home_rs*0.5 + edge_rs*2) - (opp_bs*2 + home_bs*0.5 + edge_bs*2)
        #P3 	Value of possibility of capturing a neighboring piece
        p3 = will_be_eaten_pawn*2.5 + will_be_eaten_king*8.75
        #P4 	Layout /neighboring value
        p4 = neighboring_rs*0.3 - neighboring_bs*0.3
        self.utility = p1+p2+p4+p3 #(mine - opponents) simple utility function
        self.red = r+R*2
        self.black = b+B*2
        
    def __str__(self):
        return '\n'.join(self.state)
        

#black pieces start on top and red pieces start on bottom

def get_successors(board, player_color, inside_util=None):
    moves = []
    children = []
    count =0
    
    if player_color == 'r':
        our_color = ['r','R']
    elif player_color == 'b':
        our_color = ['b', 'B']
    
    #1 moves
    if inside_util == None:
        for i in range(8):
            for j in range(8):
                if board.state[i][j] in our_color: 

                    #Check for captures
                    if can_capture(board, i, j, i-2, j-2, i-1, j-1, player_color):
                        final_positions, final_coord, moves_dict = capture_jumps(board, i, j, i-2, j-2, i-1, j-1, player_color)
                        for each in final_positions: children.append(each)
                    if can_capture(board, i, j, i-2, j+2, i-1, j+1, player_color):
                        final_positions, final_coord, moves_dict = capture_jumps(board, i, j, i-2, j+2, i-1, j+1, player_color)
                        for each in final_positions: children.append(each)
                    if can_capture(board, i, j, i+2, j-2, i+1, j-1, player_color):
                        final_positions, final_coord, moves_dict = capture_jumps(board, i, j, i+2, j-2, i+1, j-1, player_color)
                        for each in final_positions: children.append(each)
                    if can_capture(board, i, j, i+2, j+2, i+1, j+1, player_color):
                        final_positions, final_coord, moves_dict = capture_jumps(board, i, j, i+2, j+2, i+1, j+1, player_color)
                        for each in final_positions: children.append(each)

        # When it's always possible the player must eat/capture an opposing piece. One diagonal moves are allowed if there's no captures avail
        if children == []: 
            for i in range(8):
                for j in range(8):
                    if board.state[i][j] in our_color:
                        if can_move(board, i, j, i-1, j-1, player_color): 
                            children.append(update_board(board, i, j, i-1, j-1))
                        if can_move(board, i, j, i-1, j+1, player_color): children.append(update_board(board, i, j, i-1, j+1))
                        if can_move(board, i, j, i+1, j-1, player_color): children.append(update_board(board, i, j, i+1, j-1))
                        if can_move(board, i, j, i+1, j+1, player_color): children.append(update_board(board, i, j, i+1, j+1))
        return children

    if inside_util == True:
        for i in range(8):
            for j in range(8):
                if board.state[i][j] in our_color: 
                    #Check for captures
                    if can_capture(board, i, j, i-2, j-2, i-1, j-1, player_color):count += 1
                    if can_capture(board, i, j, i-2, j+2, i-1, j+1, player_color):count += 1
                    if can_capture(board, i, j, i+2, j-2, i+1, j-1, player_color):count += 1
                    if can_capture(board, i, j, i+2, j+2, i+1, j+1, player_color):count += 1
    
        # When it's always possible the player must eat/capture an opposing piece. One diagonal moves are allowed if there's no captures avail
        if count == 0: 
            for i in range(8):
                for j in range(8):
                    if board.state[i][j] in our_color:
                        if can_move(board, i, j, i-1, j-1, player_color): count += 1
                        if can_move(board, i, j, i-1, j+1, player_color): count += 1
                        if can_move(board, i, j, i+1, j-1, player_color): count += 1
                        if can_move(board, i, j, i+1, j+1, player_color): count += 1
        return count

def update_board(board, from_row, from_col, to_row, to_col, jumped_row=None, jumped_col=None):
    board_now = copy.deepcopy(board)
    piece_moved = board_now.state[from_row][from_col]
    if piece_moved == '.': return None
    board_now.state[from_row] = board_now.state[from_row][:from_col] + '.' + board_now.state[from_row][from_col+1:]
    if jumped_row != None and jumped_col != None:
        board_now.state[jumped_row] = board_now.state[jumped_row][:jumped_col] + '.' + board_now.state[jumped_row][jumped_col+1:] #eaten
    
    #Turn man to king
    if (piece_moved == 'r' and to_row == 0):
        board_now.state[to_row] = board_now.state[to_row][:to_col] + 'R' + board_now.state[to_row][to_col+1:]
    elif (piece_moved == 'b' and to_row == 7):
        board_now.state[to_row] = board_now.state[to_row][:to_col] + 'B' + board_now.state[to_row][to_col+1:]
    else:
        board_now.state[to_row] = board_now.state[to_row][:to_col] + piece_moved + board_now.state[to_row][to_col+1:]
    
    board_now.calc_utility()
    board_now.parent = board
    board_now.assign_opp_player_color()
    
    return board_now

#Returns which direction captures are possible
def capturable_neighbors(board, i, j, player_color):
    neighbors = [] 
    
    if can_capture(board, i, j, i-2, j-2, i-1, j-1, player_color): neighbors.append([i, j, i-2, j-2, i-1, j-1])
    if can_capture(board, i, j, i-2, j+2, i-1, j+1, player_color): neighbors.append([i, j, i-2, j+2, i-1, j+1])
    if can_capture(board, i, j, i+2, j-2, i+1, j-1, player_color): neighbors.append([i, j, i+2, j-2, i+1, j-1])
    if can_capture(board, i, j, i+2, j+2, i+1, j+1, player_color): neighbors.append([i, j, i+2, j+2, i+1, j+1])
    
    return neighbors #[[from_row, from_col, to_row, to_col, jumped_row, jumped_col],...]
    
#Checks if captures/jumps are possible
def can_capture(board, from_row, from_col, to_row, to_col, jumped_row, jumped_col, player_color):
    if player_color == 'r':
        our_color = ['r','R']
        forward = 'up'
        their_color = ['b', 'B']
    elif player_color == 'b':
        our_color = ['b', 'B']
        forward = 'down'
        their_color = ['r','R']
        
    #Check if row col index is out or within range
    if to_row > 7 or to_row < 0 or to_col > 7 or to_col < 0: return False
    
    #Return false if there's the 'to' position is habited by another piece
    if board.state[to_row][to_col] != '.': return False
    
    #if piece is not king
    if board.state[from_row][from_col] == our_color[0]:
        if forward == 'up' and to_row == from_row-2 and board.state[jumped_row][jumped_col] in their_color: return True
        if forward == 'down' and to_row == from_row+2 and board.state[jumped_row][jumped_col] in their_color: return True
    
    #If piece is king
    if board.state[from_row][from_col] == our_color[1] and board.state[jumped_row][jumped_col] in their_color: return True

#Checks if one move is possible
def can_move(board, from_row, from_col, to_row, to_col, player_color):
    if player_color == 'r':
        our_color = ['r','R']
        forward = 'up'
    elif player_color == 'b':
        our_color = ['b', 'B']
        forward = 'down'
        
    #Check if row col index is out or within range
    if to_row > 7 or to_row < 0 or to_col > 7 or to_col < 0: return False
    
    #Return false if there's the 'to' position is habited by another piece
    if board.state[to_row][to_col] != '.': return False

    #if piece is not king
    if board.state[from_row][from_col] == our_color[0]: 
        if forward == 'up' and to_row == from_row-1: return True
        if forward == 'down' and to_row == from_row+1: return True
    
    #If piece is king
    if board.state[from_row][from_col] == our_color[1]: return True
            
            

                    
#Checks if there could be multiple capture
def capture_jumps(board, from_row, from_col, to_row, to_col, jumped_row, jumped_col, player_color):
    moves_dict = {}
    final_positions = []
    final_coord = []
    #if king, can go zigzag back; if not, go forward
    if player_color == 'r':
        color = ['r','R']
        forward = 'up'
    elif player_color == 'b':
        color = ['b', 'B']
        forward = 'down'
    
    #update board
    board_rightafter = update_board(board, from_row, from_col, to_row, to_col, jumped_row, jumped_col)
    
    capturables = capturable_neighbors(board_rightafter, to_row, to_col, player_color) #[[from_row, from_col, to_row, to_col, jumped_row, jumped_col, []],...]    
    
    for n in range(len(capturables)):
        way = capturables[n]
        
        moves_dict.setdefault((from_row, from_col, to_row, to_col, jumped_row, jumped_col), []).append((way[0], way[1], way[2], way[3], way[4], way[5]))#become tuple
        
        board_now = update_board(board_rightafter, way[0], way[1], way[2], way[3], way[4], way[5])

        if (board_rightafter.state[way[0]][way[1]] == 'r' and way[2] == 0) or (board_rightafter.state[way[0]][way[1]] == 'b' and way[2] == 7):
                final_positions.append(copy.deepcopy(board_now))
                final_coord.append(way)
                continue
        
        #check if any neighbor is possible to be jumped over
        neighbor_of_neighbor = capturable_neighbors(board_now, way[2], way[3], player_color)
        
        while neighbor_of_neighbor:#while lis is not empty

            one_neighbor = neighbor_of_neighbor.pop()
            
            if (board_now.state[one_neighbor[0]][one_neighbor[1]] == 'r' and one_neighbor[2] == 0) or (board_now.state[one_neighbor[0]][one_neighbor[1]] == 'b' and one_neighbor[2] == 7):
                break
            
            board_now = update_board(board_now, one_neighbor[0], one_neighbor[1], one_neighbor[2], one_neighbor[3], one_neighbor[4], one_neighbor[5])
            neighbor_of_neighbor = capturable_neighbors(board_now, one_neighbor[2], one_neighbor[3], player_color)
            moves_dict.setdefault((way[0], way[1], way[2], way[3], way[4], way[5]),[]).append((one_neighbor[0], one_neighbor[1], one_neighbor[2], one_neighbor[3], one_neighbor[4], one_neighbor[5]))
            way = copy.copy(one_neighbor)
            
        final_positions.append(copy.deepcopy(board_now))
        final_coord.append(way)
    
    return final_positions, final_coord, moves_dict

def DFMiniMax(node, depth, maximizingPlayer, caching_state):
    best_child = None
    if tuple(node.state) in caching_state:
        return caching_state[tuple(node.state)][0], caching_state[tuple(node.state)][1]
    if depth == 0 or node.black == 0 or node.red == 0:
        caching_state[tuple(node.state)] = node.utility, best_child
        return node.utility, best_child
    if maximizingPlayer: 
        value = -10000
        player = 'r'
        children = get_successors(node, player)
        if children == []:
            caching_state[tuple(node.state)] = node.utility, best_child
            return node.utility, best_child
        for child in children:
            nxt_val,nxt_child = DFMiniMax(child, depth-1, False, caching_state)
            value, best_child = nxt_val, child
            
    if not maximizingPlayer: 
        value = 10000
        player = 'b'
        children = get_successors(node, player)
        if children == []:
            caching_state[tuple(node.state)] = node.utility, best_child
            return node.utility, best_child
        for child in children:
            nxt_val,nxt_child = DFMiniMax(child, depth-1, True,caching_state)
            value, best_child = nxt_val, child
    
    return value, best_child
    
def AlphaBeta(node, depth, alpha, beta, maximizingPlayer, caching_state):
    best_child = None
    #If node has been explored before with the same alpha, beta in caching_state, no need to explore further
    if tuple(node.state) in caching_state and caching_state[tuple(node.state)][1] == alpha and caching_state[tuple(node.state)][2] == beta: 
        return caching_state[tuple(node.state)][0], caching_state[tuple(node.state)][3]
    #Terminal function: if depth has been reached or one player wins
    if depth == 0 or node.black == 0 or node.red == 0:
        caching_state[tuple(node.state)] = node.utility, best_child
        return node.utility, best_child
    
    if maximizingPlayer: 
        value = -10000
        player = 'r'
        children = get_successors(node, player)
        #Another terminal criteria
        if children == []:
            caching_state[tuple(node.state)] = node.utility, alpha, beta, best_child
            return node.utility, best_child
        for child in children:
            nxt_val,nxt_child = AlphaBeta(child, depth-1, alpha, beta, False, caching_state)
            if value < nxt_val: 
                value, best_child = nxt_val, child
                caching_state[tuple(node.state)] = value, alpha, beta, best_child
            if value >= beta: 
                return value, best_child
            alpha = max(alpha, value)
        
    if not maximizingPlayer: 
        value = 10000
        player = 'b'
        children = get_successors(node, player)
        #Another terminal criteria
        if children == []:
            caching_state[tuple(node.state)] = node.utility, best_child
            return node.utility, best_child
        for child in children:
            nxt_val,nxt_child = AlphaBeta(child, depth-1, alpha, beta, True, caching_state)
            
            if value > nxt_val: 
                value, best_child = nxt_val, child
                caching_state[tuple(node.state)] = value, alpha, beta, best_child
            if value <= alpha: 
                return value, best_child
            beta = min(beta, value)
    
    return value, best_child

import sys
inFile = sys.argv[1]
outFile = sys.argv[2]

this = Board()
this.read(inFile)
this.calc_utility()

caching_state = {}

#val, best = DFMiniMax(this, 8, True, caching_state)

val, best = AlphaBeta(this, 8, float('-inf'), float('inf'), True, caching_state)

with open(outFile,'w') as o:
    o.write('\n'.join(best.state))
