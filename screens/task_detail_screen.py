from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.list import MDList, OneLineListItem, TwoLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp
from components.dialogs import DatePickerDialog, AddTaskDialog
from database.db_manager import DatabaseManager
from utils.helpers import format_date


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
            text="Set Due Date",
            pos_hint={"center_x": 0.5},
            on_release=self.show_date_picker
        )
        content.add_widget(self.due_date_btn)

        # Subtasks section
        from kivymd.uix.label import MDLabel
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

            if self.task.due_date:
                self.due_date_btn.text = format_date(self.task.due_date)

            self.load_subtasks()

    def load_subtasks(self):
        self.subtask_list.clear_widgets()

        if self.task and self.task.subtasks:
            for subtask in self.task.subtasks:
                item = TwoLineListItem(
                    text=subtask.title,
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
        dialog = DatePickerDialog(self.set_due_date)
        dialog.show()

    def set_due_date(self, date):
        self.db.update_task(self.task_id, due_date=str(date))
        self.due_date_btn.text = format_date(date)

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