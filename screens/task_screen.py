"""
Enhanced Task Screen - Phase 1 & 2 (FIXED)
✅ No text wrapping issues
✅ Instant delete (no confirmation)
✅ Checkbox-style completion (click circle)
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.widget import Widget
from datetime import datetime
from kivymd.app import MDApp
from kivymd.toast import toast

# Import custom components
from widgets.components import (
    MCard, MButton, MIconButton, MLabel, MIcon,
    MTextField, MChip, MDivider, MEmptyState
)
from config.theme import ThemeConfig


class CheckboxCircle(Widget):
    """Custom checkbox circle widget"""

    def __init__(self, is_checked=False, on_toggle=None, **kwargs):
        super().__init__(**kwargs)
        self.is_checked = is_checked
        self.on_toggle_callback = on_toggle

        self.size_hint = (None, None)
        self.size = (dp(32), dp(32))

        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        """Draw the checkbox circle"""
        self.canvas.clear()

        # Get theme colors
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        with self.canvas:
            # Outer circle (border)
            if self.is_checked:
                Color(*colors['success'])
            else:
                Color(*colors['text_secondary'])

            Line(
                circle=(self.center_x, self.center_y, dp(14)),
                width=2
            )

            # Inner filled circle (when checked)
            if self.is_checked:
                Color(*colors['success'])
                Ellipse(
                    pos=(self.center_x - dp(9), self.center_y - dp(9)),
                    size=(dp(18), dp(18))
                )

                # Checkmark (white)
                Color(1, 1, 1, 1)
                # Draw checkmark using lines
                Line(
                    points=[
                        self.center_x - dp(5), self.center_y,
                        self.center_x - dp(1), self.center_y - dp(4),
                        self.center_x + dp(6), self.center_y + dp(5)
                    ],
                    width=2.5
                )

    def on_touch_down(self, touch):
        """Handle touch/click"""
        if self.collide_point(*touch.pos):
            self.is_checked = not self.is_checked
            self.update_canvas()

            # Animate scale
            anim = Animation(size=(dp(36), dp(36)), duration=0.1) + \
                   Animation(size=(dp(32), dp(32)), duration=0.1)
            anim.start(self)

            # Call callback
            if self.on_toggle_callback:
                self.on_toggle_callback(self.is_checked)

            return True
        return super().on_touch_down(touch)


class EnhancedTaskScreen(MDScreen):
    """Enhanced task management with fixed issues"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # State
        self.selected_date = None
        self.search_query = ""
        self.active_filters = {
            'status': 'all',
            'category': 'all',
            'priority': 'all',
            'duration': 'all'
        }

        # Motivational quotes
        self.motivational_quotes = [
            "Success is the sum of small efforts repeated day in and day out. 💪",
            "The secret of getting ahead is getting started. 🚀",
            "Don't watch the clock; do what it does. Keep going. ⏰",
            "The only way to do great work is to love what you do. ❤️",
            "Focus on being productive instead of busy. 🎯",
            "Small progress is still progress. Keep moving! 🌟",
        ]
        self.selected_quote = self.motivational_quotes[0]

        # Dialog references
        self.dialog = None
        self.date_picker = None
        self.quote_menu = None

        self.build_ui()

    def build_ui(self):
        """Build enhanced task screen UI"""
        layout = BoxLayout(orientation='vertical', spacing=dp(0))

        # Header
        header = self.create_header()

        # Search bar
        search_bar = self.create_search_bar()

        # Filter chips
        filter_section = self.create_filter_section()

        # Task list
        scroll = ScrollView()
        self.task_list = BoxLayout(
            orientation='vertical',
            spacing=ThemeConfig.SPACING['md'],
            padding=ThemeConfig.SPACING['md'],
            size_hint_y=None
        )
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        scroll.add_widget(self.task_list)

        # Add task button
        add_btn_container = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            padding=ThemeConfig.SPACING['md']
        )
        self.add_task_btn = MButton(
            text="+ Add New Task",
            variant='primary',
            size='large'
        )
        self.add_task_btn.bind(on_release=lambda x: self.show_add_task_dialog())
        add_btn_container.add_widget(self.add_task_btn)

        layout.add_widget(header)
        layout.add_widget(search_bar)
        layout.add_widget(filter_section)
        layout.add_widget(scroll)
        layout.add_widget(add_btn_container)

        self.add_widget(layout)

    def create_header(self):
        """Create header with back button"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=ThemeConfig.SIZING['header_height'],
            padding=[ThemeConfig.SPACING['md'], dp(8), ThemeConfig.SPACING['md'], dp(8)]
        )

        back_btn = MIconButton(
            icon="arrow-left",
            icon_size='large',
            pos_hint={"center_y": 0.5}
        )
        back_btn.bind(on_release=lambda x: self.go_back())

        title_box = BoxLayout(orientation='vertical', size_hint_x=0.7)

        title = MLabel(
            text="My Tasks",
            variant='h5',
            color_variant='primary'
        )
        title.size_hint_y = None
        title.height = dp(35)

        subtitle = MLabel(
            text="Organized & Scheduled",
            variant='caption',
            color_variant='secondary'
        )
        subtitle.size_hint_y = None
        subtitle.height = dp(25)

        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        # Calendar button
        calendar_btn = MIconButton(
            icon="calendar",
            icon_size='large',
            pos_hint={"center_y": 0.5}
        )
        calendar_btn.bind(on_release=lambda x: self.show_date_picker())

        header.add_widget(back_btn)
        header.add_widget(title_box)
        header.add_widget(calendar_btn)

        return header

    def create_search_bar(self):
        """Create search bar"""
        container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            padding=[ThemeConfig.SPACING['md'], dp(8), ThemeConfig.SPACING['md'], dp(8)],
            spacing=ThemeConfig.SPACING['sm']
        )

        self.search_field = MTextField()
        self.search_field.hint_text = "Search tasks..."
        self.search_field.bind(text=self.on_search_text_change)

        search_btn = MIconButton(
            icon="magnify",
            icon_size='medium'
        )
        search_btn.bind(on_release=lambda x: self.apply_filters())

        container.add_widget(self.search_field)
        container.add_widget(search_btn)

        return container

    def create_filter_section(self):
        """Create filter chips section"""
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=[ThemeConfig.SPACING['md'], 0, ThemeConfig.SPACING['md'], dp(8)],
            spacing=ThemeConfig.SPACING['sm']
        )

        label = MLabel(
            text="Filters:",
            variant='caption',
            color_variant='secondary'
        )
        label.size_hint_y = None
        label.height = dp(20)

        # Filter chips in horizontal scroll
        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(
            size_hint_y=None,
            height=dp(40),
            do_scroll_x=True,
            do_scroll_y=False
        )

        chips_container = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=ThemeConfig.SPACING['sm']
        )
        chips_container.bind(minimum_width=chips_container.setter('width'))

        # Status filters
        status_filters = ['All', 'Pending', 'Completed']
        for status in status_filters:
            chip = MChip(
                text=status,
                color='primary' if self.active_filters['status'] == status.lower() else 'bg_secondary'
            )
            chip.bind(on_touch_down=lambda instance, touch, s=status: self.filter_by_status(s) if instance.collide_point(*touch.pos) else None)
            chips_container.add_widget(chip)

        # Duration filters
        duration_filters = ['Today', 'Week', 'Month']
        for duration in duration_filters:
            chip = MChip(
                text=duration,
                color='secondary' if self.active_filters['duration'] == duration.lower() else 'bg_secondary'
            )
            chip.bind(on_touch_down=lambda instance, touch, d=duration: self.filter_by_duration(d) if instance.collide_point(*touch.pos) else None)
            chips_container.add_widget(chip)

        scroll.add_widget(chips_container)

        container.add_widget(label)
        container.add_widget(scroll)

        return container

    def on_search_text_change(self, instance, value):
        """Handle search text change"""
        self.search_query = value.lower()
        self.apply_filters()

    def filter_by_status(self, status):
        """Filter by task status"""
        self.active_filters['status'] = status.lower()
        toast(f"Filter: {status}")
        self.apply_filters()

    def filter_by_duration(self, duration):
        """Filter by duration"""
        self.active_filters['duration'] = duration.lower()
        toast(f"Duration: {duration}")
        self.apply_filters()

    def apply_filters(self):
        """Apply all active filters"""
        app = MDApp.get_running_app()

        # Get tasks based on filters
        status = self.active_filters['status'] if self.active_filters['status'] != 'all' else None
        duration = self.active_filters['duration'] if self.active_filters['duration'] != 'all' else None

        tasks = app.db_manager.get_all_tasks(status=status, duration_filter=duration)

        # Apply search filter
        if self.search_query:
            tasks = [t for t in tasks if self.search_query in t[1].lower() or (t[2] and self.search_query in t[2].lower())]

        # Apply date filter
        if self.selected_date:
            tasks = [t for t in tasks if t[15][:10] == self.selected_date]  # created_at date

        self.display_tasks(tasks)

    def display_tasks(self, tasks):
        """Display filtered tasks"""
        self.task_list.clear_widgets()

        if not tasks:
            empty_state = MEmptyState(
                icon="calendar-clock",
                title="No Tasks Found",
                subtitle="Try adjusting your filters or\ncreate a new task!"
            )
            self.task_list.add_widget(empty_state)
            return

        for task in tasks:
            task_id = task[0]
            title = task[1]
            desc = task[2] if task[2] else ""
            category = task[3]
            priority = task[4]
            status = task[5]
            start_time = task[6]
            end_time = task[7] if task[7] else None
            duration_type = task[8]
            motivational_quote = task[10] if len(task) > 10 and task[10] else ""

            task_card = self.create_task_card(
                task_id, title, desc, category, priority, status,
                start_time, end_time, duration_type, motivational_quote
            )
            self.task_list.add_widget(task_card)

            # Animate card appearance
            task_card.opacity = 0
            anim = Animation(opacity=1, duration=0.3, t='out_cubic')
            anim.start(task_card)

    def create_task_card(self, task_id, title, desc, category, priority, status,
                         start_time, end_time, duration_type, motivational_quote):
        """Create enhanced task card with checkbox and instant delete"""
        app = MDApp.get_running_app()
        theme_mode = app.theme_cls.theme_style
        colors = ThemeConfig.get_theme_colors(theme_mode)

        card = MCard(variant='elevated')
        card.orientation = 'vertical'
        card.size_hint_y = None
        card.height = dp(200) if motivational_quote else dp(160)
        card.padding = ThemeConfig.SPACING['md']
        card.spacing = ThemeConfig.SPACING['sm']

        # Top row: checkbox, title, delete
        top_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=ThemeConfig.SPACING['sm']
        )

        # ✅ FIXED: Checkbox circle for completion
        checkbox = CheckboxCircle(
            is_checked=(status == 'completed'),
            on_toggle=lambda checked: self.toggle_task_completion(task_id, checked)
        )
        checkbox.size_hint_x = None
        checkbox.width = dp(40)

        # ✅ FIXED: Title with text_size to prevent wrapping
        title_label = MLabel(
            text=title,
            variant='h6',
            color_variant='primary'
        )
        title_label.size_hint_x = 0.55
        title_label.text_size = (None, None)  # Prevent text wrapping
        title_label.shorten = True  # Enable ellipsis
        title_label.shorten_from = 'right'

        # ✅ FIXED: Instant delete (no confirmation)
        delete_btn = MIconButton(
            icon="delete-outline",
            icon_size='medium'
        )
        delete_btn.size_hint_x = None
        delete_btn.width = dp(40)
        delete_btn.bind(on_release=lambda x: self.delete_task_instant(task_id))

        top_row.add_widget(checkbox)
        top_row.add_widget(title_label)
        top_row.add_widget(delete_btn)

        # Description (if exists)
        if desc:
            desc_label = MLabel(
                text=desc[:80] + "..." if len(desc) > 80 else desc,
                variant='body2',
                color_variant='secondary'
            )
            desc_label.size_hint_y = None
            desc_label.height = dp(35)
            desc_label.text_size = (None, None)
            desc_label.shorten = True
            desc_label.shorten_from = 'right'
        else:
            desc_label = BoxLayout(size_hint_y=None, height=dp(5))

        # ✅ FIXED: Time row with proper text handling
        time_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=ThemeConfig.SPACING['sm']
        )

        time_icon = MIcon(
            icon="clock-time-four",
            icon_size='small'
        )
        time_icon.size_hint_x = None
        time_icon.width = dp(25)

        time_text = f"{start_time}"
        if end_time:
            time_text += f" - {end_time}"
        time_text += f"  •  {duration_type}"

        time_label = MLabel(
            text=time_text,
            variant='caption',
            color_variant='secondary'
        )
        time_label.text_size = (None, None)
        time_label.shorten = True
        time_label.shorten_from = 'right'

        time_row.add_widget(time_icon)
        time_row.add_widget(time_label)

        # Motivational quote (if exists)
        if motivational_quote:
            quote_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=ThemeConfig.SPACING['sm']
            )

            quote_icon = MIcon(
                icon="format-quote-open",
                icon_size='small'
            )
            quote_icon.text_color = colors['accent']
            quote_icon.size_hint_x = None
            quote_icon.width = dp(25)

            quote_label = MLabel(
                text=motivational_quote[:70] + "..." if len(motivational_quote) > 70 else motivational_quote,
                variant='caption',
                color_variant='secondary'
            )
            quote_label.italic = True
            quote_label.text_size = (None, None)
            quote_label.shorten = True
            quote_label.shorten_from = 'right'

            quote_row.add_widget(quote_icon)
            quote_row.add_widget(quote_label)

        # Bottom row: chips
        bottom_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(36),
            spacing=ThemeConfig.SPACING['sm']
        )

        # Category chip
        category_chip = MChip(
            text=f"{category[:8]}",  # Limit length
            color='category_' + category
        )

        # Priority chip
        priority_chip = MChip(
            text=f"⭐ {priority[:3]}",  # Limit length
            color='priority_' + priority
        )

        bottom_row.add_widget(category_chip)
        bottom_row.add_widget(priority_chip)

        # Add all to card
        card.add_widget(top_row)
        card.add_widget(desc_label)
        card.add_widget(time_row)
        if motivational_quote:
            card.add_widget(quote_row)
        card.add_widget(bottom_row)

        return card

    def toggle_task_completion(self, task_id, is_checked):
        """Toggle task completion (instant)"""
        app = MDApp.get_running_app()
        new_status = 'completed' if is_checked else 'pending'
        app.db_manager.update_task_status(task_id, new_status)

        if is_checked:
            toast("✓ Task completed! 🎉")
        else:
            toast("Task marked as pending")

        # Refresh list
        self.apply_filters()

    def delete_task_instant(self, task_id):
        """Delete task instantly (no confirmation)"""
        app = MDApp.get_running_app()
        app.db_manager.delete_task(task_id)

        toast("Task deleted")

        # Refresh list
        self.apply_filters()

    def show_date_picker(self):
        """Show calendar date picker"""
        self.date_picker = MDDatePicker()
        self.date_picker.bind(on_save=self.on_date_selected)
        self.date_picker.open()

    def on_date_selected(self, instance, value, date_range):
        """Handle date selection"""
        self.selected_date = str(value)
        toast(f"Filter by date: {value}")
        self.apply_filters()

    def show_add_task_dialog(self):
        """Show add task dialog"""
        content = BoxLayout(
            orientation='vertical',
            spacing=ThemeConfig.SPACING['md'],
            padding=ThemeConfig.SPACING['sm'],
            size_hint_y=None,
            height=dp(450)
        )

        # Title
        self.title_field = MTextField()
        self.title_field.hint_text = "Task Title *"

        # Description
        self.desc_field = MTextField()
        self.desc_field.hint_text = "Description (optional)"
        self.desc_field.multiline = True

        # Start time
        time_label = MLabel(
            text="⏰ Start Time (Required)",
            variant='caption',
            color_variant='primary'
        )
        time_label.size_hint_y = None
        time_label.height = dp(25)

        self.start_time_field = MTextField()
        self.start_time_field.hint_text = "HH:MM (e.g., 09:00)"
        self.start_time_field.text = datetime.now().strftime("%H:%M")

        # End time
        self.end_time_field = MTextField()
        self.end_time_field.hint_text = "End Time (optional)"

        # Quote
        quote_label = MLabel(
            text="💬 Motivational Quote",
            variant='caption',
            color_variant='primary'
        )
        quote_label.size_hint_y = None
        quote_label.height = dp(25)

        self.quote_field = MTextField()
        self.quote_field.text = self.selected_quote
        self.quote_field.multiline = True

        # Add all to content
        content.add_widget(self.title_field)
        content.add_widget(self.desc_field)
        content.add_widget(time_label)
        content.add_widget(self.start_time_field)
        content.add_widget(self.end_time_field)
        content.add_widget(quote_label)
        content.add_widget(self.quote_field)

        self.dialog = MDDialog(
            title="✨ Add New Task",
            type="custom",
            content_cls=content,
            buttons=[
                MButton(
                    text="Cancel",
                    variant='error',
                    size='medium'
                ),
                MButton(
                    text="Add Task",
                    variant='primary',
                    size='medium'
                )
            ]
        )

        self.dialog.buttons[0].bind(on_release=lambda x: self.dialog.dismiss())
        self.dialog.buttons[1].bind(on_release=lambda x: self.add_task())

        self.dialog.open()

    def add_task(self):
        """Add new task"""
        if not self.title_field.text.strip():
            toast("⚠️ Task title is required!")
            return

        if not self.start_time_field.text:
            toast("⚠️ Start time is required!")
            return

        # Validate time format
        try:
            start_time = self.start_time_field.text
            hour, minute = start_time.split(':')
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                raise ValueError
        except:
            toast("⚠️ Invalid time format! Use HH:MM")
            return

        # Add to database
        app = MDApp.get_running_app()
        try:
            app.db_manager.add_task(
                title=self.title_field.text,
                description=self.desc_field.text,
                category='work',
                priority='medium',
                start_time=self.start_time_field.text,
                end_time=self.end_time_field.text if self.end_time_field.text else None,
                duration_type='today',
                motivational_quote=self.quote_field.text,
                reminder_enabled=True,
                reminder_interval=30
            )

            self.dialog.dismiss()
            self.load_tasks()
            toast("✓ Task added successfully!")

        except Exception as e:
            print(f"❌ Error adding task: {e}")
            toast(f"⚠️ Error: {str(e)}")

    def load_tasks(self):
        """Load and display tasks"""
        self.apply_filters()

    def rebuild_ui(self):
        """Rebuild UI for theme changes"""
        self.clear_widgets()
        self.build_ui()
        self.load_tasks()

    def on_enter(self):
        """Called when entering screen"""
        self.load_tasks()

    def go_back(self):
        """Navigate back"""
        self.manager.current = 'home'