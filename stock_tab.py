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
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer, QThread
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QBrush
from decimal import Decimal
import csv
from datetime import datetime
from typing import List, Dict, Optional

from unified_database import UnifiedDatabaseManager


class StockTab(QWidget):
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

        # Setup UI
        self.init_ui()
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

        layout.addWidget(self.tab_widget)

    def on_category_name_sync(self, text: str):
        """Keep the product name in sync with selected category."""
        if text and text != "Select Category":
            self.product_name_edit.setText(text)
        else:
            self.product_name_edit.clear()

    def create_products_tab(self):
        """Create products management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Top section with add form and summary
        top_splitter = QSplitter()

        # Add product form
        add_group = QGroupBox("Add New Product")
        add_layout = QGridLayout(add_group)

        # Row 0: Product name and description
        add_layout.addWidget(QLabel("Category (Name):"), 0, 0)
        self.product_name_edit = QLineEdit()
        self.product_name_edit.setPlaceholderText("Auto-filled from Category")
        self.product_name_edit.setReadOnly(True)
        add_layout.addWidget(self.product_name_edit, 0, 1)

        add_layout.addWidget(QLabel("Description:"), 0, 2)
        self.product_desc_edit = QLineEdit()
        self.product_desc_edit.setPlaceholderText("Optional description")
        add_layout.addWidget(self.product_desc_edit, 0, 3)

        # Row 1: HSN Code and Category
        add_layout.addWidget(QLabel("HSN Code:"), 1, 0)
        self.product_hsn_edit = QLineEdit()
        self.product_hsn_edit.setPlaceholderText("HSN/SAC Code")
        add_layout.addWidget(self.product_hsn_edit, 1, 1)

        add_layout.addWidget(QLabel("Category:"), 1, 2)
        self.product_category_combo = QComboBox()
        add_layout.addWidget(self.product_category_combo, 1, 3)
        # Sync product name from category selection
        self.product_category_combo.currentTextChanged.connect(
            self.on_category_name_sync
        )

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

        # Row 3: Quantity, Price, Melting %
        # Quantity removed for this workflow – hide control & label
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

        add_layout.addWidget(QLabel("Unit Price (₹):"), 3, 2)
        self.product_price_spin = QDoubleSpinBox()
        self.product_price_spin.setDecimals(2)
        self.product_price_spin.setRange(0.0, 999999.99)
        add_layout.addWidget(self.product_price_spin, 3, 3)

        # Row 4: Supplier and Melting %
        add_layout.addWidget(QLabel("Supplier:"), 4, 0)
        self.product_supplier_combo = QComboBox()
        add_layout.addWidget(self.product_supplier_combo, 4, 1)

        add_layout.addWidget(QLabel("Melting %:"), 4, 2)
        self.product_melting_spin = QDoubleSpinBox()
        self.product_melting_spin.setDecimals(1)
        self.product_melting_spin.setRange(0.0, 100.0)
        add_layout.addWidget(self.product_melting_spin, 4, 3)

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
        add_layout.addWidget(self.add_product_btn, 5, 0, 1, 4)

        top_splitter.addWidget(add_group)

        # Summary panel
        summary_group = QGroupBox("Inventory Summary")
        summary_layout = QVBoxLayout(summary_group)

        self.total_products_label = QLabel("Total Products: 0")
        self.total_quantity_label = QLabel("Total Quantity: 0")
        self.total_value_label = QLabel("Total Value: ₹0.00")
        self.low_stock_label = QLabel("Low Stock Items: 0")

        for label in [
            self.total_products_label,
            self.total_quantity_label,
            self.total_value_label,
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
        self.products_table.setColumnCount(10)
        self.products_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Name",
                "Description",
                "Category",
                "Gross Weight",
                "Net Weight",
                "Quantity",
                "Unit Price",
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
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Price
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Supplier
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Actions

        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setAlternatingRowColors(True)

        # Hide Quantity column from view
        self.products_table.setColumnHidden(6, True)

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

            # Load products
            self.load_products()

            # Load categories table
            self.load_categories_table()

            # Load suppliers table
            self.load_suppliers_table()

            # Load stock movements
            self.load_stock_movements()

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
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product["id"])))
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

            # Highlight low stock
            quantity = product["quantity"]
            quantity_item = QTableWidgetItem(str(quantity))
            if quantity <= 5:
                quantity_item.setBackground(Qt.red if quantity == 0 else Qt.yellow)
            self.products_table.setItem(row, 6, quantity_item)

            self.products_table.setItem(
                row, 7, QTableWidgetItem(f"₹{product['unit_price']:.2f}")
            )
            self.products_table.setItem(
                row, 8, QTableWidgetItem(product.get("supplier_name", ""))
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

            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(
                lambda checked, p_id=product["id"]: self.delete_product(p_id)
            )
            action_layout.addWidget(delete_btn)

            self.products_table.setCellWidget(row, 9, action_widget)

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

                delete_btn = QPushButton("Delete")
                delete_btn.clicked.connect(
                    lambda checked, s_id=supplier["id"]: self.delete_supplier(s_id)
                )
                action_layout.addWidget(delete_btn)

                self.suppliers_table.setCellWidget(row, 6, action_widget)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading suppliers: {str(e)}")

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
                self.movements_table.setItem(
                    row, 1, QTableWidgetItem(movement.get("product_name", ""))
                )
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
            total_quantity = sum(p["quantity"] for p in self.products)
            total_value = sum(p["quantity"] * p["unit_price"] for p in self.products)
            low_stock_count = len([p for p in self.products if p["quantity"] <= 5])

            self.total_products_label.setText(f"Total Products: {total_products}")
            self.total_quantity_label.setText(f"Total Quantity: {total_quantity:,}")
            self.total_value_label.setText(f"Total Value: ₹{total_value:,.2f}")
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
                QMessageBox.warning(
                    self, "Warning", "Please select a category (used as product name)."
                )
                return
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

            # Add product to database
            product_id = self.db.add_product(
                name=name,
                description=self.product_desc_edit.text().strip() or None,
                hsn_code=self.product_hsn_edit.text().strip() or None,
                gross_weight=gross_weight,
                net_weight=net_weight,
                # No explicit quantity management; default to 1 unit
                quantity=1,
                unit_price=self.product_price_spin.value(),
                supplier_id=supplier_id,
                category_id=category_id,
                melting_percentage=self.product_melting_spin.value(),
            )

            QMessageBox.information(
                self, "Success", f"Product '{name}' added successfully!"
            )

            # Clear form
            self.clear_product_form()

            # Reload data
            self.load_products()
            self.update_summary()

            # Emit signal
            self.product_added.emit(product_id, name)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding product: {str(e)}")

    def clear_product_form(self):
        """Clear the product form."""
        self.product_name_edit.clear()
        self.product_desc_edit.clear()
        self.product_hsn_edit.clear()
        self.product_category_combo.setCurrentIndex(0)
        self.product_gross_weight_spin.setValue(0.0)
        self.product_net_weight_spin.setValue(0.0)
        self.product_quantity_spin.setValue(1)
        self.product_price_spin.setValue(0.0)
        self.product_supplier_combo.setCurrentIndex(0)
        self.product_melting_spin.setValue(0.0)

    def edit_product(self, product_id):
        """Edit a product."""
        QMessageBox.information(
            self,
            "Edit Product",
            f"Edit functionality for product ID {product_id} will be implemented.",
        )

    def delete_product(self, product_id):
        """Delete a product."""
        reply = QMessageBox.question(
            self,
            "Delete Product",
            "Are you sure you want to delete this product?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                # Note: In a full implementation, you'd need to add delete_product method to the database
                QMessageBox.information(
                    self,
                    "Delete",
                    f"Product deletion for ID {product_id} will be implemented.",
                )
                # self.db.delete_product(product_id)
                # self.load_products()
                # self.update_summary()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting product: {str(e)}")

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
        reply = QMessageBox.question(
            self,
            "Delete Category",
            "Are you sure you want to delete this category?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                # Note: In a full implementation, you'd need to add delete_category method to the database
                QMessageBox.information(
                    self,
                    "Delete",
                    f"Category deletion for ID {category_id} will be implemented.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error deleting category: {str(e)}"
                )

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
        reply = QMessageBox.question(
            self,
            "Delete Supplier",
            "Are you sure you want to delete this supplier?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                # Note: In a full implementation, you'd need to add delete_supplier method to the database
                QMessageBox.information(
                    self,
                    "Delete",
                    f"Supplier deletion for ID {supplier_id} will be implemented.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error deleting supplier: {str(e)}"
                )

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
                            "Unit Price",
                            "Supplier",
                            "Melting %",
                            "Total Value",
                        ]
                    )

                    # Write data
                    for product in self.products:
                        total_value = product["quantity"] * product["unit_price"]
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
                                product["unit_price"],
                                product.get("supplier_name", ""),
                                product.get("melting_percentage", 0),
                                total_value,
                            ]
                        )

                QMessageBox.information(
                    self, "Success", f"Products exported to {filename}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting products: {str(e)}")
