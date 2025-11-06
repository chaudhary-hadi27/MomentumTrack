import sqlite3
from utils.constants import DB_NAME


class DatabaseOptimizer:
    """Optimizes database performance with indexes and query improvements"""

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_indexes(self):
        """Create performance indexes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            print("🔧 Creating database indexes...")

            # Task indexes
            indexes = [
                # Single column indexes
                ('idx_tasks_list_id', 'CREATE INDEX IF NOT EXISTS idx_tasks_list_id ON tasks(list_id)'),
                ('idx_tasks_completed', 'CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)'),
                ('idx_tasks_parent_id', 'CREATE INDEX IF NOT EXISTS idx_tasks_parent_id ON tasks(parent_id)'),
                ('idx_tasks_due_date', 'CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)'),
                ('idx_tasks_reminder', 'CREATE INDEX IF NOT EXISTS idx_tasks_reminder ON tasks(reminder_time)'),

                # Compound indexes for common queries
                ('idx_tasks_list_completed',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_list_completed ON tasks(list_id, completed, position)'),
                ('idx_tasks_list_parent',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_list_parent ON tasks(list_id, parent_id)'),
                ('idx_tasks_completed_date',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_completed_date ON tasks(completed, due_date)'),

                # List indexes
                ('idx_lists_category',
                 'CREATE INDEX IF NOT EXISTS idx_lists_category ON task_lists(category, position)'),

                # Full-text search index (for search optimization)
                ('idx_tasks_title',
                 'CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title)'),
            ]

            for name, query in indexes:
                cursor.execute(query)
                print(f"  ✓ Created index: {name}")

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
            cursor.execute('ANALYZE')
            conn.commit()
            print("✅ Database analysis complete!")
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
            cursor.execute('VACUUM')
            conn.commit()
            print("✅ Database vacuumed successfully!")
        except Exception as e:
            print(f"❌ Error vacuuming database: {e}")
        finally:
            conn.close()

    def get_database_stats(self):
        """Get database statistics"""
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

            # Tasks by category
            cursor.execute('''
                SELECT tl.category, COUNT(t.id) as count
                FROM task_lists tl
                LEFT JOIN tasks t ON tl.id = t.list_id
                GROUP BY tl.category
            ''')
            stats['tasks_by_category'] = dict(cursor.fetchall())

            # Index information
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='index' AND sql IS NOT NULL
            ''')
            stats['indexes'] = [row[0] for row in cursor.fetchall()]

            return stats

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
        finally:
            conn.close()

    def optimize_all(self):
        """Run all optimization tasks"""
        self.create_indexes()
        self.analyze_database()

        # Print stats
        stats = self.get_database_stats()
        print("\n📊 Database Statistics:")
        print(f"  Total Tasks: {stats.get('total_tasks', 0)}")
        print(f"  Total Lists: {stats.get('total_lists', 0)}")
        print(f"  Completed: {stats.get('completed_tasks', 0)}")
        print(f"  Indexes: {len(stats.get('indexes', []))}")