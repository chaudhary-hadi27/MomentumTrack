from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.slider import MDSlider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from datetime import datetime
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.uix.widget import Widget
from math import cos, sin, pi


class PieChart(Widget):
    """Custom pie chart widget for 8/8/8 visualization"""

    def __init__(self, work=0, personal=0, sleep=0, **kwargs):
        super().__init__(**kwargs)
        self.work = work
        self.personal = personal
        self.sleep = sleep
        self.bind(pos=self.update_chart, size=self.update_chart)

    def update_chart(self, *args):
        """Draw the pie chart"""
        self.canvas.clear()

        total = self.work + self.personal + self.sleep
        if total == 0:
            total = 24  # Default to 24 hours

        # Calculate percentages
        work_percent = (self.work / total) * 360
        personal_percent = (self.personal / total) * 360
        sleep_percent = (self.sleep / total) * 360

        # Center and radius
        center_x = self.center_x
        center_y = self.center_y
        radius = min(self.width, self.height) / 2 - 20

        with self.canvas:
            # Work segment (Blue)
            Color(0.2, 0.6, 0.9, 1)
            self.draw_arc(center_x, center_y, radius, 0, work_percent)

            # Personal segment (Green)
            Color(0.3, 0.7, 0.4, 1)
            self.draw_arc(center_x, center_y, radius, work_percent, work_percent + personal_percent)

            # Sleep segment (Purple)
            Color(0.6, 0.3, 0.8, 1)
            self.draw_arc(center_x, center_y, radius, work_percent + personal_percent, 360)

            # Center circle (white/background)
            from kivymd.app import MDApp
            app = MDApp.get_running_app()
            if app.theme_cls.theme_style == "Dark":
                Color(0.15, 0.15, 0.15, 1)
            else:
                Color(1, 1, 1, 1)
            Ellipse(pos=(center_x - radius * 0.6, center_y - radius * 0.6),
                    size=(radius * 1.2, radius * 1.2))

    def draw_arc(self, center_x, center_y, radius, start_angle, end_angle):
        """Draw an arc segment"""
        if end_angle - start_angle <= 0:
            return

        points = [center_x, center_y]
        num_segments = 50

        for i in range(num_segments + 1):
            angle = start_angle + (end_angle - start_angle) * i / num_segments
            rad = angle * pi / 180
            x = center_x + radius * cos(rad)
            y = center_y + radius * sin(rad)
            points.extend([x, y])

        from kivy.graphics import Mesh
        vertices = []
        indices = []
        for i in range(len(points) // 2):
            vertices.extend([points[i * 2], points[i * 2 + 1], 0, 0])
            if i > 1:
                indices.extend([0, i - 1, i])

        Mesh(vertices=vertices, indices=indices, mode='triangles')


class TimeTrackerScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.work_hours = 0
        self.personal_hours = 0
        self.sleep_hours = 0
        self.build_ui()

    def build_ui(self):
        """Build time tracker UI"""
        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16), size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        # Header
        header = self.create_header()

        # Date card
        date_card = self.create_date_card()

        # Pie chart visualization
        chart_card = self.create_chart_card()

        # Time sliders
        sliders_card = self.create_sliders_card()

        # Balance indicator
        balance_card = self.create_balance_card()

        # Save button
        save_btn = MDFillRoundFlatButton(
            text="💾 Save Today's Time",
            font_size="16sp",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=(0.2, 0.6, 0.9, 1),
            on_release=lambda x: self.save_time_block()
        )

        # Add all to layout
        layout.add_widget(header)
        layout.add_widget(date_card)
        layout.add_widget(chart_card)
        layout.add_widget(sliders_card)
        layout.add_widget(balance_card)
        layout.add_widget(save_btn)

        scroll.add_widget(layout)
        self.add_widget(scroll)

    def create_header(self):
        """Create header"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            padding=[0, dp(8), 0, dp(8)]
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            pos_hint={"center_y": 0.5},
            icon_size="28sp",
            on_release=lambda x: self.go_back()
        )

        title_box = BoxLayout(orientation='vertical', size_hint_x=0.7)
        title = MDLabel(
            text="8/8/8 Time Balance",
            font_style="H5",
            bold=True
        )
        subtitle = MDLabel(
            text="Track your daily time distribution",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(back_btn)
        header.add_widget(title_box)

        return header

    def create_date_card(self):
        """Create date display card"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(100),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        date_label = MDLabel(
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font_style="H6",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        )

        info_label = MDLabel(
            text="Balance your day: Work • Personal • Sleep",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )

        card.add_widget(date_label)
        card.add_widget(info_label)

        return card

    def create_chart_card(self):
        """Create pie chart card"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(320),
            elevation=3,
            radius=[12, 12, 12, 12]
        )

        title = MDLabel(
            text="Today's Time Distribution",
            font_style="Subtitle1",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )

        # Pie chart
        self.pie_chart = PieChart(
            work=self.work_hours,
            personal=self.personal_hours,
            sleep=self.sleep_hours,
            size_hint_y=None,
            height=dp(220)
        )

        # Legend
        legend = self.create_legend()

        card.add_widget(title)
        card.add_widget(self.pie_chart)
        card.add_widget(legend)

        return card

    def create_legend(self):
        """Create chart legend"""
        legend = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(12)
        )

        # Work legend
        work_box = BoxLayout(orientation='horizontal', spacing=dp(4))
        work_color = Widget(size_hint=(None, None), size=(dp(15), dp(15)))
        with work_color.canvas:
            Color(0.2, 0.6, 0.9, 1)
            Rectangle(pos=work_color.pos, size=work_color.size)
        self.work_label = MDLabel(
            text=f"Work: {self.work_hours}h",
            font_style="Caption"
        )
        work_box.add_widget(work_color)
        work_box.add_widget(self.work_label)

        # Personal legend
        personal_box = BoxLayout(orientation='horizontal', spacing=dp(4))
        personal_color = Widget(size_hint=(None, None), size=(dp(15), dp(15)))
        with personal_color.canvas:
            Color(0.3, 0.7, 0.4, 1)
            Rectangle(pos=personal_color.pos, size=personal_color.size)
        self.personal_label = MDLabel(
            text=f"Personal: {self.personal_hours}h",
            font_style="Caption"
        )
        personal_box.add_widget(personal_color)
        personal_box.add_widget(self.personal_label)

        # Sleep legend
        sleep_box = BoxLayout(orientation='horizontal', spacing=dp(4))
        sleep_color = Widget(size_hint=(None, None), size=(dp(15), dp(15)))
        with sleep_color.canvas:
            Color(0.6, 0.3, 0.8, 1)
            Rectangle(pos=sleep_color.pos, size=sleep_color.size)
        self.sleep_label = MDLabel(
            text=f"Sleep: {self.sleep_hours}h",
            font_style="Caption"
        )
        sleep_box.add_widget(sleep_color)
        sleep_box.add_widget(self.sleep_label)

        legend.add_widget(work_box)
        legend.add_widget(personal_box)
        legend.add_widget(sleep_box)

        return legend

    def create_sliders_card(self):
        """Create sliders for time input"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(280),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        title = MDLabel(
            text="Adjust Your Hours",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        # Work slider
        work_section = self.create_slider_section(
            "💼 Work Hours",
            0,
            lambda value: self.update_hours('work', value)
        )

        # Personal slider
        personal_section = self.create_slider_section(
            "🏃 Personal Hours",
            0,
            lambda value: self.update_hours('personal', value)
        )

        # Sleep slider
        sleep_section = self.create_slider_section(
            "😴 Sleep Hours",
            0,
            lambda value: self.update_hours('sleep', value)
        )

        card.add_widget(title)
        card.add_widget(work_section)
        card.add_widget(personal_section)
        card.add_widget(sleep_section)

        return card

    def create_slider_section(self, label_text, initial_value, callback):
        """Create a slider with label"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(70),
            spacing=dp(5)
        )

        # Label row
        label_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
        label = MDLabel(
            text=label_text,
            font_style="Body2",
            size_hint_x=0.7
        )
        value_label = MDLabel(
            text=f"{initial_value:.1f}h",
            font_style="Body2",
            bold=True,
            halign="right",
            size_hint_x=0.3
        )
        label_row.add_widget(label)
        label_row.add_widget(value_label)

        # Slider
        slider = MDSlider(
            min=0,
            max=16,
            value=initial_value,
            size_hint_y=None,
            height=dp(30)
        )

        def on_value_change(instance, value):
            value_label.text = f"{value:.1f}h"
            callback(value)

        slider.bind(value=on_value_change)

        section.add_widget(label_row)
        section.add_widget(slider)

        return section

    def create_balance_card(self):
        """Create balance indicator card"""
        self.balance_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(120),
            elevation=2,
            radius=[12, 12, 12, 12]
        )

        self.balance_icon = MDIcon(
            icon="scale-balance",
            halign="center",
            size_hint_y=None,
            height=dp(40),
            font_size="40sp",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1)
        )

        self.balance_title = MDLabel(
            text="Start Tracking",
            font_style="H6",
            bold=True,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        )

        self.balance_subtitle = MDLabel(
            text="Adjust the sliders to log your time",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(25)
        )

        self.balance_card.add_widget(self.balance_icon)
        self.balance_card.add_widget(self.balance_title)
        self.balance_card.add_widget(self.balance_subtitle)

        return self.balance_card

    def update_hours(self, category, value):
        """Update hours and refresh chart"""
        if category == 'work':
            self.work_hours = value
        elif category == 'personal':
            self.personal_hours = value
        elif category == 'sleep':
            self.sleep_hours = value

        # Update chart
        self.pie_chart.work = self.work_hours
        self.pie_chart.personal = self.personal_hours
        self.pie_chart.sleep = self.sleep_hours
        self.pie_chart.update_chart()

        # Update legend
        self.work_label.text = f"Work: {self.work_hours:.1f}h"
        self.personal_label.text = f"Personal: {self.personal_hours:.1f}h"
        self.sleep_label.text = f"Sleep: {self.sleep_hours:.1f}h"

        # Update balance indicator
        self.update_balance_indicator()

    def update_balance_indicator(self):
        """Update the balance indicator based on totals"""
        total = self.work_hours + self.personal_hours + self.sleep_hours

        # Check if balanced (around 24 hours, allowing 1 hour tolerance)
        if abs(total - 24) <= 1:
            if abs(self.work_hours - 8) <= 1 and abs(self.personal_hours - 8) <= 1 and abs(self.sleep_hours - 8) <= 1:
                # Perfect balance!
                self.balance_icon.icon = "check-circle"
                self.balance_icon.text_color = (0.2, 0.7, 0.3, 1)
                self.balance_title.text = "Perfect Balance! 🎉"
                self.balance_subtitle.text = "Your day is well balanced"
            else:
                # Total is good but not 8/8/8
                self.balance_icon.icon = "alert-circle"
                self.balance_icon.text_color = (0.9, 0.6, 0.2, 1)
                self.balance_title.text = "Almost There!"
                self.balance_subtitle.text = f"Total: {total:.1f}h - Try balancing 8/8/8"
        elif total < 24:
            # Under 24 hours
            remaining = 24 - total
            self.balance_icon.icon = "clock-outline"
            self.balance_icon.text_color = (0.2, 0.6, 0.9, 1)
            self.balance_title.text = "Add More Time"
            self.balance_subtitle.text = f"{remaining:.1f} hours remaining"
        else:
            # Over 24 hours
            excess = total - 24
            self.balance_icon.icon = "alert"
            self.balance_icon.text_color = (0.9, 0.2, 0.2, 1)
            self.balance_title.text = "Over 24 Hours!"
            self.balance_subtitle.text = f"Reduce by {excess:.1f} hours"

    def save_time_block(self):
        """Save time block to database"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        app.db_manager.update_time_block(
            date=self.current_date,
            work=self.work_hours,
            personal=self.personal_hours,
            sleep=self.sleep_hours
        )

        from kivymd.toast import toast
        toast("✓ Time saved successfully!")

    def load_today_data(self):
        """Load today's data if exists"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        data = app.db_manager.get_time_block(self.current_date)
        if data:
            _, _, work, personal, sleep = data
            self.work_hours = work
            self.personal_hours = personal
            self.sleep_hours = sleep

            # Update UI
            self.pie_chart.work = work
            self.pie_chart.personal = personal
            self.pie_chart.sleep = sleep
            self.pie_chart.update_chart()

            self.update_balance_indicator()

    def on_enter(self):
        """Load data when entering screen"""
        self.load_today_data()

    def go_back(self):
        """Navigate back to home"""
        self.manager.current = 'home'