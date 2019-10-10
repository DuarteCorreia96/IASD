#!/usr/bin/env python3

## Sudoku solver
## Code done in class of 3-Oct-2019
## Input boards can be found in, e.g., http://lipas.uwasa.fi/~timan/sudoku/
## (C) 2019 Rodrigo Ventura, Instituto Superior Tecnico, Universidade de Lisboa

import sys

#filename = "s09b.txt"
#filename = sys.argv[1]

def load_board(filename):
    with open(filename) as fh:
        lines = fh.readlines()
    return [ [ int(s) for s in ln.split() ] for ln in lines if len(ln.split())>0 ]

def print_board(board):
    for row in board:
        #print(' '.join([str(s) for s in row]))
        print(' '.join(map(str, row)))



def solve(board):
    free = find_free_slot(board)
    if free is None:
        return board
    else:
        (i, j) = free
        for n in range(1, 10):
            board[i][j] = n
            if valid(i, j, board):
                sub = solve(board)
                if sub is not None:
                    return sub
        board[i][j] = 0
        return None
                    
        
def find_free_slot(board):
    for (i,row) in enumerate(board):
        for (j,p) in enumerate(row):
            if p==0:
                return (i, j)
    return None

# def valid(board):
#     #print("valid:")
#     #print_board(board)
#     for i in range(9):
#         if repeated(board[i]):
#             return False
#     for j in range(9):
#         l = [row[j] for row in board]
#         if repeated(l):
#             return False
#     for i in range(0, 9, 3):
#         for j in range(0, 9, 3):
#             l = []
#             for subrow in board[i:i+3]:
#                 l.extend( subrow[j:j+3] )
#             if repeated(l):
#                 return False
#     return True

def valid(i, j, board):
    if repeated(board[i]):
        return False
    col = [ row[j] for row in board ]
    if repeated(col):
        return False
    si = 3*(i//3)
    sj = 3*(j//3)
    square = [ board[si+k][sj+l] for k in range(3) for l in range(3) ]
    if repeated(square):
        return False
    return True

# def repeated(line):
#     for i in range(8):
#         if line[i]!=0 and line[i] in line[i+1:]:
#             return True
#     return False

def repeated(line):
    f = [x for x in line if x!=0]
#    print(f)
#    print(set(f))
    return len(set(f)) != len(f)
        
def main():
    if len(sys.argv)>1:
        board = load_board(sys.argv[1])
        print_board(board)
        print()
        sol   = solve(board)
        if sol is None:
            print("Failed")
        else:
            print_board(sol)
    else:
        print("Usage: %s <filename>"%(sys.argv[0]))



main()

