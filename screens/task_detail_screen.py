from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import MDList, TwoLineListItem, TwoLineIconListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.toast import toast
from components.dialogs import AddTaskDialog, TimePickerDialog, RecurrenceDialog
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from database.db_manager import DatabaseManager
from utils.helpers import format_date
from utils.constants import Colors, TIME_FORMAT
from datetime import datetime, timedelta


class TaskDetailScreen(MDScreen):
    def __init__(self, task_id, on_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.on_back_callback = on_back_callback
        self.db = DatabaseManager()
        self.task = None
        self.toolbar = None
        self._theme_bound = False
        self._theme_update_scheduled = False

        self.build_ui()
        self.load_task_data()

        # Listen for theme changes
        app = MDApp.get_running_app()
        if app:
            app.theme_cls.bind(theme_style=self.on_theme_change)
            self._theme_bound = True

    def on_pre_leave(self):
        """Unbind theme when leaving screen - CRITICAL for preventing leaks"""
        if self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.unbind(theme_style=self.on_theme_change)
                self._theme_bound = False
            print("🔓 TaskDetailScreen: Theme unbound")

    def on_pre_enter(self):
        """Re-bind theme when entering screen"""
        if not self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.bind(theme_style=self.on_theme_change)
                self._theme_bound = True
            print("🔒 TaskDetailScreen: Theme bound")

    def update_toolbar_colors(self):
        """Update toolbar icon colors based on theme"""
        if not self.toolbar:
            return

        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            self.toolbar.specific_text_color = Colors.LIGHT_TEXT
        else:
            self.toolbar.specific_text_color = Colors.DARK_TEXT

    def on_theme_change(self, instance, value):
        """Called when theme changes - BATCHED"""
        if self._theme_update_scheduled:
            return

        self._theme_update_scheduled = True
        Clock.schedule_once(self._apply_theme_update, 0)

    def _apply_theme_update(self, dt):
        """Apply theme update in batch"""
        self._theme_update_scheduled = False

        if self.toolbar:
            self.toolbar.md_bg_color = self.get_toolbar_color()
            self.update_toolbar_colors()
            # Rebuild toolbar items
            self.toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
            self.toolbar.right_action_items = [["delete", lambda x: self.delete_task()]]

    def get_toolbar_color(self):
        """Get toolbar color based on current theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return Colors.DARK_BG
        return Colors.LIGHT_BG

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # Toolbar
        self.toolbar = MDTopAppBar(
            title="Task Details",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["delete", lambda x: self.delete_task()]],
            elevation=2,
            md_bg_color=self.get_toolbar_color()
        )
        self.update_toolbar_colors()
        layout.add_widget(self.toolbar)

        # Scrollable content
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Title field in card
        title_card = MDCard(
            orientation='vertical',
            padding=dp(12),
            size_hint_y=None,
            height=dp(80),
            elevation=2,
            radius=[dp(12)]
        )

        self.title_field = MDTextField(
            hint_text="Task title",
            mode="fill",
            size_hint_y=None,
            height=dp(56)
        )
        self.title_field.bind(text=self.on_title_change)
        title_card.add_widget(self.title_field)
        content.add_widget(title_card)

        # Notes field in card
        notes_card = MDCard(
            orientation='vertical',
            padding=dp(12),
            size_hint_y=None,
            height=dp(150),
            elevation=2,
            radius=[dp(12)]
        )

        self.notes_field = MDTextField(
            hint_text="Add notes...",
            mode="fill",
            multiline=True,
            size_hint_y=None,
            height=dp(120)
        )
        self.notes_field.bind(text=self.on_notes_change)
        notes_card.add_widget(self.notes_field)
        content.add_widget(notes_card)

        # Motivation field in card
        motivation_card = MDCard(
            orientation='vertical',
            padding=dp(12),
            size_hint_y=None,
            height=dp(150),
            elevation=2,
            radius=[dp(12)]
        )

        from kivymd.uix.label import MDLabel
        motivation_card.add_widget(MDLabel(
            text="💪 Motivation Quote",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(20),
            bold=True
        ))

        self.motivation_field = MDTextField(
            hint_text='e.g., "You got this! Stay focused!"',
            mode="fill",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        self.motivation_field.bind(text=self.on_motivation_change)
        motivation_card.add_widget(self.motivation_field)
        content.add_widget(motivation_card)

        # Action buttons section
        buttons_card = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(390),
            elevation=2,
            radius=[dp(12)]
        )

        # Due date button
        self.due_date_btn = MDRaisedButton(
            text="📅 Set Due Date",
            md_bg_color=Colors.PRIMARY_BLUE,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_date_picker,
            elevation=4
        )
        buttons_card.add_widget(self.due_date_btn)

        # Start time button
        self.start_time_btn = MDRaisedButton(
            text="🕐 Set Start Time",
            md_bg_color=Colors.PRIMARY_BLUE,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_start_time_picker,
            elevation=4
        )
        buttons_card.add_widget(self.start_time_btn)

        # End time button
        self.end_time_btn = MDRaisedButton(
            text="🕐 Set End Time",
            md_bg_color=Colors.PRIMARY_BLUE,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_end_time_picker,
            elevation=4
        )
        buttons_card.add_widget(self.end_time_btn)

        # Reminder minutes before input
        reminder_minutes_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8),
            padding=[dp(8), 0]
        )

        reminder_minutes_box.add_widget(MDLabel(
            text="Remind before:",
            size_hint_x=0.5,
            font_style="Body2"
        ))

        self.reminder_minutes_field = MDTextField(
            text="15",
            hint_text="Minutes",
            input_filter="int",
            mode="rectangle",
            size_hint_x=0.3,
            size_hint_y=None,
            height=dp(48)
        )
        self.reminder_minutes_field.bind(text=self.on_reminder_minutes_change)
        reminder_minutes_box.add_widget(self.reminder_minutes_field)

        reminder_minutes_box.add_widget(MDLabel(
            text="min",
            size_hint_x=0.2,
            font_style="Caption"
        ))
        buttons_card.add_widget(reminder_minutes_box)

        # Reminder time display
        self.reminder_time_label = MDLabel(
            text="Reminder: Set start time first",
            font_style="Caption",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Hint",
            halign="center"
        )
        buttons_card.add_widget(self.reminder_time_label)

        # Recurrence button
        self.recurrence_btn = MDRaisedButton(
            text="🔄 Set Recurrence",
            md_bg_color=Colors.PRIMARY_BLUE,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_recurrence_dialog,
            elevation=4
        )
        buttons_card.add_widget(self.recurrence_btn)

        content.add_widget(buttons_card)

        # Subtasks section
        content.add_widget(MDLabel(
            text="Subtasks",
            font_style="H6",
            size_hint_y=None,
            height=dp(40),
            bold=True
        ))

        self.subtask_list = MDList()
        content.add_widget(self.subtask_list)

        # Add subtask button
        add_subtask_btn = MDFlatButton(
            text="+ Add Subtask",
            on_release=self.show_add_subtask_dialog
        )
        content.add_widget(add_subtask_btn)

        scroll.add_widget(content)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def load_task_data(self):
        """Load task data from database"""
        try:
            self.task = self.db.get_task_by_id(self.task_id)
            if not self.task:
                toast("Task not found")
                self.go_back()
                return

            self.title_field.text = self.task.title
            self.notes_field.text = self.task.notes or ""
            self.motivation_field.text = self.task.motivation or ""

            # Update buttons with task data
            if self.task.due_date:
                self.due_date_btn.text = f"📅 Due: {format_date(self.task.due_date)}"

            if self.task.start_time:
                self.start_time_btn.text = f"🕐 Start: {self.task.start_time}"
                # Update reminder display
                self.update_reminder_display()

            if self.task.end_time:
                self.end_time_btn.text = f"🕐 End: {self.task.end_time}"

            if self.task.reminder_time:
                # Calculate minutes before from reminder and start time
                if self.task.start_time:
                    try:
                        start = datetime.strptime(self.task.start_time, TIME_FORMAT)
                        reminder = datetime.strptime(self.task.reminder_time, TIME_FORMAT)
                        minutes_diff = int((start - reminder).total_seconds() / 60)
                        if minutes_diff > 0:
                            self.reminder_minutes_field.text = str(minutes_diff)
                    except:
                        pass
                self.update_reminder_display()

            if self.task.recurrence_type:
                recurrence_labels = {
                    "today": "Daily",
                    "week": "Weekly",
                    "month": "Monthly",
                    "year": "Yearly",
                    "custom": f"Every {self.task.recurrence_interval} days"
                }
                label = recurrence_labels.get(self.task.recurrence_type, "Custom")
                self.recurrence_btn.text = f"🔄 Repeats: {label}"

            self.load_subtasks()

        except Exception as e:
            print(f"❌ Error loading task: {e}")
            toast("Error loading task")
            self.go_back()

    def load_subtasks(self):
        """Load subtasks for this task"""
        self.subtask_list.clear_widgets()

        if self.task and self.task.subtasks:
            for subtask in self.task.subtasks:
                status_icon = "✓" if subtask.completed else "○"
                item = TwoLineIconListItem(
                    text=f"{status_icon} {subtask.title}",
                    secondary_text="Completed" if subtask.completed else "Pending",
                    on_release=lambda x, sid=subtask.id: self.toggle_subtask(sid)
                )
                self.subtask_list.add_widget(item)

    def on_title_change(self, instance, value):
        """Handle title field changes"""
        if self.task and value.strip():
            try:
                self.db.update_task(self.task_id, title=value)
            except ValueError as e:
                toast(f"Invalid title: {e}")

    def on_notes_change(self, instance, value):
        """Handle notes field changes"""
        if self.task:
            try:
                self.db.update_task(self.task_id, notes=value)
            except ValueError as e:
                toast(f"Invalid notes: {e}")

    def on_motivation_change(self, instance, value):
        """Handle motivation field changes"""
        if self.task:
            try:
                self.db.update_task(self.task_id, motivation=value)
            except ValueError as e:
                toast(f"Invalid motivation: {e}")

    def on_reminder_minutes_change(self, instance, value):
        """Update reminder when minutes before changes"""
        self.update_reminder_display()

    def update_reminder_display(self):
        """Calculate and display reminder time"""
        if self.task and self.task.start_time:
            try:
                minutes_before = int(self.reminder_minutes_field.text or "15")
                minutes_before = max(1, min(minutes_before, 120))

                start_time = datetime.strptime(self.task.start_time, TIME_FORMAT)
                reminder_time = start_time - timedelta(minutes=minutes_before)
                reminder_str = reminder_time.strftime(TIME_FORMAT)

                # Update in database
                self.db.update_task(self.task_id, reminder_time=reminder_str)

                # Update display
                self.reminder_time_label.text = f"⏰ Reminder: {reminder_str} ({minutes_before} min before)"
                self.reminder_time_label.theme_text_color = "Primary"

            except Exception as e:
                print(f"Error updating reminder: {e}")
                self.reminder_time_label.text = "Error calculating reminder"
        else:
            self.reminder_time_label.text = "Set start time first"
            self.reminder_time_label.theme_text_color = "Hint"

    def show_date_picker(self, *args):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_due_date)
        date_dialog.open()

    def set_due_date(self, instance, value, date_range):
        try:
            date_str = str(value)
            self.db.update_task(self.task_id, due_date=date_str)
            self.due_date_btn.text = f"📅 Due: {format_date(value)}"
            toast("Due date set")
        except Exception as e:
            print(f"❌ Error setting due date: {e}")
            toast("Error setting due date")

    def show_start_time_picker(self, *args):
        now = datetime.now()
        time_dialog = MDTimePicker()
        time_dialog.set_time(now)
        time_dialog.bind(on_save=self.set_start_time)
        time_dialog.open()

    def set_start_time(self, instance, time):
        try:
            time_str = time.strftime(TIME_FORMAT)
            self.db.update_task(self.task_id, start_time=time_str)
            self.task.start_time = time_str
            self.start_time_btn.text = f"🕐 Start: {time_str}"

            # Update reminder automatically
            self.update_reminder_display()

            toast("Start time set")
        except Exception as e:
            print(f"❌ Error setting start time: {e}")
            toast("Error setting start time")

    def show_end_time_picker(self, *args):
        now = datetime.now()
        time_dialog = MDTimePicker()
        time_dialog.set_time(now)
        time_dialog.bind(on_save=self.set_end_time)
        time_dialog.open()

    def set_end_time(self, instance, time):
        try:
            time_str = time.strftime(TIME_FORMAT)
            self.db.update_task(self.task_id, end_time=time_str)
            self.end_time_btn.text = f"🕐 End: {time_str}"
            toast("End time set")
        except Exception as e:
            print(f"❌ Error setting end time: {e}")
            toast("Error setting end time")

    def show_recurrence_dialog(self, *args):
        current_type = self.task.recurrence_type if self.task else None
        current_interval = self.task.recurrence_interval if self.task else 1
        dialog = RecurrenceDialog(self.set_recurrence, current_type, current_interval)
        dialog.show()

    def set_recurrence(self, recurrence_type, interval):
        try:
            self.db.update_task(
                self.task_id,
                recurrence_type=recurrence_type,
                recurrence_interval=interval
            )

            if recurrence_type:
                recurrence_labels = {
                    "today": "Daily",
                    "week": "Weekly",
                    "month": "Monthly",
                    "year": "Yearly",
                    "custom": f"Every {interval} days"
                }
                label = recurrence_labels.get(recurrence_type, "Custom")
                self.recurrence_btn.text = f"🔄 Repeats: {label}"
                toast("Recurrence set")
            else:
                self.recurrence_btn.text = "🔄 Set Recurrence"
                toast("Recurrence removed")

        except Exception as e:
            print(f"❌ Error setting recurrence: {e}")
            toast("Error setting recurrence")

    def show_add_subtask_dialog(self, *args):
        dialog = AddTaskDialog(self.add_subtask, title="New Subtask", hint="Subtask title")
        dialog.show()

    def add_subtask(self, title):
        """Add a new subtask"""
        if self.task:
            try:
                self.db.create_task(
                    list_id=self.task.list_id,
                    title=title,
                    parent_id=self.task_id
                )
                self.load_task_data()
                toast("Subtask added")
            except ValueError as e:
                toast(f"Error: {e}")

    def toggle_subtask(self, subtask_id):
        try:
            self.db.toggle_task_completed(subtask_id)
            self.load_task_data()
        except Exception as e:
            print(f"❌ Error toggling subtask: {e}")
            toast("Error updating subtask")

    def delete_task(self):
        from components.dialogs import ConfirmDialog

        dialog = ConfirmDialog(
            title="Delete Task",
            message="Are you sure you want to delete this task?",
            callback=self.confirm_delete,
            confirm_text="DELETE"
        )
        dialog.show()

    def confirm_delete(self):
        try:
            self.db.delete_task(self.task_id)
            toast("Task deleted")
            self.go_back()
        except Exception as e:
            print(f"❌ Error deleting task: {e}")
            toast("Error deleting task")

    def go_back(self):
        if self.on_back_callback:
            self.on_back_callback()