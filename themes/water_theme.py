"""Water theme - water filling style."""
import math
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QLinearGradient
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF
from .base_theme import BaseTheme, BallData


class WaterTheme(BaseTheme):
    """Water theme with filling water effect."""

    def __init__(self, color_theme_name: str = "fulfill"):
        """Initialize water theme."""
        super().__init__(color_theme_name)

    def get_ball_size(self) -> int:
        """Return the size of a single ball."""
        return 100

    def get_spacing(self) -> int:
        """Return spacing between balls."""
        return 20

    def draw_ball(self, painter: QPainter, x_offset: int, data: BallData, animation_phase: float = 0.0, render_mode: int = 0):
        """Draw a ball with water filling effect."""
        size = self.get_ball_size()
        center_x = x_offset + size // 2
        center_y = size // 2
        radius = (size - 10) // 2

        # Draw shadow
        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x_offset + 8, 8, size - 10, size - 10)

        # Draw dim background ball (rim)
        dim_color = QColor("#CCCCCC") if not data.is_error else QColor("#999999")
        painter.setBrush(QBrush(dim_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

        # Draw water filling effect
        if not data.is_error:
            # Realistic water colors - always blue like real water
            # Lighter blue at surface, deeper blue at bottom
            water_color_light = QColor("#87CEEB")  # Sky blue - surface
            water_color_deep = QColor("#4682B4")   # Steel blue - depth

            # Add slight transparency for realism
            water_color_light.setAlpha(220)
            water_color_deep.setAlpha(240)

            # Calculate water height
            water_height = int((size - 10) * data.usage_percentage)
            water_y = (size - 10) - water_height + 5

            # Create circular clip path
            clip_path = QPainterPath()
            clip_path.addEllipse(QRectF(x_offset + 5, 5, size - 10, size - 10))
            painter.setClipPath(clip_path)

            # Create gradient for water depth effect
            gradient = QLinearGradient(x_offset + 5, water_y, x_offset + 5, water_y + water_height)
            gradient.setColorAt(0, water_color_light)
            gradient.setColorAt(1, water_color_deep)

            # Draw water with gradient
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x_offset + 5, water_y, size - 10, water_height)

            # Draw wave effect at water surface
            if water_height > 5:  # Only draw waves if there's enough water
                wave_path = QPainterPath()
                wave_y = water_y
                wave_amplitude = 3  # Height of waves
                wave_length = 15  # Length of one wave cycle

                # Start from left edge
                wave_path.moveTo(x_offset + 5, wave_y)

                # Create sine wave across the width
                for i in range(size - 10):
                    x = x_offset + 5 + i
                    y = wave_y + wave_amplitude * math.sin((i / wave_length) * 2 * math.pi)
                    wave_path.lineTo(x, y)

                # Complete the path to create a filled wave
                wave_path.lineTo(x_offset + size - 5, water_y + wave_amplitude + 5)
                wave_path.lineTo(x_offset + 5, water_y + wave_amplitude + 5)
                wave_path.closeSubpath()

                # Draw the wave with lighter color and slight transparency
                wave_color = QColor("#B0E0E6")  # Powder blue for wave highlights
                wave_color.setAlpha(180)
                painter.setBrush(QBrush(wave_color))
                painter.drawPath(wave_path)

            # Reset clip
            painter.setClipping(False)

        # Get text color from color theme
        if not data.is_error:
            text_color, _ = self.color_theme.get_text_colors(data.usage_percentage)
        else:
            text_color = QColor(147, 112, 219)  # Purple for error state

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
