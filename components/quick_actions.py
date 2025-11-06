from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.tooltip import MDTooltip
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp
from utils.constants import Colors


class TooltipIconButton(MDIconButton, MDTooltip):
    """Icon button with tooltip"""
    pass


class QuickActionsBar(MDBoxLayout):
    """Quick actions bar with common task operations"""

    def __init__(self, callbacks=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.height = dp(60)
        self.width = dp(280)
        self.spacing = dp(8)
        self.padding = [dp(12), dp(8)]

        self.callbacks = callbacks or {}
        self.is_visible = True

        # Background
        with self.canvas.before:
            self.bg_color = Color(*Colors.LIGHT_CARD)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(30)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)
        self.build_actions()
        self.update_theme_colors()

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_theme_colors(self):
        """Update colors based on theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls:
            is_dark = app.theme_cls.theme_style == "Dark"
            self.bg_color.rgba = Colors.DARK_CARD if is_dark else Colors.LIGHT_CARD

    def build_actions(self):
        """Build quick action buttons"""
        actions = [
            {
                'icon': 'plus',
                'tooltip': 'Add Task',
                'callback': 'add_task',
                'color': Colors.SUCCESS_GREEN
            },
            {
                'icon': 'magnify',
                'tooltip': 'Search',
                'callback': 'search',
                'color': Colors.PRIMARY_BLUE
            },
            {
                'icon': 'sort',
                'tooltip': 'Sort',
                'callback': 'sort',
                'color': (0.5, 0.5, 0.5, 1)
            },
            {
                'icon': 'filter',
                'tooltip': 'Filter',
                'callback': 'filter',
                'color': (0.5, 0.5, 0.5, 1)
            }
        ]

        for action in actions:
            btn = TooltipIconButton(
                icon=action['icon'],
                theme_text_color="Custom",
                text_color=action['color'],
                tooltip_text=action['tooltip'],
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=lambda x, cb=action['callback']: self._on_action(cb)
            )
            self.add_widget(btn)

    def _on_action(self, action_name):
        """Handle action button press"""
        if action_name in self.callbacks:
            self.callbacks[action_name]()

    def show(self):
        """Animate showing the bar"""
        if not self.is_visible:
            self.opacity = 0
            self.is_visible = True
            anim = Animation(opacity=1, duration=0.2)
            anim.start(self)

    def hide(self):
        """Animate hiding the bar"""
        if self.is_visible:
            self.is_visible = False
            anim = Animation(opacity=0, duration=0.2)
            anim.start(self)


class QuickActionsMenu(MDBoxLayout):
    """Floating quick actions menu (FAB style)"""

    def __init__(self, callbacks=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.spacing = dp(12)
        self.padding = dp(8)

        self.callbacks = callbacks or {}
        self.is_expanded = False

        # Calculate size dynamically
        self.width = dp(56)
        self.height = dp(56)

        self.build_menu()

    def build_menu(self):
        """Build floating action menu"""
        # Container for action buttons
        self.actions_container = MDBoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            width=dp(56),
            spacing=dp(12),
            opacity=0
        )
        self.actions_container.bind(minimum_height=self.actions_container.setter('height'))

        # Quick action buttons
        actions = [
            {'icon': 'clock-fast', 'tooltip': 'Quick Task', 'callback': 'quick_task'},
            {'icon': 'calendar-check', 'tooltip': 'Add Scheduled', 'callback': 'scheduled_task'},
            {'icon': 'repeat', 'tooltip': 'Recurring Task', 'callback': 'recurring_task'},
        ]

        for action in actions:
            btn = TooltipIconButton(
                icon=action['icon'],
                md_bg_color=Colors.PRIMARY_BLUE,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                tooltip_text=action['tooltip'],
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=lambda x, cb=action['callback']: self._on_action(cb)
            )
            self.actions_container.add_widget(btn)

        self.add_widget(self.actions_container)

        # Main FAB button
        self.fab_btn = MDIconButton(
            icon='plus',
            md_bg_color=Colors.SUCCESS_GREEN,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            on_release=self.toggle_menu
        )
        self.add_widget(self.fab_btn)

    def toggle_menu(self, *args):
        """Toggle menu expansion"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Expand menu to show actions"""
        if not self.is_expanded:
            self.is_expanded = True

            # Animate actions appearing
            self.actions_container.opacity = 0
            anim = Animation(opacity=1, duration=0.2)
            anim.start(self.actions_container)

            # Rotate FAB icon
            anim_fab = Animation(rotation=45, duration=0.2)
            anim_fab.start(self.fab_btn)

    def collapse(self):
        """Collapse menu to hide actions"""
        if self.is_expanded:
            self.is_expanded = False

            # Animate actions disappearing
            anim = Animation(opacity=0, duration=0.2)
            anim.start(self.actions_container)

            # Rotate FAB icon back
            anim_fab = Animation(rotation=0, duration=0.2)
            anim_fab.start(self.fab_btn)

    def _on_action(self, action_name):
        """Handle action button press"""
        if action_name in self.callbacks:
            self.callbacks[action_name]()
        self.collapse()


class TaskContextMenu(MDBoxLayout):
    """Context menu for task long-press actions"""

    def __init__(self, task_id, callbacks=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)
        self.width = dp(200)
        self.spacing = dp(4)
        self.padding = dp(8)

        self.task_id = task_id
        self.callbacks = callbacks or {}

        # Background
        with self.canvas.before:
            self.bg_color = Color(*Colors.LIGHT_CARD)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(minimum_height=self.setter('height'))

        self.build_menu_items()
        self.update_theme_colors()

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_theme_colors(self):
        """Update colors based on theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls:
            is_dark = app.theme_cls.theme_style == "Dark"
            self.bg_color.rgba = Colors.DARK_CARD if is_dark else Colors.LIGHT_CARD

    def build_menu_items(self):
        """Build context menu items"""
        from kivymd.uix.button import MDFlatButton

        menu_items = [
            {'icon': 'pencil', 'text': 'Edit', 'callback': 'edit'},
            {'icon': 'content-duplicate', 'text': 'Duplicate', 'callback': 'duplicate'},
            {'icon': 'share', 'text': 'Share', 'callback': 'share'},
            {'icon': 'clock-outline', 'text': 'Reschedule', 'callback': 'reschedule'},
            {'icon': 'delete', 'text': 'Delete', 'callback': 'delete', 'color': Colors.DANGER_RED},
        ]

        for item in menu_items:
            btn = MDFlatButton(
                text=f"  {item['text']}",
                icon=item['icon'],
                size_hint_y=None,
                height=dp(40),
                on_release=lambda x, cb=item['callback']: self._on_action(cb)
            )

            if 'color' in item:
                btn.text_color = item['color']

            self.add_widget(btn)

    def _on_action(self, action_name):
        """Handle menu action"""
        if action_name in self.callbacks:
            self.callbacks[action_name](self.task_id)