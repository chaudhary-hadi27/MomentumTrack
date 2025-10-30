from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel, MDIcon
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp


class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build modern settings screen UI"""
        # Scrollable layout
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Header
        header = self.create_header()

        # Theme section
        theme_section = self.create_theme_section()

        # Notifications section
        notif_section = self.create_notification_section()

        # Progress section
        progress_section = self.create_progress_section()

        # About section
        about_section = self.create_about_section()

        # Add all to layout
        layout.add_widget(header)
        layout.add_widget(theme_section)
        layout.add_widget(notif_section)
        layout.add_widget(progress_section)
        layout.add_widget(about_section)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def create_header(self):
        """Create header with back button"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            padding=[0, dp(8), 0, dp(8)]
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"center_y": 0.5},
            icon_size="28sp",
            on_release=lambda x: self.go_back()
        )

        title_box = BoxLayout(orientation='vertical', size_hint_x=0.7)
        title = MDLabel(
            text="Settings",
            font_style="H5",
            bold=True
        )
        subtitle = MDLabel(
            text="Customize your experience",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(back_btn)
        header.add_widget(title_box)

        return header

    def create_theme_section(self):
        """Create theme selection section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(250), spacing=dp(12))

        # Section title
        title = MDLabel(
            text="🎨 Appearance",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        # Theme card
        theme_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(200),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        card_title = MDLabel(
            text="Choose Your Theme",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        card_subtitle = MDLabel(
            text="Select the theme that suits you best",
            font_style="Caption",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(25)
        )

        # Theme buttons
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(12), size_hint_y=None, height=dp(100))

        # Light theme button
        light_container = BoxLayout(orientation='vertical', spacing=dp(8))
        light_icon = MDIcon(
            icon="white-balance-sunny",
            halign="center",
            size_hint_y=None,
            height=dp(40),
            font_size="40sp"
        )
        light_btn = MDFillRoundFlatButton(
            text="Light",
            size_hint=(1, None),
            height=dp(48),
            md_bg_color=(0.95, 0.95, 0.95, 1),
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            on_release=lambda x: self.switch_theme('Light')
        )
        light_container.add_widget(light_icon)
        light_container.add_widget(light_btn)

        # Dark theme button
        dark_container = BoxLayout(orientation='vertical', spacing=dp(8))
        dark_icon = MDIcon(
            icon="moon-waning-crescent",
            halign="center",
            size_hint_y=None,
            height=dp(40),
            font_size="40sp"
        )
        dark_btn = MDFillRoundFlatButton(
            text="Dark",
            size_hint=(1, None),
            height=dp(48),
            md_bg_color=(0.15, 0.15, 0.15, 1),
            theme_text_color="Custom",
            text_color=(0.9, 0.9, 0.9, 1),
            on_release=lambda x: self.switch_theme('Dark')
        )
        dark_container.add_widget(dark_icon)
        dark_container.add_widget(dark_btn)

        btn_layout.add_widget(light_container)
        btn_layout.add_widget(dark_container)

        theme_card.add_widget(card_title)
        theme_card.add_widget(card_subtitle)
        theme_card.add_widget(btn_layout)

        section.add_widget(title)
        section.add_widget(theme_card)

        return section

    def create_notification_section(self):
        """Create notification settings section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200), spacing=dp(12))

        # Section title
        title = MDLabel(
            text="🔔 Notifications",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        # Notification card
        notif_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(150),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        card_title = MDLabel(
            text="Stay Motivated",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        # Feature list
        features = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(90))

        feature1 = self.create_feature_item("✓", "Motivational messages enabled")
        feature2 = self.create_feature_item("✓", "Smart reminders active")
        feature3 = self.create_feature_item("✓", "Progress alerts on")

        features.add_widget(feature1)
        features.add_widget(feature2)
        features.add_widget(feature3)

        notif_card.add_widget(card_title)
        notif_card.add_widget(features)

        section.add_widget(title)
        section.add_widget(notif_card)

        return section

    def create_progress_section(self):
        """Create progress threshold section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180), spacing=dp(12))

        # Section title
        title = MDLabel(
            text="📊 Progress Tracking",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        # Progress card
        progress_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(130),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        card_title = MDLabel(
            text="Performance Alerts",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        threshold_info = MDLabel(
            text="Get motivated when progress drops below 60%",
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(40)
        )

        threshold_value = MDLabel(
            text="Current threshold: 60%",
            font_style="Caption",
            bold=True,
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(30)
        )

        progress_card.add_widget(card_title)
        progress_card.add_widget(threshold_info)
        progress_card.add_widget(threshold_value)

        section.add_widget(title)
        section.add_widget(progress_card)

        return section

    def create_about_section(self):
        """Create about section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(160), spacing=dp(12))

        # Section title
        title = MDLabel(
            text="ℹ️ About",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        # About card
        about_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(110),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        app_name = MDLabel(
            text="MomentumTrack",
            font_style="Subtitle1",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )

        version = MDLabel(
            text="Version 1.0 MVP",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(25)
        )

        tagline = MDLabel(
            text="Your Productivity Companion 🚀",
            font_style="Body2",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )

        about_card.add_widget(app_name)
        about_card.add_widget(version)
        about_card.add_widget(tagline)

        section.add_widget(title)
        section.add_widget(about_card)

        return section

    def create_feature_item(self, icon, text):
        """Create a feature list item"""
        item = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25), spacing=dp(8))

        icon_label = MDLabel(
            text=icon,
            size_hint_x=None,
            width=dp(20),
            theme_text_color="Custom",
            text_color=(0.2, 0.7, 0.3, 1)
        )

        text_label = MDLabel(
            text=text,
            font_style="Body2"
        )

        item.add_widget(icon_label)
        item.add_widget(text_label)

        return item

    def on_enter(self):
        """Load settings when screen is entered"""
        pass  # Settings loaded

    def switch_theme(self, theme_mode):
        """Switch app theme"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.switch_theme(theme_mode)

        # Visual feedback
        from kivymd.toast import toast
        toast(f"✓ Theme changed to {theme_mode}")

    def go_back(self):
        """Navigate back to home"""
        self.manager.current = 'home'