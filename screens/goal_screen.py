"""
MomentumTrack - Goal Tracking Screen
Complete implementation for long-term goal management
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton, MDFillRoundFlatIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import datetime


class GoalScreen(MDScreen):
    """Screen for managing long-term goals with progress tracking"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.build_ui()

    def build_ui(self):
        """Build goal management UI"""
        layout = BoxLayout(orientation='vertical', spacing=dp(12))

        # Header
        header = self.create_header()

        # Goals list with scroll
        scroll = ScrollView()
        self.goals_list = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=dp(16),
            size_hint_y=None
        )
        self.goals_list.bind(minimum_height=self.goals_list.setter('height'))
        scroll.add_widget(self.goals_list)

        # Add goal button
        add_btn_container = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(16))
        self.add_goal_btn = MDFillRoundFlatIconButton(
            icon="plus",
            text="Add New Goal",
            font_size="16sp",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.6, 0.3, 0.8, 1),
            on_release=lambda x: self.show_add_goal_dialog()
        )
        add_btn_container.add_widget(self.add_goal_btn)

        layout.add_widget(header)
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
            text="Long-term Goals",
            font_style="H5",
            bold=True
        )
        subtitle = MDLabel(
            text="Track your journey to success",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(back_btn)
        header.add_widget(title_box)

        return header

    def on_enter(self):
        """Load goals when entering screen"""
        self.load_goals()

    def load_goals(self):
        """Load all goals from database"""
        self.goals_list.clear_widgets()

        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        goals = app.db_manager.get_all_goals()

        if not goals:
            # Empty state
            empty_card = self.create_empty_state()
            self.goals_list.add_widget(empty_card)
            return

        for goal in goals:
            goal_id, title, description, target_date, progress, created_at = goal
            goal_card = self.create_goal_card(
                goal_id, title, description, target_date, progress
            )
            self.goals_list.add_widget(goal_card)

    def create_empty_state(self):
        """Create empty state card"""
        card = MDCard(
            orientation='vertical',
            padding=dp(40),
            size_hint_y=None,
            height=dp(250),
            elevation=0
        )

        icon = MDIcon(
            icon="target",
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Secondary",
            halign="center",
            font_size="80sp"
        )

        title = MDLabel(
            text="No Goals Yet",
            font_style="H6",
            halign="center",
            size_hint_y=None,
            height=dp(40)
        )

        subtitle = MDLabel(
            text="Set your first long-term goal\nand start your journey to success!",
            font_style="Body2",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(60)
        )

        card.add_widget(icon)
        card.add_widget(title)
        card.add_widget(subtitle)

        return card

    def create_goal_card(self, goal_id, title, description, target_date, progress):
        """Create a goal card with progress visualization"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(180),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        # Top row: Icon and title
        top_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(12)
        )

        icon = MDIcon(
            icon="target",
            theme_text_color="Custom",
            text_color=(0.6, 0.3, 0.8, 1),
            size_hint_x=None,
            width=dp(35),
            font_size="35sp"
        )

        title_label = MDLabel(
            text=title,
            font_style="H6",
            bold=True,
            size_hint_x=0.7
        )

        # Delete button
        delete_btn = MDIconButton(
            icon="delete-outline",
            theme_text_color="Secondary",
            icon_size="24sp",
            size_hint_x=None,
            width=dp(40),
            on_release=lambda x: self.confirm_delete_goal(goal_id)
        )

        top_row.add_widget(icon)
        top_row.add_widget(title_label)
        top_row.add_widget(delete_btn)

        # Description
        if description:
            desc_label = MDLabel(
                text=description,
                font_style="Body2",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(30)
            )
        else:
            desc_label = BoxLayout(size_hint_y=None, height=dp(5))

        # Progress section
        progress_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(8)
        )

        # Progress label
        progress_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(25)
        )

        progress_label = MDLabel(
            text=f"Progress: {progress}%",
            font_style="Body2",
            bold=True,
            size_hint_x=0.7
        )

        # Update progress button
        update_btn = MDFlatButton(
            text="Update",
            size_hint_x=0.3,
            on_release=lambda x: self.show_update_progress_dialog(goal_id, progress)
        )

        progress_row.add_widget(progress_label)
        progress_row.add_widget(update_btn)

        # Progress bar
        progress_bar = MDProgressBar(
            value=progress,
            size_hint_y=None,
            height=dp(8)
        )

        # Color based on progress
        if progress >= 75:
            progress_bar.color = (0.2, 0.7, 0.3, 1)  # Green
        elif progress >= 50:
            progress_bar.color = (0.2, 0.6, 0.9, 1)  # Blue
        elif progress >= 25:
            progress_bar.color = (0.9, 0.6, 0.2, 1)  # Orange
        else:
            progress_bar.color = (0.9, 0.3, 0.3, 1)  # Red

        progress_section.add_widget(progress_row)
        progress_section.add_widget(progress_bar)

        # Target date (if exists)
        if target_date:
            date_label = MDLabel(
                text=f"🎯 Target: {target_date}",
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(25)
            )
        else:
            date_label = BoxLayout(size_hint_y=None, height=dp(5))

        # Add all to card
        card.add_widget(top_row)
        card.add_widget(desc_label)
        card.add_widget(progress_section)
        card.add_widget(date_label)

        return card

    def show_add_goal_dialog(self):
        """Show dialog to add new goal"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(10),
            size_hint_y=None,
            height=dp(250)
        )

        self.goal_title_field = MDTextField(
            hint_text="Goal Title *",
            required=True,
            mode="rectangle"
        )

        self.goal_desc_field = MDTextField(
            hint_text="Description (optional)",
            multiline=True,
            mode="rectangle"
        )

        self.goal_date_field = MDTextField(
            hint_text="Target Date (YYYY-MM-DD)",
            mode="rectangle"
        )

        content.add_widget(self.goal_title_field)
        content.add_widget(self.goal_desc_field)
        content.add_widget(self.goal_date_field)

        self.dialog = MDDialog(
            title="🎯 Add New Goal",
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
                    text="ADD GOAL",
                    md_bg_color=(0.6, 0.3, 0.8, 1),
                    on_release=lambda x: self.add_goal()
                )
            ]
        )
        self.dialog.open()

    def add_goal(self):
        """Add goal to database"""
        if not self.goal_title_field.text:
            return

        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        target_date = self.goal_date_field.text if self.goal_date_field.text else None

        app.db_manager.add_goal(
            title=self.goal_title_field.text,
            description=self.goal_desc_field.text,
            target_date=target_date
        )

        self.dialog.dismiss()
        self.load_goals()

        from kivymd.toast import toast
        toast("✓ Goal added successfully!")

    def show_update_progress_dialog(self, goal_id, current_progress):
        """Show dialog to update goal progress"""
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(10),
            size_hint_y=None,
            height=dp(120)
        )

        current_label = MDLabel(
            text=f"Current Progress: {current_progress}%",
            font_style="Body2",
            size_hint_y=None,
            height=dp(30)
        )

        self.progress_field = MDTextField(
            hint_text="New Progress (0-100)",
            mode="rectangle",
            text=str(current_progress),
            input_filter="int"
        )

        content.add_widget(current_label)
        content.add_widget(self.progress_field)

        self.dialog = MDDialog(
            title="📊 Update Progress",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="UPDATE",
                    md_bg_color=(0.2, 0.6, 0.9, 1),
                    on_release=lambda x: self.update_progress(goal_id)
                )
            ]
        )
        self.dialog.open()

    def update_progress(self, goal_id):
        """Update goal progress"""
        try:
            new_progress = int(self.progress_field.text)
            if 0 <= new_progress <= 100:
                from kivymd.app import MDApp
                app = MDApp.get_running_app()
                app.db_manager.update_goal_progress(goal_id, new_progress)

                self.dialog.dismiss()
                self.load_goals()

                from kivymd.toast import toast
                toast(f"✓ Progress updated to {new_progress}%!")
            else:
                from kivymd.toast import toast
                toast("⚠️ Progress must be between 0 and 100")
        except ValueError:
            from kivymd.toast import toast
            toast("⚠️ Please enter a valid number")

    def confirm_delete_goal(self, goal_id):
        """Confirm before deleting goal"""
        self.dialog = MDDialog(
            title="Delete Goal?",
            text="This action cannot be undone.",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.delete_goal(goal_id)
                )
            ]
        )
        self.dialog.open()

    def delete_goal(self, goal_id):
        """Delete goal from database"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        conn = app.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
        conn.commit()
        conn.close()

        self.dialog.dismiss()
        self.load_goals()

        from kivymd.toast import toast
        toast("✓ Goal deleted")

    def go_back(self):
        """Navigate back to home"""
        self.manager.current = 'home'