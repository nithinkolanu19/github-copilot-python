import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 30,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def _is_valid_puzzle(board):
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            board[row][col] = EMPTY
            valid = is_safe(board, row, col, value)
            board[row][col] = value
            if not valid:
                return False
    return True

def _count_solutions(board, limit=2):
    if not _is_valid_puzzle(board):
        return 0

    best_cell = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue
            candidates = [
                number
                for number in range(1, SIZE + 1)
                if is_safe(board, row, col, number)
            ]
            if not candidates:
                return 0
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = (row, col)
                best_candidates = candidates

    if best_cell is None:
        return 1

    row, col = best_cell
    solution_count = 0
    for candidate in best_candidates:
        board[row][col] = candidate
        solution_count += _count_solutions(board, limit - solution_count)
        board[row][col] = EMPTY
        if solution_count >= limit:
            return solution_count
    return solution_count

def has_unique_solution(board):
    """Return whether a Sudoku puzzle has exactly one valid solution."""
    return _count_solutions(deep_copy(board), limit=2) == 1

def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1

def generate_puzzle(clues=35):
    while True:
        solution = create_empty_board()
        fill_board(solution)
        puzzle = deep_copy(solution)
        cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
        random.shuffle(cells)

        for row, col in cells:
            if sum(cell != EMPTY for row in puzzle for cell in row) <= clues:
                break
            original = puzzle[row][col]
            puzzle[row][col] = EMPTY
            if not has_unique_solution(puzzle):
                puzzle[row][col] = original

        if sum(cell != EMPTY for row in puzzle for cell in row) == clues:
            return puzzle, solution

def generate_puzzle_for_difficulty(difficulty):
    """Generate a unique-solution puzzle for a named difficulty level."""
    try:
        clues = DIFFICULTY_CLUES[difficulty.lower()]
    except (AttributeError, KeyError):
        raise ValueError('Unknown difficulty level')
    return generate_puzzle(clues)
