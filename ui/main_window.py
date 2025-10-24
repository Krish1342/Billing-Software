"""
Main application window with tabbed interface
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
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
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from logic.database_manager import SupabaseDatabaseManager as UnifiedDatabaseManager
from logic.calculator import create_calculator
from ui.billing_tab import BillingTab
from ui.stock_tab import StockTab
from ui.analytics_tab import AnalyticsTab
from ui.settings_tab import SettingsTab


class UnifiedJewelryApp(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.load_settings()
        self.init_database()
        self.init_ui()

    def load_settings(self):
        """Load application settings."""
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = self.create_default_settings()
            self.save_settings()

    def create_default_settings(self):
        """Create default settings."""
        return {
            "company": {
                "name": "Roopkala Jewellers",
                "address": "123 Jewelry Street, City, State",
                "phone": "+91-9876543210",
                "email": "info@roopkala.com",
                "gstin": "22ABCDE1234F1Z5",
            },
            "tax": {"cgst_rate": 1.5, "sgst_rate": 1.5},
            "invoice": {"prefix": "RK", "start_number": 1001},
        }

    def save_settings(self):
        """Save current settings."""
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not save settings: {str(e)}")

    def init_database(self):
        """Initialize database connection."""
        try:
            self.db = UnifiedDatabaseManager()
            self.calculator = create_calculator(
                self.settings["tax"]["cgst_rate"], self.settings["tax"]["sgst_rate"]
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Database Error", f"Failed to initialize database: {str(e)}"
            )
            sys.exit(1)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"{self.settings['company']['name']} - Management System")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget
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
        header_layout = QVBoxLayout(header_widget)

        title_label = QLabel(self.settings["company"]["name"])
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")

        subtitle_label = QLabel("Unified Billing & Stock Management System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_widget)

    def create_tabs(self, layout):
        """Create the main tab widget."""
        self.tab_widget = QTabWidget()

        # Billing tab
        self.billing_tab = BillingTab(self.db, self.calculator, self.settings)
        self.billing_tab.invoice_created.connect(self.on_invoice_created)
        self.tab_widget.addTab(self.billing_tab, "🧾 Billing")

        # Stock tab
        self.stock_tab = StockTab(self.db, self.settings)
        self.stock_tab.stock_updated.connect(self.on_stock_updated)
        self.tab_widget.addTab(self.stock_tab, "📦 Stock Management")

        # Analytics tab
        self.analytics_tab = AnalyticsTab(self.db, self.settings)
        self.tab_widget.addTab(self.analytics_tab, "📊 Analytics")

        # Settings tab
        self.settings_tab = SettingsTab(self.db, self.settings)
        self.settings_tab.settings_updated.connect(self.on_settings_updated)
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")

        # Connect tab change signal to refresh billing when switched to
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tab_widget)

    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        self.db_status_label = QLabel("Database: Connected")
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
        
        QStatusBar {
            background-color: #34495e;
            color: white;
            font-size: 12px;
        }
        """
        self.setStyleSheet(style)

    def center_on_screen(self):
        """Center the window on screen."""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2
        )

    def on_invoice_created(self, invoice_id, invoice_number):
        """Handle invoice created signal."""
        self.status_label.setText(f"Invoice {invoice_number} created successfully!")
        self.analytics_tab.refresh_data()
        self.billing_tab.refresh_products()  # Refresh products in billing tab

    def on_stock_updated(self):
        """Handle stock updated signal."""
        self.status_label.setText("Stock updated successfully!")
        self.billing_tab.refresh_products()

    def on_tab_changed(self, index):
        """Handle tab change - refresh billing tab when switched to it."""
        if index == 0:  # Billing tab index
            self.billing_tab.refresh_products()

    def on_settings_updated(self, settings):
        """Handle settings updated signal."""
        self.settings = settings
        self.save_settings()
        self.status_label.setText("Settings updated successfully!")

        # Update calculator with new tax rates
        self.calculator = create_calculator(
            settings["tax"]["cgst_rate"], settings["tax"]["sgst_rate"]
        )
        self.billing_tab.update_calculator(self.calculator)

    def new_invoice(self):
        """Create new invoice."""
        self.tab_widget.setCurrentIndex(0)  # Switch to billing tab
        self.billing_tab.new_invoice()

    def show_about(self):
        """Show about dialog."""
        about_text = f"""
        <h2>{self.settings['company']['name']}</h2>
        <h3>Unified Management System</h3>
        <p>Version 2.0.0</p>
        <p>A comprehensive solution for jewelry shop management.</p>
        <p><b>Features:</b></p>
        <ul>
        <li>Invoice generation with automatic stock deduction</li>
        <li>Complete inventory management</li>
        <li>Sales analytics and reporting</li>
        <li>Customer and supplier management</li>
        </ul>
        """
        QMessageBox.about(self, "About", about_text)

    def closeEvent(self, event):
        """Handle application close event."""
        if self.db:
            self.db.close()
        event.accept()
