// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCORE_STORAGE_KEY = 'sudokuTopScores';
const THEME_STORAGE_KEY = 'sudokuTheme';
let puzzle = [];
let currentDifficulty = 'medium';
let hintsUsed = 0;
let timerStartedAt = null;
let elapsedSeconds = 0;
let timerInterval = null;
let puzzleComplete = false;
let latestGameRequest = 0;

function applyTheme(theme) {
  const selectedTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = selectedTheme;
  const toggle = document.getElementById('theme-toggle');
  toggle.innerText = selectedTheme === 'dark' ? 'Light mode' : 'Dark mode';
  toggle.setAttribute('aria-label', selectedTheme === 'dark'
    ? 'Switch to light mode' : 'Switch to dark mode');
  toggle.setAttribute('aria-pressed', selectedTheme === 'dark' ? 'true' : 'false');
}

function loadTheme() {
  try {
    applyTheme(window.localStorage.getItem(THEME_STORAGE_KEY));
  } catch (error) {
    applyTheme('light');
  }
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  } catch (error) {
    // Keep the selected theme active for this page when storage is unavailable.
  }
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainingSeconds = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainingSeconds}`;
}

function updateTimer() {
  document.getElementById('timer').innerText = formatTime(elapsedSeconds);
}

function stopTimer() {
  if (timerStartedAt !== null) {
    elapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
  }
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  timerStartedAt = null;
  updateTimer();
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  timerStartedAt = Date.now();
  updateTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds = Math.floor((Date.now() - timerStartedAt) / 1000);
    updateTimer();
  }, 1000);
}

function isValidScore(score) {
  return score && typeof score.name === 'string' && score.name.trim() &&
    Number.isInteger(score.time) && score.time >= 0 &&
    typeof score.difficulty === 'string' &&
    Number.isInteger(score.hints) && score.hints >= 0;
}

function readScores() {
  try {
    const stored = window.localStorage.getItem(SCORE_STORAGE_KEY);
    const scores = stored ? JSON.parse(stored) : [];
    const normalized = Array.isArray(scores)
      ? sortScores(scores.filter(isValidScore)).slice(0, 10) : [];
    window.localStorage.setItem(SCORE_STORAGE_KEY, JSON.stringify(normalized));
    return normalized;
  } catch (error) {
    return [];
  }
}

function sortScores(scores) {
  return scores.sort((first, second) => first.time - second.time);
}

function renderLeaderboard() {
  const list = document.getElementById('score-list');
  const status = document.getElementById('leaderboard-status');
  list.innerHTML = '';
  const scores = sortScores(readScores()).slice(0, 10);
  if (scores.length === 0) {
    status.innerText = 'No scores saved yet.';
    return;
  }
  status.innerText = '';
  scores.forEach((score) => {
    const item = document.createElement('li');
    item.innerText = `${score.name} - ${formatTime(score.time)} - ` +
      `${score.difficulty} - ${score.hints} hint${score.hints === 1 ? '' : 's'}`;
    list.appendChild(item);
  });
}

function saveScore(score) {
  try {
    const scores = sortScores(readScores().concat(score)).slice(0, 10);
    window.localStorage.setItem(SCORE_STORAGE_KEY, JSON.stringify(scores));
    renderLeaderboard();
    return true;
  } catch (error) {
    return false;
  }
}

function getBoardValues() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const value = inputs[i * SIZE + j].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

function hasConflict(board, row, col, value) {
  for (let index = 0; index < SIZE; index++) {
    if (index !== col && board[row][index] === value) return true;
    if (index !== row && board[index][col] === value) return true;
  }
  const startRow = row - row % 3;
  const startCol = col - col % 3;
  for (let boxRow = startRow; boxRow < startRow + 3; boxRow++) {
    for (let boxCol = startCol; boxCol < startCol + 3; boxCol++) {
      if ((boxRow !== row || boxCol !== col) && board[boxRow][boxCol] === value) {
        return true;
      }
    }
  }
  return false;
}

function getConflictingCells(board, inputs) {
  const conflicts = new Set();
  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const input = inputs[row * SIZE + col];
      if (!input.disabled && board[row][col] !== 0 && hasConflict(board, row, col, board[row][col])) {
        conflicts.add(row * SIZE + col);
      }
    }
  }
  return conflicts;
}

function setCellState(input, conflicting, incorrect = false) {
  const classes = ['sudoku-cell'];
  if (input.disabled) {
    classes.push(input.dataset.hinted === 'true' ? 'hinted' : 'prefilled');
  } else if (input.value) {
    classes.push('user-entry');
  }
  if (input.dataset.block === 'alt') {
    classes.push('block-alt');
  }
  if (conflicting || incorrect) {
    classes.push('incorrect');
    input.setAttribute('aria-invalid', 'true');
    input.title = 'Conflicting or incorrect entry';
  } else {
    input.removeAttribute('aria-invalid');
    input.removeAttribute('title');
  }
  input.className = classes.join(' ');
}

function updateConflictFeedback() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const conflicts = getConflictingCells(getBoardValues(), inputs);
  for (let index = 0; index < inputs.length; index++) {
    setCellState(inputs[index], conflicts.has(index));
  }
  const feedback = document.getElementById('move-feedback');
  feedback.innerText = conflicts.size
    ? 'Conflicting entry. Check its row, column, and 3x3 box.'
    : '';
  return conflicts;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.setAttribute('role', 'gridcell');
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.block = (Math.floor(i / 3) + Math.floor(j / 3)) % 2
        ? 'alt' : 'base';
      if (i === 2 || i === 5) rowDiv.classList.add('block-boundary');
      rowDiv.setAttribute('role', 'row');
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateConflictFeedback();
        const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
        if (!Array.from(inputs).some(cell => !cell.value)) checkPuzzle();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        delete inp.dataset.hinted;
        setCellState(inp, false);
      } else {
        inp.value = '';
        inp.disabled = false;
        delete inp.dataset.hinted;
        setCellState(inp, false);
      }
    }
  }
}

async function newGame() {
  const difficultySelector = document.getElementById('difficulty-selector');
  const difficulty = difficultySelector.value;
  const requestId = ++latestGameRequest;
  const difficultyName = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
  document.getElementById('selected-difficulty').innerText = difficultyName;
  document.getElementById('message').innerText = 'Starting new puzzle...';
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  if (requestId !== latestGameRequest) return;
  renderPuzzle(data.puzzle);
  currentDifficulty = data.difficulty;
  hintsUsed = 0;
  puzzleComplete = false;
  document.getElementById('completion').hidden = true;
  document.getElementById('player-name').value = '';
  document.getElementById('score-feedback').innerText = '';
  document.getElementById('save-score').disabled = false;
  document.getElementById('selected-difficulty').innerText =
    data.difficulty.charAt(0).toUpperCase() + data.difficulty.slice(1);
  document.getElementById('message').innerText = '';
  document.getElementById('hint-count').innerText = 'Hints used: 0';
  startTimer();
}

function finishPuzzle() {
  if (puzzleComplete) return;
  puzzleComplete = true;
  stopTimer();
  document.getElementById('completion').hidden = false;
  document.getElementById('completion-summary').innerText =
    `Solved in ${formatTime(elapsedSeconds)} with ${hintsUsed} hint${hintsUsed === 1 ? '' : 's'}.`;
  document.getElementById('player-name').focus();
}

async function requestHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: getBoardValues()})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'error-message';
    msg.innerText = data.error;
    return;
  }
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const input = inputs[data.row * SIZE + data.col];
  input.value = data.value;
  input.disabled = true;
  input.dataset.hinted = 'true';
  hintsUsed = data.hints_used;
  updateConflictFeedback();
  setCellState(input, false);
  document.getElementById('hint-count').innerText = `Hints used: ${data.hints_used}`;
  msg.className = 'success-message';
  msg.innerText = 'A correct cell was filled and locked.';
  if (!Array.from(inputs).some(cell => !cell.value)) {
    await checkPuzzle();
  }
}

async function checkPuzzle() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardValues();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.className = 'error-message';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  const conflicts = getConflictingCells(board, inputs);
  const incorrectEntries = new Set();
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    const isIncorrectEntry = incorrect.has(idx) && Boolean(inp.value);
    if (isIncorrectEntry) incorrectEntries.add(idx);
    setCellState(inp, conflicts.has(idx), isIncorrectEntry);
  }
  const hasEmptyCells = Array.from(inputs).some(input => !input.value);
  if (incorrectEntries.size === 0 && !hasEmptyCells) {
    msg.className = 'success-message';
    msg.innerText = 'Congratulations! You solved it!';
    finishPuzzle();
  } else if (incorrectEntries.size > 0) {
    msg.className = 'error-message';
    msg.innerText = 'Some cells are incorrect.';
  } else {
    msg.className = 'error-message';
    msg.innerText = 'Fill in the remaining cells.';
  }
}

function saveCurrentScore() {
  const nameInput = document.getElementById('player-name');
  const name = nameInput.value.trim();
  const feedback = document.getElementById('score-feedback');
  if (!name) {
    feedback.innerText = 'Enter a player name to save your score.';
    nameInput.focus();
    return;
  }
  const saved = saveScore({
    name,
    time: elapsedSeconds,
    difficulty: currentDifficulty,
    hints: hintsUsed
  });
  feedback.innerText = saved
    ? 'Score saved.'
    : 'Scores are unavailable in this browser.';
  if (saved) document.getElementById('save-score').disabled = true;
}

// Wire buttons
window.addEventListener('load', () => {
  loadTheme();
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('difficulty-selector').addEventListener('change', newGame);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('check-puzzle').addEventListener('click', checkPuzzle);
  document.getElementById('save-score').addEventListener('click', saveCurrentScore);
  renderLeaderboard();
  // initialize
  newGame();
});