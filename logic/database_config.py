"""
Database Configuration Manager
Handles switching between online (Supabase) and offline (SQLite) modes
"""

import os
from typing import Union
from logic.database_manager import SupabaseDatabaseManager
from logic.local_database_manager import LocalDatabaseManager


class DatabaseConfig:
    """Configuration manager for database connections."""

    @staticmethod
    def get_database_manager(
        prefer_online: bool = True,
    ) -> Union[SupabaseDatabaseManager, LocalDatabaseManager]:
        """
        Get appropriate database manager based on configuration and availability.

        Args:
            prefer_online: Whether to prefer online (Supabase) connection

        Returns:
            Database manager instance (Supabase or Local)
        """

        # Check for offline mode flag
        if os.getenv("OFFLINE_MODE", "").lower() == "true":
            print("🔧 Offline mode enabled - using local database")
            return LocalDatabaseManager()

        # Try online connection if preferred
        if prefer_online:
            try:
                # Check if Supabase credentials are available
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_ANON_KEY")

                if supabase_url and supabase_key:
                    db = SupabaseDatabaseManager()
                    print("✅ Connected to Supabase (online mode)")
                    return db
                else:
                    print(
                        "⚠️  Supabase credentials not found - switching to offline mode"
                    )

            except Exception as e:
                print(f"⚠️  Supabase connection failed: {e}")
                print("🔧 Switching to offline mode...")

        # Fallback to local database
        print("💾 Using local SQLite database (offline mode)")
        return LocalDatabaseManager()

    @staticmethod
    def is_online_mode() -> bool:
        """Check if currently using online mode."""
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")
            return bool(
                supabase_url
                and supabase_key
                and os.getenv("OFFLINE_MODE", "").lower() != "true"
            )
        except:
            return False

    @staticmethod
    def switch_to_offline():
        """Switch to offline mode."""
        os.environ["OFFLINE_MODE"] = "true"
        print("🔧 Switched to offline mode")

    @staticmethod
    def switch_to_online():
        """Switch to online mode."""
        if "OFFLINE_MODE" in os.environ:
            del os.environ["OFFLINE_MODE"]
        print("🌐 Switched to online mode")


# Convenience function for main.py
def create_database_manager() -> Union[SupabaseDatabaseManager, LocalDatabaseManager]:
    """Create and return appropriate database manager."""
    return DatabaseConfig.get_database_manager()
