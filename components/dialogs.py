from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDTimePicker
from kivy.metrics import dp
from datetime import datetime
from utils.constants import *


class AddTaskDialog:
    def __init__(self, callback, title="New Task", hint="Task title"):
        self.callback = callback
        self.dialog = None
        self.dialog_title = title
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

        self.dialog = MDDialog(
            title=self.dialog_title,
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ADD",
                    md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
                    on_release=self.on_add
                ),
            ],
        )
        self.dialog.open()

    def on_add(self, *args):
        title = self.title_field.text.strip()
        if title:
            self.callback(title)
        self.dialog.dismiss()


class EditListDialog:
    def __init__(self, current_name, callback):
        self.current_name = current_name
        self.callback = callback
        self.dialog = None

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

        self.dialog = MDDialog(
            title="Rename List",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
                    on_release=self.on_save
                ),
            ],
        )
        self.dialog.open()

    def on_save(self, *args):
        name = self.name_field.text.strip()
        if name:
            self.callback(name)
        self.dialog.dismiss()


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


class RecurrenceDialog:
    def __init__(self, callback, current_type=None, current_interval=1):
        self.callback = callback
        self.current_type = current_type
        self.current_interval = current_interval
        self.selected_type = current_type
        self.dialog = None

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

        for label, value in options:
            btn = MDRaisedButton(
                text=label,
                md_bg_color=(0.1, 0.45, 0.91, 1) if self.current_type == value else (0.6, 0.6, 0.6, 1),  # Blue or gray
                size_hint_y=None,
                height=dp(40),
                on_release=lambda x, v=value: self.select_type(v)
            )
            content.add_widget(btn)

        # Custom interval field (only for custom)
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

        self.dialog = MDDialog(
            title="Task Recurrence",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="SAVE",
                    md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
                    on_release=self.on_save
                ),
            ],
        )
        self.dialog.open()

    def select_type(self, recurrence_type):
        self.selected_type = recurrence_type
        self.interval_field.disabled = recurrence_type != RECURRENCE_CUSTOM

        # Update button colors - Blue for selected, gray for others
        for child in self.dialog.content_cls.children:
            if isinstance(child, MDRaisedButton):
                if child.text.startswith(self._get_label(recurrence_type)):
                    child.md_bg_color = (0.1, 0.45, 0.91, 1)  # Blue
                else:
                    child.md_bg_color = (0.6, 0.6, 0.6, 1)  # Gray

    def _get_label(self, recurrence_type):
        labels = {
            RECURRENCE_TODAY: "Today",
            RECURRENCE_WEEK: "This Week",
            RECURRENCE_MONTH: "This Month",
            RECURRENCE_YEAR: "This Year",
            RECURRENCE_CUSTOM: "Custom",
            None: "None"
        }
        return labels.get(recurrence_type, "")

    def on_save(self, *args):
        interval = 1
        if self.selected_type == RECURRENCE_CUSTOM:
            try:
                interval = int(self.interval_field.text)
            except:
                interval = 1

        self.callback(self.selected_type, interval)
        self.dialog.dismiss()