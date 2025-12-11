import copy
import sys

from termcolor import colored
import time
import random
import pytesseract
from PIL import Image
import cv2
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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

def print_board_with_numbers(board: list[list[str]]) -> None:

    for i in range(len(board)):
        if i % 3 == 0:
            if i == 0:
                print("y ", end = "")
            else:
                print("  ", end = "")
            for x in range(len(board) * 3 + 4):
                print("-", end="")
            print()

        for j in range(len(board[0])):

            if j == 0:
                print(f"{9 - i} ", end="")

            # seperate boxes(vertical part)
            if j % 3 == 0:
                print("|", end="")

            print(" " + board[i][j] + " ",end="")

        print("|")
    print("  ", end = "")
    for x in range(len(board) * 3 + 4):
        print("-", end="")
    print("\n    1  2  3   4  5  6   7  8  9 x")

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

    MIN_CELLS = 10

    #create empty board
    board = [["." for _ in range(size)] for _ in range(size)]
    attempts = 0

    while True:

        attempts += 1
        num_filled_cells = 0
        placement_attempts = 0
        MAX_PLACEMENT_ATTEMPTS = 500

        while num_filled_cells < filled_cells:

            if placement_attempts > MAX_PLACEMENT_ATTEMPTS:
                #board failed to generate
                break

            placement_attempts += 1
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            val = str(random.randint(1, 9))

            #fill designated number of filled cells
            if board[row][col] == "." and num_is_valid(board, val, row, col) and valid_starting_conditions(board):
                board[row][col] = val
                num_filled_cells += 1

        #placement failed, restart
        if num_filled_cells < filled_cells:
            board = [["." for _ in range(size)] for _ in range(size)]
            continue

        #ensure board is solvable
        if valid_starting_conditions(board):
            test_copy = copy.deepcopy(board)
            if solve(test_copy, "1", 0, 0):
                return board

        #if board isn't solvable, restart
        board = [["." for _ in range(size)] for _ in range(size)]

        #decrease difficult if too many attempts
        if attempts > 40:
            filled_cells = max(MIN_CELLS, filled_cells - 1)
            attempts = 0

def generate_boards(num_boards: int) -> list[list[list[str]]]:
    boards = []
    count = 1
    for i in range(num_boards):
        b = generate_board(20)
        boards.append(b)
        print(f"Generated board: {count}")
        count += 1

    return boards


def determine_time_to_solve(board: list[list[str]]):
    board_copy = copy.deepcopy(board)
    start = time.perf_counter()
    solve(board_copy, "1", 0, 0)
    end = time.perf_counter()
    return end - start

def test_average_time(num_boards: int):
    boards = generate_boards(num_boards)
    times = []

    for board in boards:
        time = determine_time_to_solve(board)
        times.append(time)

    avg = sum(times) / len(times)
    print(f"Average time: {avg:.6f} seconds for {num_boards} boards")

def process_image(image_path:str) -> list[list[str]]:

    os.makedirs("processed_images", exist_ok=True)
    margin = 2

    img = cv2.imread(image_path)
    h,w,_ = img.shape

    cell_h = h // 9
    cell_w = w // 9

    board = []

    for row in range(size):
        board.append([])
        for col in range(size):

            y1 = row * cell_h
            y2 = (row + 1) * cell_h

            x1 = col * cell_w
            x2 = (col + 1) * cell_w

            cell = img[
                y1 + margin : y2 - margin,
                x1 + margin : x2 - margin
            ]

            gray = cv2.cvtColor(cell, cv2.COLOR_BGR2GRAY)

            thresh = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                11,
                2
            )

            digit = pytesseract.image_to_string(
                thresh,
                config="--psm 10 -c tessedit_char_whitelist=0123456789").strip()
            digit = str(digit)
            if len(digit) == 0: digit = "."
            board[row].append(str(digit))

            cv2.imwrite(f"processed_images/cell_{row}_{col}.png", thresh)

    return board

def confirm_board(board: list[list[str]]):

    print(colored("Enter 'e' to exit anytime and continue", 'green'))

    user_input = input("Confirm Board is Correct: (yes/no)")
    print_board_with_numbers(board)
    user_input = user_input.lower().strip()

    if user_input == "yes" or user_input == "y":
        return True

    while True:
        x = input("Enter x coordinate: ")
        if x == "e":
            return False

        y = input("Enter y coordinate: ")
        if y == "e":
            return False

        val = input("Enter value: ")
        if val == "e":
            return False
        if not (0 < int(val) < 10):
            print("Invalid Input, Enter a Number between 1 and 9")
            continue

        y = 9 - int(y)
        x = int(x) - 1

        board[y][x] = val

        print_board_with_numbers(board)
        user_input = input("Confirm Board is Correct: (yes/no)")
        user_input = user_input.lower().strip()

        if user_input == "yes" or user_input == "y":
            return True
        if user_input == "e":
            return False
        else:
            continue






#do_the_stuff(solvable_board)
#test_average_time(num_boards=10)
"""
img = Image.open("images/7.png")
digit = pytesseract.image_to_string(
    img,
    config="--psm 10 -c tessedit_char_whitelist=0123456789")
print(digit)
"""

#board = process_image("images/test2.png")
print_board_with_numbers(solvable_board)

if __name__ == "__main__":
    image_path = ""

    if len(sys.argv) > 0:
        image_path = sys.argv[1]
    else:
        while True:
            print("Options:")
            print("1) Manual Input")
            print("2) Image Input")
            print("3) Exit\n")

            user_input = input(" -> ")

            if user_input == "1":
                x = 1
            elif user_input == "2":
                x = 2
            elif user_input == "3":
                break
            else:
                print("Invalid Input")






        image_path = input("Enter Image Path: ")







