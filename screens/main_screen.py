from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineIconListItem, IconLeftWidget
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivymd.app import MDApp
from components.task_item import TaskItem
from components.list_swiper import ListSwiper
from components.dialogs import AddTaskDialog, EditListDialog
from database.db_manager import DatabaseManager
from database.models import TaskCategory
from utils.constants import BUTTON_COLOR


class ListTabs(MDBoxLayout):
    """Horizontal scrollable tabs for lists"""

    def __init__(self, lists=None, on_list_select=None, on_add_list=None, **kwargs):
        super().__init__(**kwargs)
        from kivymd.uix.button import MDFlatButton, MDRaisedButton

        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(56)
        self.padding = [dp(8), dp(4)]
        self.spacing = dp(8)

        self.lists = lists or []
        self.on_list_select = on_list_select
        self.on_add_list = on_add_list
        self.current_list_id = None
        self.tab_buttons = {}

        # Scrollable container
        self.scroll = MDScrollView(
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=0
        )

        self.tab_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(8),
            padding=[dp(4), 0]
        )
        self.tab_container.bind(minimum_width=self.tab_container.setter('width'))

        self.scroll.add_widget(self.tab_container)
        self.add_widget(self.scroll)

        # Add button
        self.add_btn = MDRaisedButton(
            text="+",
            size_hint=(None, None),
            size=(dp(48), dp(40)),
            md_bg_color=(0.1, 0.45, 0.91, 1),
            on_release=lambda x: self.on_add_list() if self.on_add_list else None,
            elevation=4
        )
        self.add_widget(self.add_btn)

        self.update_tabs()

    def update_tabs(self):
        from kivymd.uix.button import MDFlatButton

        self.tab_container.clear_widgets()
        self.tab_buttons.clear()

        for lst in self.lists:
            btn = MDFlatButton(
                text=lst.name,
                size_hint=(None, None),
                size=(dp(120), dp(40)),
                on_release=lambda x, lid=lst.id: self._on_tab_click(lid)
            )
            self.tab_buttons[lst.id] = btn
            self.tab_container.add_widget(btn)

        if self.current_list_id and self.current_list_id in self.tab_buttons:
            self.highlight_tab(self.current_list_id)

    def highlight_tab(self, list_id):
        self.current_list_id = list_id
        app = MDApp.get_running_app()

        for lid, btn in self.tab_buttons.items():
            if lid == list_id:
                btn.md_bg_color = (0.1, 0.45, 0.91, 1)
                btn.text_color = (1, 1, 1, 1)
            else:
                if app and app.theme_cls.theme_style == "Dark":
                    btn.md_bg_color = (0.2, 0.2, 0.2, 0.5)
                    btn.text_color = (1, 1, 1, 0.7)
                else:
                    btn.md_bg_color = (0.9, 0.9, 0.9, 0.5)
                    btn.text_color = (0, 0, 0, 0.7)

    def _on_tab_click(self, list_id):
        self.highlight_tab(list_id)
        if self.on_list_select:
            self.on_list_select(list_id)

    def set_lists(self, lists):
        self.lists = lists
        self.update_tabs()

    def select_list(self, list_id):
        self.highlight_tab(list_id)


class MainScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = DatabaseManager()
        self.current_category = TaskCategory.DAILY
        self.current_list_id = None
        self.current_list_name = ""
        self.current_list_index = 0
        self.category_lists = {}
        self.list_widgets = {}
        self.open_settings = None
        self.toolbar = None
        self.list_tabs = None

        self.build_ui()
        self.load_initial_data()

        app = MDApp.get_running_app()
        if app:
            app.theme_cls.bind(theme_style=self.on_theme_change)

    def update_toolbar_colors(self):
        if not self.toolbar:
            return
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            self.toolbar.specific_text_color = [0, 0, 0, 0.87]
        else:
            self.toolbar.specific_text_color = [1, 1, 1, 1]

    def on_theme_change(self, instance, value):
        if self.toolbar:
            self.toolbar.md_bg_color = self.get_toolbar_color()
            self.update_toolbar_colors()
            self.toolbar.left_action_items = [["menu", lambda x: self.toggle_nav_drawer()]]
            self.toolbar.right_action_items = [
                ["cog", lambda x: self.show_settings()],
                ["dots-vertical", lambda x: self.show_list_options()]
            ]

        # Update list tabs colors
        if self.list_tabs and self.current_list_id:
            self.list_tabs.highlight_tab(self.current_list_id)

        for list_id, task_list_widget in self.list_widgets.items():
            for child in task_list_widget.children:
                if isinstance(child, TaskItem):
                    child.update_theme_colors()

    def get_toolbar_color(self):
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return (0.12, 0.12, 0.12, 1)
        else:
            return (0.96, 0.96, 0.96, 1)

    def build_ui(self):
        self.nav_layout = MDNavigationLayout()
        from kivy.uix.screenmanager import ScreenManager, Screen
        screen_manager = ScreenManager()
        content_screen = Screen()
        content_box = MDBoxLayout(orientation='vertical')

        # Toolbar (NO + button here anymore)
        self.toolbar = MDTopAppBar(
            title="Daily Tasks",
            left_action_items=[["menu", lambda x: self.toggle_nav_drawer()]],
            right_action_items=[
                ["cog", lambda x: self.show_settings()],
                ["dots-vertical", lambda x: self.show_list_options()]
            ],
            elevation=2,
            md_bg_color=self.get_toolbar_color()
        )
        self.update_toolbar_colors()
        content_box.add_widget(self.toolbar)

        # List Tabs (Toolbar ke neeche)
        self.list_tabs = ListTabs(
            on_list_select=self.on_tab_list_select,
            on_add_list=self.show_add_list_dialog
        )
        content_box.add_widget(self.list_tabs)

        # List Swiper
        self.list_swiper = ListSwiper(on_list_change=self.on_swipe_list_change)
        content_box.add_widget(self.list_swiper)

        # FAB
        self.fab = MDFloatingActionButton(
            icon="plus",
            md_bg_color=(0.1, 0.45, 0.91, 1),
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.show_add_task_dialog,
            elevation=8
        )
        content_box.add_widget(self.fab)

        content_screen.add_widget(content_box)
        screen_manager.add_widget(content_screen)
        self.nav_layout.add_widget(screen_manager)

        # Sidebar (Only categories)
        self.nav_drawer = MDNavigationDrawer()
        nav_drawer_content = MDBoxLayout(
            orientation='vertical',
            padding=dp(8),
            spacing=dp(10)
        )

        # Header
        drawer_header = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=[dp(20), dp(24), dp(20), dp(16)]
        )
        with drawer_header.canvas.before:
            Color(0.1, 0.45, 0.91, 1)
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
            text="Time-Based Organization",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(20)
        ))
        nav_drawer_content.add_widget(drawer_header)

        # Categories scroll
        categories_scroll = MDScrollView()
        self.drawer_list = MDList()
        categories_scroll.add_widget(self.drawer_list)
        nav_drawer_content.add_widget(categories_scroll)

        self.nav_drawer.add_widget(nav_drawer_content)
        self.nav_layout.add_widget(self.nav_drawer)
        self.add_widget(self.nav_layout)

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def show_settings(self):
        if self.open_settings:
            self.open_settings()

    def load_initial_data(self):
        categories_data = self.db.get_all_categories_with_lists()
        self.category_lists = {cat_id: data['lists'] for cat_id, data in categories_data.items()}

        if self.category_lists[TaskCategory.DAILY]:
            self.current_category = TaskCategory.DAILY
            self.build_list_swiper()

        self.load_drawer_categories()

    def build_list_swiper(self):
        """Build swiper for current category"""
        self.list_swiper.unbind(index=self.list_swiper._on_index_change)
        self.list_swiper.clear_widgets()
        self.list_widgets.clear()

        lists = self.category_lists.get(self.current_category, [])

        # Update tabs
        self.list_tabs.set_lists(lists)

        for idx, task_list in enumerate(lists):
            scroll = MDScrollView()
            task_list_widget = MDList(padding=[dp(8), dp(12)])
            scroll.add_widget(task_list_widget)
            scroll.list_id = task_list.id
            scroll.list_index = idx
            self.list_widgets[task_list.id] = task_list_widget
            self.list_swiper.add_list_slide(scroll)

        self.list_swiper.bind(index=self.list_swiper._on_index_change)

        if lists:
            self.current_list_index = 0
            self.current_list_id = lists[0].id
            self.current_list_name = lists[0].name
            self.list_tabs.select_list(self.current_list_id)
            self.update_toolbar_title()
            self.load_tasks_for_list(self.current_list_id)

    def update_toolbar_title(self):
        """Update toolbar with category name"""
        cat_info = next((c for c in TaskCategory.get_all() if c['id'] == self.current_category), None)
        if cat_info:
            self.toolbar.title = f"{cat_info['icon']} {cat_info['name']}"

    def load_drawer_categories(self):
        """Load only categories in drawer"""
        self.drawer_list.clear_widgets()

        for cat in TaskCategory.get_all():
            cat_id = cat['id']
            lists = self.category_lists.get(cat_id, [])

            category_item = TwoLineIconListItem(
                text=f"{cat['icon']} {cat['name']}",
                secondary_text=f"{len(lists)} list(s)",
                on_release=lambda x, c=cat_id: self.switch_to_category(c)
            )

            icon = IconLeftWidget(icon="format-list-bulleted")
            category_item.add_widget(icon)
            self.drawer_list.add_widget(category_item)

    def switch_to_category(self, category):
        """Switch to category"""
        self.current_category = category
        self.build_list_swiper()
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")

    def on_tab_list_select(self, list_id):
        """Handle tab click"""
        lists = self.category_lists.get(self.current_category, [])

        for idx, lst in enumerate(lists):
            if lst.id == list_id:
                self.list_swiper.index = idx
                break

    def on_swipe_list_change(self, index):
        if index is None:
            return

        lists = self.category_lists.get(self.current_category, [])
        if 0 <= index < len(lists):
            task_list = lists[index]
            self.current_list_index = index
            self.current_list_id = task_list.id
            self.current_list_name = task_list.name
            self.list_tabs.select_list(task_list.id)
            self.load_tasks_for_list(task_list.id)

    def load_tasks_for_list(self, list_id):
        if list_id not in self.list_widgets:
            return

        task_list_widget = self.list_widgets[list_id]
        task_list_widget.clear_widgets()

        tasks = self.db.get_tasks_by_list(list_id, show_completed=True)
        tasks = tasks[:100]

        for task in tasks:
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
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton, MDRaisedButton

        dialog = MDDialog(
            title="Delete Task",
            text="Are you sure you want to delete this task?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.confirm_delete_task(task_id, dialog)
                ),
            ],
        )
        dialog.open()

    def confirm_delete_task(self, task_id, dialog):
        dialog.dismiss()
        self.db.delete_task(task_id)
        self.load_tasks()

    def open_task_details(self, task_id):
        pass

    def toggle_nav_drawer(self):
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
        else:
            self.nav_drawer.set_state("open")

    def show_list_options(self):
        from kivymd.uix.menu import MDDropdownMenu

        menu_items = [
            {"text": "Rename List", "viewclass": "OneLineListItem",
             "on_release": lambda: self.menu_action("rename")},
            {"text": "Delete List", "viewclass": "OneLineListItem",
             "on_release": lambda: self.menu_action("delete")},
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
            self.current_list_name = new_name
            self.reload_all_data()

    def delete_current_list(self):
        lists = self.category_lists.get(self.current_category, [])
        if self.current_list_id and len(lists) > 1:
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.button import MDFlatButton, MDRaisedButton

            dialog = MDDialog(
                title="Delete List",
                text=f"Delete '{self.current_list_name}' and all its tasks?",
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
                    MDRaisedButton(
                        text="DELETE",
                        md_bg_color=(0.9, 0.2, 0.2, 1),
                        on_release=lambda x: self.confirm_delete_list(dialog)
                    ),
                ],
            )
            dialog.open()

    def confirm_delete_list(self, dialog):
        self.db.delete_list(self.current_list_id)
        dialog.dismiss()
        self.reload_all_data()

    def show_add_list_dialog(self, *args):
        dialog = AddTaskDialog(self.add_list, title="New List", hint="List name")
        dialog.show()

    def add_list(self, name):
        self.db.create_list(name, self.current_category)
        self.reload_all_data()

    def reload_all_data(self):
        categories_data = self.db.get_all_categories_with_lists()
        self.category_lists = {cat_id: data['lists'] for cat_id, data in categories_data.items()}
        self.build_list_swiper()
        self.load_drawer_categories()