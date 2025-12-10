import copy
from termcolor import colored
import time
import random

# 1) Failing initial conditions (invalid from start)
failing_board = [
    ["5", "3", ".", ".", "7", ".", ".", ".", "5"],
    ["6", ".", ".", "1", "9", "5", ".", ".", "."],
    [".", "9", "8", ".", ".", ".", ".", "6", "."],
    ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
    ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
    ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
    [".", "6", ".", ".", ".", ".", "2", "8", "."],
    [".", ".", ".", "4", "1", "9", ".", ".", "5"],
    [".", ".", ".", ".", "8", ".", ".", "7", "9"]
]

# 2) Solvable (valid and has a unique solution)
solvable_board = [
    ["5", "3", ".", ".", "7", ".", ".", ".", "."],
    ["6", ".", ".", "1", "9", "5", ".", ".", "."],
    [".", "9", "8", ".", ".", ".", ".", "6", "."],
    ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
    ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
    ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
    [".", "6", ".", ".", ".", ".", "2", "8", "."],
    [".", ".", ".", "4", "1", "9", ".", ".", "5"],
    [".", ".", ".", ".", "8", ".", ".", "7", "9"]
]

# 3) Passing initial conditions but unsolvable
unsolvable_board = [
    ["5", "3", "1", ".", "7", ".", ".", ".", "."],
    ["6", ".", ".", "1", "9", "5", ".", ".", "."],
    [".", "9", "8", ".", ".", ".", ".", "6", "."],
    ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
    ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
    ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
    [".", "6", ".", ".", ".", ".", "2", "8", "."],
    [".", ".", ".", "4", "1", "9", ".", ".", "5"],
    [".", ".", ".", ".", "8", ".", ".", "7", "9"]
]

test_board = [
    ["1",".",".",".",".","."],
    [".",".",".",".",".","."],
    [".",".",".",".",".","."],
    [".",".",".",".",".","."],
    [".",".",".",".",".","."],
    [".",".",".",".",".","."]
]

size = 9
box = 3

def valid_starting_conditions(board: list[list[str]]) -> bool:
    # check rows
    for row in board:
        seen = set()
        for num in row:
            if not num.isdigit():
                continue
            if num in seen:
                return False
            seen.add(num)

    # check columns
    for c in range(size):
        seen = set()
        for r in range(size):
            v = board[r][c]
            if not v.isdigit() or v == "0":
                continue
            if v in seen:
                return False
            seen.add(v)

    # check boxes
    for br in range(0, size, box):           # box row start indices 0,3,6
        for bc in range(0, size, box):       # box col start indices 0,3,6
            seen = set()
            for r in range(br, br + box):    # inside the 3x3
                for c in range(bc, bc + box):
                    slot = board[r][c]
                    if not slot.isdigit():
                        continue
                    if slot in seen:
                        return False
                    seen.add(slot)

    return True

def num_is_valid(board: list[list[str]], num : str, row: int, col: int) -> bool:

    #check if num in row
    for tile in board[row]:
        if num == tile:
            return False

    #check if num in col
    for i in range(size):
        value = board[i][col]
        if num == value:
            return False

    br = row - row % 3 # box row
    bc = col - col % 3 # box col

    #check if num in box
    for i in range(box):
        for j in range(box):
            value = board[br + i][bc + j]
            if num == value:
                return False

    return True

def print_board_2(board: list[list[str]], original_board: list[list[str]]) -> None:
    #iterate through rows
    for i in range(len(board)):

        #seperate boxes (horizontal part)
        if i % 3 == 0:
            for x in range(len(board) * 3 + 4):
                print("-", end="")
            print()

        #iterate through columns
        for j in range(len(board[0])):

            #seperate boxes(vertical part)
            if j % 3 == 0:
                print("|", end="")

            #print tiles (two options incase you want to see the originals
            if original_board[i][j].isdigit():
                print(colored(" " + board[i][j] + " ", "green"),end="")
            else:
                print(" " + board[i][j] + " ", end="")

        #everything below edge case for boxes
        print("|")
    for x in range(len(board) * 3 + 4):
        print("-", end="")

#normal print board nothing fancy
def print_board(board: list[list[str]]) -> None:
    for i in range(len(board)):
        if i % 3 == 0:
            for x in range(len(board) * 3 + 4):
                print("-", end="")
            print()

        for j in range(len(board[0])):

            # seperate boxes(vertical part)
            if j % 3 == 0:
                print("|", end="")

            print(" " + board[i][j] + " ",end="")

        print("|")
    for x in range(len(board) * 3 + 4):
        print("-", end="")
    print()


def solve(board: list[list[str]],value: str, row: int, col: int) -> bool:

     #increment rows and columns if needed
    if col >= size:
        col = 0
        row += 1

    #base case
    if row >= size:
        return True

    #skip over original cases
    if board[row][col].isdigit():
        col += 1
        return solve(board, value, row, col)

    #store values in memory of current function
    this_row = row
    this_col = col
    this_val = value

    #check every value 1-9
    #if it works, place the value and test the next tile
    #if it doesn't or the tile ahead returns false, increase the value and continue iterating through loop
    while ord(this_val) < ord("9") + 1:
        if num_is_valid(board, this_val, this_row, this_col):
            board[row][col] = this_val
            if solve(board, "1", this_row, this_col + 1):
                return True
            else:
                this_val = chr(ord(this_val) + 1)
        else:
            this_val = chr(ord(this_val) + 1)

    #if all 9 values come back false, reset the tile and go back
    board[this_row][this_col] = "."
    return False

def do_the_stuff(board: list[list[str]]):
    print_board(board)
    copy_board = copy.deepcopy(board)
    if solve(board, "1", 0, 0):
        print("Solved!")
        print_board_2(board, copy_board)
    else:
        print("Impossible!")

def generate_board(filled_cells:int) -> list[list[str]]:

    #create empty board
    board = [["." for _ in range(size)] for _ in range(size)]
    attempts = 0

    while True:
        attempts += 1
        num_filled_cells = 0
        while num_filled_cells < filled_cells:

            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            val = str(random.randint(1, 9))

            #fill designated number of filled cells
            if board[row][col] == "." and num_is_valid(board, val, row, col):
                board[row][col] = val
                num_filled_cells += 1

        #ensure board if solvable
        if valid_starting_conditions(board):
            test_copy = copy.deepcopy(board)
            if solve(test_copy, "1", 0, 0):
                return board

        #if board fails reset
        board = [["." for _ in range(size)] for _ in range(size)]
        if attempts > 40:
            filled_cells -= 1
            attempts = 0









do_the_stuff(solvable_board)


