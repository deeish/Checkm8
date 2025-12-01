# Setup and Run Instructions

## Quick Start

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install tkinter (for GUI)
On macOS with Homebrew Python, you need to install Python with tkinter support:

```bash
brew install python-tk
```

Or if that doesn't work, you can reinstall Python with tkinter:
```bash
brew reinstall python@3.13
```

**Alternative**: If tkinter installation is problematic, you can use the system Python which usually has tkinter:
```bash
/usr/bin/python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Run the Game
```bash
python main.py
```

Or with custom AI depth:
```bash
python main.py --depth 4
```

### 5. Run Tests
```bash
pytest tests/
```

Or with verbose output:
```bash
pytest tests/ -v
```

## Troubleshooting

### If tkinter still doesn't work:
1. Try using system Python: `/usr/bin/python3`
2. Or install Python via pyenv with tkinter support
3. Or use a different GUI library (we can modify the code to use PyQt5 or another library)

### If you get "command not found" errors:
- Make sure the virtual environment is activated (you should see `(venv)` in your prompt)
- Use `python3` instead of `python` if needed
- Use `pip3` instead of `pip` if needed

