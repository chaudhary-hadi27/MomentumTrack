"""
Thread-Safe Notification Manager
Fixes threading issues with proper synchronization
"""

from datetime import datetime
import threading
import time
from queue import Queue, Empty
from typing import Optional
from database.db_manager import DatabaseManager


class NotificationManager:
    """
    Thread-safe notification manager with proper synchronization.

    Key improvements:
    1. Uses Queue for thread-safe communication
    2. Proper shutdown mechanism
    3. No direct database access from UI thread
    4. Event-driven notification dispatch
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

        # Thread control
        self.running = False
        self.thread: Optional[threading.Thread] = None

        # Thread-safe queue for notifications
        self.notification_queue = Queue()

        # State management
        self._lock = threading.Lock()
        self.last_check_time: Optional[str] = None

        # Statistics
        self.stats = {
            'reminders_sent': 0,
            'errors': 0,
            'last_check': None
        }

    def start(self):
        """Start notification checker thread"""
        with self._lock:
            if self.running:
                print("⚠️ Notification manager already running")
                return

            self.running = True

        # Start background thread
        self.thread = threading.Thread(
            target=self._check_notifications_loop,
            daemon=True,
            name="NotificationManager"
        )
        self.thread.start()

        # Start notification dispatcher thread
        self.dispatch_thread = threading.Thread(
            target=self._dispatch_notifications_loop,
            daemon=True,
            name="NotificationDispatcher"
        )
        self.dispatch_thread.start()

        print("🔔 Notification manager started")

    def stop(self):
        """Stop notification checker gracefully"""
        with self._lock:
            if not self.running:
                return

            self.running = False

        print("🔕 Stopping notification manager...")

        # Wait for thread to stop (max 3 seconds)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3.0)

        if self.dispatch_thread and self.dispatch_thread.is_alive():
            self.dispatch_thread.join(timeout=3.0)

        print("✅ Notification manager stopped")

    def _check_notifications_loop(self):
        """Background thread that checks for notifications"""
        while True:
            # Check if should stop
            with self._lock:
                if not self.running:
                    break

            try:
                self._check_notifications()
            except Exception as e:
                print(f"❌ Notification check error: {e}")
                with self._lock:
                    self.stats['errors'] += 1
                time.sleep(30)  # Wait longer on error

            # Sleep between checks
            time.sleep(10)

    def _check_notifications(self):
        """Check for tasks that need reminders (runs in background thread)"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")

        # Skip if we already checked this minute
        with self._lock:
            if self.last_check_time == current_time:
                return
            self.last_check_time = current_time
            self.stats['last_check'] = now.isoformat()

        try:
            # Query database (in background thread - OK!)
            tasks = self.db.get_tasks_with_reminders_today()

            for task in tasks:
                task_id, list_id, title, start_time, end_time, reminder_time, motivation_quote = task

                # Check if it's time to remind
                if reminder_time and current_time == reminder_time:
                    # Queue notification for dispatch
                    notification = {
                        'task_id': task_id,
                        'title': title,
                        'motivation': motivation_quote,
                        'start_time': start_time,
                        'end_time': end_time
                    }
                    self.notification_queue.put(notification)

                    with self._lock:
                        self.stats['reminders_sent'] += 1

        except Exception as e:
            print(f"❌ Error checking notifications: {e}")
            raise

    def _dispatch_notifications_loop(self):
        """Dispatcher thread that sends notifications from queue"""
        while True:
            # Check if should stop
            with self._lock:
                if not self.running and self.notification_queue.empty():
                    break

            try:
                # Get notification from queue (timeout to check running flag)
                notification = self.notification_queue.get(timeout=1.0)

                # Send notification
                self._send_notification(notification)

            except Empty:
                # No notifications, continue
                continue
            except Exception as e:
                print(f"❌ Error dispatching notification: {e}")

    def _send_notification(self, notification: dict):
        """Send a single notification"""
        title = notification['title']
        motivation = notification.get('motivation', '')

        # Build message
        message = f"Time to work on: {title}"
        if motivation:
            message = f"💪 {motivation}\n\n{message}"

        try:
            self._send_platform_notification(title, message)
            print(f"⏰ Reminder sent for: {title}")
            if motivation:
                print(f"   💪 With quote: {motivation}")
        except Exception as e:
            print(f"❌ Error sending notification: {e}")

    def _send_platform_notification(self, title: str, message: str):
        """Send notification to platform (Android/Desktop)"""
        try:
            # Try plyer for mobile
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Momentum Track",
                timeout=10
            )
        except ImportError:
            # Plyer not available (desktop) - print to console
            print(f"📢 NOTIFICATION: {title} - {message}")
        except Exception as e:
            # Other platform errors
            print(f"📢 NOTIFICATION: {title} - {message}")
            raise

    def get_stats(self) -> dict:
        """Get notification statistics (thread-safe)"""
        with self._lock:
            return self.stats.copy()

    def print_stats(self):
        """Print notification statistics"""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("🔔 Notification Manager Statistics")
        print("=" * 50)
        print(f"Reminders Sent: {stats['reminders_sent']}")
        print(f"Errors: {stats['errors']}")
        print(f"Last Check: {stats['last_check']}")
        print(f"Running: {self.running}")
        print("=" * 50 + "\n")


class NotificationScheduler:
    """
    Alternative implementation using scheduled callbacks instead of polling.
    More efficient for apps with fewer reminders.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._lock = threading.Lock()
        self._scheduled_tasks = {}
        self._timer_threads = {}

    def schedule_reminder(self, task_id: int, reminder_time: datetime):
        """Schedule a specific reminder"""
        with self._lock:
            # Calculate delay
            now = datetime.now()
            delay = (reminder_time - now).total_seconds()

            if delay <= 0:
                print(f"⚠️ Reminder time already passed for task {task_id}")
                return

            # Cancel existing timer if any
            self._cancel_reminder(task_id)

            # Create timer
            timer = threading.Timer(delay, self._trigger_reminder, args=[task_id])
            timer.daemon = True
            timer.start()

            self._timer_threads[task_id] = timer
            self._scheduled_tasks[task_id] = reminder_time

            print(f"⏰ Reminder scheduled for task {task_id} in {delay:.0f}s")

    def _trigger_reminder(self, task_id: int):
        """Trigger reminder (called by timer)"""
        try:
            # Get task details
            task = self.db.get_task_by_id(task_id)
            if not task:
                return

            # Send notification
            message = f"Time to work on: {task.title}"
            if task.motivation:
                message = f"💪 {task.motivation}\n\n{message}"

            self._send_notification(task.title, message)

            # Clean up
            with self._lock:
                self._timer_threads.pop(task_id, None)
                self._scheduled_tasks.pop(task_id, None)

        except Exception as e:
            print(f"❌ Error triggering reminder for task {task_id}: {e}")

    def _cancel_reminder(self, task_id: int):
        """Cancel scheduled reminder"""
        if task_id in self._timer_threads:
            self._timer_threads[task_id].cancel()
            self._timer_threads.pop(task_id, None)
            self._scheduled_tasks.pop(task_id, None)

    def cancel_all(self):
        """Cancel all scheduled reminders"""
        with self._lock:
            for timer in self._timer_threads.values():
                timer.cancel()
            self._timer_threads.clear()
            self._scheduled_tasks.clear()

    def _send_notification(self, title: str, message: str):
        """Send platform notification"""
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                app_name="Momentum Track",
                timeout=10
            )
        except:
            print(f"📢 NOTIFICATION: {title} - {message}")