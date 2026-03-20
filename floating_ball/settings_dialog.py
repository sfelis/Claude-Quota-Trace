"""Settings dialog for configuring the floating ball app."""
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton,
    QLabel, QComboBox, QDialogButtonBox, QVBoxLayout,
    QHBoxLayout, QGroupBox, QMessageBox
)
from PyQt6.QtCore import QSettings, Qt, QThread, pyqtSignal

from .auth_service import AuthService
from .api_service import APIService, APIError


class LoginThread(QThread):
    """Thread for handling login in background."""

    finished = pyqtSignal(bool, str)

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service

    def run(self):
        try:
            success = self.auth_service.login()
            if success:
                self.finished.emit(True, "Login successful")
            else:
                self.finished.emit(False, "Login cancelled or failed")
        except Exception as e:
            self.finished.emit(False, str(e))


class SettingsDialog(QDialog):
    """Dialog for configuring application settings."""

    def __init__(self, auth_service: AuthService, api_service: APIService, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.auth_service = auth_service
        self.api_service = api_service
        self.settings = QSettings("FloatingBall", "ClaudeUsage")
        self.login_thread = None

        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(450)

        self.setup_ui()
        self.load_settings()
        self.update_login_status()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout()

        # Account section
        account_group = QGroupBox("Account")
        account_layout = QVBoxLayout()

        # Login status
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Checking...")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label, 1)
        account_layout.addLayout(status_layout)

        # Login/Logout buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login with Claude")
        self.login_button.clicked.connect(self.do_login)
        button_layout.addWidget(self.login_button)

        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.do_logout)
        button_layout.addWidget(self.logout_button)

        account_layout.addLayout(button_layout)

        # Organization picker
        org_layout = QHBoxLayout()
        org_layout.addWidget(QLabel("Organization:"))
        self.org_combo = QComboBox()
        self.org_combo.currentIndexChanged.connect(self.on_org_changed)
        org_layout.addWidget(self.org_combo, 1)

        self.refresh_orgs_button = QPushButton("Refresh")
        self.refresh_orgs_button.clicked.connect(self.refresh_organizations)
        org_layout.addWidget(self.refresh_orgs_button)

        account_layout.addLayout(org_layout)

        account_group.setLayout(account_layout)
        layout.addWidget(account_group)

        # Settings section
        settings_group = QGroupBox("Settings")
        form = QFormLayout()

        # Theme selection
        self.theme_combo = QComboBox()

        # Get dev mode from app-level flag (--dev CLI) or BallWindow toggle
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        dev_mode = getattr(app, 'dev_mode', False)
        if not dev_mode and self.parent() is not None:
            dev_mode = getattr(self.parent(), 'dev_mode', False)

        # Build theme list based on dev mode
        themes = ["opus", "space", "glacier", "water", "circle"]
        if dev_mode:
            themes.extend(["glacier-test", "space-test"])

        self.theme_combo.addItems(themes)
        form.addRow("Theme:", self.theme_combo)

        # Color theme selection
        self.color_theme_combo = QComboBox()
        self.color_theme_combo.addItems(["fulfill", "alarm"])
        form.addRow("Color Theme:", self.color_theme_combo)

        # Refresh interval
        self.refresh_combo = QComboBox()
        self.refresh_combo.addItems(["1 minute", "5 minutes", "15 minutes", "30 minutes", "60 minutes"])
        form.addRow("Refresh Interval:", self.refresh_combo)

        settings_group.setLayout(form)
        layout.addWidget(settings_group)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def load_settings(self):
        """Load current settings."""
        # Load theme
        theme_name = self.settings.value("theme", "space", type=str)
        theme_index = self.theme_combo.findText(theme_name)
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)

        # Load color theme
        color_theme_name = self.settings.value("color_theme", "fulfill", type=str)
        color_theme_index = self.color_theme_combo.findText(color_theme_name)
        if color_theme_index >= 0:
            self.color_theme_combo.setCurrentIndex(color_theme_index)

        # Load refresh interval
        refresh_minutes = self.settings.value("refresh_interval", 5, type=int)
        interval_map = {1: 0, 5: 1, 15: 2, 30: 3, 60: 4}
        self.refresh_combo.setCurrentIndex(interval_map.get(refresh_minutes, 1))

    def update_login_status(self):
        """Update login status display."""
        if self.auth_service.has_cookies():
            # Test connection
            success, message = self.api_service.test_connection()
            if success:
                self.status_label.setText("Logged in")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.login_button.setEnabled(False)
                self.logout_button.setEnabled(True)
                self.org_combo.setEnabled(True)
                self.refresh_orgs_button.setEnabled(True)
                # Load organizations
                self.refresh_organizations()
            else:
                self.status_label.setText(f"Session expired: {message}")
                self.status_label.setStyleSheet("color: orange;")
                self.login_button.setEnabled(True)
                self.logout_button.setEnabled(True)
                self.org_combo.setEnabled(False)
                self.refresh_orgs_button.setEnabled(False)
        else:
            self.status_label.setText("Not logged in")
            self.status_label.setStyleSheet("color: gray;")
            self.login_button.setEnabled(True)
            self.logout_button.setEnabled(False)
            self.org_combo.setEnabled(False)
            self.refresh_orgs_button.setEnabled(False)

    def do_login(self):
        """Start login process."""
        self.login_button.setEnabled(False)
        self.status_label.setText("Opening browser for login...")
        self.status_label.setStyleSheet("color: blue;")

        # Run login in thread to not block UI
        self.login_thread = LoginThread(self.auth_service)
        self.login_thread.finished.connect(self.on_login_finished)
        self.login_thread.start()

    def on_login_finished(self, success: bool, message: str):
        """Handle login completion."""
        if success:
            self.status_label.setText("Login successful!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText(f"Login failed: {message}")
            self.status_label.setStyleSheet("color: red;")

        self.update_login_status()

    def do_logout(self):
        """Logout and clear credentials."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.auth_service.logout()
            self.org_combo.clear()
            self.update_login_status()

    def refresh_organizations(self):
        """Refresh the organizations list."""
        self.org_combo.clear()

        try:
            orgs = self.api_service.fetch_organizations()

            if not orgs:
                self.org_combo.addItem("No organizations found", None)
                return

            # Get currently selected org
            selected_org_id = self.auth_service.get_selected_org_id()

            for org in orgs:
                org_id = org.get("uuid") or org.get("id")
                org_name = org.get("name") or org.get("display_name") or org_id
                self.org_combo.addItem(org_name, org_id)

                # Select previously selected org
                if org_id == selected_org_id:
                    self.org_combo.setCurrentIndex(self.org_combo.count() - 1)

            # If no org was selected, select the first one
            if not selected_org_id and self.org_combo.count() > 0:
                self.org_combo.setCurrentIndex(0)
                self.on_org_changed(0)

        except APIError as e:
            self.org_combo.addItem(f"Error: {e.message}", None)
        except Exception as e:
            self.org_combo.addItem(f"Error: {str(e)}", None)

    def on_org_changed(self, index: int):
        """Handle organization selection change."""
        org_id = self.org_combo.currentData()
        if org_id:
            self.auth_service.set_selected_org_id(org_id)

    def save_settings(self):
        """Save settings and close dialog."""
        # Save theme
        theme_name = self.theme_combo.currentText()
        self.settings.setValue("theme", theme_name)

        # Save color theme
        color_theme_name = self.color_theme_combo.currentText()
        self.settings.setValue("color_theme", color_theme_name)

        # Save refresh interval
        interval_text = self.refresh_combo.currentText()
        interval_minutes = int(interval_text.split()[0])
        self.settings.setValue("refresh_interval", interval_minutes)

        # Save selected org (already saved in on_org_changed)

        self.accept()
