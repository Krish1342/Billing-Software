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
    QCheckBox,
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QStringListModel
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from decimal import Decimal, InvalidOperation
import json
from datetime import datetime
from typing import List, Dict, Optional

from unified_database import UnifiedDatabaseManager
from calc import create_calculator, CalculationError
from pdf_generator import InvoicePDFGenerator


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

        # Product selection
        add_layout.addWidget(QLabel("Product:"), 0, 0)
        self.product_combo = QComboBox()
        self.product_combo.setEditable(True)
        self.product_combo.currentTextChanged.connect(self.on_product_selected)
        add_layout.addWidget(self.product_combo, 0, 1)

        # Description
        add_layout.addWidget(QLabel("Description:"), 0, 2)
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Item description")
        add_layout.addWidget(self.description_edit, 0, 3)

        # HSN Code
        add_layout.addWidget(QLabel("HSN Code:"), 1, 0)
        self.hsn_edit = QLineEdit()
        self.hsn_edit.setPlaceholderText("HSN/SAC Code")
        add_layout.addWidget(self.hsn_edit, 1, 1)

        # Quantity
        add_layout.addWidget(QLabel("Quantity:"), 1, 2)
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setDecimals(3)
        self.quantity_spin.setRange(0.001, 999999.999)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.valueChanged.connect(self.calculate_line_total)
        add_layout.addWidget(self.quantity_spin, 1, 3)

        # Rate
        add_layout.addWidget(QLabel("Rate:"), 2, 0)
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setDecimals(2)
        self.rate_spin.setRange(0.0, 999999.99)
        self.rate_spin.valueChanged.connect(self.calculate_line_total)
        add_layout.addWidget(self.rate_spin, 2, 1)

        # Amount
        add_layout.addWidget(QLabel("Amount:"), 2, 2)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setDecimals(2)
        self.amount_spin.setRange(0.0, 999999.99)
        self.amount_spin.valueChanged.connect(self.calculate_from_amount)
        add_layout.addWidget(self.amount_spin, 2, 3)

        # Add button
        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.clicked.connect(self.add_line_item)
        add_layout.addWidget(self.add_item_btn, 3, 0, 1, 4)

        group_layout.addWidget(add_form)

        # Line items table
        self.line_items_table = QTableWidget()
        self.line_items_table.setColumnCount(7)
        self.line_items_table.setHorizontalHeaderLabels(
            [
                "Description",
                "HSN Code",
                "Quantity",
                "Rate",
                "Amount",
                "Stock Available",
                "Actions",
            ]
        )

        # Configure table
        header = self.line_items_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # HSN
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Quantity
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
        override_layout = QHBoxLayout()

        self.override_total_checkbox = QCheckBox("Enable")
        self.override_total_checkbox.stateChanged.connect(
            self.on_override_total_changed
        )
        override_layout.addWidget(self.override_total_checkbox)

        self.override_total_spin = QDoubleSpinBox()
        self.override_total_spin.setRange(0.0, 999999.99)
        self.override_total_spin.setDecimals(2)
        self.override_total_spin.setPrefix("₹")
        self.override_total_spin.setEnabled(False)
        self.override_total_spin.valueChanged.connect(
            self.on_override_total_spin_changed
        )
        override_layout.addWidget(self.override_total_spin)

        override_widget = QWidget()
        override_widget.setLayout(override_layout)
        group_layout.addWidget(override_widget, 5, 1)

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

            # Load products
            self.products = self.db.get_products()
            # Do not show stock quantity in the selector; name is effectively category
            product_items = ["Select Product"] + [
                f"{p['name']} - {p['description'] or 'No description'}"
                for p in self.products
            ]
            self.product_combo.clear()
            self.product_combo.addItems(product_items)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading data: {str(e)}")

    def on_product_selected(self, text):
        """Handle product selection."""
        if text == "Select Product" or not text:
            return

        try:
            # Find selected product
            for product in self.products:
                product_text = (
                    f"{product['name']} - {product['description'] or 'No description'}"
                )
                if product_text == text:
                    # Fill in product details
                    self.description_edit.setText(
                        product["description"] or product["name"]
                    )
                    self.hsn_edit.setText(product.get("hsn_code", ""))
                    self.rate_spin.setValue(float(product["unit_price"]))

                    # Show available stock
                    stock_qty = product["quantity"]
                    if stock_qty <= 0:
                        QMessageBox.warning(
                            self,
                            "No Stock",
                            f"Product '{product['name']}' is out of stock!",
                        )
                    elif stock_qty <= 5:
                        QMessageBox.information(
                            self,
                            "Low Stock",
                            f"Product '{product['name']}' has only {stock_qty} units in stock.",
                        )

                    break
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error selecting product: {str(e)}")

    def calculate_line_total(self):
        """Calculate line total when quantity or rate changes."""
        try:
            quantity = Decimal(str(self.quantity_spin.value()))
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
            quantity = Decimal(str(self.quantity_spin.value()))
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

            quantity = self.quantity_spin.value()
            rate = self.rate_spin.value()
            amount = self.amount_spin.value()

            if quantity <= 0:
                QMessageBox.warning(
                    self, "Warning", "Quantity must be greater than zero."
                )
                return

            if rate < 0:
                QMessageBox.warning(self, "Warning", "Rate cannot be negative.")
                return

            # Check stock if product selected
            product_id = None
            stock_available = "N/A"
            selected_product_text = self.product_combo.currentText()

            if selected_product_text != "Select Product":
                for product in self.products:
                    product_text = f"{product['name']} - {product['description'] or 'No description'}"
                    if product_text == selected_product_text:
                        product_id = product["id"]
                        # Quantity tracking disabled in this workflow
                        stock_available = "N/A"
                        break

            # Create line item
            line_item = {
                "product_id": product_id,
                "description": description,
                "hsn_code": self.hsn_edit.text().strip(),
                "quantity": quantity,
                "rate": rate,
                "amount": amount,
            }

            self.line_items.append(line_item)

            # Add to table
            row = self.line_items_table.rowCount()
            self.line_items_table.insertRow(row)

            self.line_items_table.setItem(row, 0, QTableWidgetItem(description))
            self.line_items_table.setItem(
                row, 1, QTableWidgetItem(line_item["hsn_code"])
            )
            self.line_items_table.setItem(row, 2, QTableWidgetItem(f"{quantity:.3f}"))
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
            if (
                hasattr(self, "override_total_checkbox")
                and self.override_total_checkbox.isChecked()
            ):
                # Reallocate amounts whenever a new item is added while override is active
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
        self.product_combo.setCurrentIndex(0)
        self.description_edit.clear()
        self.hsn_edit.clear()
        self.quantity_spin.setValue(1.0)
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
            if (
                hasattr(self, "override_total_checkbox")
                and self.override_total_checkbox.isChecked()
            ):
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
                if (
                    hasattr(self, "override_total_checkbox")
                    and self.override_total_checkbox.isChecked()
                ):
                    # Use override value
                    final_total = self.override_total_spin.value()
                    self.final_total_label.setText(f"₹{final_total:.2f}")
                else:
                    # Use calculated total
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
            if (
                not hasattr(self, "override_total_checkbox")
                or not self.override_total_checkbox.isChecked()
            ):
                return

            if not self.line_items:
                return

            user_total = Decimal(str(self.override_total_spin.value()))
            updated_items = self.calculator.allocate_amounts_by_weight(
                self.line_items, user_total
            )

            # Replace and refresh table
            self.line_items = updated_items
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

    def on_override_total_changed(self, state):
        """Handle override total checkbox change."""
        if hasattr(self, "override_total_spin"):
            self.override_total_spin.setEnabled(state == 2)  # 2 = checked
            if state == 2:  # If enabled, set current total as default
                if hasattr(self, "line_items") and self.line_items:
                    totals = self.calculator.calculate_invoice_totals(self.line_items)
                    self.override_total_spin.setValue(float(totals["final_total"]))
            self.update_totals()

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

        # Reset override total
        if hasattr(self, "override_total_checkbox"):
            self.override_total_checkbox.setChecked(False)
            self.override_total_spin.setEnabled(False)
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
                    "invoice_date": self.invoice_date_edit.date().toString(Qt.ISODate),
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

            # If override is active, reallocate amounts by weight first
            if (
                hasattr(self, "override_total_checkbox")
                and self.override_total_checkbox.isChecked()
            ):
                self.apply_override_allocation()

            # Calculate totals
            totals = self.calculator.calculate_invoice_totals(self.line_items)

            # Check if total is overridden
            final_total = float(totals["final_total"])
            if (
                hasattr(self, "override_total_checkbox")
                and self.override_total_checkbox.isChecked()
            ):
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
                "invoice_date": self.invoice_date_edit.date().toString(Qt.ISODate),
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
