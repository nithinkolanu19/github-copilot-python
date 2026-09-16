# Sudoku Game

A Flask-powered Sudoku game with uniquely solvable puzzles, difficulty levels,
guided play, timers, and a persistent local leaderboard.

## Features

- Easy, Medium, and Hard difficulty levels with different clue counts.
- Puzzle generation that guarantees exactly one unique solution.
- Locked prefilled cells and locked Hint-filled cells.
- Immediate invalid-move feedback for row, column, and 3x3 conflicts.
- Check Puzzle validation with incorrect-entry highlighting.
- Hint system that fills one correct cell and tracks hints used.
- Completion message with elapsed time and hints used.
- Timer that starts and resets with each puzzle and stops on completion.
- Top 10 leaderboard persisted in browser `localStorage`.
- Light/dark mode with persisted theme selection.
- Responsive, keyboard-friendly, and accessible interface.
- Alternating 3x3 box styling with stronger box boundaries.

## Technology Stack

- Python
- Flask
- HTML
- CSS
- JavaScript
- pytest

## Project Structure

```text
.
├── starter/
│   ├── app.py
│   ├── instruction.md
│   ├── requirements.txt
│   ├── sudoku_logic.py
│   ├── static/
│   ├── templates/
│   └── Screenshots/
└── tests/
```

## Setup and Usage

From the repository root, create and activate a virtual environment:

```bash
cd starter
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

Open <http://127.0.0.1:5000> in a browser. Select Easy, Medium, or Hard,
then use Hint and Check Puzzle while solving. Completed scores can be saved to
the Top 10 leaderboard with a player name.

## Testing

From the repository root, run:

```bash
python -m pytest -q
```

The current test suite passes **28 tests**.

## Milestone Screenshots

Screenshots documenting the Copilot development milestones are stored in
`starter/Screenshots/`, including testing setup, unique-solution generation,
Top 10 localStorage persistence, and 3x3 grid styling.

## Copilot Guidance

[`starter/instruction.md`](starter/instruction.md) is the project guidance file
for GitHub Copilot. It documents the Sudoku, testing, accessibility, scoring,
and UI requirements used during development.
