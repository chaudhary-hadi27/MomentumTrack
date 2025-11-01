"""
MomentumTrack - Reusable Component Library
Phase 1: Professional, consistent UI components
"""

from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.textfield import MDTextField
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Line
from config.theme import ThemeConfig
from kivymd.app import MDApp


class MCard(MDCard):
    """Professional card component with consistent styling"""

    def __init__(self, variant='elevated', **kwargs):
        """
        Args:
            variant: 'elevated', 'outlined', 'flat'
        """
        super().__init__(**kwargs)

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        # Apply styling based on variant
        if variant == 'elevated':
            self.elevation = ThemeConfig.ELEVATION['medium']
            self.md_bg_color = colors['bg_card']
        elif variant == 'outlined':
            self.elevation = ThemeConfig.ELEVATION['none']
            self.md_bg_color = colors['bg_card']
            self.line_color = colors['border']
        else:  # flat
            self.elevation = ThemeConfig.ELEVATION['none']
            self.md_bg_color = colors['bg_secondary']

        # Standard properties
        self.radius = [ThemeConfig.SIZING['radius_md']] * 4
        self.padding = ThemeConfig.SPACING['md']
        self.ripple_behavior = True

    def animate_press(self):
        """Animate on press"""
        anim = Animation(
            elevation=ThemeConfig.ELEVATION['high'],
            duration=ThemeConfig.ANIMATION['duration_fast']
        )
        anim.start(self)

    def animate_release(self):
        """Animate on release"""
        anim = Animation(
            elevation=ThemeConfig.ELEVATION['medium'],
            duration=ThemeConfig.ANIMATION['duration_fast']
        )
        anim.start(self)


class MButton(MDRaisedButton):
    """Professional button component"""

    def __init__(self, variant='primary', size='medium', **kwargs):
        """
        Args:
            variant: 'primary', 'secondary', 'accent', 'success', 'warning', 'error'
            size: 'small', 'medium', 'large'
        """
        super().__init__(**kwargs)

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        # Size
        size_map = {
            'small': ThemeConfig.SIZING['button_height_sm'],
            'medium': ThemeConfig.SIZING['button_height'],
            'large': ThemeConfig.SIZING['button_height_lg'],
        }
        self.size_hint_y = None
        self.height = size_map.get(size, ThemeConfig.SIZING['button_height'])

        # Variant color
        variant_colors = {
            'primary': colors['primary'],
            'secondary': colors['secondary'],
            'accent': colors['accent'],
            'success': colors['success'],
            'warning': colors['warning'],
            'error': colors['error'],
        }
        self.md_bg_color = variant_colors.get(variant, colors['primary'])

        # Standard properties
        self.font_size = ThemeConfig.TYPOGRAPHY['button']['size']
        self.font_name = 'Roboto'
        self.bold = True
        self.ripple_duration_in_slow = 0.5


class MIconButton(MDIconButton):
    """Professional icon button"""

    def __init__(self, icon_size='medium', **kwargs):
        """
        Args:
            icon_size: 'small', 'medium', 'large', 'extra_large'
        """
        super().__init__(**kwargs)

        # Size
        size_map = {
            'small': ThemeConfig.SIZING['icon_sm'],
            'medium': ThemeConfig.SIZING['icon_md'],
            'large': ThemeConfig.SIZING['icon_lg'],
            'extra_large': ThemeConfig.SIZING['icon_xl'],
        }

        self.icon_size = size_map.get(icon_size, ThemeConfig.SIZING['icon_md'])


