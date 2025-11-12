from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, TwoLineIconListItem, IconLeftWidget
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.toast import toast
from components.task_item import TaskItem
from components.list_swiper import ListSwiper
from components.list_tabs import ListTabs
from components.dialogs import CreateTaskDialog, EditListDialog, ConfirmDialog, AddTaskDialog
from database.models import TaskCategory
from services.task_service import TaskService, ListService
from utils.constants import Colors
from utils.event_system import event_bus, TaskEvents


class MainScreen(MDScreen):
    def __init__(self, task_service: TaskService, list_service: ListService, **kwargs):
        super().__init__(**kwargs)

        # USE SERVICE LAYER instead of direct DB access!
        self.task_service = task_service
        self.list_service = list_service

        # State
        self.current_category = TaskCategory.DAILY
        self.current_list_id = None
        self.current_list_name = ""
        self.current_list_index = 0
        self.category_lists = {}
        self.list_widgets = {}

        # Callbacks
        self.open_settings = None

        # UI components
        self.toolbar = None
        self.list_tabs = None
        self.loading_spinner = None

        # Theme management
        self._theme_bound = False
        self._theme_update_scheduled = False

        self.build_ui()
        self.load_initial_data()

        # Setup event listeners
        self._setup_event_listeners()

        # Bind theme changes
        app = MDApp.get_running_app()
        if app:
            app.theme_cls.bind(theme_style=self.on_theme_change)
            self._theme_bound = True

    def _setup_event_listeners(self):
        """Setup event listeners for reactive updates"""
        # Listen to task events
        self.task_service.events.on(TaskEvents.TASK_CREATED, self.on_task_event)
        self.task_service.events.on(TaskEvents.TASK_DELETED, self.on_task_event)
        self.task_service.events.on(TaskEvents.TASK_UPDATED, self.on_task_event)
        self.task_service.events.on(TaskEvents.TASK_COMPLETED, self.on_task_event)

        # Listen to list events
        self.list_service.events.on(TaskEvents.LIST_CREATED, self.on_list_event)
        self.list_service.events.on(TaskEvents.LIST_DELETED, self.on_list_event)
        self.list_service.events.on(TaskEvents.LIST_UPDATED, self.on_list_event)

    def on_task_event(self, *args):
        """Handle task events - reload current list"""
        if self.current_list_id:
            # Use Clock to schedule UI update on main thread
            Clock.schedule_once(lambda dt: self.load_tasks_for_list(self.current_list_id), 0)

    def on_list_event(self, *args):
        """Handle list events - reload category"""
        Clock.schedule_once(lambda dt: self.reload_category_data(), 0)

    def on_pre_leave(self):
        """Unbind theme when leaving screen"""
        if self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.unbind(theme_style=self.on_theme_change)
                self._theme_bound = False

        # Cleanup event listeners
        self.task_service.events.off(TaskEvents.TASK_CREATED)
        self.task_service.events.off(TaskEvents.TASK_DELETED)
        self.task_service.events.off(TaskEvents.TASK_UPDATED)
        self.task_service.events.off(TaskEvents.TASK_COMPLETED)
        self.list_service.events.off(TaskEvents.LIST_CREATED)
        self.list_service.events.off(TaskEvents.LIST_DELETED)
        self.list_service.events.off(TaskEvents.LIST_UPDATED)

    def on_pre_enter(self):
        """Re-bind theme when entering screen"""
        if not self._theme_bound:
            app = MDApp.get_running_app()
            if app:
                app.theme_cls.bind(theme_style=self.on_theme_change)
                self._theme_bound = True

    def update_toolbar_colors(self):
        """Update toolbar colors based on theme"""
        if not self.toolbar:
            return
        app = MDApp.get_running_app()
        if app.theme_cls.theme_style == "Light":
            self.toolbar.specific_text_color = Colors.LIGHT_TEXT
        else:
            self.toolbar.specific_text_color = Colors.DARK_TEXT

    def on_theme_change(self, instance, value):
        """Handle theme changes - BATCHED"""
        if self._theme_update_scheduled:
            return

        self._theme_update_scheduled = True
        Clock.schedule_once(self._apply_theme_update, 0)

    def _apply_theme_update(self, dt):
        """Apply theme update in batch"""
        self._theme_update_scheduled = False

        # Update toolbar
        if self.toolbar:
            self.toolbar.md_bg_color = self.get_toolbar_color()
            self.update_toolbar_colors()
            self.toolbar.left_action_items = [["menu", lambda x: self.toggle_nav_drawer()]]
            self.toolbar.right_action_items = [
                ["cog", lambda x: self.show_settings()],
                ["dots-vertical", lambda x: self.show_list_options()]
            ]

        # Update list tabs
        if self.list_tabs and self.current_list_id:
            self.list_tabs.highlight_tab(self.current_list_id)

        # Update visible task items
        if self.current_list_id in self.list_widgets:
            task_list_widget = self.list_widgets[self.current_list_id]
            for child in task_list_widget.children:
                if isinstance(child, TaskItem):
                    child.update_theme_colors()

    def get_toolbar_color(self):
        """Get toolbar color based on theme"""
        app = MDApp.get_running_app()
        if app and app.theme_cls.theme_style == "Dark":
            return Colors.DARK_BG
        return Colors.LIGHT_BG

    def build_ui(self):
        """Build the UI (same as before)"""
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
        """Load initial category data - USES SERVICE LAYER"""
        try:
            # Load all categories with lists
            for cat in TaskCategory.get_all():
                lists = self.list_service.get_lists_by_category(cat['id'])
                self.category_lists[cat['id']] = lists

            if self.category_lists[TaskCategory.DAILY]:
                self.current_category = TaskCategory.DAILY
                self.build_list_swiper()

            self.load_drawer_categories()
        except Exception as e:
            print(f"❌ Error loading initial data: {e}")
            toast("Error loading data")

    def build_list_swiper(self):
        """Build swiper for current category"""
        self.list_swiper.clear_slides()

        for list_id, widget in self.list_widgets.items():
            widget.clear_widgets()

        self.list_widgets.clear()

        lists = self.category_lists.get(self.current_category, [])
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

    def update_toolbar_title(self):
        """Update toolbar with category name"""
        cat_info = next((c for c in TaskCategory.get_all() if c['id'] == self.current_category), None)
        if cat_info:
            self.toolbar.title = cat_info['name']

    def load_drawer_categories(self):
        """Load categories in drawer"""
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

    def load_tasks_for_list(self, list_id):
        """Load tasks - USES SERVICE LAYER with caching!"""
        if list_id not in self.list_widgets:
            return

        task_list_widget = self.list_widgets[list_id]
        task_list_widget.clear_widgets()

        try:
            # SERVICE LAYER handles caching and optimization!
            tasks = self.task_service.get_list_tasks(
                list_id,
                show_completed=True,
                use_cache=True  # Use cache for better performance
            )

            for task in tasks:
                task_item = TaskItem(
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
                    on_delete=self.delete_task
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
                    subtask_item.update_theme_colors()
                    task_list_widget.add_widget(subtask_item)

        except Exception as e:
            print(f"❌ Error loading tasks: {e}")
            toast("Error loading tasks")

    def load_tasks(self):
        """Reload current list tasks"""
        if self.current_list_id:
            self.load_tasks_for_list(self.current_list_id)

    def show_add_task_dialog(self, *args):
        """Show task creation dialog"""
        if not self.current_list_id:
            toast("No list selected")
            return

        dialog = CreateTaskDialog(self.add_task, self.current_list_id)
        dialog.show()

    def add_task(self, task_data):
        """Add new task - USES SERVICE LAYER"""
        if not self.current_list_id:
            toast("No list selected")
            return

        try:
            # SERVICE LAYER handles validation and events!
            task_id = self.task_service.create_task(
                list_id=self.current_list_id,
                title=task_data['name'],
                notes=task_data['description'],
                start_time=task_data['start_time'],
                end_time=task_data['end_time'],
                reminder_time=task_data['reminder'],
                motivation=task_data['motivation']
            )

            if task_id:
                toast("✅ Task created!")
                # Event listener will auto-reload

        except ValueError as e:
            toast(f"Invalid task: {e}")
        except Exception as e:
            print(f"❌ Error adding task: {e}")
            toast("Failed to add task")

    def toggle_task_completed(self, task_id, completed):
        """Toggle task completion - USES SERVICE LAYER"""
        try:
            self.task_service.toggle_task_completed(task_id)
            # Event listener will auto-reload
        except Exception as e:
            print(f"❌ Error toggling task: {e}")
            toast("Error updating task")

    def delete_task(self, task_id):
        """Delete task with confirmation"""
        dialog = ConfirmDialog(
            title="Delete Task",
            message="Are you sure you want to delete this task?",
            callback=lambda: self.confirm_delete_task(task_id),
            confirm_text="DELETE"
        )
        dialog.show()

    def confirm_delete_task(self, task_id):
        """Confirm and delete task - USES SERVICE LAYER"""
        try:
            self.task_service.delete_task(task_id)
            toast("Task deleted")
            # Event listener will auto-reload
        except Exception as e:
            print(f"❌ Error deleting task: {e}")
            toast("Error deleting task")

    def open_task_details(self, task_id):
        """Will be set by main app"""
        pass

    def toggle_nav_drawer(self):
        """Toggle navigation drawer"""
        if self.nav_drawer.state == "open":
            self.nav_drawer.set_state("close")
        else:
            self.nav_drawer.set_state("open")

    def show_list_options(self):
        """Show list options menu"""
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
        """Handle menu actions"""
        self.menu.dismiss()
        if action == "rename":
            dialog = EditListDialog(self.current_list_name, self.rename_list)
            dialog.show()
        elif action == "delete":
            self.delete_current_list()

    def rename_list(self, new_name):
        """Rename current list - USES SERVICE LAYER"""
        if self.current_list_id:
            try:
                self.list_service.update_list(self.current_list_id, new_name)
                self.current_list_name = new_name
                toast("List renamed")
                # Event listener will auto-reload
            except ValueError as e:
                toast(f"Error: {e}")

    def delete_current_list(self):
        """Delete current list with confirmation"""
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
        """Confirm and delete list - USES SERVICE LAYER"""
        try:
            self.list_service.delete_list(self.current_list_id)
            toast("List deleted")
            # Event listener will auto-reload
        except Exception as e:
            print(f"❌ Error deleting list: {e}")
            toast("Error deleting list")

    def show_add_list_dialog(self, *args):
        """Show dialog to add new list"""
        dialog = AddTaskDialog(self.add_list, title="New List", hint="List name")
        dialog.show()

    def add_list(self, name):
        """Add new list - USES SERVICE LAYER"""
        try:
            self.list_service.create_list(name, self.current_category)
            toast("List created")
            # Event listener will auto-reload
        except ValueError as e:
            toast(f"Error: {e}")

    def reload_category_data(self, category=None):
        """Reload category data - USES SERVICE LAYER"""
        target = category or self.current_category

        # Force refresh from service (bypasses cache)
        self.category_lists[target] = self.list_service.get_lists_by_category(
            target,
            force_refresh=True
        )

        if target == self.current_category:
            self.build_list_swiper()

        self.load_drawer_categories()