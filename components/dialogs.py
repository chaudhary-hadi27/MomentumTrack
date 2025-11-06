from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDTimePicker
from kivy.metrics import dp
from datetime import datetime, timedelta
from utils.constants import *
from kivymd.toast import toast


class BaseDialog:
    """Base dialog class with common functionality"""

    def __init__(self, title, callback):
        self.title = title
        self.callback = callback
        self.dialog = None

    def create_dialog(self, content, buttons):
        """Create and return dialog with content and buttons"""
        self.dialog = MDDialog(
            title=self.title,
            type="custom",
            content_cls=content,
            buttons=buttons
        )
        return self.dialog

    def dismiss(self):
        """Dismiss the dialog"""
        if self.dialog:
            self.dialog.dismiss()


class CreateTaskDialog(BaseDialog):
    """Comprehensive task creation dialog with all fields"""

    def __init__(self, callback, list_id):
        super().__init__("Create New Task", callback)
        self.list_id = list_id
        self.task_data = {
            'name': '',
            'description': '',
            'start_time': None,
            'end_time': None,
            'reminder': None,
            'motivation': ''
        }

    def show(self):
        from kivymd.uix.scrollview import MDScrollView

        # Scrollable content
        scroll = MDScrollView(
            size_hint=(1, None),
            height=dp(450)
        )

        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            padding=[dp(8), dp(8)]
        )
        content.bind(minimum_height=content.setter('height'))

        # Task Name (Required)
        content.add_widget(MDLabel(
            text="Task Name *",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(20),
            bold=True
        ))

        self.name_field = MDTextField(
            hint_text="Enter task name...",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56),
            required=True
        )
        self.name_field.bind(text=self.on_name_change)
        content.add_widget(self.name_field)

        # Description (Optional)
        content.add_widget(MDLabel(
            text="Description (optional)",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(20),
            theme_text_color="Hint"
        ))

        self.description_field = MDTextField(
            hint_text="Add details...",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(self.description_field)

        # Timing Section
        content.add_widget(MDLabel(
            text="⏰ Timing",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30),
            bold=True
        ))

        # Start Time (Required)
        start_time_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8)
        )

        start_time_label = MDLabel(
            text="Start Time *",
            size_hint_x=0.4,
            font_style="Body2",
            bold=True
        )
        start_time_box.add_widget(start_time_label)

        self.start_time_btn = MDRaisedButton(
            text="Select Time 🕐",
            md_bg_color=Colors.PRIMARY_BLUE,
            size_hint_x=0.6,
            on_release=self.show_start_time_picker
        )
        start_time_box.add_widget(self.start_time_btn)
        content.add_widget(start_time_box)

        # End Time (Optional)
        end_time_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8)
        )

        end_time_label = MDLabel(
            text="End Time",
            size_hint_x=0.4,
            font_style="Body2",
            theme_text_color="Hint"
        )
        end_time_box.add_widget(end_time_label)

        self.end_time_btn = MDFlatButton(
            text="Optional 🕐",
            size_hint_x=0.6,
            on_release=self.show_end_time_picker
        )
        end_time_box.add_widget(self.end_time_btn)
        content.add_widget(end_time_box)

        # Reminder (Optional)
        reminder_box = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            spacing=dp(8)
        )

        reminder_label = MDLabel(
            text="Reminder 🔔",
            size_hint_x=0.4,
            font_style="Body2",
            theme_text_color="Hint"
        )
        reminder_box.add_widget(reminder_label)

        self.reminder_btn = MDFlatButton(
            text="Optional ⏰",
            size_hint_x=0.6,
            on_release=self.show_reminder_picker
        )
        reminder_box.add_widget(self.reminder_btn)
        content.add_widget(reminder_box)

        # Motivation (Optional)
        content.add_widget(MDLabel(
            text="💪 Motivation (optional)",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(20),
            theme_text_color="Hint"
        ))

        self.motivation_field = MDTextField(
            hint_text='"You got this!" or "Stay focused!"',
            mode="rectangle",
            size_hint_y=None,
            height=dp(56)
        )
        content.add_widget(self.motivation_field)

        scroll.add_widget(content)

        # Dialog buttons
        buttons = [
            MDFlatButton(
                text="CANCEL",
                on_release=lambda x: self.dismiss()
            ),
            MDRaisedButton(
                text="CREATE TASK",
                md_bg_color=Colors.SUCCESS_GREEN,
                on_release=self.on_create_task
            ),
        ]

        self.dialog = self.create_dialog(scroll, buttons)
        self.dialog.open()

    def on_name_change(self, instance, value):
        """Update task name in data"""
        self.task_data['name'] = value.strip()

    def show_start_time_picker(self, *args):
        """Show time picker for start time"""
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_start_time_save)
        time_dialog.open()

    def on_start_time_save(self, instance, time):
        """Save start time"""
        time_str = time.strftime(TIME_FORMAT)
        self.task_data['start_time'] = time_str
        self.start_time_btn.text = f"{time_str} 🕐"
        self.start_time_btn.md_bg_color = Colors.SUCCESS_GREEN

    def show_end_time_picker(self, *args):
        """Show time picker for end time"""
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_end_time_save)
        time_dialog.open()

    def on_end_time_save(self, instance, time):
        """Save end time"""
        time_str = time.strftime(TIME_FORMAT)
        self.task_data['end_time'] = time_str
        self.end_time_btn.text = f"{time_str} 🕐"

    def show_reminder_picker(self, *args):
        """Show time picker for reminder"""
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_reminder_save)
        time_dialog.open()

    def on_reminder_save(self, instance, time):
        """Save reminder time"""
        time_str = time.strftime(TIME_FORMAT)
        self.task_data['reminder'] = time_str
        self.reminder_btn.text = f"{time_str} 🔔"

    def validate(self):
        """Validate required fields"""
        # Check task name
        if not self.task_data['name']:
            return False, "Task name is required"

        if len(self.task_data['name']) > 500:
            return False, "Task name too long (max 500 characters)"

        # Check start time
        if not self.task_data['start_time']:
            return False, "Start time is required"

        # Check end time logic
        if self.task_data['end_time']:
            try:
                start = datetime.strptime(self.task_data['start_time'], TIME_FORMAT)
                end = datetime.strptime(self.task_data['end_time'], TIME_FORMAT)
                if end <= start:
                    return False, "End time must be after start time"
            except:
                return False, "Invalid time format"

        # Check motivation length
        motivation = self.motivation_field.text.strip()
        if motivation and len(motivation) > 500:
            return False, "Motivation too long (max 500 characters)"

        return True, ""

    def on_create_task(self, *args):
        """Create the task"""
        # Get all field values
        self.task_data['description'] = self.description_field.text.strip()
        self.task_data['motivation'] = self.motivation_field.text.strip()

        # Validate
        valid, error = self.validate()
        if not valid:
            toast(error)
            return

        try:
            # Call callback with task data
            self.callback(self.task_data)
            self.dismiss()

        except ValueError as e:
            toast(f"Error: {e}")
        except Exception as e:
            toast(f"Failed to create task: {e}")
            print(f"Task creation error: {e}")


