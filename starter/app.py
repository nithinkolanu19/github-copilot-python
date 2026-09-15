from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0
}

def _parse_board(data):
    if not isinstance(data, dict) or not isinstance(data.get('board'), list):
        return None
    board = data['board']
    if len(board) != sudoku_logic.SIZE:
        return None
    if any(not isinstance(row, list) or len(row) != sudoku_logic.SIZE for row in board):
        return None
    if any(
        not isinstance(cell, int) or isinstance(cell, bool) or cell < 0 or cell > sudoku_logic.SIZE
        for row in board
        for cell in row
    ):
        return None
    return board

def _invalid_board_response():
    return jsonify({'error': 'Board must be a 9x9 grid containing numbers from 0 to 9'}), 400

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    if difficulty:
        difficulty = difficulty.lower()
        if difficulty not in sudoku_logic.DIFFICULTY_CLUES:
            return jsonify({'error': 'Unknown difficulty level'}), 400
        puzzle, solution = sudoku_logic.generate_puzzle_for_difficulty(difficulty)
        clues = sudoku_logic.DIFFICULTY_CLUES[difficulty]
    else:
        try:
            clues = int(request.args.get('clues', 35))
        except (TypeError, ValueError):
            return jsonify({'error': 'Clues must be a valid number'}), 400
        if clues < 0 or clues > sudoku_logic.SIZE * sudoku_logic.SIZE:
            return jsonify({'error': 'Clues must be between 0 and 81'}), 400
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
        difficulty = 'medium'
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty, 'clues': clues})

@app.route('/hint', methods=['POST'])
def hint():
    data = request.get_json(silent=True)
    board = _parse_board(data)
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if board is None:
        return _invalid_board_response()

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] == sudoku_logic.EMPTY and board[row][col] == sudoku_logic.EMPTY:
                CURRENT['hints_used'] += 1
                return jsonify({
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                    'hints_used': CURRENT['hints_used']
                })

    return jsonify({
        'error': 'No empty cells available for a hint',
        'hints_used': CURRENT['hints_used']
    }), 400

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True)
    board = _parse_board(data)
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if board is None:
        return _invalid_board_response()
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)