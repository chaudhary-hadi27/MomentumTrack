from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivymd.app import MDApp
from components.dialogs import AddTaskDialog, TimePickerDialog, RecurrenceDialog
from kivymd.uix.pickers import MDDatePicker
from database.db_manager import DatabaseManager
from utils.helpers import format_date
from utils.constants import BUTTON_COLOR


class TaskDetailScreen(MDScreen):
    def __init__(self, task_id, on_back_callback, **kwargs):
        super().__init__(**kwargs)
        self.task_id = task_id
        self.on_back_callback = on_back_callback
        self.db = DatabaseManager()
        self.task = None
        self.toolbar = None

        self.build_ui()
        self.load_task_data()

        # Listen for theme changes
        app = MDApp.get_running_app()
        if app:
            app.theme_cls.bind(theme_style=self.on_theme_change)

    def update_toolbar_colors(self):
        """Update toolbar icon colors based on theme"""
        if not self.toolbar:
            return

        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            self.toolbar.specific_text_color = [0, 0, 0, 0.87]  # Black
        else:
            self.toolbar.specific_text_color = [1, 1, 1, 1]  # White

    def on_theme_change(self, instance, value):
        """Called when theme changes"""
        if self.toolbar:
            self.toolbar.md_bg_color = self.get_toolbar_color()
            self.update_toolbar_colors()

            # Rebuild toolbar items to apply new colors
            self.toolbar.left_action_items = [["arrow-left", lambda x: self.go_back()]]
            self.toolbar.right_action_items = [["delete", lambda x: self.delete_task()]]

    def get_toolbar_color(self):
        """Get toolbar color based on current theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return (0.12, 0.12, 0.12, 1)  # Dark gray
        else:
            return (0.96, 0.96, 0.96, 1)  # Light gray for better contrast

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # Toolbar with theme-aware color
        self.toolbar = MDTopAppBar(
            title="Task Details",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["delete", lambda x: self.delete_task()]],
            elevation=2,
            md_bg_color=self.get_toolbar_color()
        )

        # Set icon color after toolbar creation
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

        # Action buttons section with BLUE buttons
        buttons_card = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(340),
            elevation=2,
            radius=[dp(12)]
        )

        # Due date button (BLUE)
        self.due_date_btn = MDRaisedButton(
            text="📅 Set Due Date",
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_date_picker,
            elevation=4
        )
        buttons_card.add_widget(self.due_date_btn)

        # Start time button (BLUE)
        self.start_time_btn = MDRaisedButton(
            text="🕐 Set Start Time",
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_start_time_picker,
            elevation=4
        )
        buttons_card.add_widget(self.start_time_btn)

        # End time button (BLUE)
        self.end_time_btn = MDRaisedButton(
            text="🕐 Set End Time",
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_end_time_picker,
            elevation=4
        )
        buttons_card.add_widget(self.end_time_btn)

        # Reminder time button (BLUE)
        self.reminder_time_btn = MDRaisedButton(
            text="⏰ Set Reminder Time",
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
            pos_hint={"center_x": 0.5},
            size_hint_x=0.95,
            size_hint_y=None,
            height=dp(50),
            on_release=self.show_reminder_time_picker,
            elevation=4
        )
        buttons_card.add_widget(self.reminder_time_btn)

        # Recurrence button (BLUE)
        self.recurrence_btn = MDRaisedButton(
            text="🔄 Set Recurrence",
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
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
        from kivymd.uix.label import MDLabel
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
        self.task = self.db.get_task_by_id(self.task_id)
        if self.task:
            self.title_field.text = self.task.title
            self.notes_field.text = self.task.notes or ""

            # Update buttons with task data
            if self.task.due_date:
                self.due_date_btn.text = f"📅 Due: {format_date(self.task.due_date)}"

            if self.task.start_time:
                self.start_time_btn.text = f"🕐 Start: {self.task.start_time}"

            if self.task.end_time:
                self.end_time_btn.text = f"🕐 End: {self.task.end_time}"

            if self.task.reminder_time:
                self.reminder_time_btn.text = f"⏰ Reminder: {self.task.reminder_time}"

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

    def load_subtasks(self):
        self.subtask_list.clear_widgets()

        if self.task and self.task.subtasks:
            for subtask in self.task.subtasks:
                status_icon = "✓" if subtask.completed else "○"
                item = TwoLineListItem(
                    text=f"{status_icon} {subtask.title}",
                    secondary_text="Completed" if subtask.completed else "Pending",
                    on_release=lambda x, sid=subtask.id: self.toggle_subtask(sid)
                )
                self.subtask_list.add_widget(item)

    def on_title_change(self, instance, value):
        if self.task:
            self.db.update_task(self.task_id, title=value)

    def on_notes_change(self, instance, value):
        if self.task:
            self.db.update_task(self.task_id, notes=value)

    def show_date_picker(self, *args):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.set_due_date)
        date_dialog.open()

    def set_due_date(self, instance, value, date_range):
        date_str = str(value)
        self.db.update_task(self.task_id, due_date=date_str)
        self.due_date_btn.text = f"📅 Due: {format_date(value)}"

    def show_start_time_picker(self, *args):
        dialog = TimePickerDialog(self.set_start_time, "Select Start Time")
        dialog.show()

    def set_start_time(self, time_str):
        self.db.update_task(self.task_id, start_time=time_str)
        self.start_time_btn.text = f"🕐 Start: {time_str}"

    def show_end_time_picker(self, *args):
        dialog = TimePickerDialog(self.set_end_time, "Select End Time")
        dialog.show()

    def set_end_time(self, time_str):
        self.db.update_task(self.task_id, end_time=time_str)
        self.end_time_btn.text = f"🕐 End: {time_str}"

    def show_reminder_time_picker(self, *args):
        dialog = TimePickerDialog(self.set_reminder_time, "Select Reminder Time")
        dialog.show()

    def set_reminder_time(self, time_str):
        self.db.update_task(self.task_id, reminder_time=time_str)
        self.reminder_time_btn.text = f"⏰ Reminder: {time_str}"

    def show_recurrence_dialog(self, *args):
        current_type = self.task.recurrence_type if self.task else None
        current_interval = self.task.recurrence_interval if self.task else 1
        dialog = RecurrenceDialog(self.set_recurrence, current_type, current_interval)
        dialog.show()

    def set_recurrence(self, recurrence_type, interval):
        self.db.update_task(self.task_id, recurrence_type=recurrence_type, recurrence_interval=interval)

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
        else:
            self.recurrence_btn.text = "🔄 Set Recurrence"

    def show_add_subtask_dialog(self, *args):
        dialog = AddTaskDialog(self.add_subtask, title="New Subtask", hint="Subtask title")
        dialog.show()

    def add_subtask(self, title):
        if self.task:
            self.db.create_task(
                list_id=self.task.list_id,
                title=title,
                parent_id=self.task_id
            )
            self.load_task_data()

    def toggle_subtask(self, subtask_id):
        self.db.toggle_task_completed(subtask_id)
        self.load_task_data()

    def delete_task(self):
        self.db.delete_task(self.task_id)
        self.go_back()

    def go_back(self):
        if self.on_back_callback:
            self.on_back_callback()