class AddTaskDialog(BaseDialog):
    """Simple dialog for quick task/subtask creation"""

    def __init__(self, callback, title="New Task", hint="Task title"):
        super().__init__(title, callback)
        self.hint_text = hint

    def show(self):
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(100)
        )

        self.title_field = MDTextField(
            hint_text=self.hint_text,
            mode="rectangle",
            size_hint_y=None,
            height=dp(56)
        )
        content.add_widget(self.title_field)

        buttons = [
            MDFlatButton(
                text="CANCEL",
                on_release=lambda x: self.dismiss()
            ),
            MDRaisedButton(
                text="ADD",
                md_bg_color=Colors.PRIMARY_BLUE,
                on_release=self.on_add
            ),
        ]

        self.dialog = self.create_dialog(content, buttons)
        self.dialog.open()

    def on_add(self, *args):
        title = self.title_field.text.strip()

        if not title:
            toast("Title cannot be empty")
            return

        if len(title) > 500:
            toast("Title too long (max 500 characters)")
            return

        try:
            self.callback(title)
            self.dismiss()
        except ValueError as e:
            toast(f"Error: {e}")
        except Exception as e:
            toast(f"Failed to add: {e}")


class EditListDialog(BaseDialog):
    def __init__(self, current_name, callback):
        super().__init__("Rename List", callback)
        self.current_name = current_name

    def show(self):
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(100)
        )

        self.name_field = MDTextField(
            hint_text="List name",
            text=self.current_name,
            mode="rectangle",
            size_hint_y=None,
            height=dp(56)
        )
        content.add_widget(self.name_field)

        buttons = [
            MDFlatButton(
                text="CANCEL",
                on_release=lambda x: self.dismiss()
            ),
            MDRaisedButton(
                text="SAVE",
                md_bg_color=Colors.PRIMARY_BLUE,
                on_release=self.on_save
            ),
        ]

        self.dialog = self.create_dialog(content, buttons)
        self.dialog.open()

    def on_save(self, *args):
        name = self.name_field.text.strip()

        if not name:
            toast("List name cannot be empty")
            return

        if len(name) > 200:
            toast("List name too long (max 200 characters)")
            return

        try:
            self.callback(name)
            self.dismiss()
        except ValueError as e:
            toast(f"Error: {e}")


