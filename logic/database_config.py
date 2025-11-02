"""
Database Configuration Manager
Simplified to use only SQLite database
"""

import os
from logic.local_database_manager import LocalDatabaseManager


class DatabaseConfig:
    """Configuration manager for database connections - SQLite only."""

    @staticmethod
    def get_database_manager() -> LocalDatabaseManager:
        """
        Get SQLite database manager.

        Returns:
            LocalDatabaseManager instance
        """
        print("💾 Using local SQLite database")
        return LocalDatabaseManager()

    @staticmethod
    def is_online_mode() -> bool:
        """Always returns False since we only use SQLite."""
        return False


# Convenience function for main.py
def create_database_manager() -> LocalDatabaseManager:
    """Create and return SQLite database manager."""
    return DatabaseConfig.get_database_manager()
