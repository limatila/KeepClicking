"""Pytest configuration and fixtures for KeepClicking tests."""

import pytest
import os
import sys

# Set up virtual display BEFORE any imports that need X11
try:
    from pyvirtualdisplay import Display

    # Check if we're in a headless environment (no DISPLAY set or invalid)
    if not os.environ.get("DISPLAY"):
        _display = Display(visible=False, size=(1280, 1024))
        _display.start()

        # Register cleanup at exit
        def cleanup_display():
            try:
                _display.stop()
            except:
                pass

        import atexit
        atexit.register(cleanup_display)
except ImportError:
    # pyvirtualdisplay not installed
    pass
except Exception as e:
    # If virtual display setup fails, warn but continue
    print(f"Warning: Could not set up virtual display: {e}", file=sys.stderr)
