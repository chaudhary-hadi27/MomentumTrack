from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import MDList, TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
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

        self.build_ui()
        self.load_task_data()

    def build_ui(self):
        layout = MDBoxLayout(orientation='vertical')

        # Toolbar
        toolbar = MDTopAppBar(
            title="Task Details",
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[["delete", lambda x: self.delete_task()]],
            elevation=2
        )
        layout.add_widget(toolbar)

        # Scrollable content
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(16),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Title field
        self.title_field = MDTextField(
            hint_text="Task title",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56)
        )
        self.title_field.bind(text=self.on_title_change)
        content.add_widget(self.title_field)

        # Notes field
        self.notes_field = MDTextField(
            hint_text="Add notes",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(120)
        )
        self.notes_field.bind(text=self.on_notes_change)
        content.add_widget(self.notes_field)

        # Due date button
        self.due_date_btn = MDRaisedButton(
            text="📅 Set Due Date",
            md_bg_color=BUTTON_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            on_release=self.show_date_picker
        )
        content.add_widget(self.due_date_btn)

        # Start time button
        self.start_time_btn = MDRaisedButton(
            text="🕐 Set Start Time",
            md_bg_color=BUTTON_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            on_release=self.show_start_time_picker
        )
        content.add_widget(self.start_time_btn)

        # End time button
        self.end_time_btn = MDRaisedButton(
            text="🕐 Set End Time",
            md_bg_color=BUTTON_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            on_release=self.show_end_time_picker
        )
        content.add_widget(self.end_time_btn)

        # Reminder time button
        self.reminder_time_btn = MDRaisedButton(
            text="⏰ Set Reminder Time",
            md_bg_color=BUTTON_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            on_release=self.show_reminder_time_picker
        )
        content.add_widget(self.reminder_time_btn)

        # Recurrence button
        self.recurrence_btn = MDRaisedButton(
            text="🔄 Set Recurrence",
            md_bg_color=BUTTON_COLOR,
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
            on_release=self.show_recurrence_dialog
        )
        content.add_widget(self.recurrence_btn)

        # Divider
        from kivymd.uix.label import MDLabel
        content.add_widget(MDLabel(
            text="─" * 40,
            halign="center",
            size_hint_y=None,
            height=dp(20)
        ))

        # Subtasks section
        content.add_widget(MDLabel(
            text="Subtasks",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
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
        dialog = AddTaskDialog(self.add_subtask)
        dialog.dialog.title = "New Subtask"
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