"""
Enhanced Task Screen (FULLY FIXED)
✅ NO MDChip (replaced with MDFlatButton)
✅ NO MDSwitch (replaced with MDCheckbox)
✅ Complete error handling
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import datetime, timedelta


class EnhancedTaskScreen(MDScreen):
    """Enhanced task management - FULLY COMPATIBLE"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.duration_type = 'today'
        self.motivational_quotes = [
            "Success is the sum of small efforts repeated day in and day out. 💪",
            "The secret of getting ahead is getting started. 🚀",
            "Don't watch the clock; do what it does. Keep going. ⏰",
            "The only way to do great work is to love what you do. ❤️",
            "Focus on being productive instead of busy. 🎯",
            "Small progress is still progress. Keep moving! 🌟",
            "You are capable of amazing things! 💫",
            "Believe you can and you're halfway there. ⭐",
            "Your limitation—it's only your imagination. 🌈",
            "Push yourself, because no one else is going to do it. 💯"
        ]
        self.selected_quote = self.motivational_quotes[0]
        self.build_ui()

    def build_ui(self):
        """Build enhanced task screen UI"""
        layout = BoxLayout(orientation='vertical', spacing=dp(12))

        # Header with back button
        header = self.create_header()

        # Duration filter buttons (NO CHIPS)
        filter_section = self.create_duration_filters()

        # Task list with scroll
        scroll = ScrollView()
        self.task_list = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None
        )
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        scroll.add_widget(self.task_list)

        # Add task button
        add_btn_container = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(16))
        self.add_task_btn = MDFillRoundFlatIconButton(
            icon="plus",
            text="Add New Task",
            font_size="16sp",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.2, 0.6, 0.9, 1),
            on_release=lambda x: self.show_add_task_dialog()
        )
        add_btn_container.add_widget(self.add_task_btn)

        layout.add_widget(header)
        layout.add_widget(filter_section)
        layout.add_widget(scroll)
        layout.add_widget(add_btn_container)

        self.add_widget(layout)

    def create_header(self):
        """Create header with back button"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            padding=[dp(16), dp(8), dp(16), dp(8)]
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"center_y": 0.5},
            icon_size="28sp",
            on_release=lambda x: self.go_back()
        )

        title_box = BoxLayout(orientation='vertical', size_hint_x=0.7)
        title = MDLabel(
            text="My Tasks",
            font_style="H5",
            bold=True
        )
        subtitle = MDLabel(
            text="Scheduled & Organized",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(back_btn)
        header.add_widget(title_box)

        return header

    def create_duration_filters(self):
        """✅ FIX #2: Using MDFlatButton instead of MDChip"""
        filter_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=[dp(16), 0, dp(16), 0],
            spacing=dp(8)
        )

        title = MDLabel(
            text="Filter by Duration:",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )

        buttons_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        filters = [
            ('All', None),
            ('Today', 'today'),
            ('Week', 'week'),
            ('Month', 'month')
        ]

        for filter_name, filter_value in filters:
            btn = MDFlatButton(
                text=filter_name,
                size_hint_x=0.25,
                on_release=lambda x, f=filter_value, n=filter_name: self.apply_filter(f, n)
            )
            buttons_box.add_widget(btn)

        filter_container.add_widget(title)
        filter_container.add_widget(buttons_box)

        return filter_container

    def apply_filter(self, filter_value, filter_name):
        """Apply duration filter to task list"""
        from kivymd.toast import toast
        toast(f"Showing: {filter_name}")
        self.load_tasks(duration_filter=filter_value)

    def on_enter(self):
        """Called when screen is entered"""
        self.load_tasks()

    def load_tasks(self, duration_filter=None):
        """Load tasks from database with error handling"""
        self.task_list.clear_widgets()

        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            tasks = app.db_manager.get_all_tasks(duration_filter=duration_filter)

            if not tasks:
                empty_card = self.create_empty_state()
                self.task_list.add_widget(empty_card)
                return

            for task in tasks:
                task_id = task[0]
                title = task[1]
                desc = task[2]
                category = task[3]
                priority = task[4]
                status = task[5]
                start_time = task[6]
                end_time = task[7]
                duration_type = task[8]
                motivational_quote = task[10] if len(task) > 10 else ""

                task_card = self.create_task_card(
                    task_id, title, desc, category, priority, status,
                    start_time, end_time, duration_type, motivational_quote
                )
                self.task_list.add_widget(task_card)
        except Exception as e:
            print(f"❌ Error loading tasks: {e}")
            import traceback
            traceback.print_exc()
            from kivymd.toast import toast
            toast("Error loading tasks")

    def create_empty_state(self):
        """Create empty state card"""
        card = MDCard(
            orientation='vertical',
            padding=dp(40),
            size_hint_y=None,
            height=dp(250),
            elevation=0
        )

        icon = MDIcon(
            icon="calendar-clock",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="center",
            font_size="80sp"
        )

        title = MDLabel(
            text="No Tasks Scheduled",
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        )

        subtitle = MDLabel(
            text="Create your first task with\nstart time and get organized!",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )

        card.add_widget(icon)
        card.add_widget(title)
        card.add_widget(subtitle)

        return card

    def create_task_card(self, task_id, title, desc, category, priority, status,
                         start_time, end_time, duration_type, motivational_quote):
        """✅ FIX #2: NO MDChip - using labels instead"""
        card = MDCard(
            orientation='vertical',
            padding=dp(16),
            size_hint_y=None,
            height=dp(200) if motivational_quote else dp(160),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        # Top row: status icon, title, delete
        top_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(35), spacing=dp(12))

        if status == 'completed':
            status_icon = MDIcon(
                icon="check-circle",
                theme_text_color="Custom",
                text_color=(0.2, 0.7, 0.3, 1),
                size_hint_x=None,
                width=dp(30)
            )
        else:
            status_icon = MDIcon(
                icon="clock-outline",
                theme_text_color="Custom",
                text_color=(0.2, 0.6, 0.9, 1),
                size_hint_x=None,
                width=dp(30)
            )

        title_label = MDLabel(
            text=title,
            font_style="Subtitle1",
            bold=True,
            size_hint_x=0.6
        )

        delete_btn = MDIconButton(
            icon="delete-outline",
            theme_text_color="Secondary",
            icon_size="24sp",
            size_hint_x=None,
            width=dp(40),
            on_release=lambda x: self.confirm_delete(task_id)
        )

        top_row.add_widget(status_icon)
        top_row.add_widget(title_label)
        top_row.add_widget(delete_btn)

        # Time row
        time_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(8))

        time_icon = MDIcon(
            icon="clock-time-four",
            size_hint_x=None,
            width=dp(20),
            theme_text_color="Secondary",
            font_size="20sp"
        )

        time_text = f"⏰ {start_time}"
        if end_time:
            time_text += f" - {end_time}"
        time_text += f"  •  {duration_type.capitalize()}"

        time_label = MDLabel(
            text=time_text,
            font_style="Caption",
            theme_text_color="Secondary"
        )

        time_row.add_widget(time_icon)
        time_row.add_widget(time_label)

        # Motivational quote row
        if motivational_quote:
            quote_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(45), spacing=dp(8))

            quote_icon = MDIcon(
                icon="format-quote-open",
                size_hint_x=None,
                width=dp(20),
                theme_text_color="Custom",
                text_color=(0.9, 0.6, 0.2, 1),
                font_size="20sp"
            )

            quote_label = MDLabel(
                text=motivational_quote[:80] + "..." if len(motivational_quote) > 80 else motivational_quote,
                font_style="Caption",
                italic=True,
                theme_text_color="Custom",
                text_color=(0.9, 0.6, 0.2, 1)
            )

            quote_row.add_widget(quote_icon)
            quote_row.add_widget(quote_label)

        # Bottom row: Using LABELS instead of chips
        bottom_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(8))

        category_label = MDLabel(
            text=f"📁 {category.capitalize()}",
            font_style="Caption",
            size_hint_x=0.3
        )

        priority_label = MDLabel(
            text=f"⭐ {priority.capitalize()}",
            font_style="Caption",
            size_hint_x=0.3
        )

        if status == 'pending':
            complete_btn = MDFlatButton(
                text="✓ Complete",
                theme_text_color="Custom",
                text_color=(0.2, 0.7, 0.3, 1),
                on_release=lambda x: self.complete_task(task_id)
            )
        else:
            complete_btn = MDLabel(
                text="✓ Completed",
                font_style="Caption",
                theme_text_color="Custom",
                text_color=(0.2, 0.7, 0.3, 1),
                halign="right"
            )

        bottom_row.add_widget(category_label)
        bottom_row.add_widget(priority_label)
        bottom_row.add_widget(complete_btn)

        # Add all to card
        card.add_widget(top_row)
        card.add_widget(time_row)
        if motivational_quote:
            card.add_widget(quote_row)
        card.add_widget(bottom_row)

        return card

    def show_add_task_dialog(self):
        """✅ FIX #3: Using MDCheckbox instead of MDSwitch"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(10),
            size_hint_y=None,
            height=dp(480)
        )

        # Title field
        self.title_field = MDTextField(
            hint_text="Task Title *",
            required=True,
            mode="rectangle"
        )

        # Description field
        self.desc_field = MDTextField(
            hint_text="Description (optional)",
            multiline=True,
            mode="rectangle"
        )

        # Start Time
        time_label = MDLabel(
            text="⏰ Start Time (Required)",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
            bold=True
        )

        self.start_time_field = MDTextField(
            hint_text="HH:MM (e.g., 09:00)",
            required=True,
            mode="rectangle",
            text=datetime.now().strftime("%H:%M")
        )

        # End Time
        self.end_time_field = MDTextField(
            hint_text="End Time (optional, e.g., 10:30)",
            mode="rectangle"
        )

        # Duration Type
        duration_label = MDLabel(
            text="📅 Duration",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
            bold=True
        )

        duration_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8)
        )

        durations = ['Today', 'Week', 'Month', 'Custom']
        for dur in durations:
            btn = MDFlatButton(
                text=dur,
                size_hint_x=0.25,
                on_release=lambda x, d=dur.lower(): self.select_duration(d)
            )
            duration_buttons.add_widget(btn)

        # Custom date field
        self.custom_date_field = MDTextField(
            hint_text="Custom End Date (YYYY-MM-DD)",
            mode="rectangle",
            disabled=True
        )

        # Motivational Quote
        quote_label = MDLabel(
            text="💬 Motivational Quote",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20),
            bold=True
        )

        self.quote_field = MDTextField(
            text=self.selected_quote,
            multiline=True,
            mode="rectangle",
            on_focus=lambda instance, value: self.show_quote_menu(instance) if value else None
        )

        # ✅ FIX #3: Using MDCheckbox instead of MDSwitch
        reminder_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(12)
        )

        reminder_label = MDLabel(
            text="🔔 Enable Reminders",
            font_style="Body2",
            size_hint_x=0.7
        )

        self.reminder_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            active=True
        )

        reminder_row.add_widget(reminder_label)
        reminder_row.add_widget(self.reminder_checkbox)

        # Reminder Interval
        self.reminder_interval_field = MDTextField(
            hint_text="Reminder Interval (minutes, e.g., 30)",
            mode="rectangle",
            text="30"
        )

        # Add all to content
        content.add_widget(self.title_field)
        content.add_widget(self.desc_field)
        content.add_widget(time_label)
        content.add_widget(self.start_time_field)
        content.add_widget(self.end_time_field)
        content.add_widget(duration_label)
        content.add_widget(duration_buttons)
        content.add_widget(self.custom_date_field)
        content.add_widget(quote_label)
        content.add_widget(self.quote_field)
        content.add_widget(reminder_row)
        content.add_widget(self.reminder_interval_field)

        self.dialog = MDDialog(
            title="✨ Add New Task",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0.5, 0.5, 0.5, 1),
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD TASK",
                    md_bg_color=(0.2, 0.6, 0.9, 1),
                    on_release=lambda x: self.add_task()
                )
            ]
        )
        self.dialog.open()

    def select_duration(self, duration):
        """Handle duration selection"""
        self.duration_type = duration

        if duration == 'custom':
            self.custom_date_field.disabled = False
        else:
            self.custom_date_field.disabled = True
            self.custom_date_field.text = ""

        from kivymd.toast import toast
        toast(f"Duration: {duration.capitalize()}")

    def show_quote_menu(self, text_field):
        """Show menu to select motivational quote"""
        menu_items = [
            {
                "text": quote[:50] + "...",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=quote: self.select_quote(x, text_field)
            }
            for quote in self.motivational_quotes
        ]

        self.quote_menu = MDDropdownMenu(
            caller=text_field,
            items=menu_items,
            width_mult=4
        )
        self.quote_menu.open()

    def select_quote(self, quote, text_field):
        """Select a motivational quote"""
        self.selected_quote = quote
        text_field.text = quote
        self.quote_menu.dismiss()

    def add_task(self):
        """Add task with all scheduling information"""
        # Validation
        if not self.title_field.text.strip():
            from kivymd.toast import toast
            toast("⚠️ Task title is required!")
            return

        if not self.start_time_field.text:
            from kivymd.toast import toast
            toast("⚠️ Start time is required!")
            return

        # Validate time format
        try:
            start_time = self.start_time_field.text
            hour, minute = start_time.split(':')
            if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                raise ValueError
        except:
            from kivymd.toast import toast
            toast("⚠️ Invalid start time format! Use HH:MM")
            return

        # Get custom end date
        custom_end_date = None
        if self.duration_type == 'custom' and self.custom_date_field.text:
            custom_end_date = self.custom_date_field.text

        # Get reminder interval
        try:
            reminder_interval = int(self.reminder_interval_field.text)
        except:
            reminder_interval = 30

        # Add to database
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        try:
            app.db_manager.add_task(
                title=self.title_field.text,
                description=self.desc_field.text,
                category='work',
                priority='medium',
                start_time=self.start_time_field.text,
                end_time=self.end_time_field.text if self.end_time_field.text else None,
                duration_type=self.duration_type,
                custom_end_date=custom_end_date,
                motivational_quote=self.quote_field.text,
                reminder_enabled=self.reminder_checkbox.active,
                reminder_interval=reminder_interval
            )

            self.dialog.dismiss()
            self.load_tasks()

            from kivymd.toast import toast
            toast("✓ Task added successfully!")

        except Exception as e:
            print(f"❌ Error adding task: {e}")
            import traceback
            traceback.print_exc()
            from kivymd.toast import toast
            toast(f"⚠️ Error: {str(e)}")

    def complete_task(self, task_id):
        """Mark task as completed"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            app.db_manager.update_task_status(task_id, 'completed')
            self.load_tasks()

            from kivymd.toast import toast
            toast("✓ Task completed! Great job! 🎉")
        except Exception as e:
            print(f"❌ Error completing task: {e}")

    def confirm_delete(self, task_id):
        """Confirm before deleting"""
        self.dialog = MDDialog(
            title="Delete Task?",
            text="This action cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.delete_task(task_id)
                )
            ]
        )
        self.dialog.open()

    def delete_task(self, task_id):
        """Delete a task"""
        try:
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            app.db_manager.delete_task(task_id)
            self.dialog.dismiss()
            self.load_tasks()

            from kivymd.toast import toast
            toast("✓ Task deleted")
        except Exception as e:
            print(f"❌ Error deleting task: {e}")

    def go_back(self):
        """Navigate back to home"""
        self.manager.current = 'home'