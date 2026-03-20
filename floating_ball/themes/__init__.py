"""Theme system for floating ball."""
from .base_theme import BaseTheme
from .circle_theme import CircleTheme
from .water_theme import WaterTheme
from .glacier_theme import GlacierTheme
from .glacier_test_theme import GlacierTestTheme
from .space_test_theme import SpaceTestTheme
from .space_theme import SpaceTheme
from .opus_theme import OpusTheme

# Available themes
THEMES = {
    "circle": CircleTheme,
    "water": WaterTheme,
    "glacier": GlacierTheme,
    "glacier-test": GlacierTestTheme,
    "space-test": SpaceTestTheme,
    "space": SpaceTheme,
    "opus": OpusTheme,
}

def get_theme(name: str = "circle", color_theme_name: str = "fulfill") -> BaseTheme:
    """Get a theme by name with specified color theme."""
    theme_class = THEMES.get(name, CircleTheme)
    return theme_class(color_theme_name=color_theme_name)