class TimePickerDialog:
    def __init__(self, callback, title="Select Time"):
        self.callback = callback
        self.title = title

    def show(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(on_save=self.on_save)
        time_dialog.open()

    def on_save(self, instance, time):
        time_str = time.strftime(TIME_FORMAT)
        self.callback(time_str)


class RecurrenceDialog(BaseDialog):
    def __init__(self, callback, current_type=None, current_interval=1):
        super().__init__("Task Recurrence", callback)
        self.current_type = current_type
        self.current_interval = current_interval
        self.selected_type = current_type

    def show(self):
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=None,
            height=dp(300),
            padding=dp(16)
        )

        # Recurrence type buttons
        content.add_widget(MDLabel(
            text="Repeat:",
            font_style="Subtitle1",
            size_hint_y=None,
            height=dp(30)
        ))

        # Radio-like options
        options = [
            ("Today (Daily)", RECURRENCE_TODAY),
            ("This Week (Weekly)", RECURRENCE_WEEK),
            ("This Month (Monthly)", RECURRENCE_MONTH),
            ("This Year (Yearly)", RECURRENCE_YEAR),
            ("Custom Days", RECURRENCE_CUSTOM),
            ("None", None)
        ]

        self.option_buttons = {}
        for label, value in options:
            btn = MDRaisedButton(
                text=label,
                md_bg_color=Colors.PRIMARY_BLUE if self.current_type == value else (0.6, 0.6, 0.6, 1),
                size_hint_y=None,
                height=dp(40),
                on_release=lambda x, v=value: self.select_type(v)
            )
            self.option_buttons[value] = btn
            content.add_widget(btn)

        # Custom interval field
        self.interval_field = MDTextField(
            hint_text="Every X days",
            text=str(self.current_interval),
            input_filter="int",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56),
            disabled=self.current_type != RECURRENCE_CUSTOM
        )
        content.add_widget(self.interval_field)

        buttons = [
            MDFlatButton(
                text="CANCEL",
                on_release=lambda x: self.dismiss()
            ),
            MDRaisedButton(
                text="SAVE",
                md_bg_color=Colors.PRIMARY_BLUE,
                on_release=self.on_save
            ),
        ]

        self.dialog = self.create_dialog(content, buttons)
        self.dialog.open()

    def select_type(self, recurrence_type):
        """Select recurrence type and update UI"""
        self.selected_type = recurrence_type
        self.interval_field.disabled = recurrence_type != RECURRENCE_CUSTOM

        # Update button colors
        for value, btn in self.option_buttons.items():
            if value == recurrence_type:
                btn.md_bg_color = Colors.PRIMARY_BLUE
            else:
                btn.md_bg_color = (0.6, 0.6, 0.6, 1)

    def on_save(self, *args):
        interval = 1
        if self.selected_type == RECURRENCE_CUSTOM:
            try:
                interval = int(self.interval_field.text)
                if interval < 1:
                    interval = 1
            except (ValueError, TypeError):
                interval = 1

        self.callback(self.selected_type, interval)
        self.dismiss()


class ConfirmDialog(BaseDialog):
    """Generic confirmation dialog"""

    def __init__(self, title, message, callback, confirm_text="OK", cancel_text="CANCEL"):
        super().__init__(title, callback)
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text

    def show(self):
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(80),
            padding=dp(16)
        )

        content.add_widget(MDLabel(
            text=self.message,
            font_style="Body1"
        ))

        buttons = [
            MDFlatButton(
                text=self.cancel_text,
                on_release=lambda x: self.dismiss()
            ),
            MDRaisedButton(
                text=self.confirm_text,
                md_bg_color=Colors.DANGER_RED if "delete" in self.confirm_text.lower() else Colors.PRIMARY_BLUE,
                on_release=self.on_confirm
            ),
        ]

        self.dialog = self.create_dialog(content, buttons)
        self.dialog.open()

    def on_confirm(self, *args):
        self.callback()
        self.dismiss()