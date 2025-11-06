import sqlite3
from utils.constants import DB_NAME
import time


class DatabaseOptimizer:
    """Enhanced database optimization with query analysis"""

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        # Enable query optimization
        conn.execute('PRAGMA optimize')
        return conn

    def create_indexes(self):
        """Create comprehensive performance indexes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            print("🔧 Creating database indexes...")

            indexes = [
                # Task indexes
                ('idx_tasks_list_id',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_list_id ON tasks(list_id)'),
                ('idx_tasks_completed',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)'),
                ('idx_tasks_parent_id',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks(parent_id)'),
                ('idx_tasks_due_date',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)'),
                ('idx_tasks_reminder',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_reminder ON tasks(reminder_time)'),

                # Compound indexes for common queries
                ('idx_tasks_list_completed',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_list_completed ON tasks(list_id, completed, position)'),
                ('idx_tasks_list_parent',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_list_parent ON tasks(list_id, parent_id)'),
                ('idx_tasks_completed_date',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_completed_date ON tasks(completed, due_date)'),
                ('idx_tasks_list_parent_pos',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_list_parent_pos ON tasks(list_id, parent_id, position)'),

                # List indexes
                ('idx_lists_category',
                 'CREATE INDEX IF NOT EXISTS idx_lists_category ON task_lists(category, position)'),

                # Search optimization
                ('idx_tasks_title',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title COLLATE NOCASE)'),
                ('idx_tasks_search',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_search ON tasks(title, notes)'),

                # Recurrence optimization
                ('idx_tasks_recurrence',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_recurrence ON tasks(recurrence_type, last_completed_date)'),
            ]

            for name, query in indexes:
                start_time = time.time()
                cursor.execute(query)
                elapsed = time.time() - start_time
                print(f"  ✓ Created index: {name} ({elapsed:.3f}s)")

            conn.commit()
            print("✅ All indexes created successfully!")

        except Exception as e:
            print(f"❌ Error creating indexes: {e}")
            conn.rollback()
        finally:
            conn.close()

    def analyze_database(self):
        """Analyze database for query optimization"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            print("📊 Analyzing database...")
            start_time = time.time()
            cursor.execute('ANALYZE')
            conn.commit()
            elapsed = time.time() - start_time
            print(f"✅ Database analysis complete! ({elapsed:.3f}s)")
        except Exception as e:
            print(f"❌ Error analyzing database: {e}")
        finally:
            conn.close()

    def vacuum_database(self):
        """Optimize database file size"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            print("🧹 Vacuuming database...")
            start_time = time.time()
            cursor.execute('VACUUM')
            conn.commit()
            elapsed = time.time() - start_time
            print(f"✅ Database vacuumed successfully! ({elapsed:.3f}s)")
        except Exception as e:
            print(f"❌ Error vacuuming database: {e}")
        finally:
            conn.close()

    def get_database_stats(self):
        """Get comprehensive database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            stats = {}

            # Table sizes
            cursor.execute("SELECT COUNT(*) FROM tasks")
            stats['total_tasks'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM task_lists")
            stats['total_lists'] = cursor.fetchone()[0]

            # Completed tasks
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
            stats['completed_tasks'] = cursor.fetchone()[0]

            # Tasks with reminders
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE reminder_time IS NOT NULL")
            stats['tasks_with_reminders'] = cursor.fetchone()[0]

            # Recurring tasks
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE recurrence_type IS NOT NULL")
            stats['recurring_tasks'] = cursor.fetchone()[0]

            # Tasks by category
            cursor.execute('''
                SELECT tl.category, COUNT(t.id) as count
                FROM task_lists tl
                LEFT JOIN tasks t ON tl.id = t.list_id
                GROUP BY tl.category
            ''')
            stats['tasks_by_category'] = dict(cursor.fetchall())

            # Subtasks count
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE parent_id IS NOT NULL")
            stats['total_subtasks'] = cursor.fetchone()[0]

            # Index information
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='index' AND sql IS NOT NULL
            ''')
            stats['indexes'] = [row[0] for row in cursor.fetchall()]

            # Database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            stats['database_size_kb'] = db_size / 1024

            return stats

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
        finally:
            conn.close()

    def optimize_all(self):
        """Run all optimization tasks"""
        print("\n" + "=" * 50)
        print("🚀 Starting Database Optimization")
        print("=" * 50 + "\n")

        start_time = time.time()

        self.create_indexes()
        self.analyze_database()

        # Print stats
        stats = self.get_database_stats()

        elapsed = time.time() - start_time

        print("\n" + "=" * 50)
        print("📊 Database Statistics:")
        print("=" * 50)
        print(f"  Total Tasks: {stats.get('total_tasks', 0)}")
        print(f"  Total Lists: {stats.get('total_lists', 0)}")
        print(f"  Completed Tasks: {stats.get('completed_tasks', 0)}")
        print(f"  Subtasks: {stats.get('total_subtasks', 0)}")
        print(f"  Tasks with Reminders: {stats.get('tasks_with_reminders', 0)}")
        print(f"  Recurring Tasks: {stats.get('recurring_tasks', 0)}")
        print(f"  Database Size: {stats.get('database_size_kb', 0):.2f} KB")
        print(f"  Indexes: {len(stats.get('indexes', []))}")
        print(f"\n⏱️  Total optimization time: {elapsed:.2f}s")
        print("=" * 50 + "\n")

    def get_query_plan(self, query):
        """Get query execution plan for debugging"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = cursor.fetchall()

            print(f"\n📋 Query Plan for: {query[:50]}...")
            print("-" * 50)
            for row in plan:
                print(f"  {row}")
            print("-" * 50)

            return plan
        except Exception as e:
            print(f"Error getting query plan: {e}")
            return []
        finally:
            conn.close()

    def benchmark_query(self, query, params=None, iterations=10):
        """Benchmark a query's performance"""
        conn = self.get_connection()
        cursor = conn.cursor()

        times = []

        try:
            for i in range(iterations):
                start = time.time()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                cursor.fetchall()
                elapsed = time.time() - start
                times.append(elapsed)

            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print(f"\n⚡ Query Benchmark ({iterations} iterations):")
            print(f"  Average: {avg_time * 1000:.2f}ms")
            print(f"  Min: {min_time * 1000:.2f}ms")
            print(f"  Max: {max_time * 1000:.2f}ms")

            return {'avg': avg_time, 'min': min_time, 'max': max_time}

        except Exception as e:
            print(f"Benchmark error: {e}")
            return None
        finally:
            conn.close()