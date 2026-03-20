"""Glacier theme - floating glacier over water with glass-like lighting effects."""
import math
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QPainterPath,
                         QLinearGradient, QRadialGradient, QPixmap)
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF
from .base_theme import BaseTheme, BallData


class GlacierTheme(BaseTheme):
    """Glacier theme with floating ice over water and glass-like lighting effects."""

    def __init__(self, color_theme_name: str = "fulfill"):
        """Initialize glacier theme."""
        super().__init__(color_theme_name)
        # Caches for different x_offsets (left ball, right ball)
        self._background_cache = {}  # {x_offset: QPixmap}
        self._light_cache = {}       # {x_offset: QPixmap}
        self._cache_size = None

    def is_animated(self) -> bool:
        """This theme uses animation."""
        return True

    def get_ball_size(self) -> int:
        """Return the size of a single ball."""
        return 100

    def get_spacing(self) -> int:
        """Return spacing between balls."""
        return 20

    def clear_caches(self):
        """Clear all cached pixmaps."""
        self._background_cache.clear()
        self._light_cache.clear()
        self._cache_size = None

    def _ensure_background_cache(self, size, x_offset):
        """Create background cache (shadow + rim) if needed."""
        if x_offset not in self._background_cache or self._cache_size != size:
            pixmap = QPixmap(size + 10, size + 10)  # Extra space for shadow offset
            pixmap.fill(Qt.GlobalColor.transparent)

            p = QPainter(pixmap)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Draw shadow
            p.setBrush(QBrush(QColor(0, 0, 0, 30)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(8, 8, size - 10, size - 10)

            # Draw dim background ball (rim)
            p.setBrush(QBrush(QColor("#CCCCCC")))
            p.drawEllipse(5, 5, size - 10, size - 10)

            p.end()
            self._background_cache[x_offset] = pixmap
            self._cache_size = size

        return self._background_cache[x_offset]

    def _ensure_light_cache(self, size, x_offset):
        """Create light effect cache if needed."""
        if x_offset not in self._light_cache or self._cache_size != size:
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            p = QPainter(pixmap)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)

            # Light source position (relative to pixmap, not x_offset)
            light_center_x = 30
            light_center_y = 25

            # Clip to ball shape
            clip_path = QPainterPath()
            clip_path.addEllipse(QRectF(5, 5, size - 10, size - 10))
            p.setClipPath(clip_path)

            # Create radial gradient
            radial_gradient = QRadialGradient(
                QPointF(light_center_x, light_center_y), 35
            )
            radial_gradient.setColorAt(0, QColor(255, 255, 255, 180))
            radial_gradient.setColorAt(0.4, QColor(255, 255, 255, 100))
            radial_gradient.setColorAt(0.7, QColor(255, 255, 255, 30))
            radial_gradient.setColorAt(1, QColor(255, 255, 255, 0))

            p.setBrush(QBrush(radial_gradient))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(light_center_x - 35, light_center_y - 35, 70, 70)

            p.end()
            self._light_cache[x_offset] = pixmap

        return self._light_cache[x_offset]

    def _draw_background(self, painter, x_offset, size, is_error):
        """Draw shadow and rim directly (no cache)."""
        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x_offset + 8, 8, size - 10, size - 10)

        dim_color = QColor("#CCCCCC") if not is_error else QColor("#999999")
        painter.setBrush(QBrush(dim_color))
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

    def _draw_light_effect(self, painter, x_offset, size):
        """Draw light effect directly (no cache)."""
        light_center_x = x_offset + 30
        light_center_y = 25

        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(x_offset + 5, 5, size - 10, size - 10))
        painter.setClipPath(clip_path)

        radial_gradient = QRadialGradient(
            QPointF(light_center_x, light_center_y), 35
        )
        radial_gradient.setColorAt(0, QColor(255, 255, 255, 180))
        radial_gradient.setColorAt(0.4, QColor(255, 255, 255, 100))
        radial_gradient.setColorAt(0.7, QColor(255, 255, 255, 30))
        radial_gradient.setColorAt(1, QColor(255, 255, 255, 0))

        painter.setBrush(QBrush(radial_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(light_center_x - 35, light_center_y - 35, 70, 70)
        painter.setClipping(False)

    def _draw_dynamic_content(self, painter, x_offset, data, animation_phase, size):
        """Draw glacier, water, and animated waves."""
        if data.is_error:
            return

        # Create circular clip path
        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(x_offset + 5, 5, size - 10, size - 10))
        painter.setClipPath(clip_path)

        # Calculate water and glacier levels
        water_height = int((size - 10) * data.usage_percentage)
        water_y = (size - 10) - water_height + 5

        # Draw floating glacier
        if water_height > 15:
            glacier_offset = 6
            glacier_y = water_y - glacier_offset
            wave_amplitude = 6
            wave_length = 12
            underwater_depth = 12

            full_glacier_path = QPainterPath()
            glacier_bottom = water_y + underwater_depth

            full_glacier_path.moveTo(x_offset + 5, glacier_bottom)
            full_glacier_path.lineTo(x_offset + size - 5, glacier_bottom)

            # Add animation to glacier waves
            phase_offset = (animation_phase / 360.0) * 2 * math.pi
            for i in range(size - 10, -1, -1):
                x = x_offset + 5 + i
                y = glacier_y + wave_amplitude * math.sin((i / wave_length) * 2 * math.pi + phase_offset)
                full_glacier_path.lineTo(x, y)

            full_glacier_path.closeSubpath()

            glacier_gradient = QLinearGradient(
                x_offset + 5, glacier_y - wave_amplitude,
                x_offset + 5, glacier_bottom
            )
            glacier_gradient.setColorAt(0, QColor("#F0F8FF"))
            glacier_gradient.setColorAt(0.3, QColor("#E0F0FF"))

            total_glacier_height = glacier_bottom - (glacier_y - wave_amplitude)
            water_line_position = (water_y - (glacier_y - wave_amplitude)) / total_glacier_height

            glacier_gradient.setColorAt(water_line_position, QColor("#B0D4E8"))
            glacier_gradient.setColorAt(water_line_position + 0.01, QColor("#A0D0E8"))
            glacier_gradient.setColorAt(1, QColor("#6FA8C8"))

            painter.setBrush(QBrush(glacier_gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(full_glacier_path)

        # Draw water
        water_color_light = QColor("#87CEEB")
        water_color_deep = QColor("#4682B4")
        water_color_light.setAlpha(200)
        water_color_deep.setAlpha(220)

        gradient = QLinearGradient(x_offset + 5, water_y, x_offset + 5, size - 5)
        gradient.setColorAt(0, water_color_light)
        gradient.setColorAt(1, water_color_deep)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(x_offset + 5, water_y, size - 10, water_height)

        # Glacier shine
        if water_height > 15:
            shine_path = QPainterPath()
            glacier_offset = 6
            glacier_y = water_y - glacier_offset
            wave_amplitude = 6
            wave_length = 12
            shine_y = glacier_y + 2
            phase_offset = (animation_phase / 360.0) * 2 * math.pi

            for i in range(size - 10):
                x = x_offset + 5 + i
                y = shine_y + (wave_amplitude - 1) * math.sin((i / wave_length) * 2 * math.pi + phase_offset)
                if i == 0:
                    shine_path.moveTo(x, y)
                else:
                    shine_path.lineTo(x, y)

            shine_pen = QPen(QColor(255, 255, 255, 150), 1.5)
            painter.setPen(shine_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(shine_path)

        # Water surface waves
        if water_height > 5:
            wave_surface_path = QPainterPath()
            water_wave_amplitude = 2
            water_wave_length = 20
            phase_offset = (animation_phase / 360.0) * 2 * math.pi * 0.7

            for i in range(size - 10):
                x = x_offset + 5 + i
                y = water_y + water_wave_amplitude * math.sin((i / water_wave_length) * 2 * math.pi + phase_offset)
                if i == 0:
                    wave_surface_path.moveTo(x, y)
                else:
                    wave_surface_path.lineTo(x, y)

            wave_pen = QPen(QColor(135, 206, 235, 100), 1.0)
            painter.setPen(wave_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(wave_surface_path)

        painter.setClipping(False)

    def _draw_text(self, painter, x_offset, data, size):
        """Draw text with outline."""
        if data.is_error and x_offset == 0:
            painter.setPen(QColor(147, 112, 219))
            font = QFont("Arial", 24)
            painter.setFont(font)
            error_icon = "👤" if data.label == "login" else "⚠"
            painter.drawText(QRect(x_offset, 0, size, size), Qt.AlignmentFlag.AlignCenter, error_icon)
        elif not data.is_error:
            text_color, rim_color = self.color_theme.get_text_colors(data.usage_percentage)

            def draw_text_with_outline(font_obj, rect, text):
                painter.setFont(font_obj)
                outline_pen = QPen(rim_color, 3)
                painter.setPen(outline_pen)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            offset_rect = QRect(rect.x() + dx, rect.y() + dy, rect.width(), rect.height())
                            painter.drawText(offset_rect, Qt.AlignmentFlag.AlignCenter, text)
                painter.setPen(text_color)
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

            font = QFont("Arial", 15)
            draw_text_with_outline(font, QRect(x_offset, 15, size, 16), data.label)

            font = QFont("Arial", 16, QFont.Weight.Bold)
            draw_text_with_outline(font, QRect(x_offset, 38, size, 22), f"{int(data.utilization)}%")

            if data.reset_time:
                font = QFont("Arial", 15)
                display_time = f"in {data.reset_time}" if data.reset_time != "now" else "now"
                draw_text_with_outline(font, QRect(x_offset, 63, size, 18), f"↻ {display_time}")

    def draw_ball(self, painter: QPainter, x_offset: int, data: BallData, animation_phase: float = 0.0, render_mode: int = 2):
        """Draw a ball with glacier, glass-like lighting, and waving animation.

        render_mode:
            0 = No cache (draw everything fresh)
            1 = Background cache (shadow + rim cached)
            2 = Full cache (background + light effect cached) - DEFAULT
        """
        size = self.get_ball_size()

        if render_mode == 0:
            # Mode 0: No caching - draw everything fresh
            self._draw_background(painter, x_offset, size, data.is_error)
            self._draw_dynamic_content(painter, x_offset, data, animation_phase, size)
            self._draw_light_effect(painter, x_offset, size)
            self._draw_text(painter, x_offset, data, size)

        elif render_mode == 1:
            # Mode 1: Background cache only
            bg_pixmap = self._ensure_background_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, bg_pixmap)

            self._draw_dynamic_content(painter, x_offset, data, animation_phase, size)
            self._draw_light_effect(painter, x_offset, size)
            self._draw_text(painter, x_offset, data, size)

        else:  # render_mode == 2 (default)
            # Mode 2: Full cache (background + light effect)
            bg_pixmap = self._ensure_background_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, bg_pixmap)

            self._draw_dynamic_content(painter, x_offset, data, animation_phase, size)

            light_pixmap = self._ensure_light_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, light_pixmap)

            self._draw_text(painter, x_offset, data, size)
