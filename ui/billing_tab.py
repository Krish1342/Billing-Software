"""
Billing Tab for Unified Jewelry Management System

This module provides the billing interface with automatic stock deduction
when invoices are generated.
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
    QCheckBox,
    QDateEdit,
    QTextEdit,
    QGroupBox,
    QHeaderView,
    QMessageBox,
    QFileDialog,
    QSpinBox,
    QDoubleSpinBox,
    QCompleter,
    QAbstractItemView,
    QFrame,
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QStringListModel
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from decimal import Decimal, InvalidOperation
import json
from datetime import datetime
from typing import List, Dict, Optional

from logic.database_manager import UnifiedDatabaseManager
from logic.calculator import create_calculator, CalculationError
from logic.pdf_generator import InvoicePDFGenerator


class BillingTab(QWidget):
    """Billing tab widget with invoice creation and stock deduction."""

    # Signals
    invoice_created = pyqtSignal(int, str)  # invoice_id, invoice_number

    def __init__(self, db: UnifiedDatabaseManager, calculator, settings: dict):
        super().__init__()

        self.db = db
        self.calculator = calculator
        self.settings = settings
        self.pdf_generator = InvoicePDFGenerator("settings.json")

        # Data
        self.line_items = []
        self.customers = []
        self.products = []
        self.categories = []
        self.products_by_category = {}

        # Setup UI
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the billing UI."""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("🧾 Invoice Creation")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #2E8B57; margin: 10px;")
        layout.addWidget(header_label)

        # Invoice details section
        self.create_invoice_details_section(layout)

        # Line items section
        self.create_line_items_section(layout)

        # Totals section
        self.create_totals_section(layout)

        # Action buttons
        self.create_action_buttons(layout)

    def create_invoice_details_section(self, layout):
        """Create invoice details section."""
        group = QGroupBox("Invoice Details")
        group_layout = QGridLayout(group)

        # Row 0: Invoice number and date
        group_layout.addWidget(QLabel("Invoice No:"), 0, 0)
        self.invoice_number_edit = QLineEdit()
        self.invoice_number_edit.setReadOnly(True)
        group_layout.addWidget(self.invoice_number_edit, 0, 1)

        group_layout.addWidget(QLabel("Date:"), 0, 2)
        self.invoice_date_edit = QDateEdit()
        self.invoice_date_edit.setDate(QDate.currentDate())
        self.invoice_date_edit.setCalendarPopup(True)
        group_layout.addWidget(self.invoice_date_edit, 0, 3)

        # Row 1: Customer details
        group_layout.addWidget(QLabel("Customer Name:"), 1, 0)
        self.customer_name_edit = QLineEdit()
        self.customer_name_edit.setPlaceholderText("Enter customer name")
        group_layout.addWidget(self.customer_name_edit, 1, 1, 1, 3)

        # Row 2: Customer contact
        group_layout.addWidget(QLabel("Phone:"), 2, 0)
        self.customer_phone_edit = QLineEdit()
        self.customer_phone_edit.setPlaceholderText("Optional")
        group_layout.addWidget(self.customer_phone_edit, 2, 1)

        group_layout.addWidget(QLabel("GSTIN:"), 2, 2)
        self.customer_gstin_edit = QLineEdit()
        self.customer_gstin_edit.setPlaceholderText("Optional")
        group_layout.addWidget(self.customer_gstin_edit, 2, 3)

        layout.addWidget(group)

    def create_line_items_section(self, layout):
        """Create line items section."""
        group = QGroupBox("Line Items")
        group_layout = QVBoxLayout(group)

        # Add item form
        add_form = QFrame()
        add_form.setFrameStyle(QFrame.StyledPanel)
        add_layout = QGridLayout(add_form)

        # Row 0: Custom order toggle
        self.custom_order_check = QCheckBox("Custom Order (not in stock)")
        self.custom_order_check.setToolTip(
            "Tick for made-to-order items not present in inventory"
        )
        self.custom_order_check.toggled.connect(self.on_custom_order_toggled)
        add_layout.addWidget(self.custom_order_check, 0, 0, 1, 4)

        # Row 1: Category and Item (weight) or Weight (g) for custom
        add_layout.addWidget(QLabel("Category:"), 1, 0)
        self.category_combo = QComboBox()
        self.category_combo.currentIndexChanged.connect(self.on_category_selected)
        self.category_combo.setToolTip("Choose a category first")
        add_layout.addWidget(self.category_combo, 1, 1)

        self.item_label = QLabel("Select Weight:")
        add_layout.addWidget(self.item_label, 1, 2)
        self.item_combo = QComboBox()
        self.item_combo.setEditable(False)
        self.item_combo.currentIndexChanged.connect(self.on_item_selected)
        self.item_combo.setToolTip("Pick an item by its weight")
        add_layout.addWidget(self.item_combo, 1, 3)

        # Weight (g)
        self.weight_label = QLabel("Weight (g):")
        self.net_weight_spin = QDoubleSpinBox()
        self.net_weight_spin.setDecimals(3)
        self.net_weight_spin.setRange(0.001, 999999.999)
        self.net_weight_spin.setValue(1.000)
        self.net_weight_spin.setToolTip("Enter the net weight in grams")
        # Initially hide weight for non-custom flow; will be shown for custom
        self.weight_label.setVisible(False)
        self.net_weight_spin.setVisible(False)
        add_layout.addWidget(self.weight_label, 1, 2)
        add_layout.addWidget(self.net_weight_spin, 1, 3)

        # Row 2: Description (spans full width)
        add_layout.addWidget(QLabel("Description:"), 2, 0)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Item description")
        add_layout.addWidget(self.description_edit, 2, 1, 1, 3)

        # Row 3: HSN
        add_layout.addWidget(QLabel("HSN Code:"), 3, 0)
        self.hsn_edit = QLineEdit()
        self.hsn_edit.setPlaceholderText("HSN/SAC Code")
        add_layout.addWidget(self.hsn_edit, 3, 1)

        # Row 4: Rate and Amount
        add_layout.addWidget(QLabel("Rate:"), 4, 0)
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setDecimals(2)
        self.rate_spin.setRange(0.0, 999999.99)
        self.rate_spin.valueChanged.connect(self.calculate_line_total)
        add_layout.addWidget(self.rate_spin, 4, 1)

        # Amount
        add_layout.addWidget(QLabel("Amount:"), 4, 2)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setDecimals(2)
        self.amount_spin.setRange(0.0, 999999.99)
        self.amount_spin.valueChanged.connect(self.calculate_from_amount)
        add_layout.addWidget(self.amount_spin, 4, 3)

        # Add button
        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.clicked.connect(self.add_line_item)
        add_layout.addWidget(self.add_item_btn, 5, 0, 1, 4)

        group_layout.addWidget(add_form)

        # Line items table
        self.line_items_table = QTableWidget()
        self.line_items_table.setColumnCount(7)
        self.line_items_table.setHorizontalHeaderLabels(
            [
                "Description",
                "HSN Code",
                "Weight (g)",
                "Rate",
                "Amount",
                "Category Stock",
                "Actions",
            ]
        )

        # Configure table
        header = self.line_items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # HSN
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Weight
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Rate
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Stock
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions

        self.line_items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.line_items_table.setAlternatingRowColors(True)

        group_layout.addWidget(self.line_items_table)

        layout.addWidget(group)

    def create_totals_section(self, layout):
        """Create totals section."""
        group = QGroupBox("Invoice Totals")
        group_layout = QGridLayout(group)

        # Subtotal
        group_layout.addWidget(QLabel("Subtotal:"), 0, 0)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setAlignment(Qt.AlignRight)
        group_layout.addWidget(self.subtotal_label, 0, 1)

        # CGST
        cgst_rate = self.settings["tax"]["cgst_rate"]
        group_layout.addWidget(QLabel(f"CGST ({cgst_rate}%):"), 1, 0)
        self.cgst_label = QLabel("₹0.00")
        self.cgst_label.setAlignment(Qt.AlignRight)
        group_layout.addWidget(self.cgst_label, 1, 1)

        # SGST
        sgst_rate = self.settings["tax"]["sgst_rate"]
        group_layout.addWidget(QLabel(f"SGST ({sgst_rate}%):"), 2, 0)
        self.sgst_label = QLabel("₹0.00")
        self.sgst_label.setAlignment(Qt.AlignRight)
        group_layout.addWidget(self.sgst_label, 2, 1)

        # Total
        group_layout.addWidget(QLabel("Total:"), 3, 0)
        self.total_label = QLabel("₹0.00")
        self.total_label.setAlignment(Qt.AlignRight)
        total_font = QFont()
        total_font.setBold(True)
        total_font.setPointSize(14)
        self.total_label.setFont(total_font)
        self.total_label.setStyleSheet("color: #2E8B57;")
        group_layout.addWidget(self.total_label, 3, 1)

        # Rounded off
        group_layout.addWidget(QLabel("Rounded Off:"), 4, 0)
        self.rounded_off_label = QLabel("₹0.00")
        self.rounded_off_label.setAlignment(Qt.AlignRight)
        group_layout.addWidget(self.rounded_off_label, 4, 1)

        # Override Total functionality
        group_layout.addWidget(QLabel("Override Total:"), 5, 0)

        self.override_total_spin = QDoubleSpinBox()
        self.override_total_spin.setRange(0.0, 999999.99)
        self.override_total_spin.setDecimals(2)
        self.override_total_spin.setPrefix("₹")
        self.override_total_spin.setEnabled(True)  # Always enabled
        self.override_total_spin.valueChanged.connect(
            self.on_override_total_spin_changed
        )
        group_layout.addWidget(self.override_total_spin, 5, 1)

        # Final total (after rounding or override)
        group_layout.addWidget(QLabel("Final Total:"), 6, 0)
        self.final_total_label = QLabel("₹0.00")
        self.final_total_label.setAlignment(Qt.AlignRight)
        final_font = QFont()
        final_font.setBold(True)
        final_font.setPointSize(16)
        self.final_total_label.setFont(final_font)
        self.final_total_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
        group_layout.addWidget(self.final_total_label, 6, 1)

        layout.addWidget(group)

    def create_action_buttons(self, layout):
        """Create action buttons."""
        button_layout = QHBoxLayout()

        # New invoice
        self.new_btn = QPushButton("New Invoice")
        self.new_btn.clicked.connect(self.new_invoice)
        button_layout.addWidget(self.new_btn)

        # Save draft
        self.save_draft_btn = QPushButton("Save Draft")
        self.save_draft_btn.clicked.connect(self.save_draft)
        button_layout.addWidget(self.save_draft_btn)

        # Generate PDF
        self.generate_pdf_btn = QPushButton("Generate Invoice")
        self.generate_pdf_btn.clicked.connect(self.generate_invoice)
        self.generate_pdf_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #2E8B57;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """
        )
        button_layout.addWidget(self.generate_pdf_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def load_data(self):
        """Load data for dropdowns."""
        try:
            # Load next invoice number
            next_number = self.db.get_next_invoice_number()
            self.invoice_number_edit.setText(next_number)

            # Load customers
            self.customers = self.db.get_customers()
            customer_names = [c["name"] for c in self.customers]
            customer_completer = QCompleter(customer_names)
            self.customer_name_edit.setCompleter(customer_completer)

            # Load categories and products
            self.categories = self.db.get_categories()
            self.products = self.db.get_products()

            # Build products_by_category mapping
            self.products_by_category = {}
            for p in self.products:
                cid = p.get("category_id")
                if cid is None:
                    continue
                self.products_by_category.setdefault(cid, []).append(p)

            # Fill category combo
            self.category_combo.blockSignals(True)
            self.category_combo.clear()
            self.category_combo.addItem("Select Category", None)
            for c in self.categories:
                self.category_combo.addItem(c["name"], c["id"])
            self.category_combo.blockSignals(False)

            # Reset item combo
            self.populate_items_for_category(None)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading data: {str(e)}")

    def refresh_products(self):
        """Refresh categories/items and cached products."""
        try:
            # Clear all cached data first
            self.products = []
            self.categories = []
            self.products_by_category = {}

            # Reload products and categories from database
            self.categories = self.db.get_categories()
            self.products = self.db.get_products()

            # Rebuild mapping
            for p in self.products:
                cid = p.get("category_id")
                if cid is None:
                    continue
                self.products_by_category.setdefault(cid, []).append(p)

            # Refresh category combo, keep selection if possible
            current_cid = (
                self.category_combo.currentData()
                if hasattr(self, "category_combo")
                else None
            )
            self.category_combo.blockSignals(True)
            self.category_combo.clear()
            self.category_combo.addItem("Select Category", None)
            for c in self.categories:
                self.category_combo.addItem(c["name"], c["id"])
            # Try to restore previous selection
            if current_cid:
                index = self.category_combo.findData(current_cid)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
            self.category_combo.blockSignals(False)

            # Clear and repopulate items for current category
            self.populate_items_for_category(self.category_combo.currentData())

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error refreshing products: {str(e)}")

    def populate_items_for_category(self, category_id: Optional[int]):
        """Populate the item (weight) combo for a given category."""
        # Helper creates friendly label and stores product_id in item data
        self.item_combo.blockSignals(True)
        self.item_combo.clear()
        self.item_combo.addItem("Select Item", None)
        if not category_id:
            self.item_combo.setEnabled(False)
            self.item_combo.blockSignals(False)
            return

        # Get all items in category (deleted products are already removed from DB)
        items = self.products_by_category.get(category_id, [])
        # Sort by category_item_id for clarity
        items.sort(key=lambda x: x.get("category_item_id", 0) or 0)
        for p in items:
            cat_id = p.get(
                "category_item_id", p["id"]
            )  # Fallback to global ID if no category_item_id
            label = f"#{cat_id} — Net {float(p.get('net_weight',0)):.3f} g (Gross {float(p.get('gross_weight',0)):.3f} g)"
            self.item_combo.addItem(label, p["id"])
        self.item_combo.setEnabled(True)
        self.item_combo.setToolTip(
            "Pick the exact item by weight. Only available stock is listed."
        )
        self.item_combo.blockSignals(False)

    def on_category_selected(self, index: int):
        """When category changes, populate items list and reset fields."""
        category_id = self.category_combo.itemData(index)
        self.populate_items_for_category(category_id)
        # Reset selection-dependent fields
        self.description_edit.clear()
        self.hsn_edit.clear()
        self.rate_spin.setValue(0.0)
        self.amount_spin.setValue(0.0)
        self.net_weight_spin.setValue(1.000)

    def on_item_selected(self, index: int):
        """Handle item (weight) selection."""
        product_id = self.item_combo.itemData(index)
        if not product_id:
            return
        try:
            # Find the product
            product = next((p for p in self.products if p["id"] == product_id), None)
            if not product:
                return

            # Fill description and HSN
            category_name = next(
                (
                    c["name"]
                    for c in self.categories
                    if c["id"] == product.get("category_id")
                ),
                product.get("name", "Item"),
            )
            net_w = float(product.get("net_weight", 0))
            self.description_edit.setText(f"{category_name} - {net_w:.3f} g")
            self.hsn_edit.setText(product.get("hsn_code", ""))

            # Rate is per gram; set weight and disable editing for stock items
            unit_price = float(product.get("unit_price", 0.0))
            self.rate_spin.setValue(unit_price)
            self.net_weight_spin.setValue(net_w)
            self.net_weight_spin.setEnabled(False)
            self.calculate_line_total()

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error selecting item: {str(e)}")

    def on_custom_order_toggled(self, checked: bool):
        """Toggle between inventory item and custom order item."""
        # Toggle visibility of selectors
        self.item_label.setVisible(not checked)
        self.item_combo.setVisible(not checked)
        self.weight_label.setVisible(checked)
        self.net_weight_spin.setVisible(checked)
        # Reset some fields
        self.net_weight_spin.setValue(1.000)
        self.rate_spin.setValue(0.0)
        self.amount_spin.setValue(0.0)
        if checked:
            # For custom orders, disable item selection and clear description for user
            self.description_edit.setText("")
            self.net_weight_spin.setEnabled(True)
        else:
            # For stock items, weight is set by selection and not editable
            self.net_weight_spin.setEnabled(False)

    def calculate_line_total(self):
        """Calculate line total when weight or rate changes."""
        try:
            quantity = Decimal(str(self.net_weight_spin.value()))
            rate = Decimal(str(self.rate_spin.value()))
            amount = quantity * rate

            # Update amount without triggering signals
            self.amount_spin.blockSignals(True)
            self.amount_spin.setValue(float(amount))
            self.amount_spin.blockSignals(False)

        except (InvalidOperation, ValueError):
            pass

    def calculate_from_amount(self):
        """Calculate rate when amount changes."""
        try:
            quantity = Decimal(str(self.net_weight_spin.value()))
            amount = Decimal(str(self.amount_spin.value()))

            if quantity > 0:
                rate = amount / quantity

                # Update rate without triggering signals
                self.rate_spin.blockSignals(True)
                self.rate_spin.setValue(float(rate))
                self.rate_spin.blockSignals(False)

        except (InvalidOperation, ValueError, ZeroDivisionError):
            pass

    def add_line_item(self):
        """Add a line item to the invoice."""
        try:
            # Validate inputs
            description = self.description_edit.text().strip()
            if not description:
                QMessageBox.warning(self, "Warning", "Please enter item description.")
                return

            weight = self.net_weight_spin.value()
            rate = self.rate_spin.value()
            amount = self.amount_spin.value()

            if weight <= 0:
                QMessageBox.warning(
                    self, "Warning", "Weight must be greater than zero."
                )
                return

            if rate < 0:
                QMessageBox.warning(self, "Warning", "Rate cannot be negative.")
                return

            # Check stock if product selected
            product_id = None
            stock_available = "N/A"
            # Read selected product or custom order
            if self.custom_order_check.isChecked():
                product_id = None
                stock_available = "Custom"
                # Auto-fill description if empty
                if not description:
                    # Use category name and entered weight
                    cid = self.category_combo.currentData()
                    category_name = next(
                        (c["name"] for c in self.categories if c["id"] == cid), "Item"
                    )
                    weight = float(self.net_weight_spin.value())
                    description = f"{category_name} - {weight:.3f} g (Custom Order)"
            else:
                selected_product_index = self.item_combo.currentIndex()
                if selected_product_index > 0:
                    product_id = self.item_combo.itemData(selected_product_index)
                    # Count total items in this category
                    product = next(
                        (p for p in self.products if p["id"] == product_id), None
                    )
                    if product and product.get("category_id"):
                        category_items_count = len(
                            self.products_by_category.get(product["category_id"], [])
                        )
                        stock_available = f"{category_items_count} available"
                    else:
                        stock_available = "Yes"

            # Create line item
            line_item = {
                "product_id": product_id,
                "description": description,
                "hsn_code": self.hsn_edit.text().strip(),
                "quantity": float(weight),
                "rate": float(rate),
                "amount": float(amount),
            }

            self.line_items.append(line_item)

            # Add to table
            row = self.line_items_table.rowCount()
            self.line_items_table.insertRow(row)

            self.line_items_table.setItem(row, 0, QTableWidgetItem(description))
            self.line_items_table.setItem(
                row, 1, QTableWidgetItem(line_item["hsn_code"])
            )
            self.line_items_table.setItem(row, 2, QTableWidgetItem(f"{weight:.3f}"))
            self.line_items_table.setItem(row, 3, QTableWidgetItem(f"₹{rate:.2f}"))
            self.line_items_table.setItem(row, 4, QTableWidgetItem(f"₹{amount:.2f}"))
            self.line_items_table.setItem(row, 5, QTableWidgetItem(stock_available))

            # Add remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda: self.remove_line_item(row))
            self.line_items_table.setCellWidget(row, 6, remove_btn)

            # Clear form
            self.clear_line_item_form()

            # Update totals
            # Override total is always enabled, so reallocate amounts
            self.apply_override_allocation()
            self.update_totals()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error adding line item: {str(e)}")

    def remove_line_item(self, row):
        """Remove a line item."""
        try:
            if 0 <= row < len(self.line_items):
                self.line_items.pop(row)
                self.line_items_table.removeRow(row)

                # Update remove button connections
                for i in range(self.line_items_table.rowCount()):
                    btn = self.line_items_table.cellWidget(i, 6)
                    if btn:
                        btn.clicked.disconnect()
                        btn.clicked.connect(
                            lambda checked, r=i: self.remove_line_item(r)
                        )

                self.update_totals()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error removing line item: {str(e)}")

    def clear_line_item_form(self):
        """Clear the line item form."""
        self.category_combo.setCurrentIndex(0)
        self.item_combo.clear()
        self.item_combo.addItem("Select Item", None)
        self.item_combo.setEnabled(False)
        self.custom_order_check.setChecked(False)
        self.net_weight_spin.setValue(1.000)
        self.description_edit.clear()
        self.hsn_edit.clear()
        self.rate_spin.setValue(0.0)
        self.amount_spin.setValue(0.0)

    def update_totals(self):
        """Update invoice totals."""
        try:
            if not self.line_items:
                self.subtotal_label.setText("₹0.00")
                self.cgst_label.setText("₹0.00")
                self.sgst_label.setText("₹0.00")
                self.total_label.setText("₹0.00")
                self.rounded_off_label.setText("₹0.00")
                if hasattr(self, "final_total_label"):
                    self.final_total_label.setText("₹0.00")
                return

            # Calculate totals using the calculator
            user_total = None
            # Override is always enabled, use value if > 0
            if self.override_total_spin.value() > 0:
                user_total = Decimal(str(self.override_total_spin.value()))
            totals = self.calculator.calculate_invoice_totals(
                self.line_items, user_total_inclusive=user_total
            )

            self.subtotal_label.setText(f"₹{totals['subtotal']:.2f}")
            self.cgst_label.setText(f"₹{totals['cgst']:.2f}")
            self.sgst_label.setText(f"₹{totals['sgst']:.2f}")
            self.total_label.setText(f"₹{totals['final_total']:.2f}")
            self.rounded_off_label.setText(f"₹{totals['rounded_off']:.2f}")

            # Handle override total
            if hasattr(self, "final_total_label"):
                # Always use override value since override is always enabled
                final_total = self.override_total_spin.value()
                if final_total > 0:
                    self.final_total_label.setText(f"₹{final_total:.2f}")
                else:
                    # Use calculated total if override is 0
                    self.final_total_label.setText(f"₹{totals['final_total']:.2f}")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error calculating totals: {str(e)}")

    def on_override_total_spin_changed(self, _):
        """When user adjusts override total, reallocate and refresh totals."""
        self.apply_override_allocation()
        self.update_totals()

    def apply_override_allocation(self):
        """Redistribute per-item amounts and rates by weight based on override total."""
        try:
            # Override is always enabled now
            if not self.line_items:
                return

            user_total = Decimal(str(self.override_total_spin.value()))
            if user_total <= 0:
                return  # Don't apply allocation if override total is 0

            updated_items = self.calculator.allocate_amounts_by_weight(
                self.line_items, user_total
            )

            # Replace and refresh table
            self.line_items = updated_items

            # Ensure all values are float (not Decimal) for database compatibility
            for item in self.line_items:
                item["quantity"] = float(item["quantity"])
                item["rate"] = float(item["rate"])
                item["amount"] = float(item["amount"])

            for row, item in enumerate(self.line_items):
                if row < self.line_items_table.rowCount():
                    self.line_items_table.setItem(
                        row, 3, QTableWidgetItem(f"₹{item['rate']:.2f}")
                    )
                    self.line_items_table.setItem(
                        row, 4, QTableWidgetItem(f"₹{item['amount']:.2f}")
                    )

        except Exception as e:
            QMessageBox.warning(
                self, "Override", f"Could not apply override allocation: {str(e)}"
            )

    def calculate_totals(self):
        """Recalculate totals - alias for update_totals for compatibility."""
        self.update_totals()

    def new_invoice(self):
        """Start a new invoice."""
        if self.line_items:
            reply = QMessageBox.question(
                self,
                "New Invoice",
                "Current invoice will be cleared. Continue?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        # Clear all fields
        self.line_items.clear()
        self.line_items_table.setRowCount(0)

        self.customer_name_edit.clear()
        self.customer_phone_edit.clear()
        self.customer_gstin_edit.clear()

        # Reset override total (always enabled, just reset value)
        self.override_total_spin.setValue(0.0)

        self.clear_line_item_form()
        self.update_totals()

        # Load new invoice number
        next_number = self.db.get_next_invoice_number()
        self.invoice_number_edit.setText(next_number)

    def save_draft(self):
        """Save invoice as draft."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice Draft",
                f"invoice_draft_{self.invoice_number_edit.text()}.json",
                "JSON Files (*.json)",
            )

            if filename:
                draft_data = {
                    "invoice_number": self.invoice_number_edit.text(),
                    "customer_name": self.customer_name_edit.text(),
                    "customer_phone": self.customer_phone_edit.text(),
                    "customer_gstin": self.customer_gstin_edit.text(),
                    "invoice_date": self.invoice_date_edit.date().toString(
                        "yyyy-MM-dd"
                    ),
                    "line_items": self.line_items,
                }

                with open(filename, "w") as f:
                    json.dump(draft_data, f, indent=4, default=str)

                QMessageBox.information(self, "Success", "Draft saved successfully!")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving draft: {str(e)}")

    def generate_invoice(self):
        """Generate invoice PDF and save to database."""
        try:
            # Validate invoice
            if not self.customer_name_edit.text().strip():
                QMessageBox.warning(self, "Warning", "Please enter customer name.")
                return

            if not self.line_items:
                QMessageBox.warning(
                    self, "Warning", "Please add at least one line item."
                )
                return

            # Override is always active, reallocate amounts by weight if override > 0
            if self.override_total_spin.value() > 0:
                self.apply_override_allocation()

            # Calculate totals
            totals = self.calculator.calculate_invoice_totals(self.line_items)

            # Check if total is overridden
            final_total = float(totals["final_total"])
            if self.override_total_spin.value() > 0:
                final_total = self.override_total_spin.value()
                # Recalculate rounding for override total
                totals["rounded_off"] = final_total - (
                    float(totals["subtotal"])
                    + float(totals["cgst"])
                    + float(totals["sgst"])
                )

            # Prepare invoice data
            invoice_data = {
                "invoice_number": self.invoice_number_edit.text(),
                "customer_name": self.customer_name_edit.text().strip(),
                "customer_phone": self.customer_phone_edit.text().strip(),
                "customer_gstin": self.customer_gstin_edit.text().strip(),
                "invoice_date": self.invoice_date_edit.date().toString("yyyy-MM-dd"),
                "subtotal": float(totals["subtotal"]),
                "cgst_amount": float(totals["cgst"]),
                "sgst_amount": float(totals["sgst"]),
                "total_amount": final_total,
                "rounded_off": float(totals["rounded_off"]),
            }

            # Save to database with stock deduction
            invoice_id, warnings = self.db.generate_invoice_with_stock_deduction(
                invoice_data, self.line_items
            )

            # Show warnings if any
            if warnings:
                warning_text = "Invoice created but with warnings:\n\n" + "\n".join(
                    warnings
                )
                QMessageBox.warning(self, "Warnings", warning_text)

            # Generate PDF
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Invoice PDF",
                f"invoice_{invoice_data['invoice_number']}.pdf",
                "PDF Files (*.pdf)",
            )

            if filename:
                self.pdf_generator.generate_invoice_pdf(
                    filename, invoice_data, self.line_items
                )

                success_msg = (
                    f"Invoice {invoice_data['invoice_number']} generated successfully!"
                )
                if warnings:
                    success_msg += "\n\nNote: Check warnings for stock issues."

                QMessageBox.information(self, "Success", success_msg)

                # Emit signal
                self.invoice_created.emit(invoice_id, invoice_data["invoice_number"])

                # Reload data to refresh stock quantities
                self.load_data()

                # Start new invoice
                self.new_invoice()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating invoice: {str(e)}")