class MTextField(MDTextField):
    """Professional text field"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Standard properties
        self.mode = "rectangle"
        self.size_hint_y = None
        self.height = ThemeConfig.SIZING['input_height']
        self.font_size = ThemeConfig.TYPOGRAPHY['body1']['size']


class MLabel(MDLabel):
    """Professional label component"""

    def __init__(self, variant='body1', color_variant='primary', **kwargs):
        """
        Args:
            variant: 'h1'-'h6', 'subtitle1', 'subtitle2', 'body1', 'body2', 'caption'
            color_variant: 'primary', 'secondary', 'disabled', 'hint'
        """
        super().__init__(**kwargs)

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style

        # Typography
        typo = ThemeConfig.TYPOGRAPHY.get(variant, ThemeConfig.TYPOGRAPHY['body1'])
        self.font_size = typo['size']
        if typo.get('bold'):
            self.bold = True

        # Color
        self.theme_text_color = "Custom"
        self.text_color = ThemeConfig.get_text_color(theme_mode, color_variant)


class MIcon(MDIcon):
    """Professional icon component"""

    def __init__(self, icon_size='medium', icon_color='primary', **kwargs):
        """
        Args:
            icon_size: 'small', 'medium', 'large', 'extra_large'
            icon_color: color key or tuple
        """
        super().__init__(**kwargs)

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        # Size
        size_map = {
            'small': ThemeConfig.SIZING['icon_sm'],
            'medium': ThemeConfig.SIZING['icon_md'],
            'large': ThemeConfig.SIZING['icon_lg'],
            'extra_large': ThemeConfig.SIZING['icon_xl'],
        }

        font_size = size_map.get(icon_size, ThemeConfig.SIZING['icon_md'])
        self.font_size = f"{font_size}sp"

        # Color
        self.theme_text_color = "Custom"
        if isinstance(icon_color, str):
            self.text_color = colors.get(icon_color, colors['text_primary'])
        else:
            self.text_color = icon_color


class MStatCard(MCard):
    """Stat display card"""

    def __init__(self, icon, value, label, color='primary', **kwargs):
        super().__init__(variant='elevated', **kwargs)

        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(120)

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        # Icon
        icon_widget = MIcon(
            icon=icon,
            icon_size='large',
            halign="center"
        )
        icon_widget.text_color = colors.get(color, colors['primary'])
        icon_widget.size_hint_y = None
        icon_widget.height = dp(40)

        # Value
        value_label = MLabel(
            text=str(value),
            variant='h4',
            halign="center"
        )
        value_label.size_hint_y = None
        value_label.height = dp(40)

        # Label
        label_widget = MLabel(
            text=label,
            variant='caption',
            color_variant='secondary',
            halign="center"
        )
        label_widget.size_hint_y = None
        label_widget.height = dp(25)

        self.add_widget(icon_widget)
        self.add_widget(value_label)
        self.add_widget(label_widget)


class MEmptyState(BoxLayout):
    """Empty state component"""

    def __init__(self, icon, title, subtitle, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'
        self.padding = ThemeConfig.SPACING['xl']
        self.spacing = ThemeConfig.SPACING['md']
        self.size_hint_y = None
        self.height = dp(300)

        # Icon
        icon_widget = MIcon(
            icon=icon,
            icon_size='extra_large',
            halign="center"
        )
        icon_widget.size_hint_y = None
        icon_widget.height = dp(80)

        # Title
        title_label = MLabel(
            text=title,
            variant='h5',
            halign="center"
        )
        title_label.size_hint_y = None
        title_label.height = dp(40)

        # Subtitle
        subtitle_label = MLabel(
            text=subtitle,
            variant='body2',
            color_variant='secondary',
            halign="center"
        )
        subtitle_label.size_hint_y = None
        subtitle_label.height = dp(60)

        self.add_widget(icon_widget)
        self.add_widget(title_label)
        self.add_widget(subtitle_label)


class MDivider(Widget):
    """Horizontal divider"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint_y = None
        self.height = dp(1)

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        with self.canvas:
            Color(*colors['divider'])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MChip(BoxLayout):
    """Chip/Tag component (replacement for MDChip)"""

    def __init__(self, text, color='primary', closeable=False, on_close=None, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.height = dp(32)
        self.spacing = dp(8)
        self.padding = [dp(12), dp(6), dp(12), dp(6)]

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        # Background
        with self.canvas.before:
            Color(*colors.get(color, colors['primary']))
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(16)]
            )

        self.bind(pos=self.update_rect, size=self.update_rect)

        # Label
        label = MDLabel(
            text=text,
            font_size=ThemeConfig.TYPOGRAPHY['caption']['size'],
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        self.add_widget(label)

        # Calculate width
        self.width = len(text) * dp(8) + dp(24)

        # Close button
        if closeable and on_close:
            close_btn = MDIconButton(
                icon="close",
                icon_size="16sp",
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                on_release=on_close
            )
            self.add_widget(close_btn)
            self.width += dp(32)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class MProgressBar(Widget):
    """Custom progress bar"""

    def __init__(self, value=0, max_value=100, color='primary', **kwargs):
        super().__init__(**kwargs)

        self.value = value
        self.max_value = max_value
        self.color_key = color

        self.size_hint_y = None
        self.height = dp(8)

        self.bind(pos=self.update_bar, size=self.update_bar)
        self.update_bar()

    def update_bar(self, *args):
        self.canvas.clear()

        # Get theme
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        with self.canvas:
            # Background
            Color(*colors['bg_secondary'])
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(4)]
            )

            # Progress
            if self.value > 0:
                progress_width = (self.value / self.max_value) * self.width
                Color(*colors.get(self.color_key, colors['primary']))
                RoundedRectangle(
                    pos=self.pos,
                    size=(progress_width, self.height),
                    radius=[dp(4)]
                )

    def set_value(self, value):
        """Animate to new value"""
        self.value = min(value, self.max_value)
        self.update_bar()


class MLoadingSpinner(BoxLayout):
    """Loading spinner component"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(100)

        # Icon that will rotate
        self.spinner = MIcon(
            icon="loading",
            icon_size='large',
            halign="center"
        )
        self.spinner.size_hint_y = None
        self.spinner.height = dp(60)

        # Text
        text = MLabel(
            text="Loading...",
            variant='caption',
            color_variant='secondary',
            halign="center"
        )
        text.size_hint_y = None
        text.height = dp(30)

        self.add_widget(self.spinner)
        self.add_widget(text)

        # Start rotation animation
        self.anim = Animation(
            rotation=360,
            duration=1,
            t='linear'
        ) + Animation(
            rotation=0,
            duration=0
        )
        self.anim.repeat = True
        self.anim.start(self.spinner)