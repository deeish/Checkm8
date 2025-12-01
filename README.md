# CheckM8 - Chess Game with AI

A chess game implementation in Python featuring an AI opponent that uses Minimax search with Alpha-Beta Pruning.

## Features

- **Full Chess Implementation**: Complete chess rules including all piece movements, check, checkmate, and stalemate detection
- **AI Opponent**: Intelligent AI using Minimax algorithm with Alpha-Beta Pruning
- **Heuristic Evaluation**: Position evaluation based on:
  - Material balance (piece values)
  - King safety
  - Piece mobility (number of legal moves)
  - Center control
- **Graphical Interface**: Beautiful 2D chess board with piece graphics using Pygame (with tkinter fallback)
- **Performance Optimized**: AI moves typically complete in ≤1 second at depth 3

## Installation

### Option 1: Using System Python (Recommended for macOS)

The system Python usually has tkinter pre-installed:

```bash
# Create virtual environment with system Python
/usr/bin/python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using Homebrew Python

If you're using Homebrew Python and tkinter is missing:

```bash
# Install python-tk
brew install python-tk

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Game

**First, activate the virtual environment:**
```bash
source venv/bin/activate
```

**Start the game (automatically tries GUI, falls back to console if needed):**
```bash
python main.py
```

**Or specify a custom AI depth:**
```bash
python main.py --depth 4
```

**Force console mode (if GUI has issues):**
```bash
python main.py --console
```

**Or use the run script:**
```bash
./run.sh
```

### Game Modes

- **Pygame GUI Mode** (Default): Beautiful 2D chess board with visual pieces
  - Click a piece to select it
  - Click highlighted squares to move
  - Shows valid moves with yellow highlighting
  - Status panel at bottom shows current turn and game state
  
- **Tkinter GUI Mode**: Fallback graphical interface (if Pygame unavailable)
  
- **Console Mode**: Text-based interface using algebraic notation (e.g., "e2 e4")
  - Automatically used if both GUIs are unavailable
  - Can be forced with `--console` flag

### Running Tests

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v
```

**Note**: Higher depths (4-5) will make the AI stronger but slower. Depth 3 is recommended for a good balance.

### Playing the Game

- You play as **White**, the AI plays as **Black**
- Click on a piece to select it (valid moves will be highlighted)
- Click on a highlighted square to make a move
- The game will automatically detect checkmate, stalemate, and check

## Project Structure

```
Checkm8/
├── chess_game/
│   ├── __init__.py
│   ├── board.py          # Board representation and game logic
│   ├── pieces.py         # Piece definitions and move generation
│   ├── ai.py             # Minimax AI with Alpha-Beta Pruning
│   ├── evaluator.py      # Heuristic evaluation function
│   └── gui.py            # Graphical user interface
├── tests/
│   ├── test_board.py     # Board and move generation tests
│   ├── test_ai.py        # AI and evaluation tests
│   └── test_performance.py  # Performance benchmarks
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
├── test_positions.txt    # Sample positions for testing
└── README.md            # This file
```

## Running Tests

Run all tests:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_board.py
```

Run with verbose output:
```bash
pytest tests/ -v
```

## AI Algorithm Details

### Minimax Search
The AI uses the Minimax algorithm to look ahead several moves, choosing the best move for itself while assuming the opponent will play optimally.

### Alpha-Beta Pruning
Alpha-Beta Pruning significantly speeds up the search by eliminating branches that cannot possibly affect the final decision.

### Evaluation Function
The heuristic evaluation considers:
- **Material**: Piece values (Pawn=100, Knight=320, Bishop=330, Rook=500, Queen=900, King=20000)
- **Mobility**: Number of legal moves available
- **Center Control**: Control of central squares
- **King Safety**: Protection of the king and penalty for being in check

## Performance Targets

- **Accuracy**: Move generation verified against known legal move counts
- **Speed**: Average move time ≤1 second at depth 3 on standard hardware
- **Search Depth**: Configurable from 1-5 (default: 3)

## Team Members

- **Ashton Alva**: Backend development, AI logic and behavior systems
- **Brenen Meregilano**: Frontend development, UI/UX design, QA testing
- **Dylan Salmo**: Backend development, core game logic and mechanics

## Development Tools

- **Language**: Python 3
- **Testing**: pytest
- **Performance**: cProfile / timing utilities
- **Code Quality**: black (formatting), ruff (linting)
- **Version Control**: Git + GitHub

## License

This project is created for educational purposes as part of a course assignment.

## Future Improvements

- Castling support
- En passant capture
- Pawn promotion UI
- Move history/undo
- Save/load games
- Different AI difficulty levels
- Time controls

