"""Opus theme - orchestral aurora with golden sound wave rings."""
import math
import random
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QPainterPath,
                         QLinearGradient, QRadialGradient, QConicalGradient, QPixmap)
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF
from .base_theme import BaseTheme, BallData


class OpusTheme(BaseTheme):
    """Opus theme — deep violet cosmos with golden aurora ribbons and pulsing sound wave rings."""

    def __init__(self, color_theme_name: str = "fulfill"):
        super().__init__(color_theme_name)
        self._background_cache = {}
        self._cache_size = None

    def is_animated(self) -> bool:
        return True

    def get_ball_size(self) -> int:
        return 130

    def get_spacing(self) -> int:
        return 20

    def clear_caches(self):
        self._background_cache.clear()
        self._cache_size = None

    def _draw_background(self, painter, x_offset, size, is_error):
        """Draw shadow and outer shell."""
        # Soft shadow
        painter.setBrush(QBrush(QColor(0, 0, 0, 35)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x_offset + 7, 7, size - 10, size - 10)

        # Outer shell — dark gunmetal with slight warmth
        shell_color = QColor("#3A3040") if not is_error else QColor("#555555")
        painter.setBrush(QBrush(shell_color))
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

    def _draw_cosmos(self, painter, x_offset, size, animation_phase):
        """Draw the deep violet cosmic interior with nebula clouds."""
        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2

        # Clip to ball
        clip = QPainterPath()
        clip.addEllipse(QRectF(x_offset + 5, 5, size - 10, size - 10))
        painter.setClipPath(clip)

        # Deep violet-black radial gradient
        bg = QRadialGradient(QPointF(center_x, center_y), ball_radius)
        bg.setColorAt(0, QColor(45, 20, 60))       # Warm purple center
        bg.setColorAt(0.35, QColor(25, 12, 42))     # Deep violet
        bg.setColorAt(0.7, QColor(12, 8, 28))       # Near black
        bg.setColorAt(1, QColor(5, 3, 15))           # Abyss
        painter.setBrush(QBrush(bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

        # Warm nebula cloud (amber/gold)
        neb1 = QRadialGradient(
            QPointF(center_x + ball_radius * 0.2, center_y - ball_radius * 0.15),
            ball_radius * 0.45
        )
        neb1.setColorAt(0, QColor(200, 150, 50, 30))
        neb1.setColorAt(0.5, QColor(180, 120, 40, 15))
        neb1.setColorAt(1, QColor(150, 100, 30, 0))
        painter.setBrush(QBrush(neb1))
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

        # Cool nebula cloud (violet)
        neb2 = QRadialGradient(
            QPointF(center_x - ball_radius * 0.25, center_y + ball_radius * 0.25),
            ball_radius * 0.4
        )
        neb2.setColorAt(0, QColor(120, 60, 180, 25))
        neb2.setColorAt(0.5, QColor(80, 40, 140, 12))
        neb2.setColorAt(1, QColor(60, 30, 100, 0))
        painter.setBrush(QBrush(neb2))
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

        # Scatter some stars
        random.seed(77)  # Deterministic starfield
        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(20):
            sx = x_offset + 10 + random.randint(0, size - 25)
            sy = 10 + random.randint(0, size - 25)
            ss = random.choice([1, 1, 1, 2])
            sa = random.randint(50, 160)
            # Warm-tinted stars
            if random.random() < 0.5:
                sc = QColor(255, 230, 180, sa)  # Gold-white
            else:
                sc = QColor(220, 200, 255, sa)  # Lavender
            painter.setBrush(QBrush(sc))
            painter.drawEllipse(sx, sy, ss, ss)

        painter.setClipping(False)

    def _draw_aurora_ribbons(self, painter, x_offset, size, animation_phase, usage_pct):
        """Draw flowing golden aurora ribbons that respond to usage."""
        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2

        clip = QPainterPath()
        clip.addEllipse(QRectF(x_offset + 5, 5, size - 10, size - 10))
        painter.setClipPath(clip)

        phase_rad = math.radians(animation_phase)

        # Draw 3 aurora ribbons at different heights
        ribbon_configs = [
            (0.55, 3.0, QColor(255, 200, 80, 55), 0.0),     # Gold ribbon
            (0.40, 2.5, QColor(220, 160, 255, 40), 1.2),     # Violet ribbon
            (0.70, 2.0, QColor(255, 170, 100, 45), 2.5),     # Amber ribbon
        ]

        for y_frac, amplitude, color, phase_shift in ribbon_configs:
            ribbon = QPainterPath()
            base_y = center_y - ball_radius + ball_radius * 2 * y_frac

            points = []
            for i in range(size - 10):
                x = x_offset + 5 + i
                t = i / (size - 10)
                y = (base_y
                     + amplitude * math.sin(t * 4 * math.pi + phase_rad * 0.8 + phase_shift)
                     + amplitude * 0.5 * math.sin(t * 7 * math.pi + phase_rad * 1.3 + phase_shift))
                points.append((x, y))

            if not points:
                continue

            # Draw ribbon as a filled band
            ribbon.moveTo(points[0][0], points[0][1] - 4)
            for x, y in points:
                ribbon.lineTo(x, y - 4)
            for x, y in reversed(points):
                ribbon.lineTo(x, y + 4)
            ribbon.closeSubpath()

            # Scale opacity with usage
            scaled_alpha = int(color.alpha() * (0.4 + 0.6 * usage_pct))
            color.setAlpha(scaled_alpha)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(ribbon)

            # Bright center line
            center_color = QColor(color.red(), color.green(), color.blue(),
                                  min(255, scaled_alpha + 40))
            painter.setPen(QPen(center_color, 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            center_line = QPainterPath()
            center_line.moveTo(points[0][0], points[0][1])
            for x, y in points[1:]:
                center_line.lineTo(x, y)
            painter.drawPath(center_line)

        painter.setClipping(False)

    def _draw_sound_rings(self, painter, x_offset, size, animation_phase, usage_pct):
        """Draw concentric pulsing rings — the 'sound wave' motif."""
        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2

        clip = QPainterPath()
        clip.addEllipse(QRectF(x_offset + 5, 5, size - 10, size - 10))
        painter.setClipPath(clip)

        # 4 concentric rings that pulse outward
        num_rings = 4
        for i in range(num_rings):
            # Each ring has a phase offset so they ripple outward
            phase = (animation_phase + i * 90) % 360
            pulse = 0.5 + 0.5 * math.sin(math.radians(phase))

            base_radius = ball_radius * (0.25 + i * 0.15)
            radius = base_radius + pulse * 4

            # Fade based on distance from center and usage
            alpha = int((50 - i * 10) * (0.3 + 0.7 * usage_pct) * (0.6 + 0.4 * pulse))
            alpha = max(0, min(255, alpha))

            # Gold rings
            ring_color = QColor(255, 200, 100, alpha)
            painter.setPen(QPen(ring_color, 1.5, Qt.PenStyle.SolidLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        painter.setClipping(False)

    def _draw_usage_arc(self, painter, x_offset, size, data, animation_phase):
        """Draw the main usage arc — a sweeping golden crescent with glow."""
        center_x = x_offset + size // 2
        center_y = size // 2
        arc_radius = (size - 10) // 2 - 6

        if data.is_error:
            return

        # Outer decorative ring (subtle)
        painter.setPen(QPen(QColor(200, 170, 120, 50), 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), arc_radius + 3, arc_radius + 3)

        # Usage arc — sweeping from top, clockwise
        span_deg = data.usage_percentage * 360

        # Qt arc: angles in 1/16 degree, counter-clockwise, 0 = 3 o'clock
        qt_start = int(90 * 16)  # Top
        qt_span = int(-span_deg * 16)  # Clockwise

        # Glow layers
        glow_color = QColor(255, 200, 80)
        for width, alpha in [(9, 15), (7, 30), (5, 50)]:
            glow_color.setAlpha(alpha)
            painter.setPen(QPen(glow_color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(
                int(center_x - arc_radius), int(center_y - arc_radius),
                int(arc_radius * 2), int(arc_radius * 2),
                qt_start, qt_span
            )

        # Main arc stroke — golden gradient feel via two-tone
        arc_color = QColor(255, 210, 100, 220)
        painter.setPen(QPen(arc_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(
            int(center_x - arc_radius), int(center_y - arc_radius),
            int(arc_radius * 2), int(arc_radius * 2),
            qt_start, qt_span
        )

        # Bright tip dot at the end of the arc
        if span_deg > 2:
            tip_angle_deg = 90 - span_deg
            tip_rad = math.radians(tip_angle_deg)
            tip_x = center_x + arc_radius * math.cos(tip_rad)
            tip_y = center_y - arc_radius * math.sin(tip_rad)

            # Outer glow
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 220, 100, 80))
            painter.drawEllipse(QPointF(tip_x, tip_y), 5, 5)
            # Inner bright dot
            painter.setBrush(QColor(255, 245, 220, 240))
            painter.drawEllipse(QPointF(tip_x, tip_y), 2.5, 2.5)

        # Time indicator — small orbiting dot on the opposite track
        if data.time_percentage > 0:
            time_radius = arc_radius - 8
            time_span_deg = data.time_percentage * 360
            time_angle_deg = 90 - time_span_deg
            time_rad = math.radians(time_angle_deg)
            time_x = center_x + time_radius * math.cos(time_rad)
            time_y = center_y - time_radius * math.sin(time_rad)

            # Subtle time arc (violet)
            time_qt_span = int(-time_span_deg * 16)
            painter.setPen(QPen(QColor(180, 140, 255, 60), 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(
                int(center_x - time_radius), int(center_y - time_radius),
                int(time_radius * 2), int(time_radius * 2),
                qt_start, time_qt_span
            )

            # Time dot
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(200, 170, 255, 180))
            painter.drawEllipse(QPointF(time_x, time_y), 3, 3)
            painter.setBrush(QColor(230, 210, 255, 255))
            painter.drawEllipse(QPointF(time_x, time_y), 1.5, 1.5)

    def _draw_outer_rim(self, painter, x_offset, size):
        """Draw a thin luminous outer rim."""
        center_x = x_offset + size // 2
        center_y = size // 2
        rim_radius = (size - 10) // 2 + 1

        # Conical gradient for a prismatic rim
        cg = QConicalGradient(QPointF(center_x, center_y), 90)
        cg.setColorAt(0, QColor(255, 220, 140, 100))
        cg.setColorAt(0.25, QColor(200, 160, 255, 80))
        cg.setColorAt(0.5, QColor(255, 200, 120, 100))
        cg.setColorAt(0.75, QColor(180, 140, 240, 80))
        cg.setColorAt(1, QColor(255, 220, 140, 100))

        painter.setPen(QPen(QBrush(cg), 2.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(center_x, center_y), rim_radius, rim_radius)

    def _draw_text(self, painter, x_offset, data, size):
        """Draw text info — warm gold on dark."""
        center_x = x_offset + size // 2
        center_y = size // 2

        if data.is_error and x_offset == 0:
            painter.setPen(QColor(200, 170, 120))
            font = QFont("Georgia", 24)
            painter.setFont(font)
            icon = "\u2603" if data.label == "login" else "\u26A0"
            painter.drawText(QRect(x_offset, 0, size, size), Qt.AlignmentFlag.AlignCenter, icon)
            return

        if data.is_error:
            return

        def draw_outlined(font_obj, x, y, text, color):
            painter.setFont(font_obj)
            # Dark outline for legibility
            painter.setPen(QColor(10, 5, 20, 200))
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx or dy:
                        painter.drawText(int(x + dx), int(y + dy), text)
            painter.setPen(color)
            painter.drawText(int(x), int(y), text)

        # Label (5h / 7d) — above center
        gold = QColor(255, 215, 120, 220)
        font_label = QFont("Georgia", 11, QFont.Weight.Bold)
        painter.setFont(font_label)
        fm = painter.fontMetrics()
        lbl_w = fm.horizontalAdvance(data.label)
        draw_outlined(font_label, center_x - lbl_w // 2, center_y - 14, data.label, gold)

        # Percentage — center, large
        bright_gold = QColor(255, 230, 160, 255)
        pct_text = f"{int(data.utilization)}%"
        font_pct = QFont("Georgia", 16, QFont.Weight.Bold)
        painter.setFont(font_pct)
        fm = painter.fontMetrics()
        pct_w = fm.horizontalAdvance(pct_text)
        draw_outlined(font_pct, center_x - pct_w // 2, center_y + 8, pct_text, bright_gold)

        # Reset time — below center
        if data.reset_time:
            lavender = QColor(200, 180, 255, 200)
            time_text = f"\u21BB{data.reset_time}" if data.reset_time != "now" else "\u21BBnow"
            font_time = QFont("Georgia", 9)
            painter.setFont(font_time)
            fm = painter.fontMetrics()
            tw = fm.horizontalAdvance(time_text)
            draw_outlined(font_time, center_x - tw // 2, center_y + 24, time_text, lavender)

    def draw_ball(self, painter: QPainter, x_offset: int, data: BallData,
                  animation_phase: float = 0.0, render_mode: int = 0):
        """Draw the opus ball."""
        size = self.get_ball_size()

        self._draw_background(painter, x_offset, size, data.is_error)
        self._draw_cosmos(painter, x_offset, size, animation_phase)

        if not data.is_error:
            self._draw_aurora_ribbons(painter, x_offset, size, animation_phase, data.usage_percentage)
            self._draw_sound_rings(painter, x_offset, size, animation_phase, data.usage_percentage)
            self._draw_usage_arc(painter, x_offset, size, data, animation_phase)

        self._draw_outer_rim(painter, x_offset, size)
        self._draw_text(painter, x_offset, data, size)
