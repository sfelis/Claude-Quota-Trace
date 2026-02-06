# Contributing to Floating Ball

Thank you for your interest in contributing!

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment and install dependencies
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/floating-ball.git
cd floating-ball

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run the app
python3 main.py
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to classes and functions
- Keep functions focused and small

## Creating New Themes

See `themes/README.md` for the theme development guide.

Basic steps:
1. Create a new file in `themes/` (e.g., `my_theme.py`)
2. Extend `BaseTheme` class
3. Implement required methods: `get_ball_size()`, `get_spacing()`, `draw_ball()`
4. Register in `themes/__init__.py`
5. Add to dropdown in `settings_dialog.py`

## Pull Request Guidelines

- Create a descriptive title
- Explain what changes you made and why
- Include screenshots for UI changes
- Ensure no new warnings or errors
- Test on macOS before submitting

## Reporting Issues

When reporting bugs, please include:
- macOS version
- Python version
- Steps to reproduce
- Expected vs actual behavior
- Any error messages from terminal

## Questions?

Feel free to open an issue for questions or discussions.
