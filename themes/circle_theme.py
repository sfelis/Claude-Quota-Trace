"""Circle theme - current design."""
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRect
from .base_theme import BaseTheme, BallData


class CircleTheme(BaseTheme):
    """Circle theme with outer progress ring."""

    def __init__(self, color_theme_name: str = "fulfill"):
        """Initialize circle theme."""
        super().__init__(color_theme_name)

    def get_ball_size(self) -> int:
        """Return the size of a single ball."""
        return 100

    def get_spacing(self) -> int:
        """Return spacing between balls."""
        return 20

    def draw_ball(self, painter: QPainter, x_offset: int, data: BallData, animation_phase: float = 0.0, render_mode: int = 0):
        """Draw a ball with circular design."""
        size = self.get_ball_size()

        # Choose color based on utilization
        if data.is_error:
            color = QColor("#999999")  # Gray
        elif data.usage_percentage < 0.6:
            color = QColor("#34C759")  # Green
        elif data.usage_percentage < 0.8:
            color = QColor("#FFD60A")  # Yellow
        elif data.usage_percentage < 0.9:
            color = QColor("#FF9500")  # Orange
        else:
            color = QColor("#FF3B30")  # Red

        # Draw shadow
        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x_offset + 8, 8, size - 10, size - 10)

        # Draw filled circle (inner circle for background)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(x_offset + 13, 13, size - 26, size - 26)

        # Draw progress arc on outer ring (doesn't cover text)
        if not data.is_error:
            pen = QPen(color, 8)  # Thicker arc on outer ring
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            start_angle = 90 * 16
            span_angle = -int(data.usage_percentage * 360 * 16)
            painter.drawArc(x_offset + 5, 5, size - 10, size - 10, start_angle, span_angle)

        # Draw text with purple color for better contrast
        text_color = QColor(147, 112, 219)  # Medium purple
        painter.setPen(text_color)

        if data.is_error and x_offset == 0:  # Only show error icon on first ball
            font = QFont("Arial", 24)
            painter.setFont(font)
            error_icon = "👤" if data.label == "login" else "⚠"
            painter.drawText(QRect(x_offset, 0, size, size), Qt.AlignmentFlag.AlignCenter, error_icon)
        elif not data.is_error:
            # Draw label (5h or 7d)
            font = QFont("Arial", 15)
            painter.setFont(font)
            painter.drawText(QRect(x_offset, 15, size, 16), Qt.AlignmentFlag.AlignCenter, data.label)

            # Draw percentage
            font = QFont("Arial", 16, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(QRect(x_offset, 38, size, 22), Qt.AlignmentFlag.AlignCenter,
                           f"{int(data.utilization)}%")

            # Draw reset time
            font = QFont("Arial", 15)
            painter.setFont(font)
            if data.reset_time:
                display_time = f"in {data.reset_time}" if data.reset_time != "now" else "now"
                painter.drawText(QRect(x_offset, 63, size, 18), Qt.AlignmentFlag.AlignCenter,
                               f"↻ {display_time}")
