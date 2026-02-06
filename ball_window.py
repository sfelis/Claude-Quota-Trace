"""Floating ball window that displays Claude usage."""
from PyQt6.QtWidgets import QWidget, QMenu, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer, QSettings, QRect, QElapsedTimer
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QBrush
from datetime import datetime, timedelta
import time

from auth_service import AuthService
from api_service import APIService, APIError
from settings_dialog import SettingsDialog
from themes import get_theme
from themes.base_theme import BallData


class BallWindow(QWidget):
    """Floating ball widget that displays usage information."""

    def __init__(self, theme_name: str = None):
        """Initialize the ball window."""
        super().__init__()

        # Services and settings (need to initialize early)
        self.auth_service = AuthService()
        self.api_service = APIService(self.auth_service)
        self.settings = QSettings("FloatingBall", "ClaudeUsage")

        # Load theme from settings if not specified
        if theme_name is None:
            theme_name = self.settings.value("theme", "space", type=str)

        # Load color theme from settings
        color_theme_name = self.settings.value("color_theme", "fulfill", type=str)

        self.theme = get_theme(theme_name, color_theme_name)
        width, height = self.theme.get_window_size(num_balls=2)

        # Window properties
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.WindowDoesNotAcceptFocus |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setFixedSize(width, height)
        self.setMouseTracking(True)

        # Make window translucent
        self.setWindowOpacity(0.85)

        # State variables
        self.usage_percentage = 0.0  # 5-hour utilization
        self.usage_percentage_7day = 0.0
        self.utilization_5h = 0
        self.utilization_7d = 0
        self.resets_in = ""
        self.resets_in_7day = ""
        self.time_percentage_5h = 0.0  # Time elapsed in 5h period
        self.time_percentage_7day = 0.0  # Time elapsed in 7d period
        self.last_updated = None
        self.is_loading = False
        self.error_message = None
        self.drag_position = None
        self.needs_login = False
        self.animation_phase = 0.0  # For animated themes

        # Performance measurement
        self.perf_mode = False
        self.frame_times = []
        self.perf_timer = QElapsedTimer()

        # Render mode: 0 = no cache, 1 = background cache, 2 = full cache
        self.render_mode = 2

        # Dev mode UI
        self.dev_mode = False
        self.perf_stats = {"avg": 0, "min": 0, "max": 0, "fps": 0}
        self.frame_history = []  # For mini graph

        # Load saved position
        self.load_position()

        # Create context menu
        self.context_menu = self.create_context_menu()

        # Set up periodic updates
        self.setup_timer()

        # Set up animation timer only if theme is animated
        self.animation_timer = None
        if self.theme.is_animated():
            self.setup_animation_timer()

        # Ensure always on top
        self.raise_()
        self.activateWindow()

        # Check if login needed on startup
        self.check_initial_login()

    def check_initial_login(self):
        """Check if login is needed on startup."""
        if not self.auth_service.has_cookies():
            self.needs_login = True
            self.error_message = "Login required"
            QTimer.singleShot(500, self.prompt_login)
        else:
            self.refresh_data()

    def prompt_login(self):
        """Prompt user to login."""
        reply = QMessageBox.question(
            self,
            "Login Required",
            "Please login to Claude to view your usage.\n\nWould you like to login now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.show_settings()

    def load_position(self):
        """Load saved window position."""
        x = self.settings.value("window_x", type=int)
        y = self.settings.value("window_y", type=int)

        if x is not None and y is not None:
            self.move(x, y)
        else:
            screen = QApplication.primaryScreen().geometry()
            self.move(screen.width() - 100, 20)

    def save_position(self):
        """Save current window position."""
        self.settings.setValue("window_x", self.x())
        self.settings.setValue("window_y", self.y())

    def setup_timer(self):
        """Set up the periodic update timer."""
        refresh_minutes = self.settings.value("refresh_interval", 5, type=int)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(refresh_minutes * 60 * 1000)

    def setup_animation_timer(self):
        """Set up animation timer for smooth visual effects."""
        if self.animation_timer is None:
            self.animation_timer = QTimer(self)
            self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # Update every 50ms (20 FPS)

    def stop_animation_timer(self):
        """Stop animation timer to save resources."""
        if self.animation_timer is not None:
            self.animation_timer.stop()

    def update_animation(self):
        """Update animation phase and redraw."""
        self.animation_phase += 2.0  # Increment phase (2.0 = ~9 second cycle)
        if self.animation_phase > 360:
            self.animation_phase = 0
        self.update()  # Trigger redraw

    def refresh_data(self):
        """Refresh usage data from API."""
        if self.is_loading:
            return

        if not self.auth_service.has_cookies():
            self.error_message = "Not logged in"
            self.needs_login = True
            self.update()
            return

        self.is_loading = True
        self.error_message = None

        try:
            data = self.api_service.fetch_usage()

            self.usage_percentage = data.get("usage_percentage", 0.0)
            self.usage_percentage_7day = data.get("usage_percentage_7day", 0.0)
            self.utilization_5h = data.get("utilization_5h", 0)
            self.utilization_7d = data.get("utilization_7d", 0)
            self.resets_in = data.get("resets_in", "")
            self.resets_in_7day = data.get("resets_in_7day", "")
            self.time_percentage_5h = data.get("time_percentage_5h", 0.0)
            self.time_percentage_7day = data.get("time_percentage_7day", 0.0)
            self.last_updated = data.get("last_updated")
            self.needs_login = False

        except APIError as e:
            self.error_message = e.message
            print(f"API error: {e.message}")

            if e.error_type in ("session_expired", "forbidden", "not_authenticated"):
                self.needs_login = True
                QTimer.singleShot(100, self.prompt_relogin)

        except Exception as e:
            self.error_message = str(e)
            print(f"Error fetching usage: {e}")

        finally:
            self.is_loading = False
            self.update()

    def prompt_relogin(self):
        """Prompt user to re-login when session expires."""
        reply = QMessageBox.warning(
            self,
            "Session Expired",
            "Your Claude session has expired.\n\nWould you like to login again?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.show_settings()

    def create_context_menu(self):
        """Create the context menu."""
        menu = QMenu(self)

        refresh_action = menu.addAction("Refresh Now")
        refresh_action.triggered.connect(self.refresh_data)

        settings_action = menu.addAction("Settings...")
        settings_action.triggered.connect(self.show_settings)

        menu.addSeparator()

        # Dev menu
        dev_menu = menu.addMenu("Dev")

        self.dev_mode_action = dev_menu.addAction("Dev Mode (Show Stats)")
        self.dev_mode_action.setCheckable(True)
        self.dev_mode_action.setChecked(False)
        self.dev_mode_action.triggered.connect(self.toggle_dev_mode)

        dev_menu.addSeparator()

        # Render mode submenu
        render_menu = dev_menu.addMenu("Render Mode")
        self.render_mode_actions = []
        for i, name in enumerate(["No Cache", "Background Cache", "Full Cache"]):
            action = render_menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(i == 2)
            action.setData(i)
            action.triggered.connect(lambda checked, mode=i: self.set_render_mode(mode))
            self.render_mode_actions.append(action)

        menu.addSeparator()

        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)

        return menu

    def toggle_dev_mode(self):
        """Toggle dev mode with visual performance overlay."""
        self.dev_mode = self.dev_mode_action.isChecked()
        self.perf_mode = self.dev_mode  # Enable perf measurement when dev mode is on
        self.frame_times.clear()
        self.frame_history.clear()
        self.perf_stats = {"avg": 0, "min": 0, "max": 0, "fps": 0}
        self.update()

    def set_render_mode(self, mode):
        """Set the render mode for caching comparison."""
        self.render_mode = mode
        # Update checkmarks
        for i, action in enumerate(self.render_mode_actions):
            action.setChecked(i == mode)
        # Clear caches in theme if it supports caching
        if hasattr(self.theme, 'clear_caches'):
            self.theme.clear_caches()
        self.frame_times.clear()
        self.frame_history.clear()
        self.perf_stats = {"avg": 0, "min": 0, "max": 0, "fps": 0}

    def show_settings(self):
        """Show the settings dialog."""
        # Get current theme settings before showing dialog
        current_theme = self.settings.value("theme", "space", type=str)
        current_color_theme = self.settings.value("color_theme", "fulfill", type=str)

        dialog = SettingsDialog(self.auth_service, self.api_service, self)
        if dialog.exec():
            # Check if theme or color theme changed
            new_theme = self.settings.value("theme", "space", type=str)
            new_color_theme = self.settings.value("color_theme", "fulfill", type=str)

            if new_theme != current_theme or new_color_theme != current_color_theme:
                # Theme changed, need to reload window
                self.reload_with_theme(new_theme, new_color_theme)
            else:
                self.setup_timer()
                self.refresh_data()

    def reload_with_theme(self, theme_name: str, color_theme_name: str):
        """Reload the window with a new theme and color theme."""
        # Save current position
        self.save_position()

        # Load new theme with color theme
        self.theme = get_theme(theme_name, color_theme_name)
        width, height = self.theme.get_window_size(num_balls=2)
        self.setFixedSize(width, height)

        # Start or stop animation timer based on theme
        if self.theme.is_animated():
            if self.animation_timer is None:
                self.animation_timer = QTimer(self)
                self.animation_timer.timeout.connect(self.update_animation)
            self.setup_animation_timer()
        else:
            self.stop_animation_timer()

        # Refresh display
        self.setup_timer()
        self.refresh_data()
        self.update()

    def paintEvent(self, event):
        """Paint the balls using the theme."""
        if self.perf_mode:
            self.perf_timer.start()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ball_size = self.theme.get_ball_size()
        spacing = self.theme.get_spacing()

        if self.error_message or self.needs_login:
            # Show error/login state on first ball
            error_label = "login" if self.needs_login else "error"
            data1 = BallData(self.usage_percentage, self.utilization_5h,
                           self.resets_in, error_label, True, self.time_percentage_5h)
            self.theme.draw_ball(painter, 0, data1, self.animation_phase, self.render_mode)

            # Draw grayed out second ball
            data2 = BallData(0, 0, "", "7d", True, 0.0)
            self.theme.draw_ball(painter, ball_size + spacing, data2, self.animation_phase, self.render_mode)
        else:
            # Draw 5-hour ball (left)
            data1 = BallData(self.usage_percentage, self.utilization_5h,
                           self.resets_in, "5h", False, self.time_percentage_5h)
            self.theme.draw_ball(painter, 0, data1, self.animation_phase, self.render_mode)

            # Draw 7-day ball (right)
            data2 = BallData(self.usage_percentage_7day, self.utilization_7d,
                           self.resets_in_7day, "7d", False, self.time_percentage_7day)
            self.theme.draw_ball(painter, ball_size + spacing, data2, self.animation_phase, self.render_mode)

        # Performance measurement - STOP timer BEFORE drawing dev overlay
        if self.perf_mode:
            elapsed = self.perf_timer.nsecsElapsed() / 1_000_000  # Convert to ms
            self.frame_times.append(elapsed)
            self.frame_history.append(elapsed)

            # Keep frame history limited for graph
            if len(self.frame_history) > 50:
                self.frame_history.pop(0)

            # Update stats every 20 frames
            if len(self.frame_times) >= 20:
                avg = sum(self.frame_times) / len(self.frame_times)
                min_t = min(self.frame_times)
                max_t = max(self.frame_times)
                fps = 1000 / avg if avg > 0 else 0
                self.perf_stats = {"avg": avg, "min": min_t, "max": max_t, "fps": fps}
                self.frame_times.clear()

        # Draw dev mode overlay AFTER measuring (not included in stats)
        if self.dev_mode:
            overlay_timer = QElapsedTimer()
            overlay_timer.start()
            self._draw_dev_overlay(painter)
            self.perf_stats["overlay"] = overlay_timer.nsecsElapsed() / 1_000_000

    def _draw_dev_overlay(self, painter):
        """Draw performance stats overlay."""
        # Semi-transparent background
        painter.setBrush(QBrush(QColor(0, 0, 0, 180)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, self.height() - 60, self.width(), 60)

        # Text settings
        painter.setPen(QColor(0, 255, 0))  # Green text
        font = QFont("Courier", 10)
        painter.setFont(font)

        # Render mode names
        mode_names = ["No Cache", "BG Cache", "Full Cache"]
        mode_name = mode_names[self.render_mode] if self.render_mode < len(mode_names) else "Unknown"

        # Stats text
        y_base = self.height() - 48
        painter.drawText(5, y_base, f"Mode: {mode_name}")
        painter.drawText(5, y_base + 11, f"Render: {self.perf_stats['avg']:.2f}ms")

        # Show overlay cost if available
        overlay_cost = self.perf_stats.get('overlay', 0)
        painter.setPen(QColor(150, 150, 150))  # Gray for overlay cost
        painter.drawText(5, y_base + 22, f"Overlay: {overlay_cost:.2f}ms")

        painter.setPen(QColor(0, 255, 0))  # Green again
        painter.drawText(5, y_base + 33, f"FPS: {self.perf_stats['fps']:.0f}")

        # Mini frame time graph
        if len(self.frame_history) > 1:
            graph_x = 100
            graph_y = self.height() - 55
            graph_w = self.width() - 110
            graph_h = 50

            # Draw graph background
            painter.setBrush(QBrush(QColor(30, 30, 30)))
            painter.drawRect(graph_x, graph_y, graph_w, graph_h)

            # Draw frame times as bars
            max_time = max(self.frame_history) if self.frame_history else 1
            max_time = max(max_time, 1)  # Avoid division by zero
            bar_width = graph_w / len(self.frame_history)

            for i, frame_time in enumerate(self.frame_history):
                bar_height = int((frame_time / max_time) * (graph_h - 4))
                bar_height = max(1, min(bar_height, graph_h - 4))

                # Color based on frame time (green = fast, red = slow)
                if frame_time < 0.5:
                    color = QColor(0, 255, 0)  # Green
                elif frame_time < 1.0:
                    color = QColor(255, 255, 0)  # Yellow
                else:
                    color = QColor(255, 0, 0)  # Red

                painter.setBrush(QBrush(color))
                painter.setPen(Qt.PenStyle.NoPen)
                x = graph_x + int(i * bar_width)
                painter.drawRect(x, graph_y + graph_h - bar_height - 2, max(1, int(bar_width) - 1), bar_height)

            # Draw max time label
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(graph_x + graph_w - 40, graph_y + 12, f"{max_time:.1f}ms")

    def _get_time_ago(self):
        """Get time since last update as string."""
        if not self.last_updated:
            return "never"

        delta = datetime.now() - self.last_updated
        if delta < timedelta(minutes=1):
            return "just now"
        elif delta < timedelta(hours=1):
            mins = int(delta.total_seconds() / 60)
            return f"{mins}m ago"
        else:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours}h ago"

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        elif event.button() == Qt.MouseButton.RightButton:
            self.context_menu.exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            self.save_position()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl("https://claude.ai/settings"))

    def enterEvent(self, event):
        if self.needs_login:
            tooltip = "Not logged in\n\nRight-click → Settings to login"
        elif self.error_message:
            tooltip = f"Error: {self.error_message}\n\nRight-click to open Settings"
        else:
            tooltip = f"""Claude Usage Monitor
─────────────────────
Left ball (5h):   {self.utilization_5h}%
  Resets in: {self.resets_in}

Right ball (7d):  {self.utilization_7d}%
  Resets in: {self.resets_in_7day}

Last updated: {self._get_time_ago()}"""

        self.setToolTip(tooltip.strip())

    def leaveEvent(self, event):
        pass
