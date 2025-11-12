"""
Event System - Thread-safe event dispatching for decoupled communication
"""

from typing import Callable, Dict, List, Any
from threading import Lock
from weakref import WeakMethod, ref
import traceback


class EventDispatcher:
    """
    Thread-safe event dispatcher using weak references to prevent memory leaks.

    Usage:
        dispatcher = EventDispatcher()

        # Register listener
        dispatcher.on('event_name', my_callback)

        # Dispatch event
        dispatcher.dispatch('event_name', arg1, arg2)

        # Unregister
        dispatcher.off('event_name', my_callback)
    """

    def __init__(self):
        self._listeners: Dict[str, List[Any]] = {}
        self._lock = Lock()

    def on(self, event_name: str, callback: Callable):
        """
        Register an event listener.

        Args:
            event_name: Name of the event
            callback: Callback function to invoke
        """
        with self._lock:
            if event_name not in self._listeners:
                self._listeners[event_name] = []

            # Use weak references to prevent memory leaks
            if hasattr(callback, '__self__'):
                # Method - use WeakMethod
                weak_callback = WeakMethod(callback, self._cleanup_callback(event_name))
            else:
                # Function - use regular ref
                weak_callback = ref(callback, self._cleanup_callback(event_name))

            self._listeners[event_name].append(weak_callback)

    def off(self, event_name: str, callback: Callable = None):
        """
        Unregister an event listener.

        Args:
            event_name: Name of the event
            callback: Callback to remove (if None, removes all for this event)
        """
        with self._lock:
            if event_name not in self._listeners:
                return

            if callback is None:
                # Remove all listeners for this event
                del self._listeners[event_name]
            else:
                # Remove specific listener
                self._listeners[event_name] = [
                    weak_ref for weak_ref in self._listeners[event_name]
                    if weak_ref() != callback
                ]

                # Clean up empty list
                if not self._listeners[event_name]:
                    del self._listeners[event_name]

    def dispatch(self, event_name: str, *args, **kwargs):
        """
        Dispatch an event to all registered listeners.

        Args:
            event_name: Name of the event
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        with self._lock:
            if event_name not in self._listeners:
                return

            # Get current listeners (copy to avoid modification during iteration)
            listeners = self._listeners[event_name].copy()

        # Call listeners outside of lock to prevent deadlocks
        for weak_ref in listeners:
            try:
                callback = weak_ref()
                if callback is not None:
                    callback(*args, **kwargs)
            except Exception as e:
                print(f"⚠️ Error in event listener for '{event_name}': {e}")
                traceback.print_exc()

    def _cleanup_callback(self, event_name: str):
        """Create a cleanup function for dead weak references"""

        def cleanup(weak_ref):
            with self._lock:
                if event_name in self._listeners:
                    self._listeners[event_name] = [
                        ref for ref in self._listeners[event_name]
                        if ref != weak_ref
                    ]
                    if not self._listeners[event_name]:
                        del self._listeners[event_name]

        return cleanup

    def has_listeners(self, event_name: str) -> bool:
        """Check if event has any listeners"""
        with self._lock:
            return event_name in self._listeners and len(self._listeners[event_name]) > 0

    def clear(self):
        """Remove all event listeners"""
        with self._lock:
            self._listeners.clear()


class TaskEvents:
    """
    Predefined task events for type safety.
    Use these constants instead of strings.
    """

    TASK_CREATED = 'on_task_created'
    TASK_UPDATED = 'on_task_updated'
    TASK_DELETED = 'on_task_deleted'
    TASK_COMPLETED = 'on_task_completed'

    LIST_CREATED = 'on_list_created'
    LIST_UPDATED = 'on_list_updated'
    LIST_DELETED = 'on_list_deleted'

    REMINDER_TRIGGERED = 'on_reminder_triggered'


class EventBus:
    """
    Global event bus singleton for app-wide events.

    Usage:
        from utils.event_system import event_bus

        # Subscribe
        event_bus.on('my_event', callback)

        # Publish
        event_bus.dispatch('my_event', data)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._dispatcher = EventDispatcher()
        return cls._instance

    def on(self, event_name: str, callback: Callable):
        """Register event listener"""
        self._dispatcher.on(event_name, callback)

    def off(self, event_name: str, callback: Callable = None):
        """Unregister event listener"""
        self._dispatcher.off(event_name, callback)

    def dispatch(self, event_name: str, *args, **kwargs):
        """Dispatch event"""
        self._dispatcher.dispatch(event_name, *args, **kwargs)

    def has_listeners(self, event_name: str) -> bool:
        """Check if event has listeners"""
        return self._dispatcher.has_listeners(event_name)

    def clear(self):
        """Clear all listeners"""
        self._dispatcher.clear()


# Global event bus instance
event_bus = EventBus()