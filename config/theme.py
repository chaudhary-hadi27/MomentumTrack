"""
MomentumTrack - Professional Theme Configuration
Phase 1: Complete theme system with perfect contrast and modern design
"""

from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.core.window import Window


class ThemeConfig:
    """Professional theme configuration with Light/Dark modes"""

    # ==================== COLOR PALETTES ====================

    LIGHT_THEME = {
        # Backgrounds
        'bg_primary': (1, 1, 1, 1),  # Pure white
        'bg_secondary': (0.97, 0.97, 0.97, 1),  # Light gray
        'bg_card': (1, 1, 1, 1),  # White cards
        'bg_elevated': (0.98, 0.98, 0.98, 1),  # Slightly elevated

        # Text colors
        'text_primary': (0.1, 0.1, 0.1, 1),  # Almost black
        'text_secondary': (0.4, 0.4, 0.4, 1),  # Medium gray
        'text_disabled': (0.6, 0.6, 0.6, 1),  # Light gray
        'text_hint': (0.5, 0.5, 0.5, 1),  # Hint text

        # Accent colors
        'primary': (0.2, 0.6, 0.9, 1),  # Blue
        'primary_light': (0.5, 0.7, 1, 1),  # Light blue
        'primary_dark': (0.1, 0.4, 0.7, 1),  # Dark blue

        'secondary': (0.3, 0.7, 0.4, 1),  # Green
        'secondary_light': (0.5, 0.85, 0.6, 1),  # Light green
        'secondary_dark': (0.2, 0.5, 0.3, 1),  # Dark green

        'accent': (0.9, 0.6, 0.2, 1),  # Orange
        'accent_light': (1, 0.8, 0.5, 1),  # Light orange
        'accent_dark': (0.7, 0.4, 0.1, 1),  # Dark orange

        # Status colors
        'success': (0.2, 0.7, 0.3, 1),  # Green
        'warning': (0.9, 0.6, 0.2, 1),  # Orange
        'error': (0.9, 0.2, 0.2, 1),  # Red
        'info': (0.2, 0.6, 0.9, 1),  # Blue

        # Priority colors
        'priority_high': (0.9, 0.2, 0.2, 1),  # Red
        'priority_medium': (0.9, 0.6, 0.2, 1),  # Orange
        'priority_low': (0.2, 0.6, 0.9, 1),  # Blue

        # Category colors
        'category_work': (0.2, 0.6, 0.9, 1),  # Blue
        'category_personal': (0.6, 0.3, 0.8, 1),  # Purple
        'category_health': (0.3, 0.7, 0.4, 1),  # Green
        'category_learning': (0.9, 0.6, 0.2, 1),  # Orange

        # UI elements
        'divider': (0.9, 0.9, 0.9, 1),  # Light divider
        'border': (0.85, 0.85, 0.85, 1),  # Border color
        'shadow': (0, 0, 0, 0.1),  # Light shadow
        'overlay': (0, 0, 0, 0.3),  # Dark overlay
    }

    DARK_THEME = {
        # Backgrounds
        'bg_primary': (0.08, 0.08, 0.08, 1),  # Almost black
        'bg_secondary': (0.12, 0.12, 0.12, 1),  # Dark gray
        'bg_card': (0.15, 0.15, 0.15, 1),  # Card background
        'bg_elevated': (0.18, 0.18, 0.18, 1),  # Elevated surfaces

        # Text colors
        'text_primary': (0.95, 0.95, 0.95, 1),  # Almost white
        'text_secondary': (0.7, 0.7, 0.7, 1),  # Light gray
        'text_disabled': (0.5, 0.5, 0.5, 1),  # Medium gray
        'text_hint': (0.6, 0.6, 0.6, 1),  # Hint text

        # Accent colors (slightly muted for dark mode)
        'primary': (0.3, 0.7, 1, 1),  # Bright blue
        'primary_light': (0.5, 0.8, 1, 1),  # Lighter blue
        'primary_dark': (0.2, 0.5, 0.8, 1),  # Darker blue

        'secondary': (0.4, 0.8, 0.5, 1),  # Bright green
        'secondary_light': (0.6, 0.9, 0.7, 1),  # Light green
        'secondary_dark': (0.3, 0.6, 0.4, 1),  # Dark green

        'accent': (1, 0.7, 0.3, 1),  # Bright orange
        'accent_light': (1, 0.85, 0.6, 1),  # Light orange
        'accent_dark': (0.8, 0.5, 0.2, 1),  # Dark orange

        # Status colors (brighter for visibility)
        'success': (0.3, 0.8, 0.4, 1),  # Bright green
        'warning': (1, 0.7, 0.3, 1),  # Bright orange
        'error': (1, 0.3, 0.3, 1),  # Bright red
        'info': (0.3, 0.7, 1, 1),  # Bright blue

        # Priority colors
        'priority_high': (1, 0.3, 0.3, 1),  # Bright red
        'priority_medium': (1, 0.7, 0.3, 1),  # Bright orange
        'priority_low': (0.3, 0.7, 1, 1),  # Bright blue

        # Category colors
        'category_work': (0.3, 0.7, 1, 1),  # Bright blue
        'category_personal': (0.7, 0.4, 0.9, 1),  # Bright purple
        'category_health': (0.4, 0.8, 0.5, 1),  # Bright green
        'category_learning': (1, 0.7, 0.3, 1),  # Bright orange

        # UI elements
        'divider': (0.25, 0.25, 0.25, 1),  # Dark divider
        'border': (0.3, 0.3, 0.3, 1),  # Border color
        'shadow': (0, 0, 0, 0.5),  # Strong shadow
        'overlay': (0, 0, 0, 0.7),  # Darker overlay
    }

    # ==================== TYPOGRAPHY ====================

    TYPOGRAPHY = {
        'h1': {'size': dp(32), 'bold': True},
        'h2': {'size': dp(28), 'bold': True},
        'h3': {'size': dp(24), 'bold': True},
        'h4': {'size': dp(20), 'bold': True},
        'h5': {'size': dp(18), 'bold': True},
        'h6': {'size': dp(16), 'bold': True},
        'subtitle1': {'size': dp(16), 'bold': False},
        'subtitle2': {'size': dp(14), 'bold': False},
        'body1': {'size': dp(16), 'bold': False},
        'body2': {'size': dp(14), 'bold': False},
        'button': {'size': dp(14), 'bold': True},
        'caption': {'size': dp(12), 'bold': False},
        'overline': {'size': dp(10), 'bold': True},
    }

    # ==================== SPACING ====================

    SPACING = {
        'xs': dp(4),
        'sm': dp(8),
        'md': dp(16),
        'lg': dp(24),
        'xl': dp(32),
        'xxl': dp(48),
    }

    # ==================== SIZING ====================

    SIZING = {
        'icon_sm': dp(18),
        'icon_md': dp(24),
        'icon_lg': dp(32),
        'icon_xl': dp(48),

        'button_height': dp(48),
        'button_height_sm': dp(36),
        'button_height_lg': dp(56),

        'input_height': dp(56),
        'card_min_height': dp(120),

        'header_height': dp(64),
        'bottom_nav_height': dp(64),

        'radius_sm': dp(8),
        'radius_md': dp(12),
        'radius_lg': dp(16),
        'radius_xl': dp(24),
    }

    # ==================== ELEVATION ====================

    ELEVATION = {
        'none': 0,
        'low': 2,
        'medium': 4,
        'high': 8,
        'very_high': 16,
    }

    # ==================== ANIMATIONS ====================

    ANIMATION = {
        'duration_fast': 0.15,
        'duration_normal': 0.25,
        'duration_slow': 0.35,
        'transition': 'out_quad',
    }

    @staticmethod
    def get_theme_colors(theme_mode='Light'):
        """Get color palette for theme mode"""
        if theme_mode == 'Dark':
            return ThemeConfig.DARK_THEME
        return ThemeConfig.LIGHT_THEME

    @staticmethod
    def apply_theme(app, theme_mode='Light'):
        """Apply theme to the app"""
        app.theme_cls.theme_style = theme_mode

        # Set primary colors
        if theme_mode == 'Light':
            app.theme_cls.primary_palette = "Blue"
            app.theme_cls.primary_hue = "600"
            app.theme_cls.accent_palette = "Orange"
            app.theme_cls.accent_hue = "600"
        else:
            app.theme_cls.primary_palette = "Blue"
            app.theme_cls.primary_hue = "400"
            app.theme_cls.accent_palette = "Orange"
            app.theme_cls.accent_hue = "400"

    @staticmethod
    def get_responsive_size(base_size):
        """Get responsive size based on screen width"""
        screen_width = Window.width
        scale = screen_width / 375  # Base width (iPhone SE)
        return base_size * scale

    @staticmethod
    def get_text_color(theme_mode='Light', variant='primary'):
        """Get text color based on theme and variant"""
        colors = ThemeConfig.get_theme_colors(theme_mode)
        return colors.get(f'text_{variant}', colors['text_primary'])

    @staticmethod
    def get_status_color(status):
        """Get color for status (success, warning, error, info)"""
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)
        return colors.get(status, colors['info'])

    @staticmethod
    def get_priority_color(priority):
        """Get color for priority level"""
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        priority_map = {
            'high': 'priority_high',
            'medium': 'priority_medium',
            'low': 'priority_low',
        }

        return colors.get(priority_map.get(priority.lower(), 'priority_medium'))

    @staticmethod
    def get_category_color(category):
        """Get color for category"""
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        category_map = {
            'work': 'category_work',
            'personal': 'category_personal',
            'health': 'category_health',
            'learning': 'category_learning',
        }

        return colors.get(category_map.get(category.lower(), 'category_work'))