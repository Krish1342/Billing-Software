"""
Unified Jewelry Shop Management System
Main PyQt Application combining Billing and Stock Management

This application merges the billing system and stock management system
into a single PyQt application with automatic stock deduction when bills are generated.
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QStatusBar,
    QMenuBar,
    QAction,
    QMessageBox,
    QSplashScreen,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QFont, QIcon
from decimal import Decimal

# Import our modules
from unified_database import UnifiedDatabaseManager
from calc import create_calculator

# Import tab modules
from billing_tab import BillingTab
from stock_tab import StockTab
from analytics_tab import AnalyticsTab
from settings_tab import SettingsTab


class DatabaseInitThread(QThread):
    """Thread to initialize database in background."""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()

    def run(self):
        """Initialize database."""
        self.status.emit("Initializing database...")
        self.progress.emit(20)

        try:
            db = UnifiedDatabaseManager()
            self.status.emit("Setting up tables...")
            self.progress.emit(60)

            # Verify tables exist
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

            self.status.emit("Database ready!")
            self.progress.emit(100)

        except Exception as e:
            self.status.emit(f"Database error: {str(e)}")

        self.finished.emit()


class UnifiedJewelryApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Load settings
        self.load_settings()

        # Initialize components
        self.db = None
        self.calculator = None

        # Setup UI
        self.init_ui()

        # Initialize database in background
        self.init_database()

    def load_settings(self):
        """Load application settings."""
        self.settings_path = "settings.json"
        try:
            with open(self.settings_path, "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            # Create default settings
            self.settings = {
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
            self.save_settings()

    def save_settings(self):
        """Save application settings."""
        try:
            with open(self.settings_path, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not save settings: {str(e)}")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(
            f"{self.settings['company']['name']} - Unified Management System"
        )
        self.setGeometry(100, 100, 1400, 900)

        # Set application icon (if available)
        # self.setWindowIcon(QIcon('icon.png'))

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header
        self.create_header(main_layout)

        # Tab widget
        self.create_tabs(main_layout)

        # Status bar
        self.create_status_bar()

        # Menu bar
        self.create_menu_bar()

        # Apply styling
        self.apply_styling()

    def create_header(self, layout):
        """Create application header."""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        # Company name and title
        title_label = QLabel(self.settings["company"]["name"])
        title_label.setObjectName("title_label")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        subtitle_label = QLabel("Unified Billing & Stock Management System")
        subtitle_label.setObjectName("subtitle_label")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)

        # Vertical layout for title and subtitle
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)

        layout.addWidget(header_widget)

    def create_tabs(self, layout):
        """Create the main tab widget."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        # Create actual tabs with real functionality
        if (
            hasattr(self, "db")
            and self.db
            and hasattr(self, "calculator")
            and self.calculator
        ):
            # Billing tab
            self.billing_tab = BillingTab(self.db, self.calculator, self.settings)
            self.billing_tab.invoice_created.connect(self.on_invoice_created)
            self.tab_widget.addTab(self.billing_tab, "🧾 Billing")

            # Stock tab
            self.stock_tab = StockTab(self.db, self.settings)
            self.stock_tab.stock_updated.connect(self.on_stock_updated)
            self.stock_tab.product_added.connect(self.on_product_added)
            self.tab_widget.addTab(self.stock_tab, "📦 Stock")

            # Analytics tab
            self.analytics_tab = AnalyticsTab(self.db, self.settings)
            self.tab_widget.addTab(self.analytics_tab, "📊 Analytics")

            # Settings tab
            self.settings_tab = SettingsTab(self.db, self.settings, self.settings_path)
            self.settings_tab.settings_updated.connect(self.on_settings_updated)
            self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        else:
            # Create placeholder tabs if database not ready
            self.create_placeholder_tabs()

        layout.addWidget(self.tab_widget)

    def create_placeholder_tabs(self):
        """Create placeholder tabs when database is not ready."""
        # Create placeholder tabs (will be replaced with actual implementations)
        self.create_billing_placeholder()
        self.create_stock_placeholder()
        self.create_analytics_placeholder()
        self.create_settings_placeholder()

    def create_billing_tab(self):
        """Create billing tab (placeholder)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel("🧾 Billing Module")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #2E8B57; margin: 50px;"
        )
        layout.addWidget(label)

        info_label = QLabel(
            "This module will handle:\n• Invoice creation\n• Customer management\n• PDF generation\n• Automatic stock deduction"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; margin: 20px;")
        layout.addWidget(info_label)

        self.tab_widget.addTab(tab, "🧾 Billing")

    def create_billing_placeholder(self):
        """Create billing tab placeholder."""
        self.create_billing_tab()

    def create_stock_tab(self):
        """Create stock management tab (placeholder)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel("📦 Stock Management")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #4169E1; margin: 50px;"
        )
        layout.addWidget(label)

        info_label = QLabel(
            "This module will handle:\n• Product inventory\n• Categories & suppliers\n• Stock movements\n• Low stock alerts"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; margin: 20px;")
        layout.addWidget(info_label)

        self.tab_widget.addTab(tab, "📦 Stock")

    def create_stock_placeholder(self):
        """Create stock tab placeholder."""
        self.create_stock_tab()

    def create_analytics_tab(self):
        """Create analytics tab (placeholder)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel("📊 Analytics & Reports")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #FF6347; margin: 50px;"
        )
        layout.addWidget(label)

        info_label = QLabel(
            "This module will handle:\n• Sales reports\n• Inventory analytics\n• Charts & graphs\n• Export functionality"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; margin: 20px;")
        layout.addWidget(info_label)

        self.tab_widget.addTab(tab, "📊 Analytics")

    def create_analytics_placeholder(self):
        """Create analytics tab placeholder."""
        self.create_analytics_tab()

    def create_settings_tab(self):
        """Create settings tab (placeholder)."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel("⚙️ Settings")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #9932CC; margin: 50px;"
        )
        layout.addWidget(label)

        info_label = QLabel(
            "This module will handle:\n• Company information\n• Tax settings\n• Application preferences\n• Database management"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; margin: 20px;")
        layout.addWidget(info_label)

        self.tab_widget.addTab(tab, "⚙️ Settings")

    def create_settings_placeholder(self):
        """Create settings tab placeholder."""
        self.create_settings_tab()

    def on_invoice_created(self, invoice_id: int, invoice_number: str):
        """Handle invoice created signal."""
        self.status_label.setText(f"Invoice {invoice_number} created successfully!")

        # Refresh analytics if tab exists
        if hasattr(self, "analytics_tab"):
            self.analytics_tab.load_data()

    def on_stock_updated(self):
        """Handle stock updated signal."""
        self.status_label.setText("Stock updated successfully!")

        # Refresh billing tab product list if tab exists
        if hasattr(self, "billing_tab"):
            self.billing_tab.load_data()

    def on_product_added(self, product_id: int, product_name: str):
        """Handle product added signal."""
        self.status_label.setText(f"Product '{product_name}' added successfully!")

        # Refresh billing tab product list if tab exists
        if hasattr(self, "billing_tab"):
            self.billing_tab.load_data()

    def on_settings_updated(self, settings: dict):
        """Handle settings updated signal."""
        self.settings = settings
        self.status_label.setText("Settings updated successfully!")

        # Update calculator with new tax rates
        if hasattr(self, "calculator") and self.calculator:
            self.calculator = create_calculator(
                settings["tax"]["cgst_rate"], settings["tax"]["sgst_rate"]
            )

            # Update billing tab calculator if tab exists
            if hasattr(self, "billing_tab"):
                self.billing_tab.calculator = self.calculator

    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add permanent widgets to status bar
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Add database status
        self.db_status_label = QLabel("Database: Not Connected")
        self.status_bar.addPermanentWidget(self.db_status_label)

    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_invoice_action = QAction("&New Invoice", self)
        new_invoice_action.setShortcut("Ctrl+N")
        new_invoice_action.triggered.connect(self.new_invoice)
        file_menu.addAction(new_invoice_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        backup_action = QAction("&Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        tools_menu.addAction(backup_action)

        restore_action = QAction("&Restore Database", self)
        restore_action.triggered.connect(self.restore_database)
        tools_menu.addAction(restore_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def apply_styling(self):
        """Apply custom styling to the application."""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
            border-radius: 5px;
        }
        
        QTabWidget::tab-bar {
            alignment: center;
        }
        
        QTabBar::tab {
            background-color: #e1e1e1;
            border: 1px solid #c0c0c0;
            padding: 8px 16px;
            margin-right: 2px;
            border-radius: 4px 4px 0px 0px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom-color: white;
        }
        
        QTabBar::tab:hover {
            background-color: #f0f0f0;
        }
        
        #title_label {
            color: #2c3e50;
            padding: 10px;
        }
        
        #subtitle_label {
            color: #7f8c8d;
            padding-bottom: 10px;
        }
        
        QStatusBar {
            background-color: #34495e;
            color: white;
            font-size: 12px;
        }
        
        QStatusBar QLabel {
            color: white;
            padding: 2px 10px;
        }
        """

        self.setStyleSheet(style)

    def init_database(self):
        """Initialize database connection."""
        self.status_label.setText("Initializing database...")

        # Create and start database initialization thread
        self.db_thread = DatabaseInitThread()
        self.db_thread.status.connect(self.update_status)
        self.db_thread.finished.connect(self.on_database_ready)
        self.db_thread.start()

    def update_status(self, message):
        """Update status message."""
        self.status_label.setText(message)

    def on_database_ready(self):
        """Called when database is ready."""
        try:
            self.db = UnifiedDatabaseManager()
            self.calculator = create_calculator(
                self.settings["tax"]["cgst_rate"], self.settings["tax"]["sgst_rate"]
            )

            self.db_status_label.setText("Database: Connected")
            self.status_label.setText("Ready")

            # Clear existing tabs and create real ones
            self.tab_widget.clear()

            # Create real tabs now that database is ready
            # Billing tab
            self.billing_tab = BillingTab(self.db, self.calculator, self.settings)
            self.billing_tab.invoice_created.connect(self.on_invoice_created)
            self.tab_widget.addTab(self.billing_tab, "🧾 Billing")

            # Stock tab
            self.stock_tab = StockTab(self.db, self.settings)
            self.stock_tab.stock_updated.connect(self.on_stock_updated)
            self.stock_tab.product_added.connect(self.on_product_added)
            self.tab_widget.addTab(self.stock_tab, "📦 Stock")

            # Analytics tab
            self.analytics_tab = AnalyticsTab(self.db, self.settings)
            self.tab_widget.addTab(self.analytics_tab, "📊 Analytics")

            # Settings tab
            self.settings_tab = SettingsTab(self.db, self.settings, self.settings_path)
            self.settings_tab.settings_updated.connect(self.on_settings_updated)
            self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")

            # Enable UI components
            self.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(
                self, "Database Error", f"Failed to initialize database:\n{str(e)}"
            )
            self.db_status_label.setText("Database: Error")
            self.status_label.setText("Database initialization failed")

    def new_invoice(self):
        """Create new invoice."""
        # Switch to billing tab
        self.tab_widget.setCurrentIndex(0)
        self.status_label.setText("Creating new invoice...")

    def backup_database(self):
        """Backup database."""
        QMessageBox.information(
            self, "Backup", "Database backup functionality will be implemented."
        )

    def restore_database(self):
        """Restore database."""
        QMessageBox.information(
            self, "Restore", "Database restore functionality will be implemented."
        )

    def show_about(self):
        """Show about dialog."""
        about_text = f"""
        <h2>{self.settings['company']['name']}</h2>
        <h3>Unified Billing & Stock Management System</h3>
        <p>Version 1.0.0</p>
        <p>A comprehensive solution for jewelry shop management combining billing and inventory.</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Invoice generation with automatic stock deduction</li>
        <li>Complete inventory management</li>
        <li>Sales analytics and reporting</li>
        <li>Customer and supplier management</li>
        </ul>
        <p><i>Built with PyQt5 and SQLite</i></p>
        """

        QMessageBox.about(self, "About", about_text)

    def closeEvent(self, event):
        """Handle application close event."""
        if self.db:
            self.db.close()
        event.accept()


class SplashScreen(QSplashScreen):
    """Splash screen for application startup."""

    def __init__(self):
        super().__init__()

        # Create a simple splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)

        self.setPixmap(pixmap)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        # Add text
        self.showMessage(
            "Unified Jewelry Management System\nLoading...",
            Qt.AlignCenter | Qt.AlignBottom,
            Qt.black,
        )


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Unified Jewelry Management System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Roopkala Jewellers")

    # Show splash screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Create main window
    window = UnifiedJewelryApp()

    # Show main window and hide splash
    QTimer.singleShot(2000, splash.close)
    QTimer.singleShot(2000, window.show)

    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
