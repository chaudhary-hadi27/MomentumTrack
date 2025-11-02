from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from components.task_item import TaskItem
from components.dialogs import AddTaskDialog, EditListDialog
from database.db_manager import DatabaseManager
from utils.helpers import format_date


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_list_id = None
        self.current_list_name = ""

        self.build_ui()
        self.load_initial_data()

    def build_ui(self):
        # Navigation layout
        self.nav_layout = MDNavigationLayout()

        # Create ScreenManager for main content
        screen_manager = ScreenManager()

        # Create a screen for the content
        content_screen = Screen()

        # Content layout
        content_box = MDBoxLayout(orientation='vertical')

        # Toolbar
        self.toolbar = MDTopAppBar(
            title="My Tasks",
            left_action_items=[["menu", lambda x: self.toggle_nav_drawer()]],
            right_action_items=[["dots-vertical", lambda x: self.show_list_options()]],
            elevation=2
        )
        content_box.add_widget(self.toolbar)

        # Task list
        scroll = MDScrollView()
        self.task_list = MDList()
        scroll.add_widget(self.task_list)
        content_box.add_widget(scroll)

        # FAB
        self.fab = MDFloatingActionButton(
            icon="plus",
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.show_add_task_dialog
        )
        content_box.add_widget(self.fab)

        content_screen.add_widget(content_box)
        screen_manager.add_widget(content_screen)

        # Add ScreenManager to navigation layout
        self.nav_layout.add_widget(screen_manager)

        # Navigation drawer
        self.nav_drawer = MDNavigationDrawer()
        nav_drawer_content = MDBoxLayout(
            orientation='vertical',
            padding=dp(16),
            spacing=dp(10)
        )

        # Drawer header
        drawer_header = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=[dp(16), dp(20)]
        )
        from kivymd.uix.label import MDLabel
        drawer_header.add_widget(MDLabel(
            text="Tasks",
            font_style="H5",
            theme_text_color="Primary"
        ))
        nav_drawer_content.add_widget(drawer_header)

        # Lists scroll view
        lists_scroll = MDScrollView()
        self.drawer_list = MDList()
        lists_scroll.add_widget(self.drawer_list)
        nav_drawer_content.add_widget(lists_scroll)

        # Add list button
        add_list_btn = MDIconButton(
            icon="plus",
            on_release=self.show_add_list_dialog,
            pos_hint={"center_x": 0.5}
        )
        nav_drawer_content.add_widget(add_list_btn)

        self.nav_drawer.add_widget(nav_drawer_content)

        # Add drawer to navigation layout
        self.nav_layout.add_widget(self.nav_drawer)

        # Add navigation layout to main screen
        self.add_widget(self.nav_layout)

    def load_initial_data(self):
        # Load first list
        lists = self.db.get_all_lists()
        if lists:
            self.switch_list(lists[0].id, lists[0].name)
            self.load_drawer_lists()

    def load_drawer_lists(self):
        self.drawer_list.clear_widgets()
        lists = self.db.get_all_lists()

        for task_list in lists:
            item = OneLineListItem(
                text=task_list.name,
                on_release=lambda x, lid=task_list.id, lname=task_list.name: self.switch_list(lid, lname)
            )
            self.drawer_list.add_widget(item)

    def switch_list(self, list_id, list_name):
        self.current_list_id = list_id
        self.current_list_name = list_name
        self.toolbar.title = list_name
        self.load_tasks()
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")

    def load_tasks(self):
        self.task_list.clear_widgets()

        if not self.current_list_id:
            return

        tasks = self.db.get_tasks_by_list(self.current_list_id)

        for task in tasks:
            # Main task
            task_item = TaskItem(
                task_id=task.id,
                task_title=task.title,
                task_notes=task.notes,
                task_due_date=format_date(task.due_date) if task.due_date else "",
                task_completed=task.completed,
                on_task_click=self.open_task_details,
                on_toggle_complete=self.toggle_task_completed
            )
            self.task_list.add_widget(task_item)

            # Subtasks
            for subtask in task.subtasks:
                subtask_item = TaskItem(
                    task_id=subtask.id,
                    task_title=subtask.title,
                    task_completed=subtask.completed,
                    is_subtask=True,
                    on_task_click=self.open_task_details,
                    on_toggle_complete=self.toggle_task_completed
                )
                self.task_list.add_widget(subtask_item)

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

    def open_task_details(self, task_id):
        # Will implement in main.py
        print(f"Opening task {task_id}")

    def toggle_nav_drawer(self):
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
        else:
            self.nav_drawer.set_state("open")

    def show_list_options(self):
        # Will add rename/delete list options
        dialog = EditListDialog(self.current_list_name, self.rename_list)
        dialog.show()

    def rename_list(self, new_name):
        if self.current_list_id:
            self.db.update_list(self.current_list_id, new_name)
            self.toolbar.title = new_name
            self.current_list_name = new_name
            self.load_drawer_lists()

    def show_add_list_dialog(self, *args):
        dialog = AddTaskDialog(self.add_list)
        dialog.dialog.title = "New List"
        dialog.title_field.hint_text = "List name"
        dialog.show()

    def add_list(self, name):
        list_id = self.db.create_list(name)
        self.load_drawer_lists()
        self.switch_list(list_id, name)