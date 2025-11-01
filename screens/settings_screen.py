"""
Enhanced Settings Screen - Phase 1 & 2
✅ Beautiful theme toggle
✅ Visual theme preview
✅ Organized sections
✅ Professional design
"""

from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.app import MDApp
from kivymd.toast import toast

# Import custom components
from widgets.components import (
    MCard, MButton, MIconButton, MLabel, MIcon, MDivider
)
from config.theme import ThemeConfig


class EnhancedSettingsScreen(MDScreen):
    """Enhanced settings with theme preview and organized sections"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build enhanced settings UI"""
        scroll = ScrollView()
        self.main_layout = BoxLayout(
            orientation='vertical',
            padding=ThemeConfig.SPACING['md'],
            spacing=ThemeConfig.SPACING['md'],
            size_hint_y=None
        )
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        # Header
        header = self.create_header()

        # Theme section
        theme_section = self.create_theme_section()

        # Divider
        divider1 = MDivider()

        # Notifications section
        notif_section = self.create_notification_section()

        # Divider
        divider2 = MDivider()

        # Data section
        data_section = self.create_data_section()

        # Divider
        divider3 = MDivider()

        # About section
        about_section = self.create_about_section()

        # Add all to layout
        self.main_layout.add_widget(header)
        self.main_layout.add_widget(theme_section)
        self.main_layout.add_widget(divider1)
        self.main_layout.add_widget(notif_section)
        self.main_layout.add_widget(divider2)
        self.main_layout.add_widget(data_section)
        self.main_layout.add_widget(divider3)
        self.main_layout.add_widget(about_section)

        scroll.add_widget(self.main_layout)
        self.add_widget(scroll)

    def create_header(self):
        """Create header"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ThemeConfig.SIZING['header_height'],
            padding=[0, dp(8), 0, dp(8)]
        )

        back_btn = MIconButton(
            icon="arrow-left",
            icon_size='large',
            pos_hint={"center_y": 0.5}
        )
        back_btn.bind(on_release=lambda x: self.go_back())

        title_box = BoxLayout(orientation='vertical', size_hint_x=0.7)

        title = MLabel(
            text="Settings",
            variant='h5',
            color_variant='primary'
        )
        title.size_hint_y = None
        title.height = dp(35)

        subtitle = MLabel(
            text="Customize your experience",
            variant='caption',
            color_variant='secondary'
        )
        subtitle.size_hint_y = None
        subtitle.height = dp(25)

        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(back_btn)
        header.add_widget(title_box)

        return header

    def create_theme_section(self):
        """Create enhanced theme selection section"""
        app = MDApp.get_running_app()
        current_theme = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(current_theme)

        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(320),
            spacing=ThemeConfig.SPACING['md']
        )

        # Section title
        title = MLabel(
            text="🎨 Appearance",
            variant='h6',
            color_variant='primary'
        )
        title.size_hint_y = None
        title.height = dp(35)

        # Theme card
        theme_card = MCard(variant='elevated')
        theme_card.orientation = 'vertical'
        theme_card.size_hint_y = None
        theme_card.height = dp(270)
        theme_card.padding = ThemeConfig.SPACING['lg']
        theme_card.spacing = ThemeConfig.SPACING['md']

        # Card title
        card_title = MLabel(
            text="Choose Your Theme",
            variant='subtitle1',
            color_variant='primary'
        )
        card_title.size_hint_y = None
        card_title.height = dp(30)

        # Card subtitle
        card_subtitle = MLabel(
            text="Select the theme that suits you best",
            variant='caption',
            color_variant='secondary'
        )
        card_subtitle.size_hint_y = None
        card_subtitle.height = dp(25)

        # Theme toggle buttons
        btn_container = BoxLayout(
            orientation='horizontal',
            spacing=ThemeConfig.SPACING['md'],
            size_hint_y=None,
            height=dp(180)
        )

        # Light theme preview
        light_container = self.create_theme_preview(
            theme='Light',
            icon='white-balance-sunny',
            is_active=(current_theme == 'Light')
        )

        # Dark theme preview
        dark_container = self.create_theme_preview(
            theme='Dark',
            icon='moon-waning-crescent',
            is_active=(current_theme == 'Dark')
        )

        btn_container.add_widget(light_container)
        btn_container.add_widget(dark_container)

        theme_card.add_widget(card_title)
        theme_card.add_widget(card_subtitle)
        theme_card.add_widget(btn_container)

        section.add_widget(title)
        section.add_widget(theme_card)

        return section

    def create_theme_preview(self, theme, icon, is_active):
        """Create theme preview card"""
        container = BoxLayout(orientation='vertical', spacing=ThemeConfig.SPACING['sm'])

        # Preview card
        if theme == 'Light':
            bg_color = (0.95, 0.95, 0.95, 1)
            text_color = (0.2, 0.2, 0.2, 1)
            icon_color = (0.9, 0.6, 0.2, 1)
        else:
            bg_color = (0.15, 0.15, 0.15, 1)
            text_color = (0.9, 0.9, 0.9, 1)
            icon_color = (0.6, 0.4, 0.9, 1)

        preview_card = MCard(variant='elevated')
        preview_card.orientation = 'vertical'
        preview_card.size_hint_y = None
        preview_card.height = dp(120)
        preview_card.md_bg_color = bg_color

        # Icon
        theme_icon = MIcon(
            icon=icon,
            icon_size='extra_large',
            halign="center"
        )
        theme_icon.text_color = icon_color
        theme_icon.size_hint_y = None
        theme_icon.height = dp(60)

        # Name
        name_label = MLabel(
            text=f"{theme} Theme",
            variant='subtitle1',
            halign="center"
        )
        name_label.theme_text_color = "Custom"
        name_label.text_color = text_color
        name_label.size_hint_y = None
        name_label.height = dp(30)

        # Active indicator
        if is_active:
            active_indicator = MLabel(
                text="✓ Active",
                variant='caption',
                halign="center"
            )
            active_indicator.theme_text_color = "Custom"
            active_indicator.text_color = (0.2, 0.7, 0.3, 1)
            active_indicator.bold = True
            active_indicator.size_hint_y = None
            active_indicator.height = dp(20)
        else:
            active_indicator = BoxLayout(size_hint_y=None, height=dp(20))

        preview_card.add_widget(theme_icon)
        preview_card.add_widget(name_label)
        preview_card.add_widget(active_indicator)

        # Select button
        select_btn = MButton(
            text="Select" if not is_active else "Selected",
            variant='primary' if is_active else 'secondary',
            size='small'
        )
        select_btn.bind(on_release=lambda x: self.switch_theme(theme))

        container.add_widget(preview_card)
        container.add_widget(select_btn)

        return container

    def create_notification_section(self):
        """Create notification settings section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(220),
            spacing=ThemeConfig.SPACING['md']
        )

        # Section title
        title = MLabel(
            text="🔔 Notifications",
            variant='h6',
            color_variant='primary'
        )
        title.size_hint_y = None
        title.height = dp(35)

        # Notification card
        notif_card = MCard(variant='elevated')
        notif_card.orientation = 'vertical'
        notif_card.size_hint_y = None
        notif_card.height = dp(170)
        notif_card.padding = ThemeConfig.SPACING['lg']
        notif_card.spacing = ThemeConfig.SPACING['sm']

        # Card title
        card_title = MLabel(
            text="Stay Motivated & On Track",
            variant='subtitle1',
            color_variant='primary'
        )
        card_title.size_hint_y = None
        card_title.height = dp(30)

        # Features
        features = BoxLayout(
            orientation='vertical',
            spacing=ThemeConfig.SPACING['sm'],
            size_hint_y=None,
            height=dp(100)
        )

        feature1 = self.create_feature_item("✓", "Motivational messages enabled", (0.2, 0.7, 0.3, 1))
        feature2 = self.create_feature_item("✓", "Smart reminders active", (0.2, 0.7, 0.3, 1))
        feature3 = self.create_feature_item("✓", "Progress alerts on", (0.2, 0.7, 0.3, 1))

        features.add_widget(feature1)
        features.add_widget(feature2)
        features.add_widget(feature3)

        notif_card.add_widget(card_title)
        notif_card.add_widget(features)

        section.add_widget(title)
        section.add_widget(notif_card)

        return section

    def create_data_section(self):
        """Create data management section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            spacing=ThemeConfig.SPACING['md']
        )

        # Section title
        title = MLabel(
            text="💾 Data Management",
            variant='h6',
            color_variant='primary'
        )
        title.size_hint_y = None
        title.height = dp(35)

        # Data card
        data_card = MCard(variant='elevated')
        data_card.orientation = 'vertical'
        data_card.size_hint_y = None
        data_card.height = dp(150)
        data_card.padding = ThemeConfig.SPACING['lg']
        data_card.spacing = ThemeConfig.SPACING['md']

        # Card title
        card_title = MLabel(
            text="Backup & Export",
            variant='subtitle1',
            color_variant='primary'
        )
        card_title.size_hint_y = None
        card_title.height = dp(30)

        # Action buttons
        btn_row = BoxLayout(
            orientation='horizontal',
            spacing=ThemeConfig.SPACING['md'],
            size_hint_y=None,
            height=dp(48)
        )

        backup_btn = MButton(
            text="Backup Data",
            variant='primary',
            size='small'
        )
        backup_btn.bind(on_release=lambda x: toast("Backup feature coming soon!"))

        export_btn = MButton(
            text="Export CSV",
            variant='secondary',
            size='small'
        )
        export_btn.bind(on_release=lambda x: toast("Export feature coming soon!"))

        btn_row.add_widget(backup_btn)
        btn_row.add_widget(export_btn)

        data_card.add_widget(card_title)
        data_card.add_widget(btn_row)

        section.add_widget(title)
        section.add_widget(data_card)

        return section

    def create_about_section(self):
        """Create about section"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            spacing=ThemeConfig.SPACING['md']
        )

        # Section title
        title = MLabel(
            text="ℹ️ About",
            variant='h6',
            color_variant='primary'
        )
        title.size_hint_y = None
        title.height = dp(35)

        # About card
        about_card = MCard(variant='elevated')
        about_card.orientation = 'vertical'
        about_card.size_hint_y = None
        about_card.height = dp(150)
        about_card.padding = ThemeConfig.SPACING['lg']
        about_card.spacing = ThemeConfig.SPACING['sm']

        # App name
        app_name = MLabel(
            text="MomentumTrack",
            variant='h6',
            color_variant='primary',
            halign="center"
        )
        app_name.size_hint_y = None
        app_name.height = dp(35)

        # Version
        version = MLabel(
            text="Version 2.0 - Phase 1 & 2 Enhanced",
            variant='caption',
            color_variant='secondary',
            halign="center"
        )
        version.size_hint_y = None
        version.height = dp(25)

        # Tagline
        tagline = MLabel(
            text="Build discipline, gain momentum, achieve greatness 🚀",
            variant='body2',
            color_variant='secondary',
            halign="center"
        )
        tagline.size_hint_y = None
        tagline.height = dp(40)

        # Developer
        developer = MLabel(
            text="Developed with ❤️ by Hadi",
            variant='caption',
            color_variant='secondary',
            halign="center"
        )
        developer.size_hint_y = None
        developer.height = dp(25)

        about_card.add_widget(app_name)
        about_card.add_widget(version)
        about_card.add_widget(tagline)
        about_card.add_widget(developer)

        section.add_widget(title)
        section.add_widget(about_card)

        return section

    def create_feature_item(self, icon, text, color):
        """Create feature list item"""
        item = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=ThemeConfig.SPACING['sm']
        )

        icon_label = MLabel(
            text=icon,
            variant='body1'
        )
        icon_label.theme_text_color = "Custom"
        icon_label.text_color = color
        icon_label.size_hint_x = None
        icon_label.width = dp(25)

        text_label = MLabel(
            text=text,
            variant='body2',
            color_variant='primary'
        )

        item.add_widget(icon_label)
        item.add_widget(text_label)

        return item

    def switch_theme(self, theme_mode):
        """Switch app theme with animation"""
        app = MDApp.get_running_app()

        # Only switch if different
        if app.theme_cls.theme_style == theme_mode:
            toast(f"Already using {theme_mode} theme")
            return

        # Switch theme
        app.switch_theme(theme_mode)

        # Rebuild UI
        self.rebuild_ui()

        toast(f"✓ Switched to {theme_mode} theme")

    def rebuild_ui(self):
        """Rebuild UI for theme changes"""
        self.clear_widgets()
        self.build_ui()

    def go_back(self):
        """Navigate back"""
        self.manager.current = 'home'