from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel, MDIcon
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from datetime import datetime


class HomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build modern home screen UI"""
        # Main scrollable layout
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Header with app name and settings
        header = self.create_header()

        # Welcome card with date and motivation
        welcome_card = self.create_welcome_card()

        # Quick stats cards in grid
        stats_grid = self.create_stats_grid()

        # Quick action buttons
        actions_title = MDLabel(
            text="Quick Actions",
            font_style="H6",
            size_hint_y=None,
            height=dp(40),
            bold=True
        )

        action_buttons = self.create_action_buttons()

        # Add all to layout
        layout.add_widget(header)
        layout.add_widget(welcome_card)
        layout.add_widget(stats_grid)
        layout.add_widget(actions_title)
        layout.add_widget(action_buttons)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def create_header(self):
        """Create header with branding"""
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70))

        # App branding
        brand_box = BoxLayout(orientation='vertical', size_hint_x=0.7)
        app_name = MDLabel(
            text="MomentumTrack",
            font_style="H5",
            bold=True
        )
        tagline = MDLabel(
            text="Your Productivity Companion",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        brand_box.add_widget(app_name)
        brand_box.add_widget(tagline)

        # Settings icon
        settings_btn = MDIconButton(
            icon="cog-outline",
            pos_hint={"center_y": 0.5},
            icon_size="32sp",
            on_release=lambda x: self.go_to_settings()
        )

        header.add_widget(brand_box)
        header.add_widget(settings_btn)

        return header

    def create_welcome_card(self):
        """Create welcome card with date and greeting"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(120),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        # Date
        date_label = MDLabel(
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font_style="Body2",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(25)
        )

        # Greeting with emoji
        greeting = MDLabel(
            text="Keep the momentum going! 🚀",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        # Motivational quote
        quote = MDLabel(
            text='"Small progress is still progress"',
            font_style="Caption",
            theme_text_color="Secondary",
            italic=True,
            size_hint_y=None,
            height=dp(25)
        )

        card.add_widget(date_label)
        card.add_widget(greeting)
        card.add_widget(quote)

        return card

    def create_stats_grid(self):
        """Create grid of stat cards"""
        grid = GridLayout(cols=2, spacing=dp(12), size_hint_y=None, height=dp(180))

        # Completion Rate Card
        completion_rate = self.get_completion_rate()
        completion_card = self.create_stat_card(
            icon="check-circle-outline",
            value=f"{completion_rate}%",
            label="Completion",
            color=(0.2, 0.7, 0.3, 1) if completion_rate >= 70 else (0.9, 0.5, 0.2, 1)
        )

        # Tasks Completed Card
        completed = self.get_completed_tasks()
        total = self.get_total_tasks()
        tasks_card = self.create_stat_card(
            icon="format-list-checks",
            value=f"{completed}/{total}",
            label="Tasks Done",
            color=(0.2, 0.6, 0.9, 1)
        )

        # Streak Card (placeholder for now)
        streak_card = self.create_stat_card(
            icon="fire",
            value="3 days",
            label="Current Streak",
            color=(0.9, 0.4, 0.2, 1)
        )

        # Goals Card (placeholder for now)
        goals_card = self.create_stat_card(
            icon="target",
            value="2 active",
            label="Goals",
            color=(0.6, 0.3, 0.8, 1)
        )

        grid.add_widget(completion_card)
        grid.add_widget(tasks_card)
        grid.add_widget(streak_card)
        grid.add_widget(goals_card)

        return grid

    def create_stat_card(self, icon, value, label, color):
        """Create individual stat card"""
        card = MDCard(
            orientation='vertical',
            padding=dp(16),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        # Icon
        icon_widget = MDIcon(
            icon=icon,
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Custom",
            text_color=color,
            halign="center"
        )

        # Value
        value_label = MDLabel(
            text=value,
            font_style="H5",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        )

        # Label
        label_widget = MDLabel(
            text=label,
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(20)
        )

        card.add_widget(icon_widget)
        card.add_widget(value_label)
        card.add_widget(label_widget)

        return card

    def create_action_buttons(self):
        """Create quick action buttons"""
        btn_layout = BoxLayout(orientation='vertical', spacing=dp(12), size_hint_y=None, height=dp(180))

        # My Tasks Button
        tasks_btn = MDFillRoundFlatButton(
            text="📋  My Tasks",
            font_size="16sp",
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.2, 0.6, 0.9, 1),
            on_release=lambda x: self.go_to_tasks()
        )

        # Time Tracker Button
        time_btn = MDFillRoundFlatButton(
            text="⏰  8/8/8 Time Balance",
            font_size="16sp",
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.3, 0.7, 0.4, 1),
            on_release=lambda x: self.go_to_time_tracker()
        )

        # Goals Button
        goals_btn = MDFillRoundFlatButton(
            text="🎯  Long-term Goals",
            font_size="16sp",
            size_hint_y=None,
            height=dp(56),
            md_bg_color=(0.6, 0.3, 0.8, 1)
        )

        btn_layout.add_widget(tasks_btn)
        btn_layout.add_widget(time_btn)
        btn_layout.add_widget(goals_btn)

        return btn_layout

    def get_completion_rate(self):
        """Get task completion rate"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            return int(app.db_manager.get_completion_rate())
        except:
            return 0

    def get_completed_tasks(self):
        """Get number of completed tasks"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            tasks = app.db_manager.get_all_tasks(status='completed')
            return len(tasks)
        except:
            return 0

    def get_total_tasks(self):
        """Get total number of tasks"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            tasks = app.db_manager.get_all_tasks()
            return len(tasks)
        except:
            return 0

    def go_to_tasks(self):
        """Navigate to tasks screen"""
        self.manager.current = 'tasks'

    def go_to_time_tracker(self):
        """Navigate to time tracker screen"""
        self.manager.current = 'time_tracker'

    def go_to_settings(self):
        """Navigate to settings screen"""
        self.manager.current = 'settings'

    def on_enter(self):
        """Refresh stats when entering screen"""
        pass