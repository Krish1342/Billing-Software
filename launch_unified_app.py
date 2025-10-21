"""
Launcher script for Unified Jewelry Management System

This script checks dependencies and launches the unified application.
"""

import sys
import os
import subprocess


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False

    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        ("PyQt5", "PyQt5"),
        ("reportlab", "reportlab"),
        ("PIL", "Pillow"),
    ]

    missing_packages = []

    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"❌ {package_name} is not installed")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("\nTo install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")

        # Ask user if they want to install automatically
        try:
            response = (
                input("\nDo you want to install missing packages now? (y/n): ")
                .lower()
                .strip()
            )
            if response in ["y", "yes"]:
                print("\nInstalling packages...")
                for package in missing_packages:
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", package]
                        )
                        print(f"✓ {package} installed successfully")
                    except subprocess.CalledProcessError:
                        print(f"❌ Failed to install {package}")
                        return False
                return True
            else:
                return False
        except KeyboardInterrupt:
            print("\nInstallation cancelled.")
            return False

    return True


def check_files():
    """Check if required application files exist."""
    required_files = [
        "unified_database.py",
        "unified_main_app.py",
        "billing_tab.py",
        "stock_tab.py",
        "analytics_tab.py",
        "settings_tab.py",
        "calc.py",
    ]

    missing_files = []

    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} found")
        else:
            print(f"❌ {file} not found")
            missing_files.append(file)

    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        print("Please ensure all application files are in the current directory.")
        return False

    return True


def create_settings_if_missing():
    """Create settings.json if it doesn't exist."""
    if not os.path.exists("settings.json"):
        print("Creating default settings.json...")

        import json

        default_settings = {
            "company": {
                "name": "Roopkala Jewellers",
                "address": "Shop No. 123, Jewelry Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "phone": "+91-9876543210",
                "email": "info@roopkalajewellers.com",
                "gstin": "27XXXXX1234X1ZX",
                "logo_path": "",
            },
            "tax": {"cgst_rate": "1.5", "sgst_rate": "1.5"},
            "app": {"theme": "light", "auto_save": True, "backup_enabled": True},
        }

        try:
            with open("settings.json", "w") as f:
                json.dump(default_settings, f, indent=4)
            print("✓ Default settings.json created")
        except Exception as e:
            print(f"❌ Failed to create settings.json: {e}")
            return False
    else:
        print("✓ settings.json found")

    return True


def launch_application():
    """Launch the unified application."""
    print("\n" + "=" * 50)
    print("🚀 LAUNCHING UNIFIED JEWELRY MANAGEMENT SYSTEM")
    print("=" * 50)

    try:
        # Change to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)

        # Import and run the main application
        from unified_main_app import main

        main()

    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        print("\nFor support, please check the error details above.")


def main():
    """Main launcher function."""
    print("=" * 60)
    print("🏪 UNIFIED JEWELRY MANAGEMENT SYSTEM LAUNCHER")
    print("=" * 60)
    print("Checking system requirements...\n")

    # Check Python version
    if not check_python_version():
        input("\nPress Enter to exit...")
        return

    print()

    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return

    print()

    # Check required files
    if not check_files():
        input("\nPress Enter to exit...")
        return

    print()

    # Create settings if missing
    if not create_settings_if_missing():
        input("\nPress Enter to exit...")
        return

    print("\n✅ All checks passed! Ready to launch application.\n")

    try:
        # Give user option to continue
        response = (
            input("Press Enter to launch the application (or 'q' to quit): ")
            .lower()
            .strip()
        )
        if response in ["q", "quit", "exit"]:
            print("👋 Goodbye!")
            return

        # Launch application
        launch_application()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
