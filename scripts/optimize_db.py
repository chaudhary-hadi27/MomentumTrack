#!/usr/bin/env python3
"""
Database Optimization Script
Run this to optimize your Momentum Track database
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_optimizer import DatabaseOptimizer
from database.db_manager import DatabaseManager


def main():
    print("\n" + "=" * 60)
    print("  MOMENTUM TRACK - DATABASE OPTIMIZATION")
    print("=" * 60 + "\n")

    # Initialize
    optimizer = DatabaseOptimizer()
    db = DatabaseManager()

    # Run optimization
    print("🔧 Running full database optimization...\n")
    optimizer.optimize_all()

    # Additional analysis
    print("\n" + "=" * 60)
    print("  QUERY PERFORMANCE ANALYSIS")
    print("=" * 60 + "\n")

    # Test common queries
    queries = [
        ("Get tasks by list",
         "SELECT * FROM tasks WHERE list_id = ? AND parent_id IS NULL ORDER BY completed, position",
         (1,)),

        ("Get completed tasks",
         "SELECT * FROM tasks WHERE completed = 1",
         None),

        ("Get tasks with reminders",
         "SELECT * FROM tasks WHERE reminder_time IS NOT NULL",
         None),

        ("Search tasks",
         "SELECT * FROM tasks WHERE title LIKE ?",
         ('%test%',)),
    ]

    for name, query, params in queries:
        print(f"\n📊 Testing: {name}")
        result = optimizer.benchmark_query(query, params, iterations=20)

        if result:
            print(f"  ✅ Average: {result['avg'] * 1000:.2f}ms")
            print(f"  ⚡ Best: {result['min'] * 1000:.2f}ms")

    # Vacuum recommendation
    stats = optimizer.get_database_stats()
    db_size_mb = stats.get('database_size_kb', 0) / 1024

    print("\n" + "=" * 60)
    print("  RECOMMENDATIONS")
    print("=" * 60 + "\n")

    if db_size_mb > 10:
        print("💡 Database size is large. Consider running VACUUM:")
        print("   optimizer.vacuum_database()")

    if stats.get('total_tasks', 0) > 1000:
        print("💡 Large number of tasks detected. Virtual scrolling recommended.")

    print("\n" + "=" * 60)
    print("  ✅ OPTIMIZATION COMPLETE!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Optimization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during optimization: {e}")
        sys.exit(1)