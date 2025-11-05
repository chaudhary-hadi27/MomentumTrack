from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDTimePicker
from kivy.metrics import dp
from datetime import datetime
from utils.constants import *


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


class AddTaskDialog(BaseDialog):
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
        if title:
            try:
                self.callback(title)
            except ValueError as e:
                print(f"Validation error: {e}")
                # Could show error dialog here
        self.dismiss()


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
        if name:
            try:
                self.callback(name)
            except ValueError as e:
                print(f"Validation error: {e}")
        self.dismiss()


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
        from kivymd.uix.label import MDLabel
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
        from kivymd.uix.label import MDLabel

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