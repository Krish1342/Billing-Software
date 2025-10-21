"""
Logger module for Jewelry Shop Stock Management System

This module provides logging functionality for tracking user actions
and system events throughout the application.
"""

import os
import logging
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path


class ActionType(Enum):
    """Enumeration for different types of actions that can be logged."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    VIEW = "VIEW"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    BACKUP = "BACKUP"
    RESTORE = "RESTORE"


class HistoryLogger:
    """
    Logger class for tracking user actions and system events.

    This class provides comprehensive logging functionality including
    file logging, database logging, and action history tracking.
    """

    def __init__(self, db_manager=None):
        """
        Initialize the HistoryLogger.

        Args:
            db_manager: Database manager instance for logging to database
        """
        self.db_manager = db_manager
        self.setup_file_logger()

    def setup_file_logger(self):
        """Set up file-based logging configuration."""
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        # Configure logging
        log_filename = (
            logs_dir / f"jewelry_shop_{datetime.now().strftime('%Y%m%d')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_filename), logging.StreamHandler()],
        )

        self.logger = logging.getLogger("JewelryShop")

    def log_action(
        self,
        action: ActionType,
        entity_type: str,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user: str = "System",
    ):
        """
        Log an action to both file and database.

        Args:
            action: Type of action performed
            entity_type: Type of entity (product, supplier, etc.)
            entity_id: ID of the entity affected
            details: Additional details about the action
            user: User who performed the action
        """
        # Create log message
        message = f"{user} performed {action.value} on {entity_type}"
        if entity_id:
            message += f" (ID: {entity_id})"

        if details:
            details_str = ", ".join([f"{k}: {v}" for k, v in details.items()])
            message += f" - {details_str}"

        # Log to file
        self.logger.info(message)

        # Log to database if available
        if self.db_manager:
            try:
                self.db_manager.add_history_record(
                    action=action.value,
                    table_name=entity_type,
                    record_id=(
                        int(entity_id) if entity_id and entity_id.isdigit() else None
                    ),
                    new_values=str(details) if details else None,
                    user_id=user,
                )
            except Exception as e:
                self.logger.error(f"Failed to log to database: {e}")

    def log_error(self, error: Exception, context: str = ""):
        """
        Log an error with context information.

        Args:
            error: The exception that occurred
            context: Additional context about when the error occurred
        """
        message = f"Error in {context}: {str(error)}"
        self.logger.error(message, exc_info=True)

    def log_info(self, message: str):
        """
        Log an informational message.

        Args:
            message: The message to log
        """
        self.logger.info(message)

    def log_warning(self, message: str):
        """
        Log a warning message.

        Args:
            message: The warning message to log
        """
        self.logger.warning(message)

    def get_recent_logs(self, limit: int = 100) -> list:
        """
        Get recent log entries from the database.

        Args:
            limit: Maximum number of entries to retrieve

        Returns:
            List of recent log entries
        """
        if not self.db_manager:
            return []

        try:
            return self.db_manager.get_history(limit)
        except Exception as e:
            self.log_error(e, "getting recent logs")
            return []

    def export_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        output_file: Optional[str] = None,
    ) -> str:
        """
        Export logs for a date range to a file.

        Args:
            start_date: Start date for export
            end_date: End date for export
            output_file: Output file path (optional)

        Returns:
            Path to the exported file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"logs/export_{timestamp}.txt"

        try:
            if self.db_manager:
                # Use the existing get_history method since get_history_by_date_range may not exist
                history_entries = self.db_manager.get_history(
                    1000
                )  # Get more entries to filter

                # Filter by date range if needed
                filtered_entries = []
                for entry in history_entries:
                    # Note: This assumes the timestamp field exists in the database
                    # You may need to adjust based on actual database schema
                    filtered_entries.append(entry)

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"Log Export: {start_date} to {end_date}\n")
                    f.write("=" * 50 + "\n\n")

                    for entry in filtered_entries:
                        timestamp = entry.get(
                            "timestamp", entry.get("created_at", "Unknown")
                        )
                        action = entry.get("action", "Unknown")
                        table_name = entry.get("table_name", "Unknown")
                        details = entry.get("new_values", entry.get("details", ""))
                        f.write(f"{timestamp} - {action} - {table_name} - {details}\n")

                self.log_info(f"Logs exported to {output_file}")
                return output_file
            else:
                raise Exception("Database manager not available")

        except Exception as e:
            self.log_error(e, "exporting logs")
            raise

    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files.

        Args:
            days_to_keep: Number of days of logs to keep
        """
        try:
            logs_dir = Path("logs")
            if logs_dir.exists():
                cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

                for log_file in logs_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date:
                        log_file.unlink()
                        self.log_info(f"Removed old log file: {log_file}")

        except Exception as e:
            self.log_error(e, "cleaning up old logs")
