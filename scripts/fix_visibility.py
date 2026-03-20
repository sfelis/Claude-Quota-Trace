#!/usr/bin/env python3
"""
Fix visibility issues by resetting window position and theme settings.
"""
from PyQt6.QtCore import QSettings, QCoreApplication

def fix_settings():
    # We need a QCoreApplication to access QSettings cleanly if needed, 
    # but QSettings can often work without one on some platforms. 
    # To be safe, we verify values.
    
    settings = QSettings("FloatingBall", "ClaudeUsage")
    
    print(f"Current theme: {settings.value('theme')}")
    print(f"Current position: {settings.value('window_x')}, {settings.value('window_y')}")
    
    # Force theme to space
    print("Setting theme to 'space'...")
    settings.setValue("theme", "space")
    
    # Force position to top-right safe area
    print("Resetting position to (100, 100)...")
    settings.setValue("window_x", 100)
    settings.setValue("window_y", 100)
    
    # Check screen bounds (optional, but good for debug)
    # We can't access QScreen without QApplication, skipping that.
    
    settings.sync()
    print("Settings updated.")
    
    print(f"New theme: {settings.value('theme')}")
    print(f"New position: {settings.value('window_x')}, {settings.value('window_y')}")

if __name__ == "__main__":
    fix_settings()
