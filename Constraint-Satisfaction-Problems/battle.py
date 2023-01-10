# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 19:15:41 2022

@author: audre
"""

'''
Constraints:
1. Row constraints
2. Col constraints
3. Ships constraints
'''
#Set ship constraint as variable
#tuple for every variable. (ship-type or size, ship identifier)
#e.g. 2 of 2x1 ships then (2,0) and (2,1) 
import sys

class Variable:
    def __init__(self, name, domain=[]):
        self.name = name
        self.size = name[0]
        self.dom = domain
        self.isAssigned = False
    
    def add_domain(self, values):
        for v in values:
            self.dom.append(v)
    
#     def assigned(self):
#         self.isAssigned = True
        
class Constraint:
    def __init__(self, name, constr_val):
        self.name = name #col or row ind
        self.constr_val = constr_val #col or row constraint i.e. # of ships in its col or row
    
    def decrease_ships_left(self, number):
        self.ships_left -= number
    
    def __str__(self):
        return("{}({})".format(self.name,self.constr_val))

class Node:
    def __init__(self):
        self.state = None
        self.row_text = None
        self.col_text = None
        self.s1 = None
        self.s2 = None
        self.s3 = None
        self.s4 = None
        self.row_const = []
        self.col_const = []
        self.size = None
        self.vars = []
    
    def add_var(self, name, domain):
        self.vars.append(Variable(name,domain))
    
    def assign_var(self, n, assign_t_or_f):
        for v in self.vars:
            if v.name == n:
#                 print("inside assign_var",v.name, n)
                v.isAssigned =assign_t_or_f
        
    def add_row_const(self, name, constr_val):
        self.row_const.append(Constraint(name,constr_val))
    
    def add_col_const(self, name, constr_val):
        self.col_const.append(Constraint(name,constr_val))
        
    def check_const(self):
        for rc in self.row_const:
            row_ind = rc.name
            ships_count = self.size - self.state[row_ind].count('W') - self.state[row_ind].count('0')
            if ships_count > rc.constr_val: 
                print("saying false row_ind:", row_ind, "constr_val:",rc.constr_val," ships count:", ships_count)
                return False
        def transpose(l1, l2):
            res = []
            l2 = list(map(list, zip(*l1)))
            for row in l2: res.append(''.join(row))
            return res
        t_state = transpose(self.state,[])
        for i in range(10):
            print(self.state[i])
        print()
        for i in range(10):
            print(t_state[i])
        
        for cc in self.col_const:
            col_ind = cc.name
            ships_count = self.size - t_state[col_ind].count('W') - t_state[col_ind].count('0')
            if ships_count > cc.constr_val: 
                print("saying false col_ind:", col_ind, "constr_val:",rc.constr_val, " ships count:", ships_count)
                return False
        return True
        
    def read(self, file_path):
        file = open(file_path)
        data = file.read()
        text = data.split("\n")
        while '' in text:
            text.remove('')
        print(text)
        file.close()
        
        self.state = text[3:]
        self.row_text = text[0]
        self.col_text = text[1]
        
        ship_types = len(text[2])
        self.s1 = int(text[2][0])
        if ship_types > 1:
            self.s2 = int(text[2][1])
            if ship_types > 2:
                self.s3 = int(text[2][2])
                if ship_types > 3:
                    self.s4 = int(text[2][3])
        
        self.size = len(self.state)
        
    def replace(self, row_ind, col_ind, new_char):
        if self.state[row_ind][col_ind] == '0' or (self.state[row_ind][col_ind] == 'Z' and (new_char == "X" or new_char == "Y")) or (self.state[row_ind][col_ind] in ["X",'Y'] ):
            self.state[row_ind] = self.state[row_ind][:col_ind] + new_char + self.state[row_ind][col_ind + 1:]
    
    def find_inds(self, row_ind, ship_letter):
        #Return list of column indices that match ship_letter
        return [i for i, ltr in enumerate(self.state[row_ind]) if ltr == ship_letter]
        
#--------------------------------------------------------------------------------------------------

def solver(start_node,outFile):
    
    def change_all_unassigned_char_in_col(start_node, col_ind, new_char):
        for row_ind in range(len(start_node.state)):
            if start_node.state[row_ind][col_ind] == "0":
                start_node.state[row_ind] = start_node.state[row_ind][:col_ind] + new_char + start_node.state[row_ind][col_ind + 1:]
    
    #Apply Initializing heuristic to reduce the search space by updating the state
    
    #1. Block rows/cols that satisfy other constraints already
    def update_constraint_blocking(start_node):
        for row_ind in range(start_node.size):
            row_C = int(start_node.row_text[row_ind])
            row_ships = start_node.size - start_node.state[row_ind].count('W') - start_node.state[row_ind].count('0')
            unassigned_square = start_node.state[row_ind].count('0')
#             print("row_C", row_C, "row_ships", row_ships)
            if unassigned_square == 0: continue
            elif row_C == row_ships: 
                start_node.state[row_ind] = start_node.state[row_ind].replace('0', 'W')

        for col_ind in range(start_node.size):
            col_C = int(start_node.col_text[col_ind])
            col_ships = start_node.size
            unassigned_square = 0
            for row_ind in range(start_node.size):
                if start_node.state[row_ind][col_ind] == '0': 
                    col_ships-=1
                    unassigned_square +=1
                if start_node.state[row_ind][col_ind] == 'W':
                    col_ships-=1
#             print("col_C", col_C, "col_ships", col_ships)
            if unassigned_square == 0: continue
            elif col_C == col_ships: change_all_unassigned_char_in_col(start_node, col_ind, "W")
#         print("update_constraint_blocking", start_node.state)
        return start_node
            
    start_node = update_constraint_blocking(start_node)
    
    #2. For edge ships, add ship (X or Y) to it. X means ship is horizontal. Y means ship is vertical
    ship_part = ['L','R','T','B','M']
    
    for row_ind in range(start_node.size): 
        if any(part in start_node.state[row_ind] for part in ship_part):
#             print('row_ind', row_ind, 'masuk')
            L_inds = start_node.find_inds(row_ind, "L")
            R_inds = start_node.find_inds(row_ind, "R")
            T_inds = start_node.find_inds(row_ind, "T")
            B_inds = start_node.find_inds(row_ind, "B")
            M_inds = start_node.find_inds(row_ind, "M")
            if len(L_inds) > 0:
                for part_ind in L_inds:
                    start_node.replace(row_ind, part_ind+1, "X")
            if len(R_inds) > 0:
                for part_ind in R_inds:
                    start_node.replace(row_ind, part_ind-1, "X")
            if len(T_inds) > 0:
                for part_ind in T_inds:
                    start_node.replace(row_ind+1, part_ind, "Y")
            if len(B_inds) > 0:
                for part_ind in B_inds:
                    start_node.replace(row_ind-1, part_ind, "Y")
            if len(M_inds) > 0:
                for part_ind in M_inds:
                    #If right or left of M is W, assign ship (X) to its top and bottom
                    if start_node.state[row_ind][part_ind+1] == "W" or start_node.state[row_ind][part_ind-1] == "W":
                        start_node.replace(row_ind+1, part_ind, "Y")
                        start_node.replace(row_ind-1, part_ind, "Y")
                    #If top or bottom of M is W, 
                    if start_node.state[row_ind+1][part_ind] == "W" or start_node.state[row_ind-1][part_ind] == "W":
                        start_node.replace(row_ind, part_ind+1, "X")
                        start_node.replace(row_ind, part_ind-1, "X")
                        
    #3. Block rows/cols that satisfy constraints bcs of this added ship & add surrounding Ws for each assigned ship block accordingly
    start_node = update_constraint_blocking(start_node)
    
    def update_surrounding_blocking(start_node):
        for row_ind in range(start_node.size): 
            S_inds = start_node.find_inds(row_ind, "S")
            L_inds = start_node.find_inds(row_ind, "L")
            R_inds = start_node.find_inds(row_ind, "R")
            T_inds = start_node.find_inds(row_ind, "T")
            B_inds = start_node.find_inds(row_ind, "B")
            M_inds = start_node.find_inds(row_ind, "M")
            X_inds = start_node.find_inds(row_ind, "X")
            Y_inds = start_node.find_inds(row_ind, "Y")
            
            block_left = B_inds + L_inds + T_inds + S_inds + Y_inds
            if block_left:
                for col_ind in block_left:
                    if col_ind>0: start_node.replace(row_ind, col_ind-1, "W")
            
            block_right = B_inds + R_inds + T_inds + S_inds + Y_inds
            if block_right:
                for col_ind in block_right:
                    if col_ind<start_node.size-1: start_node.replace(row_ind, col_ind+1, "W")
                        
            block_top = L_inds + R_inds + T_inds + S_inds + X_inds
            if block_top:
                for col_ind in block_top:
                    if row_ind>0: start_node.replace(row_ind-1, col_ind, "W")
                        
            block_bottom = L_inds + R_inds + B_inds + S_inds + X_inds
            if block_bottom:
                for col_ind in block_bottom:
                    if row_ind<start_node.size-1: start_node.replace(row_ind+1, col_ind, "W")
                        
            block_diagonals = S_inds + L_inds + R_inds + T_inds + B_inds + X_inds + Y_inds + M_inds
            if block_diagonals:
                for col_ind in block_diagonals:
                    if row_ind>0 and col_ind>0: start_node.replace(row_ind-1, col_ind-1, "W") #topleft
                    if row_ind>0 and col_ind<start_node.size-1: start_node.replace(row_ind-1, col_ind+1, "W") #topright
                    if row_ind<start_node.size-1 and col_ind>0: start_node.replace(row_ind+1, col_ind-1, "W") #botleft
                    if row_ind<start_node.size-1 and col_ind<start_node.size-1: start_node.replace(row_ind+1, col_ind+1, "W") #botright
            
            if M_inds:
                for col_ind in M_inds:
                    if row_ind == 0: start_node.replace(row_ind+1, col_ind, "W")
                    elif row_ind == start_node.size-1: start_node.replace(row_ind+1, col_ind, "W")
                    if col_ind == 0: start_node.replace(row_ind, col_ind+1, "W")
                    elif col_ind == start_node.size-1: start_node.replace(row_ind, col_ind-1, "W")
#         print("update_surrounding_blocking", start_node.state)
        return start_node
            
    start_node = update_surrounding_blocking(start_node)
    
    #4. Check if previous step will help middle piece direction
    for row_ind in range(start_node.size): 
        if 'M' in start_node.state[row_ind]:
            for part_ind in M_inds:
                #If right or left of M is W, assign ship (X) to its top and bottom
                if start_node.state[row_ind][part_ind+1] == "W" or start_node.state[row_ind][part_ind-1] == "W":
                    start_node.replace(row_ind+1, part_ind, "Y")
                    start_node.replace(row_ind-1, part_ind, "Y")
                #If top or bottom of M is W, 
                if start_node.state[row_ind+1][part_ind] == "W" or start_node.state[row_ind-1][part_ind] == "W":
                    start_node.replace(row_ind, part_ind+1, "X")
                    start_node.replace(row_ind, part_ind-1, "X")
                    
    #5. If Step 4 changes something, Block rows/cols that satisfy constraints bcs of this added ship & add surrounding Ws for each assigned ship block accordingly
            start_node = update_constraint_blocking(start_node)
            start_node = update_surrounding_blocking(start_node)

    print("Final state:", start_node.state)
    
    #6. Assign ships to row/col that satisfy: Number of unassigned box in a row/col = row/col constraint
    def assign_ships_to_satisfying_const(start_node):
        for row_ind in range(start_node.size): 
            row_C = int(start_node.row_text[row_ind])
            unassigned_square = start_node.state[row_ind].count('0')
            row_ships = start_node.size - start_node.state[row_ind].count('W') - unassigned_square
    #         print(start_node.state[row_ind], row_C, unassigned_square, row_ships)

            if row_C == row_ships + unassigned_square and unassigned_square >0:
                start_node.state[row_ind] = start_node.state[row_ind].replace('0', 'Z')

        for col_ind in range(start_node.size):
            col_C = int(start_node.col_text[col_ind])
            col_ships = start_node.size
            unassigned_square = 0
            for row_ind in range(start_node.size):
                if start_node.state[row_ind][col_ind] == '0': 
                    col_ships-=1
                    unassigned_square +=1
                if start_node.state[row_ind][col_ind] == 'W':
                    col_ships-=1

#             print("col_ind",col_ind, "col_C",col_C, "col_ships",col_ships,"unassigned_square",unassigned_square)

            if col_C == col_ships + unassigned_square and unassigned_square >0:
                change_all_unassigned_char_in_col(start_node,col_ind,"Z")
#                 print("assigned z")

        #Replace Zs into X or Ys if possible to know the ship direction if its more than size 1x1
        for row_ind in range(start_node.size): 
            Z_inds = start_node.find_inds(row_ind, "Z")
#             print(Z_inds)
            for col_ind in Z_inds:
#                 print(start_node.state[row_ind], col_ind>0 and col_ind<start_node.size-1 )
                if (col_ind == 0 and start_node.state[row_ind][col_ind+1] == "W") or (col_ind==start_node.size-1 and start_node.state[row_ind][col_ind-1] == "W") or (col_ind>0 and col_ind<start_node.size-1 and start_node.state[row_ind][col_ind-1] == "W" and start_node.state[row_ind][col_ind+1] == "W"):
                    start_node.replace(row_ind, col_ind, "Y")
                if (row_ind == 0 and start_node.state[row_ind+1][col_ind] == "W") or (row_ind==start_node.size-1 and start_node.state[row_ind-1][col_ind] == "W") or (row_ind>0 and row_ind<start_node.size-1 and start_node.state[row_ind-1][col_ind] == "W" and start_node.state[row_ind+1][col_ind] == "W"):
                    start_node.replace(row_ind, col_ind, "X")
                if (col_ind == 0 and start_node.state[row_ind][col_ind+1] in ['Z','M','R','X']) or (col_ind==start_node.size-1 and start_node.state[row_ind][col_ind-1] in ['Z','M','L','X']) or ((col_ind>0 and col_ind<start_node.size-1) and (start_node.state[row_ind][col_ind-1] in ['Z','M','L','X'] or start_node.state[row_ind][col_ind+1] in ['Z','M','R','X'])):
                    start_node.replace(row_ind, col_ind, "X")
                if (row_ind == 0 and start_node.state[row_ind+1][col_ind] in ['Z','M','B','X']) or (row_ind==start_node.size-1 and start_node.state[row_ind-1][col_ind] in ['Z','M','T','X']) or ((row_ind>0 and row_ind<start_node.size-1) and (start_node.state[row_ind-1][col_ind] in ['Z','M','T','X'] or start_node.state[row_ind+1][col_ind] in ['Z','M','B','X'])):
                    start_node.replace(row_ind, col_ind, "Y")
        
        return start_node
                   
    start_node = assign_ships_to_satisfying_const(start_node)

    #7. Block rows/cols that satisfy constraints bcs of this added ship & add surrounding Ws for each assigned ship block accordingly
    start_node= update_constraint_blocking(start_node)
    start_node=update_surrounding_blocking(start_node)
    
    # print("before 8 state:", start_node.state)
    #8. Step 6 again
    start_node=assign_ships_to_satisfying_const(start_node)
    
    #9. Step 7 again
    start_node=update_constraint_blocking(start_node)
    start_node=update_surrounding_blocking(start_node)
    
    start_node=assign_ships_to_satisfying_const(start_node)
    start_node=update_constraint_blocking(start_node)
    start_node=update_surrounding_blocking(start_node)
    
    # print("Final state:", start_node.state)

    def translate(start_node,outFile):
        for row_ind in range(start_node.size): 
            X_inds = start_node.find_inds(row_ind, "X")
            Y_inds = start_node.find_inds(row_ind, "Y")
            for i_x in range(len(X_inds)):
#                 print(row_ind, X_inds[i_x], start_node.state[row_ind][X_inds[i_x]])
                if X_inds[i_x] == 0: #if col_index is 0
#                     print("masuk")
                    if start_node.state[row_ind][X_inds[i_x]+1]== "W": start_node.replace(row_ind,X_inds[i_x],"S")
                    else:
#                         print(row_ind)
                        start_node.replace(row_ind,X_inds[i_x],"L")
                elif X_inds[i_x] == start_node.size-1: #if col_index is n
                    if start_node.state[row_ind][X_inds[i_x]-1]== "W": start_node.replace(row_ind,X_inds[i_x],"S")
                    else: start_node.replace(row_ind,X_inds[i_x],"R")
                elif start_node.state[row_ind][X_inds[i_x]+1]!= "W" and start_node.state[row_ind][X_inds[i_x]-1]== "W": 
                    start_node.replace(row_ind,X_inds[i_x],"L")
                elif start_node.state[row_ind][X_inds[i_x]+1]!= "W" and start_node.state[row_ind][X_inds[i_x]-1]!= "W": 
                    start_node.replace(row_ind,X_inds[i_x],"M")
                elif start_node.state[row_ind][X_inds[i_x]+1]== "W" and start_node.state[row_ind][X_inds[i_x]-1]!= "W": 
                    start_node.replace(row_ind,X_inds[i_x],"R")
                else: start_node.replace(row_ind,X_inds[i_x],"S")
#                 elif start_node.state[row_ind][X_inds[i_x]+1]== "W" and start_node.state[row_ind][X_inds[i_x]-1]== "W" and start_node.state[row_ind+1][X_inds[i_x]] == "W" and start_node.state[row_ind-1][X_inds[i_x]] == "W": start_node.replace(row_ind,X_inds[i_x],"S")
            for i_y in range(len(Y_inds)):
#                 print(row_ind, Y_inds[i_y])
                if row_ind == 0: #if row_index is 0
                    if start_node.state[row_ind+1][Y_inds[i_y]]== "W": start_node.replace(row_ind,Y_inds[i_y],"S")
                    else: start_node.replace(row_ind,Y_inds[i_y],"T")
                elif row_ind == start_node.size-1: #if col_index is n
                    if start_node.state[row_ind-1][Y_inds[i_y]]== "W": start_node.replace(row_ind,Y_inds[i_y],"S")
                    else: start_node.replace(row_ind,Y_inds[i_y],"B")
                elif start_node.state[row_ind+1][Y_inds[i_y]]!= "W" and start_node.state[row_ind-1][Y_inds[i_y]]== "W": 
                    start_node.replace(row_ind,Y_inds[i_y],"T")
                elif start_node.state[row_ind+1][Y_inds[i_y]]!= "W" and start_node.state[row_ind-1][Y_inds[i_y]]!= "W": 
                    start_node.replace(row_ind,Y_inds[i_y],"M")
                elif start_node.state[row_ind+1][Y_inds[i_y]]== "W" and start_node.state[row_ind-1][Y_inds[i_y]]!= "W": 
                    start_node.replace(row_ind,Y_inds[i_y],"B")
                else: start_node.replace(row_ind,Y_inds[i_y],"S")
#                 elif start_node.state[row_ind][X_inds[i_x]+1]== "W" and start_node.state[row_ind][X_inds[i_x]-1]== "W" and start_node.state[row_ind+1][X_inds[i_x]] == "W" and start_node.state[row_ind-1][X_inds[i_x]] == "W": start_node.replace(row_ind,X_inds[i_x],"S")
        
        with open(outFile,'w') as o:
            o.write('\n'.join(start_node.state))
        return start_node            
    
    import copy
    
    def set_const_var(start_node):
        #Assign constraints
        for i in range(len(start_node.row_text)):
            start_node.add_row_const(i, int(start_node.row_text[i]))
        for i in range(len(start_node.col_text)):
            start_node.add_col_const(i, int(start_node.col_text[i]))

        #Find domain for each type of ship
        #domain = [(start_row, start_col, size, h_or_v),...]
        zero_grid_state = copy.copy(start_node.state)
        X_grid_state = copy.copy(start_node.state)
        for row in range(start_node.size):
#             print(row)
            zero_grid_state[row] = zero_grid_state[row].replace('T','0')
            zero_grid_state[row] = zero_grid_state[row].replace('B','0')
            zero_grid_state[row] = zero_grid_state[row].replace('M','0')
            zero_grid_state[row] = zero_grid_state[row].replace('L','0')
            zero_grid_state[row] = zero_grid_state[row].replace('R','0')
            zero_grid_state[row] = zero_grid_state[row].replace('X','0')
            zero_grid_state[row] = zero_grid_state[row].replace('Y','0')
            zero_grid_state[row] = zero_grid_state[row].replace('S','0')
            
            X_grid_state[row] = X_grid_state[row].replace('T','X')
            X_grid_state[row] = X_grid_state[row].replace('B','X')
            X_grid_state[row] = X_grid_state[row].replace('M','X')
            X_grid_state[row] = X_grid_state[row].replace('L','X')
            X_grid_state[row] = X_grid_state[row].replace('R','X')
            X_grid_state[row] = X_grid_state[row].replace('Y','X')
            X_grid_state[row] = X_grid_state[row].replace('S','X')
        
        s4_row_domain = []
        s3_row_domain = []
        s2_row_domain = []
        s1_row_domain = []
        
        row_ind = 0
        for row_const in start_node.row_const:
#             print("row_ind",row_ind)
            text = zero_grid_state[row_ind]
            if row_const.constr_val >= 4: 
                col_start_domain = [n for n in range(len(text)) if text.find('0000', n) == n]
                
                for col_ind in col_start_domain:
                    s4_row_domain.append((row_ind, col_ind, 4, 'h'))
            if row_const.constr_val >= 3:  
#                 print("col_start_domain",col_start_domain)
                col_start_domain = [n for n in range(len(text)) if text.find('000', n) == n]
                for col_ind in col_start_domain:
                    s3_row_domain.append((row_ind, col_ind, 3, 'h'))
            if row_const.constr_val >= 2:  
                col_start_domain = [n for n in range(len(text)) if text.find('00', n) == n]
#                 print("col_start_domain",col_start_domain)
                for col_ind in col_start_domain:
#                     print("col idn", col_ind)
#                     print("start_node.state[row_ind][col_ind]+start_node.state[row_ind][col_ind+1] in ['00', 'XX']", start_node.state[row_ind][col_ind]+start_node.state[row_ind][col_ind+1] in ['00', 'XX'],"start_node.state[row_ind][col_ind+2] in ['0','W']",start_node.state[row_ind][col_ind+2] in ['0','W'])
#                     print()
                    if col_ind==0:
                        if start_node.state[row_ind][col_ind]+start_node.state[row_ind][col_ind+1]+start_node.state[row_ind][col_ind+2] in ['000','XX0','XXW']:
#                         print('adding')
                            s2_row_domain.append((row_ind, col_ind, 2, 'h'))       
                    elif col_ind==start_node.size-2:
                        if start_node.state[row_ind][col_ind-1]+start_node.state[row_ind][col_ind]+start_node.state[row_ind][col_ind+1] in ['000','0XX','WXX']:
#                         print('adding')
                            s2_row_domain.append((row_ind, col_ind, 2, 'h'))
                    elif start_node.state[row_ind][col_ind-1] in ['0','W'] and start_node.state[row_ind][col_ind]+start_node.state[row_ind][col_ind+1] in ['00', 'XX'] and start_node.state[row_ind][col_ind+2] in ['0','W']:
#                         print('adding')
                        s2_row_domain.append((row_ind, col_ind, 2, 'h'))
                   
            if row_const.constr_val >= 1:  
                col_start_domain = [n for n in range(len(text)) if text.find('0', n) == n]
                for col_ind in col_start_domain:
                    if col_ind==0:
                        if row_ind==0 and (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind+1] in ['0','W'] and start_node.state[row_ind+1][col_ind] in ['0','W'])):
                            s1_row_domain.append((row_ind, col_ind, 1, 'h'))   
                        elif row_ind==start_node.size-1 and (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind+1] in ['0','W'] and start_node.state[row_ind-1][col_ind] in ['0','W'])):
                            s1_row_domain.append((row_ind, col_ind, 1, 'h'))  
                        elif (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind+1] in ['0','W'] and start_node.state[row_ind+1][col_ind] in ['0','W'] and start_node.state[row_ind-1][col_ind] in ['0','W'])):
                            s1_row_domain.append((row_ind, col_ind, 1, 'h'))   
                    elif col_ind==start_node.size-1:
                        print("row_ind",row_ind, "col_ind",col_ind)
#                         if row_ind==0 and (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind-1] in ['0','W'] and start_node.state[row_ind+1][col_ind] in ['0','W'])):
#                             s1_row_domain.append((row_ind, col_ind, 1, 'h'))   #no need already in rcol_ind==0 first elif
                        if row_ind==start_node.size-1 and (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind-1] in ['0','W'] and start_node.state[row_ind-1][col_ind] in ['0','W'])):
                            s1_row_domain.append((row_ind, col_ind, 1, 'h'))  
                        elif (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind-1] in ['0','W'] and start_node.state[row_ind+1][col_ind] in ['0','W'] and start_node.state[row_ind-1][col_ind] in ['0','W'])):
                            s1_row_domain.append((row_ind, col_ind, 1, 'h'))   
                    elif row_ind==start_node.size-1:
                        if (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind-1] in ['0','W'] and start_node.state[row_ind-1][col_ind] in ['0','W'] and start_node.state[row_ind][col_ind+1] in ['0','W'])):
                            s1_row_domain.append((row_ind, col_ind, 1, 'h'))  
                    else:
#                         print("start_node.state[row_ind][col_ind]", start_node.state[row_ind][col_ind], "row_ind",row_ind, "col_ind",col_ind)
                        if (start_node.state[row_ind][col_ind] =='S' or (start_node.state[row_ind][col_ind] =='0' and start_node.state[row_ind][col_ind-1] in ['0','W'] and start_node.state[row_ind+1][col_ind] in ['0','W'] and start_node.state[row_ind-1][col_ind] in ['0','W'] and start_node.state[row_ind][col_ind+1] in ['0','W'])):
                            s1_row_domain.append((row_ind, col_ind, 1, 'h'))        
            row_ind += 1
        
        
        def transpose(l1, l2):
            res=[]
            l2 = list(map(list, zip(*l1)))
            for row in l2: res.append(''.join(row))
            return res
        transposed_state = transpose(zero_grid_state, [])
        
        X_transposed_state = transpose(X_grid_state, [])
        
        s4_col_domain = []
        s3_col_domain = []
        s2_col_domain = []
        s1_col_domain = []
        
        col_ind = 0
        for col_const in start_node.col_const:
            # print("col_ind",col_ind)
            
            text = transposed_state[col_ind] #transposed
#             print(text)
#             print("col_ind",col_ind)
            if col_const.constr_val >= 4: 
                row_start_domain = [n for n in range(len(text)) if text.find('0000', n) == n]
                
                for row_ind in row_start_domain:
                    s4_col_domain.append((row_ind, col_ind, 4, 'v'))
            if col_const.constr_val >= 3:  
                row_start_domain = [n for n in range(len(text)) if text.find('000', n) == n]
                for row_ind in row_start_domain:
                    s3_col_domain.append((row_ind, col_ind, 3, 'v'))
                
            if col_const.constr_val >= 2:  
                row_start_domain = [n for n in range(len(text)) if text.find('00', n) == n]
                for row_ind in row_start_domain:
                    
                    if row_ind==0:
                        if X_transposed_state[col_ind][row_ind]+X_transposed_state[col_ind][row_ind+1]+X_transposed_state[col_ind][row_ind+2] in ['000','XX0','XXW','00W']:
                            s2_row_domain.append((row_ind, col_ind, 2, 'v'))  
                    elif row_ind==start_node.size-2:
                        if X_transposed_state[col_ind][row_ind-1]+X_transposed_state[col_ind][row_ind]+X_transposed_state[col_ind][row_ind+1] in ['000','0XX','WXX','W00']:
                            s2_row_domain.append((row_ind, col_ind, 2, 'v'))
                    elif X_transposed_state[col_ind][row_ind-1] in ['0','W'] and X_transposed_state[col_ind][row_ind]+X_transposed_state[col_ind][row_ind+1] in ['00', 'XX'] and X_transposed_state[col_ind][row_ind+2] in ['0','W']:
                        s2_row_domain.append((row_ind, col_ind, 2, 'v'))
            col_ind += 1    
            
        #Assign variables
        for s4_ind in range(start_node.s4):
            name = (4,s4_ind)
            start_node.add_var(name, s4_row_domain+s4_col_domain)
        for s3_ind in range(start_node.s3):
            name = (3,s3_ind)
            start_node.add_var(name, s3_row_domain+s3_col_domain)
        for s2_ind in range(start_node.s2):
            name = (2,s2_ind)
            start_node.add_var(name, s2_row_domain+s2_col_domain)
        for s1_ind in range(start_node.s1):
            name = (1,s1_ind)
            start_node.add_var(name, s1_row_domain+s1_col_domain)
        
        print("Total variables:")
        for every_var in start_node.vars:
            print("Name: ", every_var.name,every_var.dom)
            
        return start_node
    
    cache = set()
    def BT(s):
        
        print("Inside BT new Level:")
        node = copy.deepcopy(s) 
        for row in node.state: print(row)
        #See which variables are assigned
        unassign_vars = [v for v in node.vars if not v.isAssigned]
        for v in node.vars:
            print("node.var:", v.name, "isAssigned:", v.isAssigned)
        # print("node inside new BT:", node.state, unassign_vars)
        if not unassign_vars:
            node = translate(node,outFile)
            print("BT Solution Translated state:\n", '\n'.join(node.state))
            sys.exit("Solution found") 
        else:
            var = unassign_vars.pop(0)
            node.assign_var(var.name, True)
            # print("start_node", node.state)
            print("selected var", var.name, var.dom)
            
            for d in var.dom:
                h_or_v = d[3]
                start_row = d[0]
                start_col = d[1]
                length = d[2]
                
#                 print("selected domain", d)
                
                #Update the state
                node_now = copy.deepcopy(node) 
#                 print("node_now before update state", node_now.state)
                
                valid, node_now.state = update_state(node_now, start_row, start_col, length, h_or_v)
#                 print("node_now after update state from d", d, node_now.state)
                
                if valid:
                    # for each constraint C, check if they're satisfied.If not,
                    ConstraintsOK = node_now.check_const()
                    # print(ConstraintsOK)
                    if ConstraintsOK: 
                        # print("lanjut:")
                        # for row_string in node_now.state:
                        #     print(row_string)
                        BT(node_now)
                #if not valid, assign_var to false
            node.assign_var(var.name, False)
            return
                
                
            
    def update_state(node_now, start_row, start_col, length, h_or_v):
        row = start_row
        col = start_col
        if h_or_v == 'h':
            for i in range(length):
                if node_now.state[row][col] == '0':
                    if col+1 > node_now.size-1:
                        node_now.state[row] = node_now.state[row][:col] + "X"
                    else:
                        node_now.state[row] = node_now.state[row][:col] + "X" + node_now.state[row][col+1:]
                    col+=1
                else: 
#                     print("returning false in update state")
                    return False, []
            node_now = update_constraint_blocking(node_now)
            node_now = update_surrounding_blocking(node_now)
#             print("di dlm update_state", node_now.state)
            return True, node_now.state
        if h_or_v == 'v':
            print(node_now.state)
            def transpose(l1, l2):
                res = []
                l2 = list(map(list, zip(*l1)))
                for row in l2: res.append(''.join(row))
                return res
            transposed_state = transpose(node_now.state,[])
            for i in range(length):
                if transposed_state[col][row] == '0':
                    if row+1 > node_now.size-1:
                        transposed_state[col] = transposed_state[col][:row] + "Y"
                    else:
                        transposed_state[col] = transposed_state[col][:row] + "Y" + transposed_state[col][row+1:]
                    row+=1
                else: return False,[]
            node_now.state = transpose(transposed_state, [])
#             print("in update_state, before update blockings:\n", '\n'.join(node_now.state))
            node_now = update_constraint_blocking(node_now)
            node_now = update_surrounding_blocking(node_now)
            string_state = "".join(node_now.state)
            if string_state in cache:
#                 print('skipped bcs cached')
                return False,[]
            cache.add(string_state)
                
            return True, node_now.state
                
        
    for row in start_node.state:
        if '0' in row:
            start=copy.deepcopy(start_node)
            for row in range(start.size):
                start.state[row] = start.state[row].replace('T','0')
                start.state[row] = start.state[row].replace('B','0')
                start.state[row] = start.state[row].replace('M','0')
                start.state[row] = start.state[row].replace('L','0')
                start.state[row] = start.state[row].replace('R','0')
                start.state[row] = start.state[row].replace('X','0')
                start.state[row] = start.state[row].replace('Y','0')
                start.state[row] = start.state[row].replace('S','0')
#                 print(start.state[row])
            
            
            start=set_const_var(start)
            BT(start)
            break
    translate(start_node,outFile)
            
inFile = sys.argv[1]
outFile = sys.argv[2]
testh1 = Node()
testh1.read(inFile)
solver(testh1,outFile)