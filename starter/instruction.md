# GitHub Copilot Instructions

## Project Context

This project is a Python Flask Sudoku application. The existing application, tests, and user-facing behavior are the baseline for all refactoring work.

## General Development Rules

- Preserve existing working functionality unless a stated requirement requires changing it.
- Keep the code modular, readable, reusable, and well commented.
- Prefer small, focused changes that fit the existing project structure and patterns.
- Do not remove existing tests or weaken tests just to make them pass.
- Update `README.md` with relevant setup, testing, and usage instructions when behavior or workflow changes.

## Testing

- Use `pytest` for automated tests.
- Keep all existing tests passing.
- Add tests for every new or changed feature.
- Include both Sudoku logic tests and Flask/application behavior tests where appropriate.
- Test normal behavior, invalid input, boundary cases, and error handling for changed functionality.

## Sudoku Requirements

- Ensure every generated Sudoku puzzle has exactly one unique solution.
- Support Easy, Medium, and Hard difficulty levels with different numbers of prefilled cells.
- Prefilled cells must remain locked and must not be editable by the player.
- Provide immediate feedback when a player makes an invalid move.
- Provide a completion message when the puzzle is solved.
- Add Hint functionality that fills one correct cell and locks it.
- Add Check functionality that highlights incorrect entries without changing correct entries.
- Add a timer for the active puzzle and include the completed time in score records.

## Scores and Interface

- Store the Top 10 scores in `localStorage`.
- Each score must include the player name, time, difficulty, and hints used.
- Provide an accessible, responsive interface that works on desktop and mobile layouts.
- Provide light mode and dark mode, with controls that are accessible by keyboard and usable with assistive technology.
- Use alternating styling for the 3x3 Sudoku blocks while preserving clear visual distinction and sufficient color contrast.
- Ensure controls, status messages, puzzle cells, and feedback are accessible to keyboard and screen-reader users.
