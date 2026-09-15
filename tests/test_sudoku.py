import app
import sudoku_logic


def assert_valid_solution(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))
    assert all(set(row) == expected for row in board)
    assert all(
        {board[row][column] for row in range(sudoku_logic.SIZE)} == expected
        for column in range(sudoku_logic.SIZE)
    )
    assert all(
        {
            board[row][column]
            for row in range(box_row, box_row + 3)
            for column in range(box_column, box_column + 3)
        } == expected
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_column in range(0, sudoku_logic.SIZE, 3)
    )


def test_create_empty_board_has_expected_shape_and_values():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_fill_board_creates_a_valid_solution():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board) is True
    assert_valid_solution(board)


def test_has_unique_solution_accepts_puzzle_with_one_solution():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    assert sudoku_logic.has_unique_solution(puzzle) is True


def test_has_unique_solution_rejects_puzzle_with_no_solution():
    puzzle = sudoku_logic.create_empty_board()
    puzzle[0][0] = 1
    puzzle[0][1] = 1

    assert sudoku_logic.has_unique_solution(puzzle) is False


def test_has_unique_solution_rejects_puzzle_with_multiple_solutions():
    puzzle = sudoku_logic.create_empty_board()

    assert sudoku_logic.has_unique_solution(puzzle) is False


def test_generate_puzzle_preserves_solution_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(clues=40)

    assert_valid_solution(solution)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40
    assert all(
        puzzle[row][column] in (sudoku_logic.EMPTY, solution[row][column])
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
    )
    assert sudoku_logic.has_unique_solution(puzzle) is True


def test_difficulty_levels_have_distinct_unique_puzzle_sizes(client):
    clue_counts = {}
    for difficulty, expected_clues in sudoku_logic.DIFFICULTY_CLUES.items():
        response = client.get('/new', query_string={'difficulty': difficulty})

        assert response.status_code == 200
        data = response.get_json()
        puzzle = data['puzzle']
        clue_counts[difficulty] = sum(
            cell != sudoku_logic.EMPTY for row in puzzle for cell in row
        )
        assert data['difficulty'] == difficulty
        assert data['clues'] == expected_clues
        assert clue_counts[difficulty] == expected_clues
        assert sudoku_logic.has_unique_solution(puzzle) is True

    assert len(set(clue_counts.values())) == 3


def test_prefilled_cells_are_locked_by_client_script():
    script = (app.app.root_path + '/static/main.js')
    with open(script, encoding='utf-8') as script_file:
        source = script_file.read()

    assert 'if (val !== 0)' in source
    assert 'inp.disabled = true' in source


def test_client_script_validates_row_column_and_box_conflicts():
    script = (app.app.root_path + '/static/main.js')
    with open(script, encoding='utf-8') as script_file:
        source = script_file.read()

    assert 'function hasConflict(board, row, col, value)' in source
    assert 'board[row][index] === value' in source
    assert 'board[index][col] === value' in source
    assert 'boxRow < startRow + 3' in source
    assert 'boxCol < startCol + 3' in source
    assert 'updateConflictFeedback();' in source


def test_invalid_move_feedback_has_accessible_non_color_indicator():
    template = app.app.root_path + '/templates/index.html'
    script = app.app.root_path + '/static/main.js'
    styles = app.app.root_path + '/static/styles.css'
    with open(template, encoding='utf-8') as template_file:
        template_source = template_file.read()
    with open(script, encoding='utf-8') as script_file:
        script_source = script_file.read()
    with open(styles, encoding='utf-8') as styles_file:
        styles_source = styles_file.read()

    assert 'id="move-feedback" role="status"' in template_source
    assert "input.setAttribute('aria-invalid', 'true')" in script_source
    assert 'border: 2px dashed' in styles_source


def test_index_route_renders_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_new_route_returns_requested_number_of_clues(client):
    response = client.get('/new?clues=40')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert len(puzzle) == sudoku_logic.SIZE
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 40


def test_check_route_requires_game_in_progress(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_route_reports_incorrect_cells(client):
    client.get('/new?clues=81')
    solution = app.CURRENT['solution']
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = sudoku_logic.EMPTY

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 0]]


def test_hint_fills_one_empty_cell_and_tracks_usage(client):
    response = client.get('/new?clues=80')
    puzzle = response.get_json()['puzzle']

    hint_response = client.post('/hint', json={'board': puzzle})

    assert hint_response.status_code == 200
    hint = hint_response.get_json()
    assert hint['value'] == app.CURRENT['solution'][hint['row']][hint['col']]
    assert puzzle[hint['row']][hint['col']] == sudoku_logic.EMPTY
    assert hint['hints_used'] == 1
    assert 'solution' not in hint


def test_hint_does_not_overwrite_existing_user_entry(client):
    response = client.get('/new?clues=80')
    puzzle = response.get_json()['puzzle']
    solution = app.CURRENT['solution']
    empty_cell = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] == sudoku_logic.EMPTY
    )
    board = sudoku_logic.deep_copy(puzzle)
    board[empty_cell[0]][empty_cell[1]] = solution[empty_cell[0]][empty_cell[1]]

    hint_response = client.post('/hint', json={'board': board})

    assert hint_response.status_code == 400
    assert hint_response.get_json()['error'] == 'No empty cells available for a hint'
    assert app.CURRENT['hints_used'] == 0


def test_hint_handles_no_empty_cells(client):
    client.get('/new?clues=81')
    solution = app.CURRENT['solution']

    response = client.post('/hint', json={'board': solution})

    assert response.status_code == 400
    assert response.get_json()['hints_used'] == 0


