"""Floating Ball - Claude API Usage Monitor.

A macOS floating desktop widget that displays Claude API subscription usage in real-time.
"""

__version__ = "1.0.0"
__author__ = "Floating Ball Contributors"

from .ball_window import BallWindow
from .auth_service import AuthService
from .api_service import APIService

__all__ = ["BallWindow", "AuthService", "APIService", "__version__"]
