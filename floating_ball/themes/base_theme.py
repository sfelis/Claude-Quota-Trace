"""Base theme class for floating ball themes."""
from abc import ABC, abstractmethod
from typing import Tuple
from PyQt6.QtGui import QPainter
from .color_themes import ColorTheme, get_color_theme


class BallData:
    """Data class for ball information."""

    def __init__(self, usage_percentage: float, utilization: int, reset_time: str,
                 label: str, is_error: bool, time_percentage: float = 0.0):
        """
        Initialize ball data.

        Args:
            usage_percentage: Usage as percentage (0.0 to 1.0)
            utilization: Usage as integer percentage (0-100)
            reset_time: Time until reset (formatted string)
            label: Label for the ball (e.g., "5h", "7d")
            is_error: Whether this is an error state
            time_percentage: Time elapsed in reset period (0.0 to 1.0)
        """
        self.usage_percentage = usage_percentage
        self.utilization = utilization
        self.reset_time = reset_time
        self.label = label
        self.is_error = is_error
        self.time_percentage = time_percentage


class BaseTheme(ABC):
    """Base class for themes. Subclass this to create new themes."""

    def __init__(self, color_theme_name: str = "fulfill"):
        """Initialize theme with a color theme."""
        self.color_theme = get_color_theme(color_theme_name)

    def is_animated(self) -> bool:
        """Return True if this theme uses animation, False otherwise."""
        return False

    @abstractmethod
    def get_ball_size(self) -> int:
        """Return the size of a single ball in pixels."""
        pass

    @abstractmethod
    def get_spacing(self) -> int:
        """Return the spacing between balls in pixels."""
        pass

    def get_window_size(self, num_balls: int = 2) -> Tuple[int, int]:
        """Calculate total window size for given number of balls."""
        ball_size = self.get_ball_size()
        spacing = self.get_spacing()
        width = ball_size * num_balls + spacing * (num_balls - 1)
        height = ball_size
        return (width, height)

    @abstractmethod
    def draw_ball(self, painter: QPainter, x_offset: int, data: BallData,
                  animation_phase: float = 0.0, render_mode: int = 0):
        """
        Draw a single ball.

        Args:
            painter: QPainter instance
            x_offset: X offset for this ball
            data: BallData with all information to display
            animation_phase: Animation phase (0-360) for animated effects
            render_mode: 0=no cache, 1=background cache, 2=full cache
        """
        pass
