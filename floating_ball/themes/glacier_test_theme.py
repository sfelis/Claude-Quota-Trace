"""Glacier test theme - testing glass-like lighting effects with caching options."""
import math
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QPainterPath,
                         QLinearGradient, QRadialGradient, QPixmap)
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF
from .base_theme import BaseTheme, BallData


class GlacierTestTheme(BaseTheme):
    """Glacier test theme with glass-like lighting effects and caching options."""

    def __init__(self, color_theme_name: str = "fulfill"):
        """Initialize glacier test theme."""
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
        return 140  # Increased to fully accommodate outer ring and white rim without any clipping

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

    def _draw_clock_surface(self, painter, x_offset, size):
        """Draw dark clock surface ring around the ball with radial light rays."""
        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2

        # Draw translucent background for the entire area (so it doesn't blend with apps behind)
        bg_radius = size // 2 - 2
        painter.setBrush(QBrush(QColor(0, 0, 0, 100)))  # Semi-transparent black
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            center_x - bg_radius, center_y - bg_radius,
            bg_radius * 2, bg_radius * 2
        )

        # Ring dimensions - make it thicker (100% thicker as requested)
        # Leave 3 pixels margin for white rim
        outer_ring_radius = size // 2 - 6  # Leave space for white rim
        ring_width = 15  # Thick ring
        inner_ring_radius = outer_ring_radius - ring_width  # Create thick ring

        # Create ring clip path (donut shape)
        ring_path = QPainterPath()
        ring_path.addEllipse(QRectF(
            center_x - outer_ring_radius, center_y - outer_ring_radius,
            outer_ring_radius * 2, outer_ring_radius * 2
        ))
        ring_path.addEllipse(QRectF(
            center_x - inner_ring_radius, center_y - inner_ring_radius,
            inner_ring_radius * 2, inner_ring_radius * 2
        ))
        painter.setClipPath(ring_path)

        # Draw dark blue/black ring background
        dark_bg_gradient = QRadialGradient(QPointF(center_x, center_y), outer_ring_radius)
        dark_bg_gradient.setColorAt(0, QColor(20, 30, 50, 200))   # Dark blue (inner)
        dark_bg_gradient.setColorAt(0.7, QColor(10, 15, 30, 220))  # Darker
        dark_bg_gradient.setColorAt(1, QColor(5, 8, 15, 240))     # Almost black (outer)
        painter.setBrush(QBrush(dark_bg_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            center_x - outer_ring_radius, center_y - outer_ring_radius,
            outer_ring_radius * 2, outer_ring_radius * 2
        )

        # Draw radial light rays in the ring
        num_rays = 24
        for i in range(num_rays):
            angle = (i * 15 - 90) * math.pi / 180

            # Vary colors - mostly cyan/blue, some green and orange
            if i % 8 == 0:
                ray_color = QColor(0, 255, 200, 50)  # Cyan
            elif i % 8 == 3:
                ray_color = QColor(0, 200, 100, 40)  # Green
            elif i % 8 == 6:
                ray_color = QColor(255, 100, 50, 35)  # Orange
            else:
                ray_color = QColor(0, 180, 255, 45)  # Blue

            # Draw ray as a thin triangle extending to the ring
            ray_path = QPainterPath()
            ray_path.moveTo(center_x + inner_ring_radius * math.cos(angle),
                          center_y + inner_ring_radius * math.sin(angle))

            angle1 = angle - 0.015
            angle2 = angle + 0.015
            ray_path.lineTo(
                center_x + outer_ring_radius * math.cos(angle1),
                center_y + outer_ring_radius * math.sin(angle1)
            )
            ray_path.lineTo(
                center_x + outer_ring_radius * math.cos(angle2),
                center_y + outer_ring_radius * math.sin(angle2)
            )
            ray_path.closeSubpath()

            painter.setBrush(QBrush(ray_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(ray_path)

        painter.setClipping(False)

        # Draw translucent white outer rim extending beyond the clock ring
        white_rim_outer = outer_ring_radius + 4
        white_rim_inner = outer_ring_radius - 1

        # Create white rim path (donut shape)
        white_rim_path = QPainterPath()
        white_rim_path.addEllipse(QRectF(
            center_x - white_rim_outer, center_y - white_rim_outer,
            white_rim_outer * 2, white_rim_outer * 2
        ))
        white_rim_path.addEllipse(QRectF(
            center_x - white_rim_inner, center_y - white_rim_inner,
            white_rim_inner * 2, white_rim_inner * 2
        ))

        # Draw with gradient for depth
        white_gradient = QRadialGradient(QPointF(center_x, center_y), white_rim_outer)
        white_gradient.setColorAt(0, QColor(255, 255, 255, 0))
        white_gradient.setColorAt(0.85, QColor(255, 255, 255, 80))
        white_gradient.setColorAt(1, QColor(220, 230, 255, 120))

        painter.setBrush(QBrush(white_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(white_rim_path)

        # Draw subtle inner and outer borders for definition
        painter.setPen(QPen(QColor(50, 70, 100, 150), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            center_x - inner_ring_radius, center_y - inner_ring_radius,
            inner_ring_radius * 2, inner_ring_radius * 2
        )
        painter.setPen(QPen(QColor(180, 190, 200, 100), 1))
        painter.drawEllipse(
            center_x - outer_ring_radius, center_y - outer_ring_radius,
            outer_ring_radius * 2, outer_ring_radius * 2
        )

    def _draw_clock_dial(self, painter, x_offset, data, size):
        """Draw enhanced clock-style dial with numbers and decorative elements."""
        if data.is_error:
            return

        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2
        outer_ring_radius = size // 2 - 2
        ring_width = 15
        inner_ring_radius = outer_ring_radius - ring_width
        mid_ring_radius = (outer_ring_radius + inner_ring_radius) // 2

        # Draw all 60 minute marks (subtle)
        for i in range(60):
            angle = (i * 6 - 90) * math.pi / 180

            if i % 5 == 0:
                # Hour marks (skip these, will draw separately)
                continue
            else:
                # Minute marks - very subtle
                tick_length = 2
                tick_width = 0.8
                tick_color = QColor(120, 140, 160, 80)

                x_outer = center_x + (outer_ring_radius - 3) * math.cos(angle)
                y_outer = center_y + (outer_ring_radius - 3) * math.sin(angle)
                x_inner = center_x + (outer_ring_radius - 3 - tick_length) * math.cos(angle)
                y_inner = center_y + (outer_ring_radius - 3 - tick_length) * math.sin(angle)

                painter.setPen(QPen(tick_color, tick_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                painter.drawLine(int(x_inner), int(y_inner), int(x_outer), int(y_outer))

        # Draw hour tick marks (more prominent)
        for i in range(12):
            angle = (i * 30 - 90) * math.pi / 180

            # Major ticks at 12, 3, 6, 9 - extra prominent
            if i % 3 == 0:
                tick_length = 12
                tick_width = 3.0
                tick_color = QColor(220, 240, 255, 255)  # Very bright

                # Draw glow around major ticks
                for glow_width in [5, 3]:
                    glow_alpha = 40 if glow_width == 5 else 80
                    glow_color = QColor(180, 220, 255, glow_alpha)
                    painter.setPen(QPen(glow_color, glow_width + tick_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                    x_outer = center_x + (outer_ring_radius - 2) * math.cos(angle)
                    y_outer = center_y + (outer_ring_radius - 2) * math.sin(angle)
                    x_inner = center_x + (inner_ring_radius + 2) * math.cos(angle)
                    y_inner = center_y + (inner_ring_radius + 2) * math.sin(angle)
                    painter.drawLine(int(x_inner), int(y_inner), int(x_outer), int(y_outer))
            else:
                tick_length = 8
                tick_width = 2.0
                tick_color = QColor(180, 200, 230, 200)

            # Draw the tick
            x_outer = center_x + (outer_ring_radius - 2) * math.cos(angle)
            y_outer = center_y + (outer_ring_radius - 2) * math.sin(angle)
            x_inner = center_x + (inner_ring_radius + 2) * math.cos(angle)
            y_inner = center_y + (inner_ring_radius + 2) * math.sin(angle)

            painter.setPen(QPen(tick_color, tick_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(x_inner), int(y_inner), int(x_outer), int(y_outer))

        # Draw glowing time pointer extending to the outer ring
        pointer_angle = (data.time_percentage * 360 - 90) * math.pi / 180
        pointer_length = outer_ring_radius - 6  # Reach almost to the outer edge
        pointer_end_x = center_x + pointer_length * math.cos(pointer_angle)
        pointer_end_y = center_y + pointer_length * math.sin(pointer_angle)

        # Pointer color based on time (cyan glow like the reference)
        if data.time_percentage < 0.5:
            pointer_color = QColor(0, 220, 255)  # Cyan (early)
        elif data.time_percentage < 0.85:
            pointer_color = QColor(0, 255, 150)  # Green-cyan (mid)
        else:
            pointer_color = QColor(255, 100, 80)  # Orange-red (late)

        # Draw outer glow layers (blur effect)
        for width in [9, 7, 5, 3]:
            glow_alpha = 20 if width == 9 else 35 if width == 7 else 50 if width == 5 else 80
            glow_color = QColor(pointer_color.red(), pointer_color.green(), pointer_color.blue(), glow_alpha)
            painter.setPen(QPen(glow_color, width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(center_x), int(center_y), int(pointer_end_x), int(pointer_end_y))

        # Draw bright core of pointer
        painter.setPen(QPen(pointer_color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(center_x), int(center_y), int(pointer_end_x), int(pointer_end_y))

        # Draw glowing center dot
        for radius in [6, 4, 2]:
            glow_alpha = 60 if radius == 6 else 120 if radius == 4 else 255
            glow_color = QColor(pointer_color.red(), pointer_color.green(), pointer_color.blue(), glow_alpha)
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(center_x - radius), int(center_y - radius), radius * 2, radius * 2)

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

    def draw_ball(self, painter: QPainter, x_offset: int, data: BallData,
                  animation_phase: float = 0.0, render_mode: int = 0):
        """Draw a ball with modern clock face styling.

        render_mode:
            0 = No cache (draw everything fresh)
            1 = Background cache (shadow + rim cached)
            2 = Full cache (background + light effect cached)
        """
        size = self.get_ball_size()

        if render_mode == 0:
            # Mode 0: No caching - draw everything fresh
            self._draw_background(painter, x_offset, size, data.is_error)

            # Draw clock surface with radial rays
            if not data.is_error:
                self._draw_clock_surface(painter, x_offset, size)

            # Draw dynamic content (water/glacier) with transparency
            self._draw_dynamic_content(painter, x_offset, data, animation_phase, size)
            self._draw_light_effect(painter, x_offset, size)
            self._draw_clock_dial(painter, x_offset, data, size)
            self._draw_text(painter, x_offset, data, size)

        elif render_mode == 1:
            # Mode 1: Background cache only
            bg_pixmap = self._ensure_background_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, bg_pixmap)

            if not data.is_error:
                self._draw_clock_surface(painter, x_offset, size)

            self._draw_dynamic_content(painter, x_offset, data, animation_phase, size)
            self._draw_light_effect(painter, x_offset, size)
            self._draw_clock_dial(painter, x_offset, data, size)
            self._draw_text(painter, x_offset, data, size)

        elif render_mode == 2:
            # Mode 2: Full cache (background + light effect)
            bg_pixmap = self._ensure_background_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, bg_pixmap)

            if not data.is_error:
                self._draw_clock_surface(painter, x_offset, size)

            self._draw_dynamic_content(painter, x_offset, data, animation_phase, size)

            light_pixmap = self._ensure_light_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, light_pixmap)

            self._draw_clock_dial(painter, x_offset, data, size)
            self._draw_text(painter, x_offset, data, size)
