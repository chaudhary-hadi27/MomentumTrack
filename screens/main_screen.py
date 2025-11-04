from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.button import MDIconButton, MDFloatingActionButton, MDRaisedButton
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivymd.uix.card import MDCard
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp
from components.task_item import TaskItem
from components.list_swiper import ListSwiper
from components.dialogs import AddTaskDialog, EditListDialog
from database.db_manager import DatabaseManager
from utils.constants import BUTTON_COLOR


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_list_id = None
        self.current_list_name = ""
        self.all_lists = []
        self.current_list_index = 0
        self.list_widgets = {}  # Store task list widgets for each list
        self.open_settings = None  # Will be set by main app

        self.build_ui()
        self.load_initial_data()

    def get_toolbar_color(self):
        """Get toolbar color based on current theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return (0.12, 0.12, 0.12, 1)  # Dull dark
        else:
            return (0.96, 0.96, 0.96, 1)  # Dull white/light

    def build_ui(self):
        # Navigation layout
        self.nav_layout = MDNavigationLayout()

        # Create ScreenManager for main content
        screen_manager = ScreenManager()

        # Create a screen for the content
        content_screen = Screen()

        # Content layout
        content_box = MDBoxLayout(orientation='vertical')

        # Toolbar with dull color (changes with theme)
        self.toolbar = MDTopAppBar(
            title="My Tasks",
            left_action_items=[["menu", lambda x: self.toggle_nav_drawer()]],
            right_action_items=[
                ["magnify", lambda x: self.toggle_search()],
                ["cog", lambda x: self.show_settings()],
                ["dots-vertical", lambda x: self.show_list_options()]
            ],
            elevation=2,
            md_bg_color=self.get_toolbar_color()
        )

        content_box.add_widget(self.toolbar)

        # List Swiper (Carousel for swiping between lists)
        self.list_swiper = ListSwiper(on_list_change=self.on_swipe_list_change)
        content_box.add_widget(self.list_swiper)

        # Blue FAB (keep original blue)
        self.fab = MDFloatingActionButton(
            icon="plus",
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.show_add_task_dialog,
            elevation=8
        )
        content_box.add_widget(self.fab)

        content_screen.add_widget(content_box)
        screen_manager.add_widget(content_screen)

        # Add ScreenManager to navigation layout
        self.nav_layout.add_widget(screen_manager)

        # Modern Navigation drawer
        self.nav_drawer = MDNavigationDrawer()
        nav_drawer_content = MDBoxLayout(
            orientation='vertical',
            padding=dp(8),
            spacing=dp(10)
        )

        # Blue drawer header (keep original blue)
        drawer_header = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=[dp(20), dp(24), dp(20), dp(16)]
        )

        with drawer_header.canvas.before:
            Color(0.1, 0.45, 0.91, 1)  # Blue
            self.header_rect = RoundedRectangle(
                pos=drawer_header.pos,
                size=drawer_header.size,
                radius=[0, 0, dp(20), dp(20)]
            )

        drawer_header.bind(pos=self._update_header_rect, size=self._update_header_rect)

        from kivymd.uix.label import MDLabel
        drawer_header.add_widget(MDLabel(
            text="Momentum Track",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True
        ))
        drawer_header.add_widget(MDLabel(
            text="Stay Focused. Get Things Done.",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(20)
        ))
        nav_drawer_content.add_widget(drawer_header)

        # Lists scroll view
        lists_scroll = MDScrollView()
        self.drawer_list = MDList()
        lists_scroll.add_widget(self.drawer_list)
        nav_drawer_content.add_widget(lists_scroll)

        # Blue add list button (keep original blue)
        add_list_btn = MDRaisedButton(
            text="+ New List",
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
            pos_hint={"center_x": 0.5},
            size_hint_x=0.85,
            size_hint_y=None,
            height=dp(48),
            elevation=4,
            on_release=self.show_add_list_dialog
        )
        nav_drawer_content.add_widget(add_list_btn)

        self.nav_drawer.add_widget(nav_drawer_content)

        # Add drawer to navigation layout
        self.nav_layout.add_widget(self.nav_drawer)

        # Add navigation layout to main screen
        self.add_widget(self.nav_layout)

    def _update_header_rect(self, instance, value):
        """Update header background rectangle"""
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def show_settings(self):
        """Open settings screen"""
        if self.open_settings:
            self.open_settings()

    def load_initial_data(self):
        # Load all lists
        self.all_lists = self.db.get_all_lists()

        if self.all_lists:
            # Build swiper with all lists
            self.build_list_swiper()
            self.load_drawer_lists()

    def build_list_swiper(self):
        """Build the swipeable list carousel"""
        # Temporarily unbind the index change to prevent callback during clear
        self.list_swiper.unbind(index=self.list_swiper._on_index_change)

        self.list_swiper.clear_widgets()
        self.list_widgets.clear()

        for idx, task_list in enumerate(self.all_lists):
            # Create a scroll view with task list for each list
            scroll = MDScrollView()
            task_list_widget = MDList(padding=[dp(8), dp(12)])
            scroll.add_widget(task_list_widget)

            # Store references
            scroll.list_id = task_list.id
            scroll.list_index = idx
            self.list_widgets[task_list.id] = task_list_widget

            self.list_swiper.add_list_slide(scroll)

        # Re-bind the index change
        self.list_swiper.bind(index=self.list_swiper._on_index_change)

        # Load first list
        if self.all_lists:
            self.current_list_index = 0
            self.current_list_id = self.all_lists[0].id
            self.current_list_name = self.all_lists[0].name
            self.toolbar.title = self.current_list_name
            self.load_tasks_for_list(self.current_list_id)

    def on_swipe_list_change(self, index):
        """Called when user swipes to a different list"""
        if index is None:
            return

        if 0 <= index < len(self.all_lists):
            task_list = self.all_lists[index]
            self.current_list_index = index
            self.current_list_id = task_list.id
            self.current_list_name = task_list.name
            self.toolbar.title = task_list.name

            # Load tasks for this list if not already loaded
            self.load_tasks_for_list(task_list.id)

    def load_drawer_lists(self):
        self.drawer_list.clear_widgets()

        for i, task_list in enumerate(self.all_lists):
            item = OneLineListItem(
                text=task_list.name,
                on_release=lambda x, idx=i: self.switch_to_list_by_index(idx)
            )
            self.drawer_list.add_widget(item)

    def switch_to_list_by_index(self, index):
        """Switch to a list by index (from drawer)"""
        if 0 <= index < len(self.all_lists):
            self.list_swiper.index = index
            # on_swipe_list_change will be called automatically
            if self.nav_drawer.state == "open":
                self.nav_drawer.set_state("close")

    def load_tasks_for_list(self, list_id):
        """Load tasks for a specific list with limit"""
        if list_id not in self.list_widgets:
            return

        task_list_widget = self.list_widgets[list_id]
        task_list_widget.clear_widgets()

        # Get tasks with limit for performance
        tasks = self.db.get_tasks_by_list(list_id, show_completed=True)

        # Limit to first 100 tasks for performance
        tasks = tasks[:100]

        for task in tasks:
            # Main task
            task_item = TaskItem(
                task_id=task.id,
                task_title=task.title,
                task_notes=task.notes,
                task_start_time=task.start_time or "",
                task_end_time=task.end_time or "",
                task_recurrence=task.recurrence_type or "",
                task_completed=task.completed,
                on_task_click=self.open_task_details,
                on_toggle_complete=self.toggle_task_completed,
                on_delete=self.delete_task
            )
            task_list_widget.add_widget(task_item)

            # Subtasks
            for subtask in task.subtasks:
                subtask_item = TaskItem(
                    task_id=subtask.id,
                    task_title=subtask.title,
                    task_completed=subtask.completed,
                    is_subtask=True,
                    on_task_click=self.open_task_details,
                    on_toggle_complete=self.toggle_task_completed,
                    on_delete=self.delete_task
                )
                task_list_widget.add_widget(subtask_item)

    def load_tasks(self):
        """Reload tasks for current list"""
        self.load_tasks_for_list(self.current_list_id)

    def show_add_task_dialog(self, *args):
        dialog = AddTaskDialog(self.add_task)
        dialog.show()

    def add_task(self, title):
        if self.current_list_id:
            self.db.create_task(self.current_list_id, title)
            self.load_tasks()

    def toggle_task_completed(self, task_id, completed):
        self.db.toggle_task_completed(task_id)
        self.load_tasks()

    def delete_task(self, task_id):
        """Delete a specific task"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDRaisedButton

        dialog = MDDialog(
            title="Delete Task",
            text="Are you sure you want to delete this task?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.confirm_delete_task(task_id, dialog)
                ),
            ],
        )
        dialog.open()

    def confirm_delete_task(self, task_id, dialog):
        """Confirm and delete the task"""
        self.db.delete_task(task_id)
        self.load_tasks()
        dialog.dismiss()

    def open_task_details(self, task_id):
        # Implemented in main.py
        pass

    def toggle_nav_drawer(self):
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
        else:
            self.nav_drawer.set_state("open")

    def show_list_options(self):
        from kivymd.uix.menu import MDDropdownMenu

        menu_items = [
            {
                "text": "Rename List",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_action("rename"),
            },
            {
                "text": "Delete List",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.menu_action("delete"),
            },
        ]

        self.menu = MDDropdownMenu(
            caller=self.toolbar.ids.right_actions,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def menu_action(self, action):
        self.menu.dismiss()
        if action == "rename":
            dialog = EditListDialog(self.current_list_name, self.rename_list)
            dialog.show()
        elif action == "delete":
            self.delete_current_list()

    def rename_list(self, new_name):
        if self.current_list_id:
            self.db.update_list(self.current_list_id, new_name)
            self.toolbar.title = new_name
            self.current_list_name = new_name
            self.all_lists = self.db.get_all_lists()
            self.load_drawer_lists()

    def delete_current_list(self):
        if self.current_list_id and len(self.all_lists) > 1:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.button import MDFlatButton, MDRaisedButton

            dialog = MDDialog(
                title="Delete List",
                text=f"Are you sure you want to delete '{self.current_list_name}' and all its tasks?",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="DELETE",
                        md_bg_color=(0.9, 0.2, 0.2, 1),
                        on_release=lambda x: self.confirm_delete_list(dialog)
                    ),
                ],
            )
            dialog.open()

    def confirm_delete_list(self, dialog):
        """Confirm and delete the current list"""
        self.db.delete_list(self.current_list_id)
        dialog.dismiss()

        # Reload all lists
        self.all_lists = self.db.get_all_lists()
        self.build_list_swiper()
        self.load_drawer_lists()

    def show_add_list_dialog(self, *args):
        dialog = AddTaskDialog(self.add_list, title="New List", hint="List name")
        dialog.show()

    def add_list(self, name):
        list_id = self.db.create_list(name)

        # Reload all lists
        self.all_lists = self.db.get_all_lists()
        self.build_list_swiper()
        self.load_drawer_lists()

        # Switch to new list
        new_index = len(self.all_lists) - 1
        self.list_swiper.index = new_index

    def toggle_search(self):
        """Toggle search bar"""
        if hasattr(self, 'search_field') and self.search_field.parent:
            # Remove search field
            self.search_field.parent.remove_widget(self.search_field)
        else:
            # Add search field
            from kivymd.uix.textfield import MDTextField

            # Find the content box
            content_box = self.toolbar.parent

            self.search_field = MDTextField(
                hint_text="Search tasks...",
                mode="rectangle",
                size_hint_y=None,
                height=dp(56),
                on_text=self.on_search_text
            )
            content_box.add_widget(self.search_field, index=1)

    def on_search_text(self, instance, text):
        """Filter tasks based on search"""
        if not text.strip():
            self.load_tasks()
            return

        # Filter current tasks
        if self.current_list_id not in self.list_widgets:
            return

        task_list_widget = self.list_widgets[self.current_list_id]

        # Hide tasks that don't match
        for child in task_list_widget.children:
            if isinstance(child, TaskItem):
                if text.lower() in child.task_title.lower():
                    child.opacity = 1
                    child.disabled = False
                else:
                    child.opacity = 0.3
                    child.disabled = True