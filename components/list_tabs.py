from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.metrics import dp
from kivymd.app import MDApp


class ListTabs(MDBoxLayout):
    """Horizontal scrollable tabs showing list names"""

    def __init__(self, lists=None, on_list_select=None, on_add_list=None, **kwargs):
        super().__init__(**kwargs)
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

        # Scrollable container for tabs
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

        # Add "+" button (fixed on right)
        self.add_btn = MDRaisedButton(
            text="+",
            size_hint=(None, None),
            size=(dp(48), dp(40)),
            md_bg_color=(0.1, 0.45, 0.91, 1),  # Blue
            on_release=self._on_add_list,
            elevation=4
        )
        self.add_widget(self.add_btn)

        self.update_tabs()

    def update_tabs(self):
        """Update tabs with current lists"""
        self.tab_container.clear_widgets()
        self.tab_buttons.clear()

        for lst in self.lists:
            btn = MDFlatButton(
                text=lst.name,
                size_hint=(None, None),
                size=(dp(120), dp(40)),
                on_release=lambda x, lid=lst.id: self._on_tab_click(lid)
            )

            # Store reference
            self.tab_buttons[lst.id] = btn
            self.tab_container.add_widget(btn)

        # Highlight current tab
        if self.current_list_id and self.current_list_id in self.tab_buttons:
            self.highlight_tab(self.current_list_id)

    def highlight_tab(self, list_id):
        """Highlight selected tab"""
        self.current_list_id = list_id

        app = MDApp.get_running_app()
        for lid, btn in self.tab_buttons.items():
            if lid == list_id:
                # Selected tab - Blue background
                btn.md_bg_color = (0.1, 0.45, 0.91, 1)
                btn.text_color = (1, 1, 1, 1)
            else:
                # Unselected tab - Transparent with theme text
                if app and app.theme_cls.theme_style == "Dark":
                    btn.md_bg_color = (0.2, 0.2, 0.2, 0.5)
                    btn.text_color = (1, 1, 1, 0.7)
                else:
                    btn.md_bg_color = (0.9, 0.9, 0.9, 0.5)
                    btn.text_color = (0, 0, 0, 0.7)

    def _on_tab_click(self, list_id):
        """Handle tab click"""
        self.highlight_tab(list_id)
        if self.on_list_select:
            self.on_list_select(list_id)

    def _on_add_list(self, *args):
        """Handle add list button"""
        if self.on_add_list:
            self.on_add_list()

    def set_lists(self, lists):
        """Update lists and rebuild tabs"""
        self.lists = lists
        self.update_tabs()

    def select_list(self, list_id):
        """Programmatically select a list"""
        self.highlight_tab(list_id)