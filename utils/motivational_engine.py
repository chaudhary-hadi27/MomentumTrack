"""
MomentumTrack - Motivational Intelligence Engine
Provides smart motivational and discipline messages based on user performance
"""

import random
from datetime import datetime, timedelta


class MotivationalEngine:
    """Smart motivational system that adapts to user behavior"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

        # Motivational messages (when user needs encouragement)
        self.motivational_messages = [
            "You're doing great! Keep going! 💪",
            "Small progress is still progress 🚀",
            "Believe in yourself! You've got this! ⭐",
            "Every task completed is a step forward! 🎯",
            "You're building momentum! Don't stop now! 🔥",
            "Proud of you for showing up today! 💙",
            "Your effort today shapes your tomorrow 🌟",
            "One step at a time, you're making it happen! 👏",
            "Keep pushing! Your future self will thank you! 🎉",
            "You're stronger than you think! 💫"
        ]

        # Discipline messages (when user needs firm push)
        self.discipline_messages = [
            "Stop procrastinating. Start now! ⏰",
            "No excuses. Time to work! 💼",
            "Focus. Execute. Succeed! 🎯",
            "You said you'd do it. Prove it! 💪",
            "Comfort zone is the enemy of growth! 🚀",
            "Your future self will thank you! ⭐",
            "Action beats intention every time! ⚡",
            "Winners do what losers won't! 🏆",
            "Discipline equals freedom! 🔥",
            "The work won't do itself! 💼"
        ]

        # Celebration messages (for achievements)
        self.celebration_messages = [
            "Incredible work! You crushed it today! 🎉",
            "You're on fire! Keep this energy! 🔥",
            "Achievement unlocked! You're amazing! 🏆",
            "This is what dedication looks like! ⭐",
            "You're unstoppable! Keep going! 💫",
            "That's the spirit! Phenomenal progress! 👏",
            "You just leveled up! Amazing work! 🚀",
            "Excellence in action! Well done! 💪"
        ]

        # Morning boost messages
        self.morning_messages = [
            "Good morning! Today is your day to shine! 🌅",
            "New day, new opportunities! Let's go! ☀️",
            "Rise and grind! Make today count! 💪",
            "Morning champion! Ready to conquer? 🏆",
            "Today's goals are waiting for you! 🎯"
        ]

        # Evening reflection messages
        self.evening_messages = [
            "How was your day? Reflect and rest! 🌙",
            "Time to recharge for tomorrow! 😴",
            "Review your progress before sleep 📊",
            "Rest well, you've earned it! 🌟",
            "Tomorrow is another chance to excel! 🌃"
        ]

    def get_message(self, mode='auto'):
        """
        Get appropriate message based on mode and user performance

        Args:
            mode: 'motivational', 'discipline', 'celebration', 'morning', 'evening', or 'auto'

        Returns:
            str: Selected message
        """
        if mode == 'auto':
            # Automatically determine mode based on completion rate
            completion_rate = self.db_manager.get_completion_rate()

            if completion_rate >= 80:
                mode = 'celebration'
            elif completion_rate < 60:
                mode = 'discipline'
            else:
                mode = 'motivational'

        # Select message based on mode
        if mode == 'motivational':
            return random.choice(self.motivational_messages)
        elif mode == 'discipline':
            return random.choice(self.discipline_messages)
        elif mode == 'celebration':
            return random.choice(self.celebration_messages)
        elif mode == 'morning':
            return random.choice(self.morning_messages)
        elif mode == 'evening':
            return random.choice(self.evening_messages)
        else:
            return random.choice(self.motivational_messages)

    def get_daily_insight(self):
        """Generate daily performance insight"""
        completion_rate = self.db_manager.get_completion_rate()
        total_tasks = len(self.db_manager.get_all_tasks())
        completed_tasks = len(self.db_manager.get_all_tasks(status='completed'))

        insight = f"📊 Today's Performance:\n"
        insight += f"✓ {completed_tasks}/{total_tasks} tasks completed\n"
        insight += f"📈 {int(completion_rate)}% completion rate\n\n"

        if completion_rate >= 80:
            insight += "🌟 Outstanding! You're on fire today!"
        elif completion_rate >= 60:
            insight += "👍 Good progress! Keep it up!"
        elif completion_rate >= 40:
            insight += "⚠️ You can do better! Push harder!"
        else:
            insight += "🚨 Time to focus! Get to work!"

        return insight

    def get_streak_message(self, streak_days):
        """Get message based on current streak"""
        if streak_days == 0:
            return "Start your streak today! 🔥"
        elif streak_days < 7:
            return f"🔥 {streak_days} day streak! Keep going!"
        elif streak_days < 30:
            return f"🔥🔥 {streak_days} days! You're building a habit!"
        else:
            return f"🔥🔥🔥 {streak_days} days! You're unstoppable!"

    def should_send_reminder(self, last_activity_hours):
        """Determine if reminder should be sent based on inactivity"""
        return last_activity_hours > 4

    def get_time_based_message(self):
        """Get message based on current time of day"""
        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            return self.get_message('morning')
        elif 20 <= current_hour < 24:
            return self.get_message('evening')
        else:
            return self.get_message('auto')

    def analyze_productivity_trend(self):
        """Analyze productivity trend over last 7 days"""
        # This would require historical data tracking
        # For now, return current status
        completion_rate = self.db_manager.get_completion_rate()

        if completion_rate >= 70:
            return "trending_up", "Your productivity is excellent! 📈"
        elif completion_rate >= 50:
            return "trending_flat", "You're doing okay, but can improve! ➡️"
        else:
            return "trending_down", "Your productivity needs attention! 📉"

    def get_goal_encouragement(self, goal_progress):
        """Get encouragement based on goal progress"""
        if goal_progress >= 80:
            return "You're almost there! Final push! 🎯"
        elif goal_progress >= 50:
            return "Halfway done! Keep the momentum! 💪"
        elif goal_progress >= 25:
            return "Good start! Stay consistent! 🚀"
        else:
            return "Every journey starts with a step! 👣"

    def get_balance_feedback(self, work_hours, personal_hours, sleep_hours):
        """Provide feedback on 8/8/8 balance"""
        total = work_hours + personal_hours + sleep_hours

        # Check if close to 8/8/8
        work_diff = abs(work_hours - 8)
        personal_diff = abs(personal_hours - 8)
        sleep_diff = abs(sleep_hours - 8)

        if work_diff <= 1 and personal_diff <= 1 and sleep_diff <= 1:
            return "Perfect balance! Your life is well-structured! 🎯"
        elif work_hours > 12:
            return "⚠️ Too much work! Remember self-care and rest!"
        elif sleep_hours < 6:
            return "😴 You need more sleep! Rest is crucial!"
        elif personal_hours < 4:
            return "🏃 Don't forget personal time! Life needs balance!"
        else:
            return "Keep working toward 8/8/8 balance! 💪"