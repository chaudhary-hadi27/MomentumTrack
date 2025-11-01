"""
Enhanced Home Screen - Phase 1 & 2
✅ No text overlapping
✅ Perfect theme support
✅ Smooth animations
✅ Professional design
"""

from kivymd.uix.screen import MDScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.animation import Animation
from datetime import datetime
from kivymd.app import MDApp

# Import custom components
from widgets.components import (
    MCard, MButton, MIconButton, MLabel, MIcon,
    MStatCard, MDivider, MEmptyState
)
from config.theme import ThemeConfig


class EnhancedHomeScreen(MDScreen):
    """Enhanced home screen with professional UI"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build enhanced home screen UI"""
        # Main scrollable layout
        scroll = ScrollView()
        self.main_layout = BoxLayout(
            orientation='vertical',
            padding=ThemeConfig.SPACING['md'],
            spacing=ThemeConfig.SPACING['md'],
            size_hint_y=None
        )
        self.main_layout.bind(minimum_height=self.main_layout.setter('height'))

        # Build sections
        header = self.create_header()
        welcome_card = self.create_welcome_card()
        quick_stats = self.create_quick_stats()

        # Divider
        divider = MDivider()

        actions_title = MLabel(
            text="Quick Actions",
            variant='h6',
            color_variant='primary'
        )
        actions_title.size_hint_y = None
        actions_title.height = dp(40)

        action_buttons = self.create_action_buttons()
        motivation_card = self.create_motivation_card()

        # Add all to layout
        self.main_layout.add_widget(header)
        self.main_layout.add_widget(welcome_card)
        self.main_layout.add_widget(quick_stats)
        self.main_layout.add_widget(divider)
        self.main_layout.add_widget(actions_title)
        self.main_layout.add_widget(action_buttons)
        self.main_layout.add_widget(motivation_card)

        scroll.add_widget(self.main_layout)
        self.add_widget(scroll)

    def create_header(self):
        """Create app header"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ThemeConfig.SIZING['header_height']
        )

        # Brand section
        brand_box = BoxLayout(orientation='vertical', size_hint_x=0.75)

        app_name = MLabel(
            text="MomentumTrack",
            variant='h4',
            color_variant='primary'
        )
        app_name.size_hint_y = None
        app_name.height = dp(35)

        tagline = MLabel(
            text="Your Productivity Companion",
            variant='caption',
            color_variant='secondary'
        )
        tagline.size_hint_y = None
        tagline.height = dp(25)

        brand_box.add_widget(app_name)
        brand_box.add_widget(tagline)

        # Settings button
        settings_btn = MIconButton(
            icon="cog-outline",
            icon_size='large',
            pos_hint={"center_y": 0.5}
        )
        settings_btn.bind(on_release=lambda x: self.go_to_settings())

        header.add_widget(brand_box)
        header.add_widget(settings_btn)

        return header

    def create_welcome_card(self):
        """Create welcome card with date and greeting"""
        card = MCard(variant='elevated')
        card.orientation = 'vertical'
        card.size_hint_y = None
        card.height = dp(140)
        card.padding = ThemeConfig.SPACING['lg']

        # Date
        date_label = MLabel(
            text=datetime.now().strftime("%A, %B %d, %Y"),
            variant='body2',
            color_variant='secondary'
        )
        date_label.size_hint_y = None
        date_label.height = dp(25)

        # Greeting
        hour = datetime.now().hour
        if hour < 12:
            greeting = "Good Morning! ☀️"
        elif hour < 18:
            greeting = "Good Afternoon! 🌤️"
        else:
            greeting = "Good Evening! 🌙"

        greeting_label = MLabel(
            text=greeting,
            variant='h5',
            color_variant='primary'
        )
        greeting_label.size_hint_y = None
        greeting_label.height = dp(40)

        # Motivational message
        app = MDApp.get_running_app()
        try:
            quote = app.get_motivational_message('auto')
        except:
            quote = "Keep the momentum going! 🚀"

        quote_label = MLabel(
            text=quote,
            variant='body2',
            color_variant='secondary'
        )
        quote_label.italic = True
        quote_label.size_hint_y = None
        quote_label.height = dp(45)

        card.add_widget(date_label)
        card.add_widget(greeting_label)
        card.add_widget(quote_label)

        return card

    def create_quick_stats(self):
        """Create statistics grid"""
        grid = GridLayout(
            cols=2,
            spacing=ThemeConfig.SPACING['md'],
            size_hint_y=None,
            height=dp(250)
        )

        # Get stats
        app = MDApp.get_running_app()

        try:
            completion_rate = int(app.db_manager.get_completion_rate())
            completed = len(app.db_manager.get_all_tasks(status='completed'))
            total = len(app.db_manager.get_all_tasks())
            active_goals = len(app.db_manager.get_all_goals())
        except:
            completion_rate = 0
            completed = 0
            total = 0
            active_goals = 0

        # Determine completion color
        if completion_rate >= 70:
            comp_color = 'success'
        elif completion_rate >= 50:
            comp_color = 'primary'
        else:
            comp_color = 'warning'

        # Create stat cards
        completion_card = MStatCard(
            icon="check-circle-outline",
            value=f"{completion_rate}%",
            label="Completion Rate",
            color=comp_color
        )

        tasks_card = MStatCard(
            icon="format-list-checks",
            value=f"{completed}/{total}",
            label="Tasks Completed",
            color='primary'
        )

        streak_card = MStatCard(
            icon="fire",
            value="3 days",
            label="Current Streak",
            color='warning'
        )

        goals_card = MStatCard(
            icon="target",
            value=f"{active_goals}",
            label="Active Goals",
            color='secondary'
        )

        grid.add_widget(completion_card)
        grid.add_widget(tasks_card)
        grid.add_widget(streak_card)
        grid.add_widget(goals_card)

        # Animate cards on appear
        for i, card in enumerate([completion_card, tasks_card, streak_card, goals_card]):
            card.opacity = 0
            anim = Animation(
                opacity=1,
                duration=0.3,
                t='out_cubic'
            )
            anim.start(card)

        return grid

    def create_action_buttons(self):
        """Create quick action buttons"""
        btn_layout = BoxLayout(
            orientation='vertical',
            spacing=ThemeConfig.SPACING['md'],
            size_hint_y=None,
            height=dp(260)
        )

        # Tasks button
        tasks_btn = MButton(
            text="📋  My Tasks",
            variant='primary',
            size='large'
        )
        tasks_btn.bind(on_release=lambda x: self.go_to_tasks())

        # Time tracker button
        time_btn = MButton(
            text="⏰  8/8/8 Time Balance",
            variant='secondary',
            size='large'
        )
        time_btn.bind(on_release=lambda x: self.go_to_time_tracker())

        # Goals button
        goals_btn = MButton(
            text="🎯  Long-term Goals",
            variant='accent',
            size='large'
        )
        goals_btn.bind(on_release=lambda x: self.go_to_goals())

        # Progress button
        progress_btn = MButton(
            text="📊  Progress & Analytics",
            variant='warning',
            size='large'
        )
        progress_btn.bind(on_release=lambda x: self.go_to_progress())

        btn_layout.add_widget(tasks_btn)
        btn_layout.add_widget(time_btn)
        btn_layout.add_widget(goals_btn)
        btn_layout.add_widget(progress_btn)

        # Animate buttons
        for i, btn in enumerate([tasks_btn, time_btn, goals_btn, progress_btn]):
            btn.opacity = 0
            anim = Animation(
                opacity=1,
                duration=0.4,
                t='out_cubic'
            )
            anim.start(btn)

        return btn_layout

    def create_motivation_card(self):
        """Create daily motivation card"""
        card = MCard(variant='elevated')
        card.orientation = 'vertical'
        card.size_hint_y = None
        card.height = dp(140)
        card.padding = ThemeConfig.SPACING['lg']

        # Icon
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        icon = MIcon(
            icon="lightbulb-on-outline",
            icon_size='extra_large',
            halign="center"
        )
        icon.text_color = colors['accent']
        icon.size_hint_y = None
        icon.height = dp(50)

        # Title
        title = MLabel(
            text="Daily Motivation",
            variant='h6',
            color_variant='primary',
            halign="center"
        )
        title.size_hint_y = None
        title.height = dp(35)

        # Message
        app = MDApp.get_running_app()
        try:
            message = app.get_motivational_message('motivational')
        except:
            message = "You're doing great! Keep going! 💪"

        message_label = MLabel(
            text=message,
            variant='body2',
            color_variant='secondary',
            halign="center"
        )
        message_label.size_hint_y = None
        message_label.height = dp(45)

        card.add_widget(icon)
        card.add_widget(title)
        card.add_widget(message_label)

        return card

    def rebuild_ui(self):
        """Rebuild UI (for theme changes)"""
        self.clear_widgets()
        self.build_ui()

    def on_enter(self):
        """Called when entering screen"""
        pass

    def go_to_tasks(self):
        """Navigate to tasks screen"""
        self.manager.current = 'tasks'

    def go_to_time_tracker(self):
        """Navigate to time tracker"""
        self.manager.current = 'time_tracker'

    def go_to_goals(self):
        """Navigate to goals"""
        self.manager.current = 'goals'

    def go_to_progress(self):
        """Navigate to progress"""
        self.manager.current = 'progress'

    def go_to_settings(self):
        """Navigate to settings"""
        self.manager.current = 'settings'