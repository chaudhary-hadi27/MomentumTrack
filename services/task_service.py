"""
Task Service Layer - Business logic for task operations
Abstracts database access and provides caching, validation, and events
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from threading import Lock
from database.db_manager import DatabaseManager
from database.models import Task, TaskList
from utils.event_system import EventDispatcher, TaskEvents


class TaskService:
    """
    Service layer for task operations.
    Provides caching, validation, and event notifications.
    Thread-safe for concurrent access.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.events = EventDispatcher()

        # Thread-safe cache
        self._cache_lock = Lock()
        self._task_cache: Dict[int, Task] = {}
        self._list_tasks_cache: Dict[int, List[Task]] = {}

        # Statistics
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'db_queries': 0
        }

    # ===== TASK OPERATIONS =====

    def get_task(self, task_id: int, use_cache: bool = True) -> Optional[Task]:
        """
        Get a single task by ID with caching.

        Args:
            task_id: Task ID
            use_cache: Whether to use cache (default True)

        Returns:
            Task object or None if not found
        """
        # Check cache first
        if use_cache:
            with self._cache_lock:
                if task_id in self._task_cache:
                    self._stats['cache_hits'] += 1
                    return self._task_cache[task_id]

        # Cache miss - query database
        self._stats['cache_misses'] += 1
        self._stats['db_queries'] += 1

        try:
            task = self.db.get_task_by_id(task_id)

            # Update cache
            if task and use_cache:
                with self._cache_lock:
                    self._task_cache[task_id] = task

            return task

        except Exception as e:
            print(f"❌ Error getting task {task_id}: {e}")
            return None

    def get_list_tasks(
            self,
            list_id: int,
            show_completed: bool = True,
            use_cache: bool = True,
            force_refresh: bool = False
    ) -> List[Task]:
        """
        Get all tasks for a list with caching.

        Args:
            list_id: List ID
            show_completed: Whether to include completed tasks
            use_cache: Whether to use cache
            force_refresh: Force refresh from database

        Returns:
            List of Task objects
        """
        cache_key = list_id

        # Check cache
        if use_cache and not force_refresh:
            with self._cache_lock:
                if cache_key in self._list_tasks_cache:
                    self._stats['cache_hits'] += 1
                    tasks = self._list_tasks_cache[cache_key]

                    # Filter completed if needed
                    if not show_completed:
                        tasks = [t for t in tasks if not t.completed]

                    return tasks

        # Cache miss or force refresh
        self._stats['cache_misses'] += 1
        self._stats['db_queries'] += 1

        try:
            from utils.constants import MAX_TASKS_PER_LIST
            tasks = self.db.get_tasks_by_list(
                list_id,
                show_completed=show_completed,
                limit=MAX_TASKS_PER_LIST
            )

            # Update cache
            if use_cache:
                with self._cache_lock:
                    self._list_tasks_cache[cache_key] = tasks

            return tasks

        except Exception as e:
            print(f"❌ Error getting tasks for list {list_id}: {e}")
            return []

    def create_task(
            self,
            list_id: int,
            title: str,
            **kwargs
    ) -> Optional[int]:
        """
        Create a new task with validation and events.

        Args:
            list_id: Parent list ID
            title: Task title
            **kwargs: Additional task fields

        Returns:
            New task ID or None if failed
        """
        # Validate
        if not title or not title.strip():
            raise ValueError("Task title is required")

        if len(title) > 500:
            raise ValueError("Task title too long (max 500 characters)")

        # Check list exists
        list_obj = self.db.get_list_by_id(list_id)
        if not list_obj:
            raise ValueError(f"List {list_id} does not exist")

        try:
            # Create task
            task_id = self.db.create_task(list_id, title, **kwargs)

            if task_id:
                # Invalidate cache
                self._invalidate_list_cache(list_id)

                # Dispatch event
                self.events.dispatch('on_task_created', task_id, list_id)

                print(f"✅ Task created: {task_id}")

            return task_id

        except Exception as e:
            print(f"❌ Error creating task: {e}")
            raise

    def update_task(self, task_id: int, **fields) -> bool:
        """
        Update task with validation and events.

        Args:
            task_id: Task ID
            **fields: Fields to update

        Returns:
            True if successful
        """
        # Get current task
        task = self.get_task(task_id, use_cache=False)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        # Validate fields
        if 'title' in fields:
            title = fields['title']
            if not title or not title.strip():
                raise ValueError("Task title cannot be empty")
            if len(title) > 500:
                raise ValueError("Task title too long")

        try:
            # Update in database
            self.db.update_task(task_id, **fields)

            # Invalidate cache
            self._invalidate_task_cache(task_id)
            self._invalidate_list_cache(task.list_id)

            # Dispatch event
            self.events.dispatch('on_task_updated', task_id, fields)

            return True

        except Exception as e:
            print(f"❌ Error updating task {task_id}: {e}")
            raise

    def delete_task(self, task_id: int) -> bool:
        """
        Delete task with validation and events.

        Args:
            task_id: Task ID

        Returns:
            True if successful
        """
        # Get task to get list_id
        task = self.get_task(task_id, use_cache=False)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        try:
            # Delete from database
            self.db.delete_task(task_id)

            # Invalidate cache
            self._invalidate_task_cache(task_id)
            self._invalidate_list_cache(task.list_id)

            # Dispatch event
            self.events.dispatch('on_task_deleted', task_id, task.list_id)

            return True

        except Exception as e:
            print(f"❌ Error deleting task {task_id}: {e}")
            raise

    def toggle_task_completed(self, task_id: int) -> bool:
        """
        Toggle task completion status.

        Args:
            task_id: Task ID

        Returns:
            New completion status
        """
        task = self.get_task(task_id, use_cache=False)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        try:
            # Toggle in database
            new_status = self.db.toggle_task_completed(task_id)

            # Invalidate cache
            self._invalidate_task_cache(task_id)
            self._invalidate_list_cache(task.list_id)

            # Dispatch event
            self.events.dispatch('on_task_completed', task_id, new_status)

            return new_status

        except Exception as e:
            print(f"❌ Error toggling task {task_id}: {e}")
            raise

    def search_tasks(self, query: str, limit: int = 50) -> List[Task]:
        """
        Search tasks by title or notes.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching tasks
        """
        if not query or len(query) < 2:
            return []

        try:
            self._stats['db_queries'] += 1
            return self.db.search_tasks(query, limit)
        except Exception as e:
            print(f"❌ Error searching tasks: {e}")
            return []

    # ===== BATCH OPERATIONS =====

    def batch_update_completion(self, task_ids: List[int], completed: bool) -> int:
        """
        Batch update completion status for multiple tasks.

        Args:
            task_ids: List of task IDs
            completed: New completion status

        Returns:
            Number of tasks updated
        """
        if not task_ids:
            return 0

        try:
            updates = [(tid, {'completed': completed}) for tid in task_ids]
            self.db.batch_update_tasks(updates)

            # Invalidate cache for all affected tasks
            for task_id in task_ids:
                self._invalidate_task_cache(task_id)

            # Dispatch events
            for task_id in task_ids:
                self.events.dispatch('on_task_completed', task_id, completed)

            return len(task_ids)

        except Exception as e:
            print(f"❌ Error batch updating tasks: {e}")
            raise

    def batch_delete_tasks(self, task_ids: List[int]) -> int:
        """
        Batch delete multiple tasks.

        Args:
            task_ids: List of task IDs

        Returns:
            Number of tasks deleted
        """
        if not task_ids:
            return 0

        try:
            self.db.batch_delete_tasks(task_ids)

            # Invalidate cache
            for task_id in task_ids:
                self._invalidate_task_cache(task_id)

            return len(task_ids)

        except Exception as e:
            print(f"❌ Error batch deleting tasks: {e}")
            raise

    # ===== CACHE MANAGEMENT =====

    def _invalidate_task_cache(self, task_id: int):
        """Remove task from cache"""
        with self._cache_lock:
            self._task_cache.pop(task_id, None)

    def _invalidate_list_cache(self, list_id: int):
        """Remove list tasks from cache"""
        with self._cache_lock:
            self._list_tasks_cache.pop(list_id, None)

    def clear_cache(self):
        """Clear all caches"""
        with self._cache_lock:
            self._task_cache.clear()
            self._list_tasks_cache.clear()
            print("🧹 Service cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        with self._cache_lock:
            return {
                **self._stats,
                'cached_tasks': len(self._task_cache),
                'cached_lists': len(self._list_tasks_cache)
            }

    def print_stats(self):
        """Print service statistics"""
        stats = self.get_stats()
        total = stats['cache_hits'] + stats['cache_misses']
        hit_rate = (stats['cache_hits'] / total * 100) if total > 0 else 0

        print("\n" + "=" * 50)
        print("📊 Task Service Statistics")
        print("=" * 50)
        print(f"Cache Hits: {stats['cache_hits']}")
        print(f"Cache Misses: {stats['cache_misses']}")
        print(f"Hit Rate: {hit_rate:.1f}%")
        print(f"DB Queries: {stats['db_queries']}")
        print(f"Cached Tasks: {stats['cached_tasks']}")
        print(f"Cached Lists: {stats['cached_lists']}")
        print("=" * 50 + "\n")


class ListService:
    """
    Service layer for list operations.
    Thread-safe with caching.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.events = EventDispatcher()

        # Thread-safe cache
        self._cache_lock = Lock()
        self._lists_cache: Dict[str, List[TaskList]] = {}  # category -> lists

    def get_lists_by_category(
            self,
            category: str,
            use_cache: bool = True,
            force_refresh: bool = False
    ) -> List[TaskList]:
        """
        Get lists for a category with caching.

        Args:
            category: Category ID
            use_cache: Whether to use cache
            force_refresh: Force refresh from database

        Returns:
            List of TaskList objects
        """
        # Check cache
        if use_cache and not force_refresh:
            with self._cache_lock:
                if category in self._lists_cache:
                    return self._lists_cache[category]

        # Query database
        try:
            lists = self.db.get_lists_by_category(category)

            # Update cache
            if use_cache:
                with self._cache_lock:
                    self._lists_cache[category] = lists

            return lists

        except Exception as e:
            print(f"❌ Error getting lists for category {category}: {e}")
            return []

    def get_list(self, list_id: int) -> Optional[TaskList]:
        """Get a single list by ID"""
        try:
            return self.db.get_list_by_id(list_id)
        except Exception as e:
            print(f"❌ Error getting list {list_id}: {e}")
            return None

    def create_list(self, name: str, category: str) -> Optional[int]:
        """Create a new list with validation"""
        if not name or not name.strip():
            raise ValueError("List name is required")

        try:
            list_id = self.db.create_list(name, category)

            if list_id:
                # Invalidate cache
                self._invalidate_cache(category)

                # Dispatch event
                self.events.dispatch('on_list_created', list_id, category)

            return list_id

        except Exception as e:
            print(f"❌ Error creating list: {e}")
            raise

    def update_list(self, list_id: int, name: str) -> bool:
        """Update list name"""
        if not name or not name.strip():
            raise ValueError("List name cannot be empty")

        try:
            # Get list to find category
            list_obj = self.get_list(list_id)
            if not list_obj:
                raise ValueError(f"List {list_id} not found")

            self.db.update_list(list_id, name)

            # Invalidate cache
            self._invalidate_cache(list_obj.category)

            # Dispatch event
            self.events.dispatch('on_list_updated', list_id, name)

            return True

        except Exception as e:
            print(f"❌ Error updating list {list_id}: {e}")
            raise

    def delete_list(self, list_id: int) -> bool:
        """Delete list"""
        try:
            # Get list to find category
            list_obj = self.get_list(list_id)
            if not list_obj:
                raise ValueError(f"List {list_id} not found")

            self.db.delete_list(list_id)

            # Invalidate cache
            self._invalidate_cache(list_obj.category)

            # Dispatch event
            self.events.dispatch('on_list_deleted', list_id, list_obj.category)

            return True

        except Exception as e:
            print(f"❌ Error deleting list {list_id}: {e}")
            raise

    def _invalidate_cache(self, category: str):
        """Invalidate category cache"""
        with self._cache_lock:
            self._lists_cache.pop(category, None)

    def clear_cache(self):
        """Clear all caches"""
        with self._cache_lock:
            self._lists_cache.clear()
            print("🧹 List service cache cleared")