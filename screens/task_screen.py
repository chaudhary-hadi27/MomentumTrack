from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.chip import MDChip
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp


class TaskScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.build_ui()

    def build_ui(self):
        """Build modern task screen UI"""
        layout = BoxLayout(orientation='vertical', spacing=dp(12))

        # Header with back button and title
        header = self.create_header()

        # Task filter chips
        filter_section = self.create_filter_chips()

        # Task list with scroll
        scroll = ScrollView()
        self.task_list = MDList(spacing=dp(8))
        scroll.add_widget(self.task_list)

        # Floating Add Button (simulated at bottom)
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
            text="Organize your work efficiently",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(back_btn)
        header.add_widget(title_box)

        return header

    def create_filter_chips(self):
        """Create filter buttons for task categories"""
        filter_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(16), 0, dp(16), 0],
            spacing=dp(8)
        )

        # Filter info label
        filter_label = MDLabel(
            text="📋 Showing all tasks",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="left"
        )

        filter_container.add_widget(filter_label)

        return filter_container

    def on_enter(self):
        """Called when screen is entered"""
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from database with modern cards"""
        self.task_list.clear_widgets()
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = app.db_manager.get_all_tasks()

        if not tasks:
            # Empty state
            empty_card = MDCard(
                orientation='vertical',
                padding=dp(40),
                size_hint_y=None,
                height=dp(200),
                elevation=0
            )

            empty_icon = MDIcon(
                icon="clipboard-text-outline",
                size_hint_y=None,
                height=dp(60),
                theme_text_color="Secondary",
                halign="center",
                font_size="60sp"
            )

            empty_label = MDLabel(
                text="No tasks yet",
                font_style="H6",
                halign="center",
                size_hint_y=None,
                height=dp(40)
            )

            empty_subtitle = MDLabel(
                text="Tap the button below to add your first task",
                font_style="Caption",
                theme_text_color="Secondary",
                halign="center",
                size_hint_y=None,
                height=dp(30)
            )

            empty_card.add_widget(empty_icon)
            empty_card.add_widget(empty_label)
            empty_card.add_widget(empty_subtitle)
            self.task_list.add_widget(empty_card)
            return

        for task in tasks:
            task_id, title, desc, category, priority, status, due_date, created_at, completed_at = task

            # Create modern task card
            task_card = self.create_task_card(task_id, title, desc, category, priority, status)
            self.task_list.add_widget(task_card)

    def create_task_card(self, task_id, title, desc, category, priority, status):
        """Create a modern task card"""
        card = MDCard(
            orientation='vertical',
            padding=dp(16),
            size_hint_y=None,
            height=dp(120),
            elevation=2,
            radius=[12, 12, 12, 12],
            on_release=lambda x: self.show_task_options(task_id)
        )

        # Top row: status icon and title
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
                icon="circle-outline",
                theme_text_color="Secondary",
                size_hint_x=None,
                width=dp(30)
            )

        title_label = MDLabel(
            text=title,
            font_style="Subtitle1",
            bold=True,
            size_hint_x=0.7
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

        # Description
        if desc:
            desc_label = MDLabel(
                text=desc,
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(25)
            )
        else:
            desc_label = BoxLayout(size_hint_y=None, height=dp(25))

        # Bottom row: category and priority tags
        bottom_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30), spacing=dp(8))

        category_chip = MDChip(
            text=f"📁 {category.capitalize()}",
            radius=15,
            size_hint_x=None,
            width=dp(100)
        )

        priority_colors = {
            'high': (0.9, 0.2, 0.2, 1),
            'medium': (0.9, 0.6, 0.2, 1),
            'low': (0.3, 0.7, 0.3, 1)
        }

        priority_chip = MDChip(
            text=priority.capitalize(),
            radius=15,
            size_hint_x=None,
            width=dp(100)
        )

        bottom_row.add_widget(category_chip)
        bottom_row.add_widget(priority_chip)

        card.add_widget(top_row)
        card.add_widget(desc_label)
        card.add_widget(bottom_row)

        return card

    def show_add_task_dialog(self):
        """Show modern dialog to add new task"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(10), size_hint_y=None, height=dp(200))

        self.title_field = MDTextField(
            hint_text="Task Title *",
            required=True,
            mode="rectangle"
        )
        self.desc_field = MDTextField(
            hint_text="Description (optional)",
            multiline=True,
            mode="rectangle"
        )

        content.add_widget(self.title_field)
        content.add_widget(self.desc_field)

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

    def add_task(self):
        """Add task to database"""
        if not self.title_field.text:
            return

        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.db_manager.add_task(
            title=self.title_field.text,
            description=self.desc_field.text,
            category='work',
            priority='medium'
        )

        self.dialog.dismiss()
        self.load_tasks()

    def show_task_options(self, task_id):
        """Show options for a task"""
        self.dialog = MDDialog(
            title="Task Options",
            text="What would you like to do with this task?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=(0.5, 0.5, 0.5, 1),
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="✓ COMPLETE",
                    md_bg_color=(0.2, 0.7, 0.3, 1),
                    on_release=lambda x: self.complete_task(task_id)
                )
            ]
        )
        self.dialog.open()

    def complete_task(self, task_id):
        """Mark task as completed"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.db_manager.update_task_status(task_id, 'completed')
        self.dialog.dismiss()
        self.load_tasks()

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
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app.db_manager.delete_task(task_id)
        self.dialog.dismiss()
        self.load_tasks()

    def go_back(self):
        """Navigate back to home"""
        self.manager.current = 'home'