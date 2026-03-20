"""Space test theme - modern clock dial with radial light rays and time visualization."""
import math
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QPainterPath,
                         QLinearGradient, QRadialGradient, QPixmap)
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF
from .base_theme import BaseTheme, BallData


class SpaceTestTheme(BaseTheme):
    """Space theme with clock dial, radial light rays, and animated time pointer."""

    def __init__(self, color_theme_name: str = "fulfill"):
        """Initialize space test theme."""
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

    def _draw_clock_surface(self, painter, x_offset, size, data=None):
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

        # Draw 7-day arcs for 7-day ball
        if data and data.label == "7d":
            self._draw_7day_arcs(painter, center_x, center_y, outer_ring_radius, data.time_percentage)

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

    def _draw_7day_arcs(self, painter, center_x, center_y, outer_ring_radius, time_percentage):
        """Draw 7 arcs representing the 7 days, with premium visual effects."""
        # Arc radius (slightly inside the outer ring)
        arc_radius = outer_ring_radius - 3
        
        # Each day is 1/7 of the circle (360 / 7 ≈ 51.43 degrees)
        degrees_per_day = 360.0 / 7.0
        
        # Calculate which day we're in (0-6)
        current_day = int(time_percentage * 7)
        if current_day >= 7:
            current_day = 6  # Cap at day 6
            
        # Calculate the time within the current day (0.0 to 1.0)
        day_progress = (time_percentage * 7) % 1.0
        
        # Draw background track for all days (7 distinct shallow arcs)
        # This gives a "slotted" feeling as requested
        for day in range(7):
             # Calculate angles for each slot
            start_angle_deg = -90 + day * degrees_per_day
            span_angle_deg = degrees_per_day
            
            gap_deg = 5.0
            qt_start_angle = 90 - (day * degrees_per_day) - (gap_deg / 2)
            qt_span_angle = -(degrees_per_day - gap_deg)
            
            start_angle_qt = int(qt_start_angle * 16)
            span_angle_qt = int(qt_span_angle * 16)
            
            # Shallow arc style (dim, always there)
            # Using a visible blue-grey
            shallow_pen = QPen(QColor(60, 90, 120, 150), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(shallow_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(
                int(center_x - arc_radius), int(center_y - arc_radius),
                int(arc_radius * 2), int(arc_radius * 2),
                start_angle_qt, span_angle_qt
            )
        
        # Draw each of the 7 days (the "Deep" arcs covering the shallow ones)
        for day in range(7):
            # Start angle for this day (start from top, go clockwise)
            # -90 is top. 
            start_angle_deg = -90 + day * degrees_per_day
            span_angle_deg = degrees_per_day
            
            # Add visible gap between days for visual separation
            gap_deg = 5.0
            draw_start_deg = start_angle_deg + gap_deg / 2
            draw_span_deg = span_angle_deg - gap_deg
            
            # Qt's drawArc uses 1/16 degree units
            start_angle_qt = int(-draw_start_deg * 16) # Qt angles are counter-clockwise, so negate
            span_angle_qt = int(-draw_span_deg * 16)   # Negate for clockwise direction from top? 
            # Wait, standard math: 0 is right, 90 is bottom (y grows down).
            # Qt: 0 is 3 o'clock, positive is counter-clockwise.
            # We want: 0 progress at top (-90/270 deg). Clockwise.
            
            # Let's recalculate angles for Qt (CCW positive, 0 at 3 o'clock)
            # Top is 90 degrees. Clockwise means decreasing angle.
            # Day 0 starts at 90, goes to 90 - 51.4
            
            qt_start_angle = 90 - (day * degrees_per_day) - (gap_deg / 2)
            qt_span_angle = -(degrees_per_day - gap_deg)
            
            start_angle_qt = int(qt_start_angle * 16)
            span_angle_qt = int(qt_span_angle * 16)
            
            if day < current_day:
                # Past days - highlight with glow effect (same style as active)
                
                # GLOW EFFECT
                glow_color = QColor(0, 255, 255) # Cyan glow
                for glow_w, glow_a in [(8, 20), (6, 40)]:
                     glow_pen = QPen(glow_color, glow_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                     glow_color.setAlpha(glow_a)
                     glow_pen.setColor(glow_color)
                     painter.setPen(glow_pen)
                     painter.drawArc(
                        int(center_x - arc_radius), int(center_y - arc_radius),
                        int(arc_radius * 2), int(arc_radius * 2),
                        start_angle_qt, span_angle_qt
                    )

                # MAIN STROKE (Bright Cyan)
                main_pen = QPen(QColor(200, 255, 255), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                painter.setPen(main_pen)
                painter.drawArc(
                    int(center_x - arc_radius), int(center_y - arc_radius),
                    int(arc_radius * 2), int(arc_radius * 2),
                    start_angle_qt, span_angle_qt
                )
                
            elif day == current_day:
                # Current day - Needs special handling
                
                # 1. Draw the "remaining" part logic (empty track)
                # Actually we already drew the global track, so just drawing progress is enough?
                # Let's draw the remaining part slightly lighter than track to show it's "active day" but empty
                
                # 2. Draw the progress part with Glow and Gradient
                if day_progress > 0:
                    current_span_deg = (degrees_per_day - gap_deg) * day_progress
                    current_span_qt = int(-current_span_deg * 16)
                    
                    # GLOW EFFECT (Multiple transparent wide strokes)
                    glow_color = QColor(0, 255, 255) # Cyan glow
                    for glow_w, glow_a in [(8, 20), (6, 40)]:
                         glow_pen = QPen(glow_color, glow_w, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                         glow_color.setAlpha(glow_a)
                         glow_pen.setColor(glow_color)
                         painter.setPen(glow_pen)
                         painter.drawArc(
                            int(center_x - arc_radius), int(center_y - arc_radius),
                            int(arc_radius * 2), int(arc_radius * 2),
                            start_angle_qt, current_span_qt
                        )

                    # MAIN STROKE (Gradient)
                    # For arc gradient, ConicalGradient is best centered at arc center
                    # But for simple short arcs, a solid bright color is often cleaner.
                    # Let's use a very bright cyan to white.
                    main_pen = QPen(QColor(200, 255, 255), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                    painter.setPen(main_pen)
                    painter.drawArc(
                        int(center_x - arc_radius), int(center_y - arc_radius),
                        int(arc_radius * 2), int(arc_radius * 2),
                        start_angle_qt, current_span_qt
                    )
                    
                    # TIP HIGHLIGHT (Glowing dot at the end)
                    # Calculate position of the tip
                    tip_angle_deg = 90 - (day * degrees_per_day) - (gap_deg/2) - ((degrees_per_day - gap_deg) * day_progress)
                    tip_angle_rad = math.radians(tip_angle_deg) # Math uses radians, standard circle (0 is right, CCW positive)
                    # wait, qpainter 0 is right, CCW positive. 
                    # 90 is top.
                    
                    tip_x = center_x + arc_radius * math.cos(math.radians(-tip_angle_deg)) # Manual flipped y? No
                    # Standard math: x = r*cos(a), y = -r*sin(a) (screen coords y is down)
                    # Angle is in standard unit circle degrees (CCW from right = 0)
                    
                    # My qt_start_angle was: 90 (top) - angle. Correct.
                    # So tip_angle_deg is correct in standard math reference if we handle y correctly.
                    # On screen y grows down: y = center_y - r * sin(angle)
                    
                    tip_x = center_x + arc_radius * math.cos(tip_angle_rad)
                    tip_y = center_y - arc_radius * math.sin(tip_angle_rad)
                    
                    # Draw glow dot
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(QColor(255, 255, 255, 200))
                    painter.drawEllipse(QPointF(tip_x, tip_y), 2.5, 2.5)
                    
                    # Outer glow for dot
                    painter.setBrush(QColor(0, 255, 255, 100))
                    painter.drawEllipse(QPointF(tip_x, tip_y), 5, 5)

            else:
                # Future days
                # Draw just a faint dot pattern or very dim line?
                # Let's keep the track we drew earlier, maybe add a very faint highlight
                pass

        # Separators are now implicitly handled by the gaps we added to angles


    def _draw_space_background(self, painter, x_offset, size):
        """Draw astronomical space background inside the ball."""
        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2

        # Create circular clip path for the ball interior
        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(x_offset + 5, 5, size - 10, size - 10))
        painter.setClipPath(clip_path)

        # Draw deep space with nebula-like gradient
        space_gradient = QRadialGradient(QPointF(center_x, center_y), ball_radius)
        space_gradient.setColorAt(0, QColor(30, 20, 50))      # Purple center (nebula)
        space_gradient.setColorAt(0.3, QColor(15, 10, 35))    # Dark purple
        space_gradient.setColorAt(0.6, QColor(8, 12, 25))     # Blue-black
        space_gradient.setColorAt(1, QColor(2, 5, 12))        # Deep space black
        painter.setBrush(QBrush(space_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

        # Add nebula clouds (semi-transparent colored regions)
        import random
        random.seed(42)

        # Purple nebula cloud
        nebula_gradient = QRadialGradient(
            QPointF(center_x - ball_radius * 0.3, center_y - ball_radius * 0.2),
            ball_radius * 0.4
        )
        nebula_gradient.setColorAt(0, QColor(100, 50, 150, 40))
        nebula_gradient.setColorAt(0.5, QColor(80, 40, 120, 20))
        nebula_gradient.setColorAt(1, QColor(60, 30, 90, 0))
        painter.setBrush(QBrush(nebula_gradient))
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

        # Blue nebula cloud
        nebula_gradient2 = QRadialGradient(
            QPointF(center_x + ball_radius * 0.3, center_y + ball_radius * 0.3),
            ball_radius * 0.35
        )
        nebula_gradient2.setColorAt(0, QColor(50, 100, 180, 35))
        nebula_gradient2.setColorAt(0.5, QColor(40, 80, 140, 15))
        nebula_gradient2.setColorAt(1, QColor(30, 60, 100, 0))
        painter.setBrush(QBrush(nebula_gradient2))
        painter.drawEllipse(x_offset + 5, 5, size - 10, size - 10)

        # Add varied stars
        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(25):
            star_x = x_offset + 10 + random.randint(0, size - 25)
            star_y = 10 + random.randint(0, size - 25)
            star_size = random.choice([1, 1, 1, 2, 2, 3])
            star_alpha = random.randint(60, 180)

            # Vary star colors
            if random.random() < 0.7:
                star_color = QColor(200, 220, 255, star_alpha)  # Blue-white
            elif random.random() < 0.5:
                star_color = QColor(255, 230, 200, star_alpha)  # Orange
            else:
                star_color = QColor(255, 200, 220, star_alpha)  # Pink

            painter.setBrush(QBrush(star_color))
            painter.drawEllipse(star_x, star_y, star_size, star_size)

            # Add glow to larger stars
            if star_size > 1:
                glow_gradient = QRadialGradient(QPointF(star_x + star_size//2, star_y + star_size//2), star_size * 2)
                glow_gradient.setColorAt(0, QColor(star_color.red(), star_color.green(), star_color.blue(), 30))
                glow_gradient.setColorAt(1, QColor(star_color.red(), star_color.green(), star_color.blue(), 0))
                painter.setBrush(QBrush(glow_gradient))
                painter.drawEllipse(star_x - star_size, star_y - star_size, star_size * 4, star_size * 4)

        painter.setClipping(False)

    def _draw_clock_dial(self, painter, x_offset, data, size, animation_phase=0.0):
        """Draw enhanced clock-style dial with numbers and decorative elements."""
        if data.is_error:
            return

        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2
        outer_ring_radius = size // 2 - 6  # Match _draw_clock_surface
        ring_width = 15
        inner_ring_radius = outer_ring_radius - ring_width
        mid_ring_radius = (outer_ring_radius + inner_ring_radius) // 2

        # ===== ANIMATED DECORATIVE RING (rotating clockwise) =====
        pointer_length = outer_ring_radius - 10  # Same as pointers
        decoration_radius = pointer_length

        # Draw base ring (dim)
        painter.setPen(QPen(QColor(60, 100, 160, 60), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            int(center_x - decoration_radius), int(center_y - decoration_radius),
            int(decoration_radius * 2), int(decoration_radius * 2)
        )

        # Draw rotating bright segments (clockwise animation)
        num_segments = 8
        segment_length = 30  # degrees
        phase_offset = animation_phase * 0.7  # Rotation based on animation (30% slower)

        for i in range(num_segments):
            # Calculate segment start angle (clockwise from top)
            base_angle = (i * (360 / num_segments) + phase_offset) % 360
            start_angle = (90 - base_angle - segment_length / 2) * 16  # Qt uses 1/16 degree

            # Vary brightness for trailing effect
            brightness = 255 - (i * 20)
            alpha = max(80, 180 - (i * 15))

            painter.setPen(QPen(QColor(80, 160, 255, alpha), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawArc(
                int(center_x - decoration_radius), int(center_y - decoration_radius),
                int(decoration_radius * 2), int(decoration_radius * 2),
                int(start_angle), int(segment_length * 16)
            )

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

        # Make both pointers longer (extend closer to outer ring)
        pointer_length = outer_ring_radius - 10

        # ========== QUOTA/USAGE DIAL (BLUE) ==========
        # Draw usage pointer with pointed tip
        usage_angle = (data.usage_percentage * 360 - 90) * math.pi / 180
        usage_end_x = center_x + pointer_length * math.cos(usage_angle)
        usage_end_y = center_y + pointer_length * math.sin(usage_angle)

        # Quota dial - fixed blue color
        usage_color = QColor(80, 160, 255)  # Blue

        # Usage pointer with glow
        for width in [7, 5, 3]:
            glow_alpha = 25 if width == 7 else 45 if width == 5 else 70
            painter.setPen(QPen(QColor(usage_color.red(), usage_color.green(), usage_color.blue(), glow_alpha),
                               width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(center_x), int(center_y), int(usage_end_x), int(usage_end_y))

        painter.setPen(QPen(usage_color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(center_x), int(center_y), int(usage_end_x), int(usage_end_y))

        # Draw pointed tip (arrow head) for quota dial
        arrow_size = 8
        # Calculate perpendicular angle for arrow wings
        perp_angle1 = usage_angle + 2.8  # ~160 degrees back
        perp_angle2 = usage_angle - 2.8
        wing1_x = usage_end_x + arrow_size * math.cos(perp_angle1)
        wing1_y = usage_end_y + arrow_size * math.sin(perp_angle1)
        wing2_x = usage_end_x + arrow_size * math.cos(perp_angle2)
        wing2_y = usage_end_y + arrow_size * math.sin(perp_angle2)

        # Draw filled arrow head
        arrow_path = QPainterPath()
        arrow_path.moveTo(usage_end_x, usage_end_y)
        arrow_path.lineTo(wing1_x, wing1_y)
        arrow_path.lineTo(wing2_x, wing2_y)
        arrow_path.closeSubpath()

        painter.setBrush(QBrush(usage_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(arrow_path)

        # ========== TIME DIAL (GREEN with clock-like tick decoration) ==========
        # Time dial - fixed green color
        time_color = QColor(0, 255, 120)  # Green

        # Draw small tick marks along the time pointer's path (clock decoration)
        time_arc_radius = pointer_length - 8
        num_time_ticks = 12
        for i in range(num_time_ticks + 1):
            tick_progress = i / num_time_ticks
            if tick_progress > data.time_percentage:
                break
            tick_angle = (tick_progress * 360 - 90) * math.pi / 180

            # Small tick marks along the arc
            tick_inner = time_arc_radius - 3
            tick_outer = time_arc_radius + 3
            x1 = center_x + tick_inner * math.cos(tick_angle)
            y1 = center_y + tick_inner * math.sin(tick_angle)
            x2 = center_x + tick_outer * math.cos(tick_angle)
            y2 = center_y + tick_outer * math.sin(tick_angle)

            painter.setPen(QPen(QColor(time_color.red(), time_color.green(), time_color.blue(), 150), 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Draw time pointer with pointed tip
        time_angle = (data.time_percentage * 360 - 90) * math.pi / 180
        time_end_x = center_x + pointer_length * math.cos(time_angle)
        time_end_y = center_y + pointer_length * math.sin(time_angle)

        # Time pointer with glow
        for width in [7, 5, 3]:
            glow_alpha = 25 if width == 7 else 45 if width == 5 else 70
            painter.setPen(QPen(QColor(time_color.red(), time_color.green(), time_color.blue(), glow_alpha),
                               width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(center_x), int(center_y), int(time_end_x), int(time_end_y))

        painter.setPen(QPen(time_color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(int(center_x), int(center_y), int(time_end_x), int(time_end_y))

        # Draw pointed tip (arrow head) for time dial
        arrow_size = 8
        # Calculate perpendicular angle for arrow wings
        perp_angle1 = time_angle + 2.8  # ~160 degrees back
        perp_angle2 = time_angle - 2.8
        wing1_x = time_end_x + arrow_size * math.cos(perp_angle1)
        wing1_y = time_end_y + arrow_size * math.sin(perp_angle1)
        wing2_x = time_end_x + arrow_size * math.cos(perp_angle2)
        wing2_y = time_end_y + arrow_size * math.sin(perp_angle2)

        # Draw filled arrow head
        arrow_path = QPainterPath()
        arrow_path.moveTo(time_end_x, time_end_y)
        arrow_path.lineTo(wing1_x, wing1_y)
        arrow_path.lineTo(wing2_x, wing2_y)
        arrow_path.closeSubpath()

        painter.setBrush(QBrush(time_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(arrow_path)

        # Draw glowing center dot
        for radius in [5, 3, 2]:
            glow_alpha = 60 if radius == 5 else 120 if radius == 3 else 255
            glow_color = QColor(255, 255, 255, glow_alpha)
            painter.setBrush(QBrush(glow_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(center_x - radius), int(center_y - radius), radius * 2, radius * 2)

    def _draw_text(self, painter, x_offset, data, size):
        """Draw text with labels attached to their respective dials."""
        center_x = x_offset + size // 2
        center_y = size // 2
        ball_radius = (size - 10) // 2
        outer_ring_radius = size // 2 - 6
        inner_ring_radius = outer_ring_radius - 15
        pointer_length = inner_ring_radius - 5

        if data.is_error and x_offset == 0:
            painter.setPen(QColor(147, 112, 219))
            font = QFont("Arial", 24)
            painter.setFont(font)
            error_icon = "👤" if data.label == "login" else "⚠"
            painter.drawText(QRect(x_offset, 0, size, size), Qt.AlignmentFlag.AlignCenter, error_icon)
        elif not data.is_error:
            # Helper to draw text with dark outline for visibility
            def draw_outlined_text(font_obj, x, y, text, color, outline_color=QColor(0, 0, 0, 200)):
                painter.setFont(font_obj)
                # Draw outline
                painter.setPen(outline_color)
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:
                            painter.drawText(int(x + dx), int(y + dy), text)
                # Draw main text
                painter.setPen(color)
                painter.drawText(int(x), int(y), text)

            # Draw label (5h/7d) in center
            font = QFont("Arial", 11, QFont.Weight.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()
            label_width = fm.horizontalAdvance(data.label)
            draw_outlined_text(font, center_x - label_width // 2, center_y + 4,
                             data.label, QColor(180, 180, 180, 220))

            # ===== QUOTA INFO (near quota dial pointer) =====
            # Quota dial - fixed blue color
            quota_color = QColor(80, 160, 255)  # Blue

            # Position quota text near the quota pointer tip
            usage_angle = (data.usage_percentage * 360 - 90) * math.pi / 180
            text_radius = pointer_length * 0.55  # Position along pointer
            quota_x = center_x + text_radius * math.cos(usage_angle)
            quota_y = center_y + text_radius * math.sin(usage_angle)

            font = QFont("Arial", 12, QFont.Weight.Bold)
            painter.setFont(font)
            fm = painter.fontMetrics()
            pct_text = f"{int(data.utilization)}%"
            pct_width = fm.horizontalAdvance(pct_text)
            pct_height = fm.height()
            draw_outlined_text(font, quota_x - pct_width // 2, quota_y + pct_height // 4,
                             pct_text, quota_color)

            # ===== TIME INFO (near time dial pointer) =====
            if data.reset_time:
                # Time dial - fixed green color
                time_color = QColor(0, 255, 120)  # Green

                # Position time text near the time pointer tip
                time_angle = (data.time_percentage * 360 - 90) * math.pi / 180
                text_radius = pointer_length * 0.55
                time_x = center_x + text_radius * math.cos(time_angle)
                time_y = center_y + text_radius * math.sin(time_angle)

                font = QFont("Arial", 10)
                painter.setFont(font)
                fm = painter.fontMetrics()
                display_time = f"↻{data.reset_time}" if data.reset_time != "now" else "↻now"
                time_width = fm.horizontalAdvance(display_time)
                time_height = fm.height()
                draw_outlined_text(font, time_x - time_width // 2, time_y + time_height // 4,
                                 display_time, time_color)

    def draw_ball(self, painter: QPainter, x_offset: int, data: BallData,
                  animation_phase: float = 0.0, render_mode: int = 0):
        """Draw a ball with space theme - dual dials for time and usage.

        render_mode:
            0 = No cache (draw everything fresh)
            1 = Background cache (shadow + rim cached)
            2 = Full cache (background + light effect cached)
        """
        size = self.get_ball_size()

        if render_mode == 0:
            # Mode 0: No caching - draw everything fresh
            self._draw_background(painter, x_offset, size, data.is_error)

            # Draw space background inside the ball (moved before clock surface)
            self._draw_space_background(painter, x_offset, size)
            
            # Draw clock surface with radial rays (now on top of space bg)
            if not data.is_error:
                self._draw_clock_surface(painter, x_offset, size, data)

            self._draw_light_effect(painter, x_offset, size)
            self._draw_clock_dial(painter, x_offset, data, size, animation_phase)
            self._draw_text(painter, x_offset, data, size)

        elif render_mode == 1:
            # Mode 1: Background cache only
            bg_pixmap = self._ensure_background_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, bg_pixmap)

            self._draw_space_background(painter, x_offset, size)

            if not data.is_error:
                self._draw_clock_surface(painter, x_offset, size, data)

            self._draw_light_effect(painter, x_offset, size)
            self._draw_clock_dial(painter, x_offset, data, size, animation_phase)
            self._draw_text(painter, x_offset, data, size)

        elif render_mode == 2:
            # Mode 2: Full cache (background + light effect)
            bg_pixmap = self._ensure_background_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, bg_pixmap)

            self._draw_space_background(painter, x_offset, size)

            light_pixmap = self._ensure_light_cache(size, x_offset)
            painter.drawPixmap(x_offset, 0, light_pixmap)

            if not data.is_error:
                self._draw_clock_surface(painter, x_offset, size, data)

            self._draw_clock_dial(painter, x_offset, data, size, animation_phase)
            self._draw_text(painter, x_offset, data, size)
