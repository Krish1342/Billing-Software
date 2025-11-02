#!/usr/bin/env python3
"""
Database Clearing Utility for Jewelry Management System
This script allows you to clear all data from the SQLite database while keeping the schema intact.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the logic directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "logic"))

from local_database_manager import LocalDatabaseManager


def clear_database_data(db_path: str = "jewelry_management.db"):
    """Clear all data from the database while keeping the schema."""

    # Check if database file exists
    if not os.path.exists(db_path):
        print(f"⚠️  Database file '{db_path}' not found.")
        print("🔍 The database will be created when the application runs.")
        return True

    try:
        print(f"🗃️  Working with database: {db_path}")

        # Create database manager instance
        db_manager = LocalDatabaseManager(db_path)

        # Clear all data
        success = db_manager.clear_all_data()

        if success:
            print("\n✅ Database cleared successfully!")
            print("📋 All tables are now empty but schema is preserved.")
            print("🔄 Sample data will be re-added when the application starts.")
        else:
            print("\n❌ Failed to clear database.")

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def reset_database_with_sample_data(db_path: str = "jewelry_management.db"):
    """Reset database and add sample data."""

    try:
        print(f"🗃️  Working with database: {db_path}")

        # Create database manager instance
        db_manager = LocalDatabaseManager(db_path)

        # Reset with sample data
        success = db_manager.reset_database()

        if success:
            print("\n✅ Database reset successfully!")
            print("📋 Schema preserved and sample data added.")
        else:
            print("\n❌ Failed to reset database.")

        return success

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function to handle user choices."""

    print("=" * 50)
    print("🗄️  JEWELRY MANAGEMENT DATABASE CLEANER")
    print("=" * 50)
    print()

    # Check for database files
    db_files = []
    for file in os.listdir("."):
        if file.endswith(".db"):
            db_files.append(file)

    if db_files:
        print("📁 Found database files:")
        for i, db_file in enumerate(db_files, 1):
            size = os.path.getsize(db_file)
            print(f"   {i}. {db_file} ({size:,} bytes)")
        print()
    else:
        print("📁 No database files found in current directory.")
        print("   Database will be created when application runs.")
        print()

    print("Choose an option:")
    print("1. Clear all data (keep schema)")
    print("2. Reset database with sample data")
    print("3. Exit")
    print()

    try:
        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            print("\n🧹 Clearing all database data...")
            db_path = "jewelry_management.db"
            if db_files and len(db_files) == 1:
                db_path = db_files[0]
            elif db_files and len(db_files) > 1:
                print(
                    "\nMultiple database files found. Using default: jewelry_management.db"
                )

            clear_database_data(db_path)

        elif choice == "2":
            print("\n🔄 Resetting database with sample data...")
            db_path = "jewelry_management.db"
            if db_files and len(db_files) == 1:
                db_path = db_files[0]
            elif db_files and len(db_files) > 1:
                print(
                    "\nMultiple database files found. Using default: jewelry_management.db"
                )

            reset_database_with_sample_data(db_path)

        elif choice == "3":
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
