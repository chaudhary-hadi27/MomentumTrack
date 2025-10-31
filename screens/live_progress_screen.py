"""
Live Progress Screen - Only Real Data, No Dummy Data
Shows actual task completion and analytics based on user activity
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.metrics import dp
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')
from io import BytesIO
from kivy.core.image import Image as CoreImage


class LiveProgressScreen(MDScreen):
    """Screen for visualizing LIVE productivity analytics - NO DUMMY DATA"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build live progress visualization UI"""
        layout = BoxLayout(orientation='vertical', spacing=dp(12))

        # Header
        header = self.create_header()

        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(16),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))

        # Overview stats card (LIVE DATA)
        stats_card = self.create_live_stats_card()

        # Completion rate chart (LIVE DATA)
        completion_chart_card = self.create_live_completion_chart_card()

        # Today's performance
        today_card = self.create_today_performance_card()

        # Weekly summary (LIVE DATA)
        weekly_card = self.create_weekly_summary_card()

        content.add_widget(stats_card)
        content.add_widget(completion_chart_card)
        content.add_widget(today_card)
        content.add_widget(weekly_card)

        scroll.add_widget(content)

        layout.add_widget(header)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def create_header(self):
        """Create header"""
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
            text="Live Progress",
            font_style="H5",
            bold=True
        )
        subtitle = MDLabel(
            text="Real-time analytics",
            font_style="Caption",
            theme_text_color="Secondary"
        )
        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        refresh_btn = MDIconButton(
            icon="refresh",
            pos_hint={"center_y": 0.5},
            icon_size="28sp",
            on_release=lambda x: self.refresh_data()
        )

        header.add_widget(back_btn)
        header.add_widget(title_box)
        header.add_widget(refresh_btn)

        return header

    def create_live_stats_card(self):
        """Create overview statistics card with LIVE DATA"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(250),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        title = MDLabel(
            text="📊 Live Statistics",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        # Get REAL statistics from database
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        # All-time stats
        all_tasks = app.db_manager.get_all_tasks()
        completed_tasks = app.db_manager.get_all_tasks(status='completed')
        pending_tasks = app.db_manager.get_all_tasks(status='pending')

        total_tasks = len(all_tasks)
        completed_count = len(completed_tasks)
        pending_count = len(pending_tasks)

        # Calculate REAL completion rate
        if total_tasks > 0:
            completion_rate = int((completed_count / total_tasks) * 100)
        else:
            completion_rate = 0

        # Today's stats
        today_stats = app.db_manager.get_daily_stats()
        today_created = today_stats[2] if today_stats else 0
        today_completed = today_stats[3] if today_stats else 0

        # Stats grid
        stats_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(190)
        )

        # Show REAL data
        stat1 = self.create_stat_row("All Tasks", str(total_tasks), "📋")
        stat2 = self.create_stat_row("Completed", str(completed_count), "✅")
        stat3 = self.create_stat_row("Pending", str(pending_count), "⏳")
        stat4 = self.create_stat_row("Completion Rate", f"{completion_rate}%", "📈")
        stat5 = self.create_stat_row("Today Created", str(today_created), "🆕")
        stat6 = self.create_stat_row("Today Done", str(today_completed), "✓")

        stats_layout.add_widget(stat1)
        stats_layout.add_widget(stat2)
        stats_layout.add_widget(stat3)
        stats_layout.add_widget(stat4)
        stats_layout.add_widget(stat5)
        stats_layout.add_widget(stat6)

        card.add_widget(title)
        card.add_widget(stats_layout)

        return card

    def create_stat_row(self, label, value, icon):
        """Create a stat row"""
        row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(12)
        )

        icon_label = MDLabel(
            text=icon,
            size_hint_x=None,
            width=dp(30),
            font_size="20sp"
        )

        label_widget = MDLabel(
            text=label,
            font_style="Body2",
            size_hint_x=0.6
        )

        value_widget = MDLabel(
            text=value,
            font_style="Body1",
            bold=True,
            halign="right",
            size_hint_x=0.4
        )

        row.add_widget(icon_label)
        row.add_widget(label_widget)
        row.add_widget(value_widget)

        return row

    def create_live_completion_chart_card(self):
        """Create card with LIVE completion chart"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(380),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        title = MDLabel(
            text="📈 Weekly Completion Trend (Live Data)",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        # Generate chart with REAL data
        chart_image = self.generate_live_completion_chart()

        # Info label
        info = MDLabel(
            text="Based on your actual task completions",
            font_style="Caption",
            theme_text_color="Secondary",
            halign="center",
            size_hint_y=None,
            height=dp(25)
        )

        card.add_widget(title)
        card.add_widget(chart_image)
        card.add_widget(info)

        return card

    def generate_live_completion_chart(self):
        """Generate completion rate chart with REAL DATA ONLY"""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        # Get REAL weekly stats
        weekly_stats = app.db_manager.get_weekly_stats()

        # Extract data
        days = []
        completion_rates = []

        for stat in weekly_stats:
            date_str = stat[1]  # date column
            date_obj = datetime.fromisoformat(date_str)
            day_name = date_obj.strftime('%a')  # Mon, Tue, etc.

            tasks_created = stat[2]
            tasks_completed = stat[3]

            # Calculate REAL completion rate
            if tasks_created > 0:
                rate = (tasks_completed / tasks_created) * 100
            else:
                rate = 0

            days.append(day_name)
            completion_rates.append(rate)

        # Create figure
        fig, ax = plt.subplots(figsize=(6, 4))

        # Plot with colors based on performance
        colors = []
        for rate in completion_rates:
            if rate >= 70:
                colors.append('#4CAF50')  # Green
            elif rate >= 50:
                colors.append('#2196F3')  # Blue
            else:
                colors.append('#FF9800')  # Orange

        ax.bar(days, completion_rates, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for i, (day, rate) in enumerate(zip(days, completion_rates)):
            if rate > 0:
                ax.text(i, rate + 2, f'{int(rate)}%',
                        ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_xlabel('Day', fontsize=10, fontweight='bold')
        ax.set_ylabel('Completion Rate (%)', fontsize=10, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_facecolor('#f5f5f5')

        # Add horizontal line at 70% (good performance)
        ax.axhline(y=70, color='green', linestyle='--', alpha=0.5, label='Target: 70%')
        ax.legend()

        # Save to bytes
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=100, facecolor='white')
        buf.seek(0)
        plt.close()

        # Convert to Kivy image
        core_image = CoreImage(buf, ext='png')
        image = Image(size_hint_y=None, height=dp(290))
        image.texture = core_image.texture

        return image

    def create_today_performance_card(self):
        """Create today's performance card with LIVE DATA"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(200),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        title = MDLabel(
            text="📅 Today's Performance",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        # Get today's REAL data
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        today_stats = app.db_manager.get_daily_stats()

        if today_stats and today_stats[2] > 0:  # If tasks created today
            tasks_created = today_stats[2]
            tasks_completed = today_stats[3]
            completion_rate = int(today_stats[4])

            # Performance info
            info_box = BoxLayout(
                orientation='vertical',
                spacing=dp(12),
                size_hint_y=None,
                height=dp(140)
            )

            created_label = MDLabel(
                text=f"Tasks Created: {tasks_created}",
                font_style="Body1",
                halign="center",
                size_hint_y=None,
                height=dp(30)
            )

            completed_label = MDLabel(
                text=f"Tasks Completed: {tasks_completed}",
                font_style="Body1",
                halign="center",
                size_hint_y=None,
                height=dp(30)
            )

            # Rate with emoji
            if completion_rate >= 70:
                emoji = "🌟"
                status = "Excellent!"
                color = (0.2, 0.7, 0.3, 1)
            elif completion_rate >= 50:
                emoji = "👍"
                status = "Good!"
                color = (0.2, 0.6, 0.9, 1)
            else:
                emoji = "💪"
                status = "Keep Going!"
                color = (0.9, 0.6, 0.2, 1)

            rate_label = MDLabel(
                text=f"{emoji} {completion_rate}% - {status}",
                font_style="H5",
                bold=True,
                halign="center",
                theme_text_color="Custom",
                text_color=color,
                size_hint_y=None,
                height=dp(45)
            )

            info_box.add_widget(created_label)
            info_box.add_widget(completed_label)
            info_box.add_widget(rate_label)

        else:
            # No data yet today
            info_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(140)
            )

            no_data_label = MDLabel(
                text="No tasks created today yet.\nCreate your first task to start tracking!",
                font_style="Body1",
                halign="center",
                theme_text_color="Secondary"
            )

            info_box.add_widget(no_data_label)

        card.add_widget(title)
        card.add_widget(info_box)

        return card

    def create_weekly_summary_card(self):
        """Create weekly summary with LIVE DATA"""
        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            size_hint_y=None,
            height=dp(250),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        title = MDLabel(
            text="📊 This Week's Summary",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        # Get weekly REAL data
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        weekly_stats = app.db_manager.get_weekly_stats()

        # Calculate totals
        total_created = sum(stat[2] for stat in weekly_stats)
        total_completed = sum(stat[3] for stat in weekly_stats)

        if total_created > 0:
            avg_completion = int((total_completed / total_created) * 100)
        else:
            avg_completion = 0

        # Active days (days with tasks created)
        active_days = sum(1 for stat in weekly_stats if stat[2] > 0)

        # Summary info
        summary_box = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            size_hint_y=None,
            height=dp(190)
        )

        stat1 = self.create_stat_row("Tasks This Week", str(total_created), "📋")
        stat2 = self.create_stat_row("Completed", str(total_completed), "✅")
        stat3 = self.create_stat_row("Average Rate", f"{avg_completion}%", "📈")
        stat4 = self.create_stat_row("Active Days", f"{active_days}/7", "🔥")

        # Weekly insight
        if avg_completion >= 70:
            insight = "🌟 Outstanding week! Keep it up!"
            color = (0.2, 0.7, 0.3, 1)
        elif avg_completion >= 50:
            insight = "👍 Good progress this week!"
            color = (0.2, 0.6, 0.9, 1)
        else:
            insight = "💪 Focus more next week!"
            color = (0.9, 0.6, 0.2, 1)

        insight_label = MDLabel(
            text=insight,
            font_style="Body2",
            bold=True,
            halign="center",
            theme_text_color="Custom",
            text_color=color,
            size_hint_y=None,
            height=dp(35)
        )

        summary_box.add_widget(stat1)
        summary_box.add_widget(stat2)
        summary_box.add_widget(stat3)
        summary_box.add_widget(stat4)
        summary_box.add_widget(insight_label)

        card.add_widget(title)
        card.add_widget(summary_box)

        return card

    def refresh_data(self):
        """Refresh all data"""
        from kivymd.toast import toast
        toast("🔄 Refreshing data...")

        # Rebuild UI
        self.clear_widgets()
        self.build_ui()

        toast("✓ Data refreshed!")

    def on_enter(self):
        """Refresh data when entering screen"""
        pass  # Data loads automatically in create methods

    def go_back(self):
        """Navigate back to home"""
        self.manager.current = 'home'