from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineIconListItem, IconLeftWidget
from kivymd.uix.button import MDIconButton, MDFloatingActionButton, MDFlatButton
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.toast import toast
from components.task_item import TaskItem
from components.list_swiper import ListSwiper
from components.dialogs import CreateTaskDialog, EditListDialog, ConfirmDialog
from database.db_manager import DatabaseManager
from database.models import TaskCategory
from utils.constants import Colors, MAX_TASKS_PER_LIST
from components.quick_actions import QuickActionsBar
from components.task_item_enhanced import TaskItemEnhanced
from utils.gesture_handler import PullToRefreshHandler

class ListTabs(MDBoxLayout):
    """Clean horizontal tabs like Google Tasks"""

    def __init__(self, lists=None, on_list_select=None, on_add_list=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(48)
        self.padding = [dp(4), 0]
        self.spacing = 0

        self.lists = lists or []
        self.on_list_select = on_list_select
        self.on_add_list = on_add_list
        self.current_list_id = None
        self.tab_buttons = {}

        # Add bottom border
        with self.canvas.after:
            self.border_color = Color(0.9, 0.9, 0.9, 1)
            self.border_line = Line(width=1)

        self.bind(pos=self._update_border, size=self._update_border)

        # Scrollable container
        self.scroll = MDScrollView(
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=0,
            size_hint_x=1
        )

        self.tab_container = MDBoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=0,
            padding=[dp(8), 0]
        )
        self.tab_container.bind(minimum_width=self.tab_container.setter('width'))

        self.scroll.add_widget(self.tab_container)
        self.add_widget(self.scroll)

        # Add button - minimal icon style
        self.add_btn = MDIconButton(
            icon="plus",
            size_hint=(None, None),
            size=(dp(48), dp(48)),
            on_release=lambda x: self.on_add_list() if self.on_add_list else None
        )
        self.add_widget(self.add_btn)

        self.update_tabs()

    def _update_border(self, *args):
        """Update bottom border line"""
        self.border_line.points = [
            self.x, self.y,
            self.x + self.width, self.y
        ]
        # Update border color based on theme
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            self.border_color.rgba = (0.3, 0.3, 0.3, 1)
        else:
            self.border_color.rgba = (0.9, 0.9, 0.9, 1)

    def update_tabs(self):
        """Create clean tab buttons"""
        self.tab_container.clear_widgets()
        self.tab_buttons.clear()

        for lst in self.lists:
            # Create tab button container
            tab_wrapper = MDBoxLayout(
                orientation='vertical',
                size_hint=(None, None),
                size=(dp(120), dp(48)),
                spacing=0
            )

            # Tab button
            btn = MDFlatButton(
                text=lst.name,
                size_hint=(None, None),
                size=(dp(120), dp(45)),
                on_release=lambda x, lid=lst.id: self._on_tab_click(lid),
                md_bg_color=(0, 0, 0, 0)  # Transparent background
            )

            # Bottom indicator line (will be drawn in canvas)
            tab_wrapper.btn = btn
            tab_wrapper.list_id = lst.id

            with tab_wrapper.canvas.after:
                tab_wrapper.indicator_color = Color(0, 0, 0, 0)  # Hidden by default
                tab_wrapper.indicator = Line(width=3)

            tab_wrapper.bind(pos=self._update_indicator, size=self._update_indicator)
            tab_wrapper.add_widget(btn)

            self.tab_buttons[lst.id] = tab_wrapper
            self.tab_container.add_widget(tab_wrapper)

        if self.current_list_id and self.current_list_id in self.tab_buttons:
            self.highlight_tab(self.current_list_id)

    def _update_indicator(self, instance, value):
        """Update indicator line position"""
        if hasattr(instance, 'indicator'):
            # Draw line at bottom of tab
            instance.indicator.points = [
                instance.x, instance.y,
                instance.x + instance.width, instance.y
            ]

    def highlight_tab(self, list_id):
        """Highlight selected tab with minimal style"""
        self.current_list_id = list_id
        app = MDApp.get_running_app()
        is_dark = app and app.theme_cls.theme_style == "Dark"

        for lid, tab_wrapper in self.tab_buttons.items():
            btn = tab_wrapper.btn

            if lid == list_id:
                # Active tab - Blue text and indicator
                btn.text_color = Colors.PRIMARY_BLUE
                tab_wrapper.indicator_color.rgba = Colors.PRIMARY_BLUE
            else:
                # Inactive tab - Gray text, no indicator
                if is_dark:
                    btn.text_color = (0.7, 0.7, 0.7, 1)
                else:
                    btn.text_color = (0.4, 0.4, 0.4, 1)
                tab_wrapper.indicator_color.rgba = (0, 0, 0, 0)  # Hide indicator

    def _on_tab_click(self, list_id):
        """Handle tab click"""
        self.highlight_tab(list_id)
        if self.on_list_select:
            self.on_list_select(list_id)

    def set_lists(self, lists):
        """Update lists and rebuild tabs"""
        self.lists = lists
        self.update_tabs()

    def select_list(self, list_id):
        """Programmatically select a list"""
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
        self.loading_spinner = None
        self._theme_bound = False

        self.build_ui()
        self.load_initial_data()

        # Bind theme changes
        app = MDApp.get_running_app()
        if app:
            app.theme_cls.bind(theme_style=self.on_theme_change)
            self._theme_bound = True

    def on_pre_leave(self):
        """Unbind theme when leaving screen"""
        if self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.unbind(theme_style=self.on_theme_change)
                self._theme_bound = False

    def on_pre_enter(self):
        """Re-bind theme when entering screen"""
        if not self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.bind(theme_style=self.on_theme_change)
                self._theme_bound = True

    def update_toolbar_colors(self):
        if not self.toolbar:
            return
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            self.toolbar.specific_text_color = Colors.LIGHT_TEXT
        else:
            self.toolbar.specific_text_color = Colors.DARK_TEXT

    def on_theme_change(self, instance, value):
        """Handle theme changes efficiently"""
        if self.toolbar:
            self.toolbar.md_bg_color = self.get_toolbar_color()
            self.update_toolbar_colors()
            # Rebuild action items to apply color
            self.toolbar.left_action_items = [["menu", lambda x: self.toggle_nav_drawer()]]
            self.toolbar.right_action_items = [
                ["cog", lambda x: self.show_settings()],
                ["dots-vertical", lambda x: self.show_list_options()]
            ]

        # Update list tabs
        if self.list_tabs and self.current_list_id:
            self.list_tabs.highlight_tab(self.current_list_id)

        # Update all visible task items
        for list_id, task_list_widget in self.list_widgets.items():
            for child in task_list_widget.children:
                if isinstance(child, TaskItem):
                    child.update_theme_colors()

    def get_toolbar_color(self):
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return Colors.DARK_BG
        return Colors.LIGHT_BG

    def build_ui(self):
        self.nav_layout = MDNavigationLayout()
        from kivy.uix.screenmanager import ScreenManager, Screen
        screen_manager = ScreenManager()
        content_screen = Screen()
        content_box = MDBoxLayout(orientation='vertical')

        # Toolbar
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

        # List Tabs
        self.list_tabs = ListTabs(
            on_list_select=self.on_tab_list_select,
            on_add_list=self.show_add_list_dialog
        )
        content_box.add_widget(self.list_tabs)

        # Add quick actions bar
        self.quick_actions = QuickActionsBar(
            callbacks={
                'add_task': self.show_add_task_dialog,
                'search': self.show_search,
                'sort': self.show_sort_options,
                'filter': self.show_filter_options
            },
            pos_hint={'center_x': 0.5, 'y': 0.02}
        )
        content_box.add_widget(self.quick_actions)

        # List Swiper
        self.list_swiper = ListSwiper(on_list_change=self.on_swipe_list_change)
        content_box.add_widget(self.list_swiper)

        # FAB
        self.fab = MDFloatingActionButton(
            icon="plus",
            md_bg_color=Colors.PRIMARY_BLUE,
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.show_add_task_dialog,
            elevation=8
        )
        content_box.add_widget(self.fab)

        content_screen.add_widget(content_box)
        screen_manager.add_widget(content_screen)
        self.nav_layout.add_widget(screen_manager)

        # Sidebar
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
            Color(*Colors.PRIMARY_BLUE)
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
        # Clear existing slides safely
        self.list_swiper.clear_slides()
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

        if lists:
            self.current_list_index = 0
            self.current_list_id = lists[0].id
            self.current_list_name = lists[0].name
            self.list_tabs.select_list(self.current_list_id)
            self.update_toolbar_title()
            self.load_tasks_for_list(self.current_list_id)

            # Add pull-to-refresh
            refresh_handler = PullToRefreshHandler(
                scroll,
                on_refresh=lambda: self.refresh_list(task_list.id)
            )
            self.refresh_handlers[task_list.id] = refresh_handler

    def refresh_list(self, list_id):
        """Refresh specific list"""
        self.load_tasks_for_list(list_id)
        # Call finish_refresh after loading
        if list_id in self.refresh_handlers:
            self.refresh_handlers[list_id].finish_refresh()




    def update_toolbar_title(self):
        """Update toolbar with category name - WITHOUT EMOJI"""
        cat_info = next((c for c in TaskCategory.get_all() if c['id'] == self.current_category), None)
        if cat_info:
            self.toolbar.title = cat_info['name']

    def load_drawer_categories(self):
        """Load only categories in drawer - WITHOUT EMOJIS"""
        self.drawer_list.clear_widgets()

        for cat in TaskCategory.get_all():
            cat_id = cat['id']
            lists = self.category_lists.get(cat_id, [])

            category_item = TwoLineIconListItem(
                text=cat['name'],
                secondary_text=f"{len(lists)} lists",
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
                self.list_swiper.safe_set_index(idx)
                break

    def on_swipe_list_change(self, index):
        """Handle swipe change"""
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

    def show_loading(self):
        """Show loading spinner"""
        if not self.loading_spinner:
            self.loading_spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(46), dp(46)),
                pos_hint={'center_x': .5, 'center_y': .5}
            )

        if self.loading_spinner not in self.children:
            self.add_widget(self.loading_spinner)

    def hide_loading(self):
        """Hide loading spinner"""
        if self.loading_spinner and self.loading_spinner in self.children:
            self.remove_widget(self.loading_spinner)

    def load_tasks_for_list(self, list_id):
        """Load tasks for a specific list with limit warning"""
        if list_id not in self.list_widgets:
            print(f"Warning: List widget not found for list_id {list_id}")
            return

        task_list_widget = self.list_widgets[list_id]
        task_list_widget.clear_widgets()

        try:
            tasks = self.db.get_tasks_by_list(list_id, show_completed=True)

            # Show warning if tasks exceed limit
            if len(tasks) > MAX_TASKS_PER_LIST:
                toast(f"Showing first {MAX_TASKS_PER_LIST} of {len(tasks)} tasks")

            tasks = tasks[:MAX_TASKS_PER_LIST]

            for task in tasks:
                # Use enhanced task item instead of basic one
                task_item = TaskItemEnhanced(
                    task_id=task.id,
                    task_title=task.title,
                    task_notes=task.notes,
                    task_start_time=task.start_time or "",
                    task_end_time=task.end_time or "",
                    task_recurrence=task.recurrence_type or "",
                    task_motivation=task.motivation or "",
                    task_completed=task.completed,
                    on_task_click=self.open_task_details,
                    on_toggle_complete=self.toggle_task_completed,
                    on_delete=self.delete_task,
                    on_edit=self.edit_task,
                    on_duplicate=self.duplicate_task
                )
                task_list_widget.add_widget(task_item)

                # Add subtasks
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
                    # Apply theme to subtasks too
                    subtask_item.update_theme_colors()
                    task_list_widget.add_widget(subtask_item)

        except Exception as e:
            print(f"Error loading tasks: {e}")
            toast("Error loading tasks")

    def load_tasks(self):
        """Reload current list tasks"""
        if self.current_list_id:
            self.load_tasks_for_list(self.current_list_id)

    def show_add_task_dialog(self, *args):
        """Show comprehensive task creation dialog"""
        if not self.current_list_id:
            toast("No list selected")
            return

        dialog = CreateTaskDialog(self.add_task, self.current_list_id)
        dialog.show()

    def add_task(self, task_data):
        """Add new task with comprehensive data"""
        if not self.current_list_id:
            toast("No list selected")
            return

        try:
            # Create task with all fields
            task_id = self.db.create_task(
                list_id=self.current_list_id,
                title=task_data['name'],
                notes=task_data['description'],
                start_time=task_data['start_time'],
                end_time=task_data['end_time'],
                reminder_time=task_data['reminder'],
                motivation=task_data['motivation']
            )

            if task_id:
                # Reload tasks for current list
                self.load_tasks_for_list(self.current_list_id)
                toast("✅ Task created successfully!")
            else:
                toast("Failed to create task")

        except ValueError as e:
            toast(f"Invalid task: {e}")
        except Exception as e:
            print(f"Error adding task: {e}")
            toast("Failed to add task")

    def toggle_task_completed(self, task_id, completed):
        try:
            self.db.toggle_task_completed(task_id)
            self.load_tasks()
        except Exception as e:
            print(f"Error toggling task: {e}")
            toast("Error updating task")

    def delete_task(self, task_id):
        dialog = ConfirmDialog(
            title="Delete Task",
            message="Are you sure you want to delete this task?",
            callback=lambda: self.confirm_delete_task(task_id),
            confirm_text="DELETE"
        )
        dialog.show()

    def confirm_delete_task(self, task_id):
        try:
            self.db.delete_task(task_id)
            self.load_tasks()
            toast("Task deleted")
        except Exception as e:
            print(f"Error deleting task: {e}")
            toast("Error deleting task")

    def open_task_details(self, task_id):
        """Will be set by main app"""
        pass

    def toggle_nav_drawer(self):
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
        else:
            self.nav_drawer.set_state("open")

    def on_back_button(self):
        """Handle back button press"""
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
            return True
        return False

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
            try:
                self.db.update_list(self.current_list_id, new_name)
                self.current_list_name = new_name
                self.reload_category_data()
                toast("List renamed")
            except ValueError as e:
                toast(f"Error: {e}")

    def delete_current_list(self):
        lists = self.category_lists.get(self.current_category, [])
        if self.current_list_id and len(lists) > 1:
            dialog = ConfirmDialog(
                title="Delete List",
                message=f"Delete '{self.current_list_name}' and all its tasks?",
                callback=self.confirm_delete_list,
                confirm_text="DELETE"
            )
            dialog.show()
        else:
            toast("Cannot delete the last list")

    def confirm_delete_list(self):
        try:
            self.db.delete_list(self.current_list_id)
            self.reload_category_data()
            toast("List deleted")
        except Exception as e:
            print(f"Error deleting list: {e}")
            toast("Error deleting list")

    def show_add_list_dialog(self, *args):
        dialog = AddTaskDialog(self.add_list, title="New List", hint="List name")
        dialog.show()

    def add_list(self, name):
        try:
            self.db.create_list(name, self.current_category)
            self.reload_category_data()
            toast("List created")
        except ValueError as e:
            toast(f"Error: {e}")

    def reload_category_data(self, category=None):
        """Reload only specific category data - optimized"""
        target = category or self.current_category
        self.category_lists[target] = self.db.get_lists_by_category(target)

        if target == self.current_category:
            self.build_list_swiper()

        self.load_drawer_categories()

    def reload_all_data(self):
        """Full reload - use sparingly"""
        categories_data = self.db.get_all_categories_with_lists()
        self.category_lists = {cat_id: data['lists'] for cat_id, data in categories_data.items()}
        self.build_list_swiper()
        self.load_drawer_categories()

    def show_search(self):
        """Show search dialog"""
        # Implement search functionality
        pass

    def show_sort_options(self):
        """Show sort menu"""
        # Implement sort menu
        pass

    def show_filter_options(self):
        """Show filter options"""
        # Implement filter dialog
        pass