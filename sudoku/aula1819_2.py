#!/usr/bin/env python3

## Sudoku solver
## Code done in class of 7-Oct-2019
## Input boards can be found in, e.g., http://lipas.uwasa.fi/~timan/sudoku/
## (C) 2019 Rodrigo Ventura, Instituto Superior Tecnico, Universidade de Lisboa

import sys

def load_board(filename):
    with open(filename) as fh:
        b = [ [ int(a) for a in ln.split() ] for ln in fh.readlines() if len(ln.split())>0 ]
        #print(b)
        return b

#fh.close()

# lines = fh.readlines()
# board = []
# for ln in lines:
#     row = [int(a) for a in ln.split()]
#     # row = []
#     # for a in ln.split():
#     #     n = int(a)
#     #     row.append(n)
#     board.append(row)

def print_board(board):
    for row in board:
        print(' '.join(map(str, row)))
        #print(' '.join([str(n) for n in row]))



def solve(board):
    free = find_free_slot(board)
    if free is None:
        return board
    else:
        # i = free[0]
        # j = free[1]
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
        for (j,value) in enumerate(row):
            if value==0:
                return (i, j)
    return None
    
    # for i in range(9):
    #     row = board[i]
    #     for j in range(9):
    #         value = row[j]
    #         if value==0:
    #             return (i, j)
    # return None

    
def valid(i, j, board):
    # check row
    if repeated(board[i]):
        return False
    # check column
    col = [row[j] for row in board]
    if repeated(col):
        return False
    # check sub-square
    oi = 3*(i//3)
    oj = 3*(j//3)
    l = [ board[oi+di][oj+dj] for di in range(3) for dj in range(3) ]
    # l = []
    # for di in range(3):
    #     for dj in range(3):
    #         l.append(board[oi+di][oj+dj])
    if repeated(l):
        return False
    # all is good
    return True

    

def repeated(line):
    f = [n for n in line if n!=0]
    return len(set(f))!=len(f)

    # for (i,value) in enumerate(line[:-1]):
    #     if value!=0 and value in line[i+1:]:
    #         return True
    # return False


def main():
    # try:
    #     board = load_board(sys.argv[1])
    #     print_board(board)
    # except IndexError:
    #     print("Usage:", sys.argv[0], "<filename>")
        
    if len(sys.argv)>1:
        board = load_board(sys.argv[1])
        print_board(board)
        # print(valid(0, 0, board))
        # return
        sol = solve(board)
        if sol is None:
            print("Unsolvable")
        else:
            print("Solution:")
            print_board(sol)
    else:
        print("Usage:", sys.argv[0], "<filename>")


main()

