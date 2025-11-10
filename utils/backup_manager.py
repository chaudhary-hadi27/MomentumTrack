"""
Backup Manager for Momentum Track
Handles export/import of tasks and lists in multiple formats
"""

import json
import os
from datetime import datetime
from pathlib import Path


class BackupManager:
    """Manage backups and exports of tasks and lists"""

    def __init__(self, db_manager):
        self.db = db_manager
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

    def create_full_backup(self):
        """Create a complete backup of all data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"momentum_backup_{timestamp}.json"
        filepath = self.backup_dir / filename

        try:
            # Get all data
            all_lists = self.db.get_all_lists()

            backup_data = {
                "metadata": {
                    "app_name": "Momentum Track",
                    "version": "1.0",
                    "backup_date": datetime.now().isoformat(),
                    "total_lists": len(all_lists),
                    "total_tasks": 0
                },
                "lists": []
            }

            total_tasks = 0

            for task_list in all_lists:
                # Get tasks for this list
                tasks = self.db.get_tasks_by_list(task_list.id, show_completed=True)
                total_tasks += len(tasks)

                list_data = {
                    "id": task_list.id,
                    "name": task_list.name,
                    "category": task_list.category,
                    "position": task_list.position,
                    "created_at": task_list.created_at.isoformat() if hasattr(task_list.created_at,
                                                                              'isoformat') else str(
                        task_list.created_at),
                    "tasks": []
                }

                for task in tasks:
                    task_data = {
                        "id": task.id,
                        "title": task.title,
                        "notes": task.notes,
                        "due_date": task.due_date,
                        "start_time": task.start_time,
                        "end_time": task.end_time,
                        "reminder_time": task.reminder_time,
                        "motivation": task.motivation,
                        "completed": task.completed,
                        "parent_id": task.parent_id,
                        "position": task.position,
                        "recurrence_type": task.recurrence_type,
                        "recurrence_interval": task.recurrence_interval,
                        "last_completed_date": task.last_completed_date,
                        "created_at": task.created_at.isoformat() if hasattr(task.created_at, 'isoformat') else str(
                            task.created_at),
                        "subtasks": []
                    }

                    # Add subtasks
                    for subtask in task.subtasks:
                        subtask_data = {
                            "id": subtask.id,
                            "title": subtask.title,
                            "completed": subtask.completed,
                            "position": subtask.position
                        }
                        task_data["subtasks"].append(subtask_data)

                    list_data["tasks"].append(task_data)

                backup_data["lists"].append(list_data)

            backup_data["metadata"]["total_tasks"] = total_tasks

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Full backup created: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ Backup failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def export_list(self, list_id):
        """Export a single list with all its tasks"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            task_list = self.db.get_list_by_id(list_id)
            if not task_list:
                print(f"❌ List {list_id} not found")
                return None

            # Sanitize filename
            safe_name = "".join(c for c in task_list.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"list_{safe_name}_{timestamp}.json"
            filepath = self.backup_dir / filename

            tasks = self.db.get_tasks_by_list(list_id, show_completed=True)

            export_data = {
                "list": {
                    "name": task_list.name,
                    "category": task_list.category,
                    "exported_at": datetime.now().isoformat()
                },
                "tasks": []
            }

            for task in tasks:
                task_data = {
                    "title": task.title,
                    "notes": task.notes,
                    "due_date": task.due_date,
                    "start_time": task.start_time,
                    "end_time": task.end_time,
                    "reminder_time": task.reminder_time,
                    "motivation": task.motivation,
                    "completed": task.completed,
                    "recurrence_type": task.recurrence_type,
                    "recurrence_interval": task.recurrence_interval,
                    "subtasks": [{"title": st.title, "completed": st.completed} for st in task.subtasks]
                }
                export_data["tasks"].append(task_data)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"✅ List exported: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ Export failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def export_category(self, category):
        """Export all lists in a category"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"category_{category}_{timestamp}.json"
        filepath = self.backup_dir / filename

        try:
            lists = self.db.get_lists_by_category(category)

            export_data = {
                "category": category,
                "exported_at": datetime.now().isoformat(),
                "lists": []
            }

            for task_list in lists:
                tasks = self.db.get_tasks_by_list(task_list.id, show_completed=True)

                list_data = {
                    "name": task_list.name,
                    "tasks": []
                }

                for task in tasks:
                    task_data = {
                        "title": task.title,
                        "notes": task.notes,
                        "start_time": task.start_time,
                        "end_time": task.end_time,
                        "reminder_time": task.reminder_time,
                        "motivation": task.motivation,
                        "completed": task.completed,
                        "subtasks": [{"title": st.title, "completed": st.completed} for st in task.subtasks]
                    }
                    list_data["tasks"].append(task_data)

                export_data["lists"].append(list_data)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Category exported: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ Export failed: {e}")
            return None

    def export_to_markdown(self, list_id=None):
        """Export tasks to readable Markdown format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            if list_id:
                # Export single list
                task_list = self.db.get_list_by_id(list_id)
                if not task_list:
                    return None

                safe_name = "".join(c for c in task_list.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_name}_{timestamp}.md"
                lists_to_export = [(task_list, self.db.get_tasks_by_list(list_id, show_completed=True))]
            else:
                # Export all
                filename = f"all_tasks_{timestamp}.md"
                all_lists = self.db.get_all_lists()
                lists_to_export = [(lst, self.db.get_tasks_by_list(lst.id, show_completed=True)) for lst in all_lists]

            filepath = self.backup_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Momentum Track Export\n\n")
                f.write(f"**Exported on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")

                for task_list, tasks in lists_to_export:
                    f.write(f"## {task_list.name}\n\n")
                    f.write(f"*Category:* {task_list.category.title()}\n\n")

                    if not tasks:
                        f.write("*No tasks*\n\n")
                        continue

                    # Completed tasks
                    completed = [t for t in tasks if t.completed]
                    pending = [t for t in tasks if not t.completed]

                    if pending:
                        f.write("### 📝 Pending Tasks\n\n")
                        for task in pending:
                            f.write(f"- [ ] **{task.title}**\n")
                            if task.notes:
                                f.write(f"  - *Notes:* {task.notes}\n")
                            if task.start_time:
                                time_info = f"  - ⏰ {task.start_time}"
                                if task.end_time:
                                    time_info += f" - {task.end_time}"
                                f.write(f"{time_info}\n")
                            if task.motivation:
                                f.write(f"  - 💪 *\"{task.motivation}\"*\n")
                            if task.subtasks:
                                f.write(f"  - **Subtasks:**\n")
                                for st in task.subtasks:
                                    status = "x" if st.completed else " "
                                    f.write(f"    - [{status}] {st.title}\n")
                            f.write("\n")

                    if completed:
                        f.write("### ✅ Completed Tasks\n\n")
                        for task in completed:
                            f.write(f"- [x] ~~{task.title}~~\n")
                            if task.subtasks:
                                for st in task.subtasks:
                                    status = "x" if st.completed else " "
                                    f.write(f"  - [{status}] {st.title}\n")
                            f.write("\n")

                    f.write("\n---\n\n")

            print(f"✅ Markdown exported: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ Markdown export failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def import_from_backup(self, filepath):
        """Import data from a backup file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)

            imported_lists = 0
            imported_tasks = 0

            for list_data in backup_data.get("lists", []):
                # Create list
                list_id = self.db.create_list(
                    name=list_data["name"],
                    category=list_data["category"]
                )

                imported_lists += 1

                # Create tasks
                for task_data in list_data.get("tasks", []):
                    if task_data.get("parent_id") is None:  # Only parent tasks
                        task_id = self.db.create_task(
                            list_id=list_id,
                            title=task_data["title"],
                            notes=task_data.get("notes", ""),
                            due_date=task_data.get("due_date"),
                            start_time=task_data.get("start_time"),
                            end_time=task_data.get("end_time"),
                            reminder_time=task_data.get("reminder_time"),
                            recurrence_type=task_data.get("recurrence_type"),
                            recurrence_interval=task_data.get("recurrence_interval", 1),
                            motivation=task_data.get("motivation", "")
                        )

                        imported_tasks += 1

                        # Create subtasks
                        for subtask_data in task_data.get("subtasks", []):
                            self.db.create_task(
                                list_id=list_id,
                                title=subtask_data["title"],
                                parent_id=task_id
                            )
                            imported_tasks += 1

            print(f"✅ Import complete: {imported_lists} lists, {imported_tasks} tasks")
            return True

        except Exception as e:
            print(f"❌ Import failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def auto_backup(self):
        """Create automatic backup (keep last 5)"""
        try:
            backup_file = self.create_full_backup()

            # Clean old backups (keep last 5)
            backups = sorted(self.backup_dir.glob("momentum_backup_*.json"))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    old_backup.unlink()
                    print(f"🗑️ Deleted old backup: {old_backup.name}")

            return backup_file

        except Exception as e:
            print(f"❌ Auto-backup failed: {e}")
            return None

    def get_backup_list(self):
        """Get list of available backups"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob("*.json"):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "filepath": str(backup_file),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })

            return sorted(backups, key=lambda x: x["created"], reverse=True)

        except Exception as e:
            print(f"❌ Error getting backup list: {e}")
            return []

    def export_to_csv(self, list_id=None):
        """Export tasks to CSV format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tasks_export_{timestamp}.csv"
        filepath = self.backup_dir / filename

        try:
            import csv

            if list_id:
                lists_to_export = [self.db.get_list_by_id(list_id)]
            else:
                lists_to_export = self.db.get_all_lists()

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "List Name", "Category", "Task Title", "Notes",
                    "Start Time", "End Time", "Reminder", "Motivation",
                    "Completed", "Recurrence", "Created"
                ])

                for task_list in lists_to_export:
                    if not task_list:
                        continue
                    tasks = self.db.get_tasks_by_list(task_list.id, show_completed=True)

                    for task in tasks:
                        writer.writerow([
                            task_list.name,
                            task_list.category,
                            task.title,
                            task.notes or "",
                            task.start_time or "",
                            task.end_time or "",
                            task.reminder_time or "",
                            task.motivation or "",
                            "Yes" if task.completed else "No",
                            task.recurrence_type or "None",
                            task.created_at if hasattr(task, 'created_at') else ""
                        ])

            print(f"✅ CSV exported: {filepath}")
            return str(filepath)

        except Exception as e:
            print(f"❌ CSV export failed: {e}")
            return None