def test_check_route_reports_only_incorrect_entries(client):
    client.get('/new?clues=81')
    solution = app.CURRENT['solution']
    board = sudoku_logic.deep_copy(solution)
    board[0][0] = (solution[0][0] % sudoku_logic.SIZE) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert response.get_json()['incorrect'] == [[0, 0]]


def test_hint_and_check_controls_are_wired_in_client():
    template = app.app.root_path + '/templates/index.html'
    script = app.app.root_path + '/static/main.js'
    with open(template, encoding='utf-8') as template_file:
        template_source = template_file.read()
    with open(script, encoding='utf-8') as script_file:
        script_source = script_file.read()

    assert 'id="hint">Hint</button>' in template_source
    assert 'id="check-puzzle">Check Puzzle</button>' in template_source
    assert "fetch('/hint'" in script_source
    assert "addEventListener('click', requestHint)" in script_source
    assert "addEventListener('click', checkPuzzle)" in script_source
    assert 'input.disabled = true' in script_source


def test_timer_and_leaderboard_are_wired_without_solution_storage():
    template = app.app.root_path + '/templates/index.html'
    script = app.app.root_path + '/static/main.js'
    with open(template, encoding='utf-8') as template_file:
        template_source = template_file.read()
    with open(script, encoding='utf-8') as script_file:
        script_source = script_file.read()

    assert 'id="timer" role="timer"' in template_source
    assert 'id="player-name"' in template_source
    assert 'id="score-list"' in template_source
    assert "window.localStorage.getItem(SCORE_STORAGE_KEY)" in script_source
    assert "window.localStorage.setItem(SCORE_STORAGE_KEY" in script_source
    assert 'setInterval' in script_source
    assert 'stopTimer();' in script_source
    assert 'time: elapsedSeconds' in script_source
    assert 'difficulty: currentDifficulty' in script_source
    assert 'hints: hintsUsed' in script_source
    assert 'solution' not in script_source


def test_theme_toggle_and_accessible_responsive_board_are_wired():
    template = app.app.root_path + '/templates/index.html'
    script = app.app.root_path + '/static/main.js'
    styles = app.app.root_path + '/static/styles.css'
    with open(template, encoding='utf-8') as template_file:
        template_source = template_file.read()
    with open(script, encoding='utf-8') as script_file:
        script_source = script_file.read()
    with open(styles, encoding='utf-8') as styles_file:
        styles_source = styles_file.read()

    assert 'id="theme-toggle"' in template_source
    assert 'aria-pressed="false"' in template_source
    assert "const THEME_STORAGE_KEY = 'sudokuTheme'" in script_source
    assert 'window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme)' in script_source
    assert 'role="grid"' in template_source
    assert "input.setAttribute('role', 'gridcell')" in script_source
    assert 'grid-template-columns: repeat(9, minmax(0, 1fr));' in styles_source
    assert ':root[data-theme="dark"]' in styles_source
    assert 'nth-child(3n + 3)' in styles_source
    assert 'border-bottom: 3px solid var(--border-strong)' in styles_source
    assert "input.dataset.block =" in script_source
    assert 'block-alt' in script_source


def test_difficulty_change_sends_selection_and_ignores_stale_game_responses():
    script = app.app.root_path + '/static/main.js'
    with open(script, encoding='utf-8') as script_file:
        source = script_file.read()

    assert "fetch(`/new?difficulty=${difficulty}`)" in source
    assert 'let latestGameRequest = 0;' in source
    assert 'const requestId = ++latestGameRequest;' in source
    assert 'if (requestId !== latestGameRequest) return;' in source
    assert "addEventListener('change', newGame)" in source


def test_invalid_board_requests_return_json_400_without_solution(client):
    client.get('/new?clues=81')
    for endpoint in ('/hint', '/check'):
        response = client.post(endpoint, data='not-json', content_type='application/json')
        assert response.status_code == 400
        assert response.get_json() == {
            'error': 'Board must be a 9x9 grid containing numbers from 0 to 9'
        }
        assert 'solution' not in response.get_json()

        response = client.post(endpoint, json={'board': [[0]]})
        assert response.status_code == 400
        assert 'solution' not in response.get_json()


def test_invalid_clues_return_json_400(client):
    response = client.get('/new?clues=invalid')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'Clues must be a valid number'}


def test_client_completion_and_leaderboard_normalization_are_wired():
    script = app.app.root_path + '/static/main.js'
    with open(script, encoding='utf-8') as script_file:
        source = script_file.read()

    assert 'if (!Array.from(inputs).some(cell => !cell.value)) checkPuzzle();' in source
    assert 'slice(0, 10)' in source
    assert 'window.localStorage.setItem(SCORE_STORAGE_KEY, JSON.stringify(normalized))' in source


def test_grid_rows_and_actual_block_boundary_styles_are_wired():
    template = app.app.root_path + '/templates/index.html'
    script = app.app.root_path + '/static/main.js'
    styles = app.app.root_path + '/static/styles.css'
    with open(template, encoding='utf-8') as template_file:
        template_source = template_file.read()
    with open(script, encoding='utf-8') as script_file:
        script_source = script_file.read()
    with open(styles, encoding='utf-8') as styles_file:
        styles_source = styles_file.read()

    assert 'role="grid"' in template_source
    assert "rowDiv.setAttribute('role', 'row')" in script_source
    assert 'rowDiv.classList.add(\'block-boundary\')' in script_source
    assert '.sudoku-row.block-boundary .sudoku-cell' in styles_source
    assert 'border-bottom: 3px solid var(--border-strong)' in styles_source
    assert '--error-text:' in styles_source