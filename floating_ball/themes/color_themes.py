"""Color themes for text and status indicators."""
from abc import ABC, abstractmethod
from typing import Tuple
from PyQt6.QtGui import QColor


class ColorTheme(ABC):
    """Base class for color themes."""

    @abstractmethod
    def get_text_colors(self, usage_percentage: float) -> Tuple[QColor, QColor]:
        """
        Get text and rim colors based on usage percentage.

        Args:
            usage_percentage: Usage as decimal (0.0 to 1.0)

        Returns:
            Tuple of (text_color, rim_color)
        """
        pass


class AlarmColorTheme(ColorTheme):
    """Alarm color theme - treats high usage as warning (Purple → Orange → Red)."""

    def get_text_colors(self, usage_percentage: float) -> Tuple[QColor, QColor]:
        """Get alarm-style colors."""
        if usage_percentage < 0.6:
            text_color = QColor(147, 112, 219)  # Purple
            rim_color = QColor(80, 60, 120)     # Dark purple
        elif usage_percentage < 0.8:
            text_color = QColor(255, 140, 0)    # Orange
            rim_color = QColor(180, 80, 0)      # Dark orange
        else:
            text_color = QColor(220, 20, 60)    # Red/Crimson
            rim_color = QColor(139, 0, 0)       # Dark red

        return text_color, rim_color


class FulfillColorTheme(ColorTheme):
    """Fulfill color theme - treats high usage as achievement (Green → Orange → Purple)."""

    def get_text_colors(self, usage_percentage: float) -> Tuple[QColor, QColor]:
        """Get fulfill-style colors."""
        if usage_percentage < 0.6:
            text_color = QColor(34, 197, 94)    # Green
            rim_color = QColor(22, 101, 52)     # Dark green
        elif usage_percentage < 0.8:
            text_color = QColor(255, 140, 0)    # Orange
            rim_color = QColor(180, 80, 0)      # Dark orange
        else:
            text_color = QColor(147, 112, 219)  # Purple
            rim_color = QColor(80, 60, 120)     # Dark purple

        return text_color, rim_color


# Available color themes
COLOR_THEMES = {
    "alarm": AlarmColorTheme,
    "fulfill": FulfillColorTheme,
}


def get_color_theme(name: str = "fulfill") -> ColorTheme:
    """Get a color theme by name."""
    theme_class = COLOR_THEMES.get(name, FulfillColorTheme)
    return theme_class()
