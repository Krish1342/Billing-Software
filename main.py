"""
Unified Jewelry Shop Management System
Main application entry point
"""

import sys
import os
from PyQt5.QtWidgets import QApplication


# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


# Load environment variables
load_env_file()

# Add paths for our organized structure
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ui"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "logic"))

from ui.main_window import UnifiedJewelryApp


def main():
    """Main application entry point."""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Unified Jewelry Management System")
        app.setOrganizationName("Roopkala Jewellers")

        # Create and show main window
        window = UnifiedJewelryApp()
        window.show()

        # Center window on screen
        window.center_on_screen()

        sys.exit(app.exec_())

    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
