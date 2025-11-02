"""
Stock Management Tab for Unified Jewelry Management System

This module provides comprehensive inventory management functionality
including product management, categories, suppliers, and stock tracking.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QDateEdit,
    QTextEdit,
    QGroupBox,
    QDialog,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QSpinBox,
    QDoubleSpinBox,
    QTabWidget,
    QCheckBox,
    QProgressBar,
    QSplitter,
    QAbstractItemView,
    QFrame,
    QScrollArea,
    QCompleter,
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer, QThread, QStringListModel
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QBrush
from decimal import Decimal
import csv
from datetime import datetime
from typing import List, Dict, Optional

from logic.database_manager import SupabaseDatabaseManager as UnifiedDatabaseManager
from logic.label_printer import LabelPrinter
from ui.keyboard_navigation import (
    KeyboardNavigationMixin,
    ConfirmationDialog,
    create_shortcut_tooltip,
)


class StockTab(QWidget, KeyboardNavigationMixin):
    """Stock management tab widget."""

    # Signals
    stock_updated = pyqtSignal()
    product_added = pyqtSignal(int, str)  # product_id, product_name

    def __init__(self, db: UnifiedDatabaseManager, settings: dict):
        super().__init__()

        self.db = db
        self.settings = settings

        # Data
        self.products = []
        self.categories = []
        self.suppliers = []

        # Initialize label printer
        self.label_printer = LabelPrinter()

        # Setup UI
        self.init_ui()
        self.setup_keyboard_navigation()
        self.load_data()

    def init_ui(self):
        """Initialize the stock management UI."""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("📦 Stock Management")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #4169E1; margin: 10px;")
        layout.addWidget(header_label)

        # Create tab widget for different sections
        self.tab_widget = QTabWidget()

        # Products tab
        self.create_products_tab()

        # Categories tab
        self.create_categories_tab()

        # Suppliers tab
        self.create_suppliers_tab()

        # Stock movements tab
        self.create_stock_movements_tab()

        # Inventory summary tab
        self.create_inventory_summary_tab()

        layout.addWidget(self.tab_widget)

    def setup_tab_order(self):
        """Setup keyboard navigation order for stock management fields."""
        # Note: Stock tab uses multiple tabs, so setup navigation for each tab separately
        # This is a placeholder implementation for the main fields
        if hasattr(self, "product_category_combo"):
            navigation_sequence = [
                self.product_category_combo,
                self.product_desc_edit,
                self.product_hsn_edit,
                self.product_supplier_combo,
                self.product_gross_weight_spin,
                self.product_net_weight_spin,
            ]

            # Add to navigation
            self.add_navigation_sequence(navigation_sequence)

            # Add action shortcuts for add product button
            if hasattr(self, "add_product_btn"):
                self.add_action_shortcut(
                    self.product_net_weight_spin, self.add_product_with_confirmation
                )
                self.add_product_btn.setToolTip(
                    create_shortcut_tooltip(
                        "Add new product to inventory",
                        "Enter (when net weight field is focused)",
                    )
                )

    def setup_hsn_autocomplete(self):
        """Setup HSN code autocomplete from history."""
        try:
            # Get HSN history from database
            hsn_history = self.db.get_hsn_code_history()
            hsn_codes = [
                item["hsn_code"] for item in hsn_history if item.get("hsn_code")
            ]

            # Create completer
            self.hsn_completer = QCompleter(hsn_codes)
            self.hsn_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.hsn_completer.setCompletionMode(QCompleter.PopupCompletion)

            # Apply to HSN edit field
            self.product_hsn_edit.setCompleter(self.hsn_completer)

        except Exception as e:
            print(f"Warning: Could not setup HSN autocomplete: {e}")

    def create_products_tab(self):
        """Create products management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Top section with add form and summary
        top_splitter = QSplitter()

        # Add product form
        add_group = QGroupBox("Add New Product")
        add_layout = QGridLayout(add_group)

        # Row 0: Category and Description
        add_layout.addWidget(QLabel("Category:"), 0, 0)
        self.product_category_combo = QComboBox()
        add_layout.addWidget(self.product_category_combo, 0, 1)

        add_layout.addWidget(QLabel("Description:"), 0, 2)
        self.product_desc_edit = QLineEdit()
        self.product_desc_edit.setPlaceholderText("Optional description")
        add_layout.addWidget(self.product_desc_edit, 0, 3)

        # Row 1: HSN Code and Supplier
        add_layout.addWidget(QLabel("HSN Code:"), 1, 0)
        self.product_hsn_edit = QLineEdit()
        self.product_hsn_edit.setPlaceholderText("HSN/SAC Code")
        add_layout.addWidget(self.product_hsn_edit, 1, 1)

        add_layout.addWidget(QLabel("Supplier:"), 1, 2)
        self.product_supplier_combo = QComboBox()
        add_layout.addWidget(self.product_supplier_combo, 1, 3)

        # Row 2: Weights
        add_layout.addWidget(QLabel("Gross Weight (g):"), 2, 0)
        self.product_gross_weight_spin = QDoubleSpinBox()
        self.product_gross_weight_spin.setDecimals(3)
        self.product_gross_weight_spin.setRange(0.001, 99999.999)
        add_layout.addWidget(self.product_gross_weight_spin, 2, 1)

        add_layout.addWidget(QLabel("Net Weight (g):"), 2, 2)
        self.product_net_weight_spin = QDoubleSpinBox()
        self.product_net_weight_spin.setDecimals(3)
        self.product_net_weight_spin.setRange(0.001, 99999.999)
        add_layout.addWidget(self.product_net_weight_spin, 2, 3)

        # Row 3: Quantity (hidden) and Melting %
        add_layout.addWidget(QLabel("Quantity:"), 3, 0)
        self.product_quantity_spin = QSpinBox()
        self.product_quantity_spin.setRange(0, 999999)
        self.product_quantity_spin.setValue(1)
        add_layout.addWidget(self.product_quantity_spin, 3, 1)
        # Hide quantity UI (label and spinbox)
        try:
            qty_label_item = add_layout.itemAtPosition(3, 0)
            if qty_label_item and qty_label_item.widget():
                qty_label_item.widget().hide()
        except Exception:
            pass
        self.product_quantity_spin.hide()

        add_layout.addWidget(QLabel("Melting %:"), 3, 2)
        self.product_melting_spin = QDoubleSpinBox()
        self.product_melting_spin.setDecimals(1)
        self.product_melting_spin.setRange(0.0, 100.0)
        add_layout.addWidget(self.product_melting_spin, 3, 3)

        # Add button
        self.add_product_btn = QPushButton("Add Product")
        self.add_product_btn.clicked.connect(self.add_product)
        self.add_product_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4169E1;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
        """
        )
        add_layout.addWidget(self.add_product_btn, 4, 0, 1, 4)

        top_splitter.addWidget(add_group)

        # Summary panel
        summary_group = QGroupBox("Inventory Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.total_products_label = QLabel("Total Products: 0")
        self.total_quantity_label = QLabel("Total Quantity: 0")
        self.low_stock_label = QLabel("Low Stock Items: 0")

        for label in [
            self.total_products_label,
            self.total_quantity_label,
            self.low_stock_label,
        ]:
            label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
            summary_layout.addWidget(label)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_data)
        summary_layout.addWidget(refresh_btn)

        top_splitter.addWidget(summary_group)
        top_splitter.setSizes([700, 300])

        layout.addWidget(top_splitter)

        # Search and filter section
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search products...")
        self.search_edit.textChanged.connect(self.filter_products)
        filter_layout.addWidget(self.search_edit)

        filter_layout.addWidget(QLabel("Category:"))
        self.filter_category_combo = QComboBox()
        self.filter_category_combo.currentTextChanged.connect(self.filter_products)
        filter_layout.addWidget(self.filter_category_combo)

        filter_layout.addWidget(QLabel("Supplier:"))
        self.filter_supplier_combo = QComboBox()
        self.filter_supplier_combo.currentTextChanged.connect(self.filter_products)
        filter_layout.addWidget(self.filter_supplier_combo)

        self.low_stock_check = QCheckBox("Show Low Stock Only")
        self.low_stock_check.toggled.connect(self.filter_products)
        filter_layout.addWidget(self.low_stock_check)

        filter_layout.addStretch()

        # Export button
        export_btn = QPushButton("📊 Export CSV")
        export_btn.clicked.connect(self.export_products)
        filter_layout.addWidget(export_btn)

        layout.addWidget(filter_frame)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(9)
        self.products_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Name",
                "Description",
                "Category",
                "Gross Weight",
                "Net Weight",
                "Status",
                "Supplier",
                "Actions",
            ]
        )

        # Configure table
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Gross Weight
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Net Weight
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Supplier
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Actions

        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setAlternatingRowColors(True)

        layout.addWidget(self.products_table)

        self.tab_widget.addTab(tab, "📦 Products")

    def create_categories_tab(self):
        """Create categories management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add category form
        add_group = QGroupBox("Add New Category")
        add_layout = QGridLayout(add_group)

        add_layout.addWidget(QLabel("Category Name:"), 0, 0)
        self.category_name_edit = QLineEdit()
        self.category_name_edit.setPlaceholderText("Enter category name")
        add_layout.addWidget(self.category_name_edit, 0, 1)

        add_layout.addWidget(QLabel("Description:"), 0, 2)
        self.category_desc_edit = QLineEdit()
        self.category_desc_edit.setPlaceholderText("Optional description")
        add_layout.addWidget(self.category_desc_edit, 0, 3)

        self.add_category_btn = QPushButton("Add Category")
        self.add_category_btn.clicked.connect(self.add_category)
        add_layout.addWidget(self.add_category_btn, 1, 0, 1, 4)

        layout.addWidget(add_group)

        # Categories table
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(4)
        self.categories_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Description", "Actions"]
        )

        header = self.categories_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.categories_table.setAlternatingRowColors(True)
        layout.addWidget(self.categories_table)

        self.tab_widget.addTab(tab, "🏷️ Categories")

    def create_suppliers_tab(self):
        """Create suppliers management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Add supplier form
        add_group = QGroupBox("Add New Supplier")
        add_layout = QGridLayout(add_group)

        # Row 0: Name and Code
        add_layout.addWidget(QLabel("Supplier Name:"), 0, 0)
        self.supplier_name_edit = QLineEdit()
        self.supplier_name_edit.setPlaceholderText("Enter supplier name")
        add_layout.addWidget(self.supplier_name_edit, 0, 1)

        add_layout.addWidget(QLabel("Code:"), 0, 2)
        self.supplier_code_edit = QLineEdit()
        self.supplier_code_edit.setPlaceholderText("Supplier code")
        add_layout.addWidget(self.supplier_code_edit, 0, 3)

        # Row 1: Contact person and phone
        add_layout.addWidget(QLabel("Contact Person:"), 1, 0)
        self.supplier_contact_edit = QLineEdit()
        self.supplier_contact_edit.setPlaceholderText("Contact person name")
        add_layout.addWidget(self.supplier_contact_edit, 1, 1)

        add_layout.addWidget(QLabel("Phone:"), 1, 2)
        self.supplier_phone_edit = QLineEdit()
        self.supplier_phone_edit.setPlaceholderText("Phone number")
        add_layout.addWidget(self.supplier_phone_edit, 1, 3)

        # Row 2: Email and address
        add_layout.addWidget(QLabel("Email:"), 2, 0)
        self.supplier_email_edit = QLineEdit()
        self.supplier_email_edit.setPlaceholderText("Email address")
        add_layout.addWidget(self.supplier_email_edit, 2, 1)

        add_layout.addWidget(QLabel("Address:"), 2, 2)
        self.supplier_address_edit = QLineEdit()
        self.supplier_address_edit.setPlaceholderText("Address")
        add_layout.addWidget(self.supplier_address_edit, 2, 3)

        self.add_supplier_btn = QPushButton("Add Supplier")
        self.add_supplier_btn.clicked.connect(self.add_supplier)
        add_layout.addWidget(self.add_supplier_btn, 3, 0, 1, 4)

        layout.addWidget(add_group)

        # Suppliers table
        self.suppliers_table = QTableWidget()
        self.suppliers_table.setColumnCount(7)
        self.suppliers_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Code", "Contact Person", "Phone", "Email", "Actions"]
        )

        header = self.suppliers_table.horizontalHeader()
        for i in range(6):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.suppliers_table.setAlternatingRowColors(True)
        layout.addWidget(self.suppliers_table)

        self.tab_widget.addTab(tab, "🏢 Suppliers")

    def create_stock_movements_tab(self):
        """Create stock movements tracking tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filter section
        filter_group = QGroupBox("Filter Stock Movements")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("Product:"))
        self.movement_product_combo = QComboBox()
        filter_layout.addWidget(self.movement_product_combo)

        filter_layout.addWidget(QLabel("Movement Type:"))
        self.movement_type_combo = QComboBox()
        self.movement_type_combo.addItems(["All", "IN", "OUT", "ADJUSTMENT"])
        filter_layout.addWidget(self.movement_type_combo)

        filter_btn = QPushButton("Filter")
        filter_btn.clicked.connect(self.load_stock_movements)
        filter_layout.addWidget(filter_btn)

        filter_layout.addStretch()
        layout.addWidget(filter_group)

        # Stock movements table
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(7)
        self.movements_table.setHorizontalHeaderLabels(
            [
                "Date",
                "Product",
                "Type",
                "Quantity",
                "Reference",
                "Reference ID",
                "Notes",
            ]
        )

        header = self.movements_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Product
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Reference
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Reference ID
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # Notes

        self.movements_table.setAlternatingRowColors(True)
        layout.addWidget(self.movements_table)

        self.tab_widget.addTab(tab, "📊 Stock Movements")

    def create_inventory_summary_tab(self):
        """Create inventory summary tab with category-wise and total summaries."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Summary header
        header_group = QGroupBox("📈 Inventory Summary")
        header_layout = QHBoxLayout(header_group)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Summary")
        refresh_btn.clicked.connect(self.load_inventory_summary)
        refresh_btn.setMaximumWidth(200)
        header_layout.addWidget(refresh_btn)

        # Export category-wise button
        export_cat_btn = QPushButton("📊 Export Category-wise CSV")
        export_cat_btn.clicked.connect(self.export_category_wise_csv)
        export_cat_btn.setMaximumWidth(250)
        header_layout.addWidget(export_cat_btn)

        # Export total summary button
        export_summary_btn = QPushButton("📋 Export Total Summary CSV")
        export_summary_btn.clicked.connect(self.export_total_summary_csv)
        export_summary_btn.setMaximumWidth(250)
        header_layout.addWidget(export_summary_btn)

        # Print Labels button
        print_labels_btn = QPushButton("🏷️ Print Labels")
        print_labels_btn.clicked.connect(self.print_labels_dialog)
        print_labels_btn.setMaximumWidth(200)
        print_labels_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2E8B57;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3CB371;
            }
        """
        )
        header_layout.addWidget(print_labels_btn)

        header_layout.addStretch()

        layout.addWidget(header_group)

        # Create splitter for two sections
        splitter = QSplitter()
        # splitter.setOrientation(1)  # Vertical orientation - disabled due to import issue

        # Category-wise summary section
        category_group = QGroupBox("📋 Category-wise Summary")
        category_layout = QVBoxLayout(category_group)

        self.category_summary_table = QTableWidget()
        self.category_summary_table.setColumnCount(5)
        self.category_summary_table.setHorizontalHeaderLabels(
            [
                "Sr. No.",
                "Category",
                "Total Items",
                "Available Items",
                "Total Weight (g)",
            ]
        )

        # Configure category summary table
        cat_header = self.category_summary_table.horizontalHeader()
        if cat_header:
            cat_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Sr. No.
            cat_header.setSectionResizeMode(1, QHeaderView.Stretch)  # Category
            cat_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Items
            cat_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Quantity
            cat_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Weight

        self.category_summary_table.setAlternatingRowColors(True)
        category_layout.addWidget(self.category_summary_table)
        splitter.addWidget(category_group)

        # Total summary section
        total_group = QGroupBox("📊 Overall Summary")
        total_layout = QGridLayout(total_group)

        # Summary labels
        total_layout.addWidget(QLabel("Total Categories:"), 0, 0)
        self.total_categories_label = QLabel("0")
        self.total_categories_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        total_layout.addWidget(self.total_categories_label, 0, 1)

        total_layout.addWidget(QLabel("Total Items:"), 1, 0)
        self.total_products_label = QLabel("0")
        self.total_products_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        total_layout.addWidget(self.total_products_label, 1, 1)

        total_layout.addWidget(QLabel("Available Items:"), 2, 0)
        self.total_available_label = QLabel("0")
        self.total_available_label.setStyleSheet("font-weight: bold; color: #4169E1;")
        total_layout.addWidget(self.total_available_label, 2, 1)

        total_layout.addWidget(QLabel("Total Gross Weight:"), 0, 2)
        self.total_gross_weight_label = QLabel("0.0 g")
        self.total_gross_weight_label.setStyleSheet(
            "font-weight: bold; color: #8B4513;"
        )
        total_layout.addWidget(self.total_gross_weight_label, 0, 3)

        total_layout.addWidget(QLabel("Total Net Weight:"), 1, 2)
        self.total_net_weight_label = QLabel("0.0 g")
        self.total_net_weight_label.setStyleSheet("font-weight: bold; color: #8B4513;")
        total_layout.addWidget(self.total_net_weight_label, 1, 3)

        # Remove total value as we don't track unit prices

        splitter.addWidget(total_group)
        layout.addWidget(splitter)

        self.tab_widget.addTab(tab, "📈 Summary")

    def load_data(self):
        """Load all data for the stock management."""
        try:
            # Load categories
            self.categories = self.db.get_categories()
            category_items = ["Select Category"] + [
                cat["name"] for cat in self.categories
            ]

            self.product_category_combo.clear()
            self.product_category_combo.addItems(category_items)

            self.filter_category_combo.clear()
            self.filter_category_combo.addItems(
                ["All Categories"] + [cat["name"] for cat in self.categories]
            )

            # Load suppliers
            self.suppliers = self.db.get_suppliers()
            supplier_items = ["Select Supplier"] + [
                f"{sup['name']} ({sup['code']})" for sup in self.suppliers
            ]

            self.product_supplier_combo.clear()
            self.product_supplier_combo.addItems(supplier_items)

            self.filter_supplier_combo.clear()
            self.filter_supplier_combo.addItems(
                ["All Suppliers"]
                + [f"{sup['name']} ({sup['code']})" for sup in self.suppliers]
            )

            # Setup HSN autocomplete
            self.setup_hsn_autocomplete()

            # Load products
            self.load_products()

            # Load categories table
            self.load_categories_table()

            # Load suppliers table
            self.load_suppliers_table()

            # Load stock movements
            self.load_stock_movements()

            # Load inventory summary
            self.load_inventory_summary()

            # Update summary
            self.update_summary()

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading data: {str(e)}")

    def load_products(self):
        """Load products into the table."""
        try:
            self.products = self.db.get_products()
            self.populate_products_table(self.products)

            # Update movement product combo
            product_items = ["All Products"] + [p["name"] for p in self.products]
            self.movement_product_combo.clear()
            self.movement_product_combo.addItems(product_items)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading products: {str(e)}")

    def populate_products_table(self, products):
        """Populate products table with given products list."""
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            # Show category_item_id if available, otherwise global ID
            cat_item_id = product.get("category_item_id")
            if cat_item_id:
                id_display = f"{product['category_name']} #{cat_item_id}"
            else:
                id_display = str(product["id"])[:8] + "..."
            self.products_table.setItem(row, 0, QTableWidgetItem(id_display))
            self.products_table.setItem(row, 1, QTableWidgetItem(product["name"]))
            self.products_table.setItem(
                row, 2, QTableWidgetItem(product.get("description", ""))
            )
            self.products_table.setItem(
                row, 3, QTableWidgetItem(product.get("category_name", ""))
            )
            self.products_table.setItem(
                row, 4, QTableWidgetItem(f"{product['gross_weight']:.3f}")
            )
            self.products_table.setItem(
                row, 5, QTableWidgetItem(f"{product['net_weight']:.3f}")
            )

            # Status instead of quantity
            status = product.get("status", "AVAILABLE")
            status_item = QTableWidgetItem(status)
            if status == "SOLD":
                status_item.setBackground(Qt.lightGray)
            elif status == "RESERVED":
                status_item.setBackground(Qt.yellow)
            self.products_table.setItem(row, 6, status_item)

            self.products_table.setItem(
                row, 7, QTableWidgetItem(product.get("supplier_name", ""))
            )

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 4, 4, 4)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(
                lambda checked, p_id=product["id"]: self.edit_product(p_id)
            )
            action_layout.addWidget(edit_btn)

            # Only show delete button for available items
            if status == "AVAILABLE":
                delete_btn = QPushButton("Delete")
                delete_btn.clicked.connect(
                    lambda checked, p_id=product["id"]: self.delete_product(p_id)
                )
                action_layout.addWidget(delete_btn)

            self.products_table.setCellWidget(row, 8, action_widget)

    def load_categories_table(self):
        """Load categories into the table."""
        try:
            self.categories_table.setRowCount(len(self.categories))

            for row, category in enumerate(self.categories):
                self.categories_table.setItem(
                    row, 0, QTableWidgetItem(str(category["id"]))
                )
                self.categories_table.setItem(
                    row, 1, QTableWidgetItem(category["name"])
                )
                self.categories_table.setItem(
                    row, 2, QTableWidgetItem(category.get("description", ""))
                )

                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(4, 4, 4, 4)

                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(
                    lambda checked, c_id=category["id"]: self.edit_category(c_id)
                )
                action_layout.addWidget(edit_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.clicked.connect(
                    lambda checked, c_id=category["id"]: self.delete_category(c_id)
                )
                action_layout.addWidget(delete_btn)

                self.categories_table.setCellWidget(row, 3, action_widget)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading categories: {str(e)}")

    def load_suppliers_table(self):
        """Load suppliers into the table."""
        try:
            self.suppliers_table.setRowCount(len(self.suppliers))

            for row, supplier in enumerate(self.suppliers):
                self.suppliers_table.setItem(
                    row, 0, QTableWidgetItem(str(supplier["id"]))
                )
                self.suppliers_table.setItem(row, 1, QTableWidgetItem(supplier["name"]))
                self.suppliers_table.setItem(row, 2, QTableWidgetItem(supplier["code"]))
                self.suppliers_table.setItem(
                    row, 3, QTableWidgetItem(supplier.get("contact_person", ""))
                )
                self.suppliers_table.setItem(
                    row, 4, QTableWidgetItem(supplier.get("phone", ""))
                )
                self.suppliers_table.setItem(
                    row, 5, QTableWidgetItem(supplier.get("email", ""))
                )

                # Action buttons
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(4, 4, 4, 4)

                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(
                    lambda checked, s_id=supplier["id"]: self.edit_supplier(s_id)
                )
                action_layout.addWidget(edit_btn)

                delete_btn = QPushButton("Delete")
                delete_btn.clicked.connect(
                    lambda checked, s_id=supplier["id"]: self.delete_supplier(s_id)
                )
                action_layout.addWidget(delete_btn)

                self.suppliers_table.setCellWidget(row, 6, action_widget)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading suppliers: {str(e)}")

    def load_inventory_summary(self):
        """Load inventory summary data with category-wise and total summaries."""
        try:
            # Get category summary data using new view
            category_summary = self.db.get_category_summary()

            # Update category summary table
            self.category_summary_table.setRowCount(len(category_summary))

            total_available_items = 0
            total_sold_items = 0
            total_gross_weight = 0.0
            total_net_weight = 0.0

            for row, summary in enumerate(category_summary):
                # Sr. No.
                self.category_summary_table.setItem(
                    row, 0, QTableWidgetItem(str(row + 1))
                )

                # Category Name
                self.category_summary_table.setItem(
                    row, 1, QTableWidgetItem(summary["category_name"])
                )

                # Total Items
                self.category_summary_table.setItem(
                    row, 2, QTableWidgetItem(str(summary["total_items"]))
                )

                # Available Items
                self.category_summary_table.setItem(
                    row, 3, QTableWidgetItem(str(summary["available_items"]))
                )

                # Total Weight (Net Weight)
                self.category_summary_table.setItem(
                    row, 4, QTableWidgetItem(f"{summary['available_net_weight']:.3f}")
                )

                # Add to totals
                total_available_items += summary["available_items"]
                total_sold_items += summary["sold_items"]
                total_gross_weight += float(summary["available_gross_weight"])
                total_net_weight += float(summary["available_net_weight"])

            # Get total summary
            total_summary = self.db.get_total_summary()

            # Update total summary labels
            self.total_categories_label.setText(str(len(category_summary)))
            self.total_products_label.setText(
                str(
                    total_summary.get("total_available_items", 0)
                    + total_summary.get("total_sold_items", 0)
                )
            )
            self.total_available_label.setText(
                str(total_summary.get("total_available_items", 0))
            )
            self.total_gross_weight_label.setText(
                f"{total_summary.get('total_available_gross_weight', 0):.3f} g"
            )
            self.total_net_weight_label.setText(
                f"{total_summary.get('total_available_net_weight', 0):.3f} g"
            )

        except Exception as e:
            QMessageBox.warning(
                self, "Warning", f"Error loading inventory summary: {str(e)}"
            )

    def load_stock_movements(self):
        """Load stock movements."""
        try:
            # Get filter values
            selected_product = self.movement_product_combo.currentText()
            selected_type = self.movement_type_combo.currentText()

            product_id = None
            if selected_product != "All Products":
                # Find product ID
                for product in self.products:
                    if product["name"] == selected_product:
                        product_id = product["id"]
                        break

            # Get movements from database
            movements = self.db.get_stock_movements(product_id, limit=200)

            # Filter by type
            if selected_type != "All":
                movements = [
                    m for m in movements if m["movement_type"] == selected_type
                ]

            self.movements_table.setRowCount(len(movements))

            for row, movement in enumerate(movements):
                # Format date
                created_at = movement["created_at"]
                if isinstance(created_at, str):
                    date_str = created_at.split()[0]  # Get date part
                else:
                    date_str = str(created_at)

                self.movements_table.setItem(row, 0, QTableWidgetItem(date_str))

                # Show product name with category_item_id if available
                product_name = movement.get("product_name", "Deleted Product")
                cat_item_id = movement.get("category_item_id")
                category_name = movement.get("category_name")
                if cat_item_id and category_name:
                    product_display = f"{category_name} #{cat_item_id}"
                    if product_name and product_name != "Deleted Product":
                        product_display += f" ({product_name})"
                else:
                    product_display = product_name

                self.movements_table.setItem(row, 1, QTableWidgetItem(product_display))
                self.movements_table.setItem(
                    row, 2, QTableWidgetItem(movement["movement_type"])
                )
                self.movements_table.setItem(
                    row, 3, QTableWidgetItem(f"{movement['quantity']:.3f}")
                )
                self.movements_table.setItem(
                    row, 4, QTableWidgetItem(movement.get("reference_type", ""))
                )
                self.movements_table.setItem(
                    row, 5, QTableWidgetItem(str(movement.get("reference_id", "")))
                )
                self.movements_table.setItem(
                    row, 6, QTableWidgetItem(movement.get("notes", ""))
                )

        except Exception as e:
            QMessageBox.warning(
                self, "Warning", f"Error loading stock movements: {str(e)}"
            )

    def update_summary(self):
        """Update inventory summary."""
        try:
            total_products = len(self.products)
            total_available = len(
                [p for p in self.products if p["status"] == "AVAILABLE"]
            )
            low_stock_count = (
                0  # In serialized inventory, low stock is when category has < 5 items
            )

            self.total_products_label.setText(f"Total Products: {total_products}")
            self.total_available_label.setText(f"Available Items: {total_available}")
            self.low_stock_label.setText(f"Low Stock Items: {low_stock_count}")

            # Set color for low stock warning
            if low_stock_count > 0:
                self.low_stock_label.setStyleSheet(
                    "color: red; font-weight: bold; font-size: 14px; margin: 5px;"
                )
            else:
                self.low_stock_label.setStyleSheet(
                    "color: green; font-weight: bold; font-size: 14px; margin: 5px;"
                )

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error updating summary: {str(e)}")

    def filter_products(self):
        """Filter products based on search criteria."""
        try:
            search_text = self.search_edit.text().lower()
            selected_category = self.filter_category_combo.currentText()
            selected_supplier = self.filter_supplier_combo.currentText()
            show_low_stock = self.low_stock_check.isChecked()

            filtered_products = []

            for product in self.products:
                # Text search
                if search_text and search_text not in product["name"].lower():
                    if (
                        not product.get("description")
                        or search_text not in product["description"].lower()
                    ):
                        continue

                # Category filter
                if selected_category != "All Categories":
                    if product.get("category_name") != selected_category:
                        continue

                # Supplier filter
                if selected_supplier != "All Suppliers":
                    supplier_text = f"{product.get('supplier_name', '')} ({product.get('supplier_code', '')})"
                    if supplier_text != selected_supplier:
                        continue

                # Low stock filter
                if show_low_stock and product["quantity"] > 5:
                    continue

                filtered_products.append(product)

            self.populate_products_table(filtered_products)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error filtering products: {str(e)}")

    def add_product(self):
        """Add a new product."""
        try:
            # Validate inputs
            selected_category = self.product_category_combo.currentText()
            if not selected_category or selected_category == "Select Category":
                QMessageBox.warning(self, "Warning", "Please select a category.")
                return

            # Category name is used as the product name
            name = selected_category

            gross_weight = self.product_gross_weight_spin.value()
            net_weight = self.product_net_weight_spin.value()

            if gross_weight <= 0 or net_weight <= 0:
                QMessageBox.warning(
                    self, "Warning", "Weights must be greater than zero."
                )
                return

            if gross_weight < net_weight:
                QMessageBox.warning(
                    self, "Warning", "Gross weight cannot be less than net weight."
                )
                return

            # Get category ID
            category_id = None
            for cat in self.categories:
                if cat["name"] == selected_category:
                    category_id = cat["id"]
                    break

            # Get supplier ID
            supplier_id = None
            selected_supplier = self.product_supplier_combo.currentText()
            if selected_supplier != "Select Supplier":
                supplier_name = selected_supplier.split(" (")[0]
                for sup in self.suppliers:
                    if sup["name"] == supplier_name:
                        supplier_id = sup["id"]
                        break

            # Add product to database (name parameter is ignored, category is used)
            product_id = self.db.add_product(
                name=name,  # This will be ignored by the database manager
                description=self.product_desc_edit.text().strip() or None,
                hsn_code=self.product_hsn_edit.text().strip() or None,
                gross_weight=gross_weight,
                net_weight=net_weight,
                quantity=1,  # Always 1 for serialized inventory
                supplier_id=supplier_id,
                category_id=category_id,
                melting_percentage=self.product_melting_spin.value(),
            )

            QMessageBox.information(
                self, "Success", f"Product added to category '{name}' successfully!"
            )

            # Clear form
            self.clear_product_form()

            # Reload data
            self.load_products()
            self.load_inventory_summary()  # Refresh inventory summary
            self.update_summary()
            self.setup_hsn_autocomplete()  # Refresh HSN autocomplete

            # Emit signal
            self.product_added.emit(product_id, name)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding product: {str(e)}")

    def clear_product_form(self):
        """Clear the product form."""
        self.product_desc_edit.clear()
        self.product_hsn_edit.clear()
        self.product_category_combo.setCurrentIndex(0)
        self.product_gross_weight_spin.setValue(0.0)
        self.product_net_weight_spin.setValue(0.0)
        self.product_quantity_spin.setValue(1)
        self.product_supplier_combo.setCurrentIndex(0)
        self.product_melting_spin.setValue(0.0)

    def add_product_with_confirmation(self):
        """Add product with confirmation dialog."""
        # Get values for confirmation
        selected_category = self.product_category_combo.currentText()
        gross_weight = self.product_gross_weight_spin.value()
        net_weight = self.product_net_weight_spin.value()

        if not selected_category or selected_category == "Select Category":
            QMessageBox.warning(self, "Warning", "Please select a category first.")
            self.product_category_combo.setFocus()
            return

        message = (
            f"Add new product to inventory?\n\n"
            f"Category/Name: {selected_category}\n"
            f"Gross Weight: {gross_weight}g\n"
            f"Net Weight: {net_weight}g"
        )

        if ConfirmationDialog.confirm_action(self, "Add Product", message):
            self.add_product()

    def edit_product(self, product_id):
        """Edit a product."""
        try:
            # Get current product data
            product = None
            for p in self.products:
                if p["id"] == product_id:
                    product = p
                    break

            if not product:
                QMessageBox.warning(self, "Error", "Product not found!")
                return

            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Product")
            dialog.setModal(True)
            dialog.resize(400, 500)

            layout = QFormLayout(dialog)

            # Form fields
            name_edit = QLineEdit(product["name"])
            desc_edit = QLineEdit(product.get("description", ""))
            hsn_edit = QLineEdit(product.get("hsn_code", ""))

            gross_weight_spin = QDoubleSpinBox()
            gross_weight_spin.setDecimals(3)
            gross_weight_spin.setRange(0.0, 9999.999)
            gross_weight_spin.setValue(product["gross_weight"])

            net_weight_spin = QDoubleSpinBox()
            net_weight_spin.setDecimals(3)
            net_weight_spin.setRange(0.0, 9999.999)
            net_weight_spin.setValue(product["net_weight"])

            quantity_spin = QSpinBox()
            quantity_spin.setRange(0, 99999)
            quantity_spin.setValue(product["quantity"])

            category_combo = QComboBox()
            category_combo.addItem("", None)
            for cat in self.categories:
                category_combo.addItem(cat["name"], cat["id"])
                if cat["id"] == product.get("category_id"):
                    category_combo.setCurrentIndex(category_combo.count() - 1)

            supplier_combo = QComboBox()
            supplier_combo.addItem("", None)
            for sup in self.suppliers:
                supplier_combo.addItem(sup["name"], sup["id"])
                if sup["id"] == product.get("supplier_id"):
                    supplier_combo.setCurrentIndex(supplier_combo.count() - 1)

            melting_spin = QDoubleSpinBox()
            melting_spin.setDecimals(1)
            melting_spin.setRange(0.0, 100.0)
            melting_spin.setValue(product.get("melting_percentage", 0.0))

            # Add fields to layout
            layout.addRow("Name:", name_edit)
            layout.addRow("Description:", desc_edit)
            layout.addRow("HSN Code:", hsn_edit)
            layout.addRow("Gross Weight:", gross_weight_spin)
            layout.addRow("Net Weight:", net_weight_spin)
            layout.addRow("Quantity:", quantity_spin)
            layout.addRow("Category:", category_combo)
            layout.addRow("Supplier:", supplier_combo)
            layout.addRow("Melting %:", melting_spin)

            # Buttons
            button_box = QHBoxLayout()
            save_btn = QPushButton("Save")
            cancel_btn = QPushButton("Cancel")
            button_box.addWidget(save_btn)
            button_box.addWidget(cancel_btn)
            layout.addRow(button_box)

            # Connect buttons
            save_btn.clicked.connect(dialog.accept)
            cancel_btn.clicked.connect(dialog.reject)

            # Show dialog
            if dialog.exec_() == QDialog.Accepted:
                # Update product
                success = self.db.update_product(
                    product_id=product_id,
                    name=name_edit.text().strip(),
                    description=desc_edit.text().strip() or None,
                    hsn_code=hsn_edit.text().strip() or None,
                    gross_weight=gross_weight_spin.value(),
                    net_weight=net_weight_spin.value(),
                    quantity=quantity_spin.value(),
                    category_id=category_combo.currentData(),
                    supplier_id=supplier_combo.currentData(),
                    melting_percentage=melting_spin.value(),
                )

                if success:
                    QMessageBox.information(
                        self, "Success", "Product updated successfully!"
                    )
                    self.load_products()
                    self.load_inventory_summary()  # Refresh inventory summary
                    self.update_summary()
                    self.stock_updated.emit()  # Notify other tabs
                else:
                    QMessageBox.warning(self, "Error", "Failed to update product!")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error editing product: {str(e)}")

    def delete_product(self, product_id):
        """Delete a product."""
        try:
            # Get product name for confirmation
            product = None
            for p in self.products:
                if p["id"] == product_id:
                    product = p
                    break

            if not product:
                QMessageBox.warning(self, "Error", "Product not found!")
                return

            reply = QMessageBox.question(
                self,
                "Delete Product",
                f"Are you sure you want to delete '{product['name']}'?\n\n"
                f"This will remove:\n"
                f"• The product from inventory\n"
                f"• All related stock movement history\n"
                f"• Product ID {product_id} will be available for reuse\n\n"
                f"This action cannot be undone!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                success = self.db.delete_product(product_id)

                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Product '{product['name']}' deleted successfully!\n"
                        f"Product ID {product_id} is now available for reuse.",
                    )
                    self.load_products()
                    self.load_inventory_summary()  # Refresh inventory summary
                    self.update_summary()
                    self.stock_updated.emit()  # Notify other tabs
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete product!")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error deleting product: {str(e)}")

    def add_category(self):
        """Add a new category."""
        try:
            name = self.category_name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "Warning", "Please enter category name.")
                return

            description = self.category_desc_edit.text().strip() or None

            category_id = self.db.add_category(name, description)

            QMessageBox.information(
                self, "Success", f"Category '{name}' added successfully!"
            )

            # Clear form
            self.category_name_edit.clear()
            self.category_desc_edit.clear()

            # Reload data
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding category: {str(e)}")

    def delete_category(self, category_id):
        """Delete a category."""
        try:
            # Get category details for better user message
            category = next(
                (cat for cat in self.categories if cat["id"] == category_id), None
            )
            if not category:
                QMessageBox.warning(self, "Warning", "Category not found.")
                return

            reply = QMessageBox.question(
                self,
                "Delete Category",
                f"Are you sure you want to delete the category '{category['name']}'?\n\n"
                f"Note: You cannot delete a category that is being used by products.",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                success = self.db.delete_category(category_id)
                if success:
                    QMessageBox.information(
                        self, "Success", "Category deleted successfully!"
                    )
                    self.load_data()  # Refresh all data
                else:
                    QMessageBox.warning(
                        self, "Warning", "Category could not be deleted."
                    )

        except ValueError as ve:
            QMessageBox.warning(self, "Cannot Delete", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error deleting category: {str(e)}")

    def edit_category(self, category_id):
        """Edit a category."""
        try:
            # Find the category
            category = next(
                (cat for cat in self.categories if cat["id"] == category_id), None
            )
            if not category:
                QMessageBox.warning(self, "Warning", "Category not found.")
                return

            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Category")
            dialog.setModal(True)
            dialog.resize(400, 200)

            layout = QFormLayout(dialog)

            # Form fields
            name_edit = QLineEdit(category["name"])
            layout.addRow("Category Name:", name_edit)

            desc_edit = QLineEdit(category.get("description", ""))
            layout.addRow("Description:", desc_edit)

            # Buttons
            button_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            cancel_btn = QPushButton("Cancel")
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addRow(button_layout)

            # Connect buttons
            cancel_btn.clicked.connect(dialog.reject)

            def save_changes():
                name = name_edit.text().strip()
                description = desc_edit.text().strip()

                if not name:
                    QMessageBox.warning(
                        dialog, "Warning", "Please enter a category name."
                    )
                    return

                try:
                    success = self.db.update_category(
                        category_id, name, description or None
                    )
                    if success:
                        QMessageBox.information(
                            dialog, "Success", "Category updated successfully!"
                        )
                        dialog.accept()
                        self.load_data()  # Refresh all data
                    else:
                        QMessageBox.warning(
                            dialog, "Warning", "Category could not be updated."
                        )
                except Exception as e:
                    QMessageBox.critical(
                        dialog, "Error", f"Error updating category: {str(e)}"
                    )

            save_btn.clicked.connect(save_changes)

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error editing category: {str(e)}")

    def add_supplier(self):
        """Add a new supplier."""
        try:
            name = self.supplier_name_edit.text().strip()
            code = self.supplier_code_edit.text().strip()

            if not name or not code:
                QMessageBox.warning(
                    self, "Warning", "Please enter supplier name and code."
                )
                return

            supplier_id = self.db.add_supplier(
                name=name,
                code=code,
                contact_person=self.supplier_contact_edit.text().strip() or None,
                phone=self.supplier_phone_edit.text().strip() or None,
                email=self.supplier_email_edit.text().strip() or None,
                address=self.supplier_address_edit.text().strip() or None,
            )

            QMessageBox.information(
                self, "Success", f"Supplier '{name}' added successfully!"
            )

            # Clear form
            self.supplier_name_edit.clear()
            self.supplier_code_edit.clear()
            self.supplier_contact_edit.clear()
            self.supplier_phone_edit.clear()
            self.supplier_email_edit.clear()
            self.supplier_address_edit.clear()

            # Reload data
            self.load_data()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding supplier: {str(e)}")

    def delete_supplier(self, supplier_id):
        """Delete a supplier."""
        try:
            # Get supplier details for better user message
            supplier = next(
                (sup for sup in self.suppliers if sup["id"] == supplier_id), None
            )
            if not supplier:
                QMessageBox.warning(self, "Warning", "Supplier not found.")
                return

            reply = QMessageBox.question(
                self,
                "Delete Supplier",
                f"Are you sure you want to delete the supplier '{supplier['name']}'?\n\n"
                f"Note: You cannot delete a supplier that is being used by products.",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                success = self.db.delete_supplier(supplier_id)
                if success:
                    QMessageBox.information(
                        self, "Success", "Supplier deleted successfully!"
                    )
                    self.load_data()  # Refresh all data
                else:
                    QMessageBox.warning(
                        self, "Warning", "Supplier could not be deleted."
                    )

        except ValueError as ve:
            QMessageBox.warning(self, "Cannot Delete", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error deleting supplier: {str(e)}")

    def edit_supplier(self, supplier_id):
        """Edit a supplier."""
        try:
            # Find the supplier
            supplier = next(
                (sup for sup in self.suppliers if sup["id"] == supplier_id), None
            )
            if not supplier:
                QMessageBox.warning(self, "Warning", "Supplier not found.")
                return

            # Create edit dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Supplier")
            dialog.setModal(True)
            dialog.resize(500, 300)

            layout = QFormLayout(dialog)

            # Form fields
            name_edit = QLineEdit(supplier["name"])
            layout.addRow("Supplier Name:", name_edit)

            code_edit = QLineEdit(supplier["code"])
            layout.addRow("Code:", code_edit)

            contact_edit = QLineEdit(supplier.get("contact_person", ""))
            layout.addRow("Contact Person:", contact_edit)

            phone_edit = QLineEdit(supplier.get("phone", ""))
            layout.addRow("Phone:", phone_edit)

            email_edit = QLineEdit(supplier.get("email", ""))
            layout.addRow("Email:", email_edit)

            address_edit = QLineEdit(supplier.get("address", ""))
            layout.addRow("Address:", address_edit)

            # Buttons
            button_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            cancel_btn = QPushButton("Cancel")
            button_layout.addWidget(save_btn)
            button_layout.addWidget(cancel_btn)
            layout.addRow(button_layout)

            # Connect buttons
            cancel_btn.clicked.connect(dialog.reject)

            def save_changes():
                name = name_edit.text().strip()
                code = code_edit.text().strip()
                contact_person = contact_edit.text().strip()
                phone = phone_edit.text().strip()
                email = email_edit.text().strip()
                address = address_edit.text().strip()

                if not name or not code:
                    QMessageBox.warning(
                        dialog, "Warning", "Please enter supplier name and code."
                    )
                    return

                try:
                    success = self.db.update_supplier(
                        supplier_id,
                        name,
                        code,
                        contact_person or None,
                        phone or None,
                        email or None,
                        address or None,
                    )
                    if success:
                        QMessageBox.information(
                            dialog, "Success", "Supplier updated successfully!"
                        )
                        dialog.accept()
                        self.load_data()  # Refresh all data
                    else:
                        QMessageBox.warning(
                            dialog, "Warning", "Supplier could not be updated."
                        )
                except Exception as e:
                    QMessageBox.critical(
                        dialog, "Error", f"Error updating supplier: {str(e)}"
                    )

            save_btn.clicked.connect(save_changes)

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error editing supplier: {str(e)}")

    def export_products(self):
        """Export products to CSV."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Products",
                f"products_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)",
            )

            if filename:
                with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)

                    # Write header
                    writer.writerow(
                        [
                            "ID",
                            "Name",
                            "Description",
                            "Category",
                            "HSN Code",
                            "Gross Weight",
                            "Net Weight",
                            "Quantity",
                            "Supplier",
                            "Melting %",
                        ]
                    )

                    # Write data
                    for product in self.products:
                        writer.writerow(
                            [
                                product["id"],
                                product["name"],
                                product.get("description", ""),
                                product.get("category_name", ""),
                                product.get("hsn_code", ""),
                                product["gross_weight"],
                                product["net_weight"],
                                product["quantity"],
                                product.get("supplier_name", ""),
                                product.get("melting_percentage", 0),
                            ]
                        )

                QMessageBox.information(
                    self, "Success", f"Products exported to {filename}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting products: {str(e)}")

    def export_category_wise_csv(self):
        """Export category-wise inventory to CSV."""
        try:
            # Create dialog to select category
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Category to Export")
            dialog.setModal(True)
            dialog.resize(400, 150)

            layout = QVBoxLayout(dialog)

            layout.addWidget(QLabel("Select category to export:"))
            category_combo = QComboBox()
            category_combo.addItems([cat["name"] for cat in self.categories])
            layout.addWidget(category_combo)

            button_layout = QHBoxLayout()
            export_btn = QPushButton("Export")
            cancel_btn = QPushButton("Cancel")
            button_layout.addWidget(export_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)

            cancel_btn.clicked.connect(dialog.reject)

            def do_export():
                selected_category = category_combo.currentText()
                # Find category ID
                category_id = None
                for cat in self.categories:
                    if cat["name"] == selected_category:
                        category_id = cat["id"]
                        break

                if not category_id:
                    QMessageBox.warning(
                        dialog, "Error", "Please select a valid category"
                    )
                    return

                # Get filename
                filename, _ = QFileDialog.getSaveFileName(
                    dialog,
                    "Export Category-wise CSV",
                    f"category_{selected_category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "CSV Files (*.csv)",
                )

                if filename:
                    success = self.db.export_category_wise_csv(category_id, filename)
                    if success:
                        QMessageBox.information(
                            dialog, "Success", f"Category data exported to {filename}"
                        )
                        dialog.accept()
                    else:
                        QMessageBox.warning(
                            dialog, "Error", "Failed to export category data"
                        )

            export_btn.clicked.connect(do_export)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error exporting category CSV: {str(e)}"
            )

    def export_total_summary_csv(self):
        """Export total summary to CSV."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Total Summary CSV",
                f"inventory_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)",
            )

            if filename:
                success = self.db.export_total_summary_csv(filename)
                if success:
                    QMessageBox.information(
                        self, "Success", f"Inventory summary exported to {filename}"
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "Failed to export inventory summary"
                    )

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Error exporting summary CSV: {str(e)}"
            )

    def print_labels_dialog(self):
        """Show dialog to select label printing options."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Print Item Labels")
            dialog.setModal(True)
            dialog.resize(550, 400)

            layout = QVBoxLayout(dialog)

            # Title
            title_label = QLabel("🏷️ Print Labels for Inventory Items")
            title_label.setStyleSheet(
                "font-size: 14px; font-weight: bold; margin: 10px;"
            )
            layout.addWidget(title_label)

            # Options group
            options_group = QGroupBox("Select Items to Print Labels")
            options_layout = QVBoxLayout(options_group)

            # Radio buttons for selection
            self.print_all_radio = QCheckBox("Print labels for ALL available items")
            options_layout.addWidget(self.print_all_radio)

            # Category selection
            category_layout = QHBoxLayout()
            self.print_category_radio = QCheckBox("Print labels for specific category:")
            category_layout.addWidget(self.print_category_radio)

            self.print_category_combo = QComboBox()
            self.print_category_combo.addItems([cat["name"] for cat in self.categories])
            self.print_category_combo.setEnabled(False)
            category_layout.addWidget(self.print_category_combo)
            options_layout.addLayout(category_layout)

            # Single item selection
            item_layout = QHBoxLayout()
            self.print_item_radio = QCheckBox("Print label for specific item:")
            item_layout.addWidget(self.print_item_radio)

            self.print_item_combo = QComboBox()
            self.print_item_combo.setEnabled(False)
            # Populate with available items
            available_items = [
                p for p in self.products if p.get("status") == "AVAILABLE"
            ]
            for item in available_items:
                cat_item_id = item.get("category_item_id")
                if cat_item_id:
                    display_name = f"{item['category_name']} #{cat_item_id} - {item['net_weight']:.3f}g"
                else:
                    display_name = f"{item['name']} - {item['net_weight']:.3f}g"
                self.print_item_combo.addItem(display_name, item["id"])
            item_layout.addWidget(self.print_item_combo)
            options_layout.addLayout(item_layout)

            # Enable/disable combos based on radio selection
            self.print_category_radio.toggled.connect(
                lambda checked: self.print_category_combo.setEnabled(checked)
            )
            self.print_item_radio.toggled.connect(
                lambda checked: self.print_item_combo.setEnabled(checked)
            )

            layout.addWidget(options_group)

            # Info label
            info_label = QLabel(
                "📌 Labels will include: Serial Number, Net Weight, and Supplier Code\n"
                "📄 Tag size: 55mm x 30mm with tie hole for attaching to items"
            )
            info_label.setStyleSheet("color: #666; margin: 10px; font-size: 11px;")
            layout.addWidget(info_label)

            # Buttons
            button_layout = QHBoxLayout()

            print_btn = QPushButton("🖨️ Generate Labels PDF")
            print_btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #2E8B57;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3CB371;
                }
            """
            )
            print_btn.clicked.connect(lambda: self.generate_labels(dialog))
            button_layout.addWidget(print_btn)

            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(dialog.reject)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)

            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening label dialog: {str(e)}")

    def generate_labels(self, dialog: QDialog):
        """Generate label PDF based on selected options."""
        try:
            # Determine what to print
            if self.print_all_radio.isChecked():
                # Print all items
                output_file = self.label_printer.generate_labels_for_all_inventory(
                    self.db,
                    filename=f"all_labels_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                )
                message = "Labels generated for all inventory items!"

            elif self.print_category_radio.isChecked():
                # Print category items
                selected_category = self.print_category_combo.currentText()

                # Find category ID
                category_id = None
                for cat in self.categories:
                    if cat["name"] == selected_category:
                        category_id = cat["id"]
                        break

                if not category_id:
                    QMessageBox.warning(
                        dialog, "Error", "Please select a valid category"
                    )
                    return

                output_file = self.label_printer.generate_labels_for_category(
                    self.db,
                    category_id,
                    filename=f"labels_{selected_category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                )
                message = f"Labels generated for category '{selected_category}'!"

            elif self.print_item_radio.isChecked():
                # Print single item
                item_id = self.print_item_combo.currentData()
                item_name = self.print_item_combo.currentText()

                if not item_id:
                    QMessageBox.warning(dialog, "Error", "Please select a valid item")
                    return

                output_file = self.label_printer.generate_label_for_item(
                    self.db,
                    item_id,
                    filename=f"label_item_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                )
                message = f"Label generated for item: {item_name}!"

            else:
                QMessageBox.warning(dialog, "Warning", "Please select an option")
                return

            # Show success message with option to open file
            result = QMessageBox.information(
                dialog,
                "Success",
                f"{message}\n\nFile saved to: {output_file}\n\nWould you like to open the PDF?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if result == QMessageBox.Yes:
                # Open the PDF file
                import os
                import subprocess

                if os.name == "nt":  # Windows
                    os.startfile(output_file)
                elif os.name == "posix":  # macOS and Linux
                    subprocess.call(
                        [
                            "open" if os.uname().sysname == "Darwin" else "xdg-open",
                            output_file,
                        ]
                    )

            dialog.accept()

        except ValueError as ve:
            QMessageBox.warning(dialog, "Warning", str(ve))
        except Exception as e:
            QMessageBox.critical(dialog, "Error", f"Error generating labels: {str(e)}")
