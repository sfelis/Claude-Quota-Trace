# Theme System

The floating ball app uses a theme system to customize the appearance of the usage indicators.

## Current Themes

- **circle**: Circle design with outer progress ring
- **water**: Water filling style with vivid colors that change based on usage (blue, gold, orange, red)
- **real-water**: Water filling style with realistic water color (always blue like real water)
- **glacier**: Floating glacier over water with jagged ice peaks, glass-like lighting effects, and gradient text with darker rims
- **glacier-test**: (Same as glacier - testing ground for experimental features)

## Color Themes

Color themes control the text color progression based on usage percentage. You can mix any visual theme with any color theme.

- **fulfill** (default): Green → Orange → Purple
  - Treats high usage as achievement/fulfillment
  - 0-59%: Green
  - 60-79%: Orange
  - 80-100%: Purple

- **alarm**: Purple → Orange → Red
  - Treats high usage as warning
  - 0-59%: Purple
  - 60-79%: Orange
  - 80-100%: Red

## Creating a New Visual Theme

1. Create a new file in `themes/` directory (e.g., `my_theme.py`)
2. Inherit from `BaseTheme` class
3. Implement required methods:
   - `__init__(color_theme_name: str = "fulfill")`: Call `super().__init__(color_theme_name)`
   - `get_ball_size()`: Return ball size in pixels
   - `get_spacing()`: Return spacing between balls
   - `draw_ball(painter, x_offset, data)`: Draw the ball

4. Use color theme for text colors:
   ```python
   # Get colors from the color theme
   text_color, rim_color = self.color_theme.get_text_colors(data.usage_percentage)
   ```

5. Register your theme in `themes/__init__.py`:
```python
from .my_theme import MyTheme

THEMES = {
    "circle": CircleTheme,
    "my_theme": MyTheme,  # Add your theme
}
```

## Creating a New Color Theme

1. Open `themes/color_themes.py`
2. Create a new class inheriting from `ColorTheme`
3. Implement `get_text_colors(usage_percentage)` method:
   ```python
   class MyColorTheme(ColorTheme):
       def get_text_colors(self, usage_percentage: float) -> Tuple[QColor, QColor]:
           if usage_percentage < 0.6:
               text_color = QColor(...)
               rim_color = QColor(...)
           # ... more thresholds
           return text_color, rim_color
   ```

4. Register in `COLOR_THEMES` dict:
   ```python
   COLOR_THEMES = {
       "fulfill": FulfillColorTheme,
       "alarm": AlarmColorTheme,
       "my_colors": MyColorTheme,  # Add your color theme
   }
   ```

## BallData Class

The `draw_ball()` method receives a `BallData` object with:

- `usage_percentage` (float): Usage as decimal (0.0 to 1.0)
- `utilization` (int): Usage as integer percentage (0-100)
- `reset_time` (str): Formatted reset time (e.g., "3:45")
- `label` (str): Ball label ("5h" or "7d")
- `is_error` (bool): Whether in error state

## Example Theme

```python
from PyQt6.QtGui import QPainter, QColor, QBrush
from PyQt6.QtCore import Qt
from .base_theme import BaseTheme, BallData

class SquareTheme(BaseTheme):
    def get_ball_size(self):
        return 80

    def get_spacing(self):
        return 10

    def draw_ball(self, painter, x_offset, data):
        # Draw a square instead of circle
        size = self.get_ball_size()

        color = QColor("#34C759") if data.usage_percentage < 0.8 else QColor("#FF3B30")

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_offset, 0, size, size)

        # Draw text...
```

## Switching Themes

You can switch both visual themes and color themes in two ways:

1. **Via Settings Dialog (Recommended)**:
   - Right-click on the floating ball
   - Select "Settings..."
   - Choose your preferred visual theme from the "Theme" dropdown
   - Choose your preferred color scheme from the "Color Theme" dropdown
   - Click "Save"
   - The app will automatically reload with the new themes

2. **Programmatically in code**:
   ```python
   ball = BallWindow(theme_name="circle")  # Visual theme
   # Color theme is loaded from settings
   ```
