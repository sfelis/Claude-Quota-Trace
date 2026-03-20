#!/usr/bin/env python3
"""Floating ball app that displays Claude API usage."""
import sys
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from .ball_window import BallWindow


def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Floating Ball - Claude Usage Monitor')
    parser.add_argument('--dev', action='store_true', help='Enable development mode (shows test themes)')
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("FloatingBall")
    app.setOrganizationName("FloatingBall")
    app.setOrganizationDomain("floatingball.local")

    # Store dev mode flag in app for global access
    app.dev_mode = args.dev

    # Don't quit when last window closes (for settings dialog)
    app.setQuitOnLastWindowClosed(False)

    # Create and show the floating ball
    ball = BallWindow()
    ball.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
