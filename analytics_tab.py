"""
Analytics Tab for Unified Jewelry Management System

This module provides analytics and reporting functionality including
sales reports, inventory analytics, and data visualization.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QHeaderView,
    QComboBox,
    QDateEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QFrame,
    QTextEdit,
    QTabWidget,
    QProgressBar,
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QThread
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
import csv
from typing import Dict, List

from unified_database import UnifiedDatabaseManager


class AnalyticsTab(QWidget):
    """Analytics and reporting tab widget."""

    def __init__(self, db: UnifiedDatabaseManager, settings: dict):
        super().__init__()

        self.db = db
        self.settings = settings

        # Setup UI
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the analytics UI."""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("📊 Analytics & Reports")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #FF6347; margin: 10px;")
        layout.addWidget(header_label)

        # Create tab widget for different analytics sections
        self.tab_widget = QTabWidget()

        # Sales Analytics tab
        self.create_sales_analytics_tab()

        # Inventory Analytics tab
        self.create_inventory_analytics_tab()

        # Reports tab
        self.create_reports_tab()

        layout.addWidget(self.tab_widget)

    def create_sales_analytics_tab(self):
        """Create sales analytics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Date range selection
        date_group = QGroupBox("Date Range")
        date_layout = QHBoxLayout(date_group)

        date_layout.addWidget(QLabel("From:"))
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setDate(QDate.currentDate().addDays(-30))
        self.from_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.from_date_edit)

        date_layout.addWidget(QLabel("To:"))
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.to_date_edit)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_sales_data)
        date_layout.addWidget(refresh_btn)

        date_layout.addStretch()
        layout.addWidget(date_group)

        # Sales summary
        summary_group = QGroupBox("Sales Summary")
        summary_layout = QGridLayout(summary_group)

        # Summary labels
        self.total_invoices_label = QLabel("Total Invoices: 0")
        self.total_sales_label = QLabel("Total Sales: ₹0.00")
        self.average_sale_label = QLabel("Average Sale: ₹0.00")
        self.total_items_sold_label = QLabel("Total Items Sold: 0")

        # Style summary labels
        for label in [
            self.total_invoices_label,
            self.total_sales_label,
            self.average_sale_label,
            self.total_items_sold_label,
        ]:
            label.setStyleSheet(
                "font-size: 14px; font-weight: bold; padding: 10px; background-color: #f0f0f0; border-radius: 5px;"
            )

        summary_layout.addWidget(self.total_invoices_label, 0, 0)
        summary_layout.addWidget(self.total_sales_label, 0, 1)
        summary_layout.addWidget(self.average_sale_label, 1, 0)
        summary_layout.addWidget(self.total_items_sold_label, 1, 1)

        layout.addWidget(summary_group)

        # Recent invoices table
        invoices_group = QGroupBox("Recent Invoices")
        invoices_layout = QVBoxLayout(invoices_group)

        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(6)
        self.invoices_table.setHorizontalHeaderLabels(
            ["Invoice No", "Date", "Customer", "Items", "Total Amount", "Status"]
        )

        # Configure table
        header = self.invoices_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        self.invoices_table.setAlternatingRowColors(True)
        invoices_layout.addWidget(self.invoices_table)

        layout.addWidget(invoices_group)

        # Top selling items table
        top_items_group = QGroupBox("Top Selling Items")
        top_items_layout = QVBoxLayout(top_items_group)

        self.top_items_table = QTableWidget()
        self.top_items_table.setColumnCount(3)
        self.top_items_table.setHorizontalHeaderLabels(
            ["Product", "Quantity Sold", "Total Revenue"]
        )

        header = self.top_items_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        self.top_items_table.setAlternatingRowColors(True)
        top_items_layout.addWidget(self.top_items_table)

        layout.addWidget(top_items_group)

        self.tab_widget.addTab(tab, "📈 Sales Analytics")

    def create_inventory_analytics_tab(self):
        """Create inventory analytics tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Inventory summary
        summary_group = QGroupBox("Inventory Overview")
        summary_layout = QGridLayout(summary_group)

        self.total_products_label = QLabel("Total Products: 0")
        self.total_stock_label = QLabel("Total Stock: 0")
        self.total_value_label = QLabel("Total Value: ₹0.00")
        self.low_stock_items_label = QLabel("Low Stock Items: 0")

        # Style labels
        for label in [
            self.total_products_label,
            self.total_stock_label,
            self.total_value_label,
            self.low_stock_items_label,
        ]:
            label.setStyleSheet(
                "font-size: 14px; font-weight: bold; padding: 10px; background-color: #f0f0f0; border-radius: 5px;"
            )

        summary_layout.addWidget(self.total_products_label, 0, 0)
        summary_layout.addWidget(self.total_stock_label, 0, 1)
        summary_layout.addWidget(self.total_value_label, 1, 0)
        summary_layout.addWidget(self.low_stock_items_label, 1, 1)

        layout.addWidget(summary_group)

        # Low stock alert
        low_stock_group = QGroupBox("Low Stock Alert")
        low_stock_layout = QVBoxLayout(low_stock_group)

        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))

        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems(["1", "5", "10", "20", "50"])
        self.threshold_combo.setCurrentText("5")
        self.threshold_combo.currentTextChanged.connect(self.load_low_stock_data)
        threshold_layout.addWidget(self.threshold_combo)

        threshold_layout.addStretch()
        low_stock_layout.addLayout(threshold_layout)

        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels(
            ["Product", "Category", "Current Stock", "Unit Price", "Total Value"]
        )

        header = self.low_stock_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        self.low_stock_table.setAlternatingRowColors(True)
        low_stock_layout.addWidget(self.low_stock_table)

        layout.addWidget(low_stock_group)

        # Category breakdown
        category_group = QGroupBox("Stock by Category")
        category_layout = QVBoxLayout(category_group)

        self.category_table = QTableWidget()
        self.category_table.setColumnCount(4)
        self.category_table.setHorizontalHeaderLabels(
            ["Category", "Product Count", "Total Quantity", "Total Value"]
        )

        header = self.category_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        self.category_table.setAlternatingRowColors(True)
        category_layout.addWidget(self.category_table)

        layout.addWidget(category_group)

        self.tab_widget.addTab(tab, "📦 Inventory Analytics")

    def create_reports_tab(self):
        """Create reports generation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Report generation
        reports_group = QGroupBox("Generate Reports")
        reports_layout = QVBoxLayout(reports_group)

        # Report type selection
        report_layout = QHBoxLayout()
        report_layout.addWidget(QLabel("Report Type:"))

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(
            [
                "Sales Report",
                "Inventory Report",
                "Low Stock Report",
                "Customer Report",
                "Supplier Report",
            ]
        )
        report_layout.addWidget(self.report_type_combo)

        report_layout.addStretch()
        reports_layout.addLayout(report_layout)

        # Date range for reports
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.report_from_date = QDateEdit()
        self.report_from_date.setDate(QDate.currentDate().addDays(-30))
        self.report_from_date.setCalendarPopup(True)
        date_layout.addWidget(self.report_from_date)

        date_layout.addWidget(QLabel("To:"))
        self.report_to_date = QDateEdit()
        self.report_to_date.setDate(QDate.currentDate())
        self.report_to_date.setCalendarPopup(True)
        date_layout.addWidget(self.report_to_date)

        date_layout.addStretch()
        reports_layout.addLayout(date_layout)

        # Generate buttons
        button_layout = QHBoxLayout()

        preview_btn = QPushButton("👁️ Preview Report")
        preview_btn.clicked.connect(self.preview_report)
        button_layout.addWidget(preview_btn)

        export_btn = QPushButton("📊 Export to CSV")
        export_btn.clicked.connect(self.export_report)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()
        reports_layout.addLayout(button_layout)

        layout.addWidget(reports_group)

        # Report preview
        preview_group = QGroupBox("Report Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setPlainText(
            "Select a report type and click 'Preview Report' to see the data."
        )
        preview_layout.addWidget(self.report_preview)

        layout.addWidget(preview_group)

        self.tab_widget.addTab(tab, "📋 Reports")

    def load_data(self):
        """Load initial analytics data."""
        self.load_sales_data()
        self.load_inventory_data()
        self.load_low_stock_data()
        self.load_category_data()

    def load_sales_data(self):
        """Load sales analytics data."""
        try:
            from_date = self.from_date_edit.date().toString(Qt.ISODate)
            to_date = self.to_date_edit.date().toString(Qt.ISODate)

            # Get sales summary
            summary = self.db.get_sales_summary(from_date, to_date)

            # Update summary labels
            invoice_count = summary.get("invoice_count", 0) or 0
            total_sales = summary.get("total_sales", 0) or 0
            average_sale = summary.get("average_sale", 0) or 0

            self.total_invoices_label.setText(f"Total Invoices: {invoice_count}")
            self.total_sales_label.setText(f"Total Sales: ₹{total_sales:,.2f}")
            self.average_sale_label.setText(f"Average Sale: ₹{average_sale:,.2f}")

            # Calculate total items sold
            top_items = summary.get("top_items", [])
            total_items_sold = sum(item.get("total_sold", 0) for item in top_items)
            self.total_items_sold_label.setText(f"Total Items Sold: {total_items_sold}")

            # Load recent invoices
            invoices = self.db.get_invoices(50)
            self.invoices_table.setRowCount(len(invoices))

            for row, invoice in enumerate(invoices):
                self.invoices_table.setItem(
                    row, 0, QTableWidgetItem(invoice["invoice_number"])
                )
                self.invoices_table.setItem(
                    row, 1, QTableWidgetItem(invoice["invoice_date"])
                )
                self.invoices_table.setItem(
                    row, 2, QTableWidgetItem(invoice["customer_name"])
                )

                # Get item count for this invoice
                items = self.db.get_invoice_items(invoice["id"])
                self.invoices_table.setItem(row, 3, QTableWidgetItem(str(len(items))))

                self.invoices_table.setItem(
                    row, 4, QTableWidgetItem(f"₹{invoice['total_amount']:,.2f}")
                )
                self.invoices_table.setItem(
                    row, 5, QTableWidgetItem(invoice.get("status", "GENERATED"))
                )

            # Load top selling items
            self.top_items_table.setRowCount(len(top_items))

            for row, item in enumerate(top_items):
                self.top_items_table.setItem(
                    row, 0, QTableWidgetItem(item["description"])
                )
                self.top_items_table.setItem(
                    row, 1, QTableWidgetItem(f"{item['total_sold']:.3f}")
                )
                self.top_items_table.setItem(
                    row, 2, QTableWidgetItem(f"₹{item['total_revenue']:,.2f}")
                )

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading sales data: {str(e)}")

    def load_inventory_data(self):
        """Load inventory analytics data."""
        try:
            products = self.db.get_products()

            total_products = len(products)
            total_stock = sum(p["quantity"] for p in products)
            total_value = sum(p["quantity"] * p["unit_price"] for p in products)
            low_stock_count = len([p for p in products if p["quantity"] <= 5])

            self.total_products_label.setText(f"Total Products: {total_products}")
            self.total_stock_label.setText(f"Total Stock: {total_stock:,}")
            self.total_value_label.setText(f"Total Value: ₹{total_value:,.2f}")
            self.low_stock_items_label.setText(f"Low Stock Items: {low_stock_count}")

            # Set color for low stock warning
            if low_stock_count > 0:
                self.low_stock_items_label.setStyleSheet(
                    "font-size: 14px; font-weight: bold; padding: 10px; "
                    "background-color: #ffcccc; border-radius: 5px; color: red;"
                )
            else:
                self.low_stock_items_label.setStyleSheet(
                    "font-size: 14px; font-weight: bold; padding: 10px; "
                    "background-color: #ccffcc; border-radius: 5px; color: green;"
                )

        except Exception as e:
            QMessageBox.warning(
                self, "Warning", f"Error loading inventory data: {str(e)}"
            )

    def load_low_stock_data(self):
        """Load low stock data."""
        try:
            threshold = int(self.threshold_combo.currentText())
            low_stock_products = self.db.get_low_stock_products(threshold)

            self.low_stock_table.setRowCount(len(low_stock_products))

            for row, product in enumerate(low_stock_products):
                self.low_stock_table.setItem(row, 0, QTableWidgetItem(product["name"]))
                self.low_stock_table.setItem(
                    row, 1, QTableWidgetItem(product.get("category_name", ""))
                )

                # Highlight critical stock levels
                stock_item = QTableWidgetItem(str(product["quantity"]))
                if product["quantity"] == 0:
                    stock_item.setBackground(Qt.red)
                elif product["quantity"] <= 2:
                    stock_item.setBackground(Qt.yellow)
                self.low_stock_table.setItem(row, 2, stock_item)

                self.low_stock_table.setItem(
                    row, 3, QTableWidgetItem(f"₹{product['unit_price']:.2f}")
                )

                total_value = product["quantity"] * product["unit_price"]
                self.low_stock_table.setItem(
                    row, 4, QTableWidgetItem(f"₹{total_value:.2f}")
                )

        except Exception as e:
            QMessageBox.warning(
                self, "Warning", f"Error loading low stock data: {str(e)}"
            )

    def load_category_data(self):
        """Load category breakdown data."""
        try:
            categories = self.db.get_categories()
            products = self.db.get_products()

            # Group products by category
            category_stats = {}

            for product in products:
                category = product.get("category_name", "Uncategorized")
                if category not in category_stats:
                    category_stats[category] = {"count": 0, "quantity": 0, "value": 0}

                category_stats[category]["count"] += 1
                category_stats[category]["quantity"] += product["quantity"]
                category_stats[category]["value"] += (
                    product["quantity"] * product["unit_price"]
                )

            self.category_table.setRowCount(len(category_stats))

            for row, (category, stats) in enumerate(category_stats.items()):
                self.category_table.setItem(row, 0, QTableWidgetItem(category))
                self.category_table.setItem(
                    row, 1, QTableWidgetItem(str(stats["count"]))
                )
                self.category_table.setItem(
                    row, 2, QTableWidgetItem(f"{stats['quantity']:,}")
                )
                self.category_table.setItem(
                    row, 3, QTableWidgetItem(f"₹{stats['value']:,.2f}")
                )

        except Exception as e:
            QMessageBox.warning(
                self, "Warning", f"Error loading category data: {str(e)}"
            )

    def preview_report(self):
        """Preview the selected report."""
        try:
            report_type = self.report_type_combo.currentText()
            from_date = self.report_from_date.date().toString(Qt.ISODate)
            to_date = self.report_to_date.date().toString(Qt.ISODate)

            report_text = f"=== {report_type} ===\n"
            report_text += f"Period: {from_date} to {to_date}\n"
            report_text += (
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            if report_type == "Sales Report":
                summary = self.db.get_sales_summary(from_date, to_date)
                report_text += f"Total Invoices: {summary.get('invoice_count', 0)}\n"
                report_text += f"Total Sales: ₹{summary.get('total_sales', 0):,.2f}\n"
                report_text += (
                    f"Average Sale: ₹{summary.get('average_sale', 0):,.2f}\n\n"
                )

                report_text += "Top Selling Items:\n"
                for item in summary.get("top_items", [])[:10]:
                    report_text += f"- {item['description']}: {item['total_sold']:.3f} units, ₹{item['total_revenue']:,.2f}\n"

            elif report_type == "Inventory Report":
                products = self.db.get_products()
                total_value = sum(p["quantity"] * p["unit_price"] for p in products)

                report_text += f"Total Products: {len(products)}\n"
                report_text += f"Total Stock Value: ₹{total_value:,.2f}\n\n"

                report_text += "Products by Category:\n"
                category_stats = {}
                for product in products:
                    category = product.get("category_name", "Uncategorized")
                    if category not in category_stats:
                        category_stats[category] = {"count": 0, "value": 0}
                    category_stats[category]["count"] += 1
                    category_stats[category]["value"] += (
                        product["quantity"] * product["unit_price"]
                    )

                for category, stats in category_stats.items():
                    report_text += f"- {category}: {stats['count']} products, ₹{stats['value']:,.2f}\n"

            elif report_type == "Low Stock Report":
                threshold = int(self.threshold_combo.currentText())
                low_stock = self.db.get_low_stock_products(threshold)

                report_text += f"Products with stock <= {threshold}:\n\n"
                for product in low_stock:
                    report_text += f"- {product['name']}: {product['quantity']} units\n"

            else:
                report_text += "Report generation for this type is not yet implemented."

            self.report_preview.setPlainText(report_text)

        except Exception as e:
            QMessageBox.warning(
                self, "Warning", f"Error generating report preview: {str(e)}"
            )

    def export_report(self):
        """Export the current report to CSV."""
        try:
            report_type = self.report_type_combo.currentText()
            from_date = self.report_from_date.date().toString(Qt.ISODate)
            to_date = self.report_to_date.date().toString(Qt.ISODate)

            filename, _ = QFileDialog.getSaveFileName(
                self,
                f"Export {report_type}",
                f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)",
            )

            if filename:
                with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)

                    if report_type == "Sales Report":
                        summary = self.db.get_sales_summary(from_date, to_date)

                        # Write header
                        writer.writerow(
                            ["Sales Report", f"From: {from_date}", f"To: {to_date}"]
                        )
                        writer.writerow([])

                        # Write summary
                        writer.writerow(["Summary"])
                        writer.writerow(
                            ["Total Invoices", summary.get("invoice_count", 0)]
                        )
                        writer.writerow(
                            ["Total Sales", f"₹{summary.get('total_sales', 0):,.2f}"]
                        )
                        writer.writerow(
                            ["Average Sale", f"₹{summary.get('average_sale', 0):,.2f}"]
                        )
                        writer.writerow([])

                        # Write top items
                        writer.writerow(["Top Selling Items"])
                        writer.writerow(["Product", "Quantity Sold", "Total Revenue"])

                        for item in summary.get("top_items", []):
                            writer.writerow(
                                [
                                    item["description"],
                                    f"{item['total_sold']:.3f}",
                                    f"₹{item['total_revenue']:,.2f}",
                                ]
                            )

                    elif report_type == "Inventory Report":
                        products = self.db.get_products()

                        writer.writerow(
                            [
                                "Inventory Report",
                                f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                            ]
                        )
                        writer.writerow([])
                        writer.writerow(
                            [
                                "Product Name",
                                "Category",
                                "Quantity",
                                "Unit Price",
                                "Total Value",
                            ]
                        )

                        for product in products:
                            total_value = product["quantity"] * product["unit_price"]
                            writer.writerow(
                                [
                                    product["name"],
                                    product.get("category_name", ""),
                                    product["quantity"],
                                    f"₹{product['unit_price']:.2f}",
                                    f"₹{total_value:.2f}",
                                ]
                            )

                    elif report_type == "Low Stock Report":
                        threshold = int(self.threshold_combo.currentText())
                        low_stock = self.db.get_low_stock_products(threshold)

                        writer.writerow(
                            [
                                "Low Stock Report",
                                f"Threshold: {threshold}",
                                f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                            ]
                        )
                        writer.writerow([])
                        writer.writerow(
                            [
                                "Product Name",
                                "Category",
                                "Current Stock",
                                "Unit Price",
                                "Supplier",
                            ]
                        )

                        for product in low_stock:
                            writer.writerow(
                                [
                                    product["name"],
                                    product.get("category_name", ""),
                                    product["quantity"],
                                    f"₹{product['unit_price']:.2f}",
                                    product.get("supplier_name", ""),
                                ]
                            )

                QMessageBox.information(
                    self, "Success", f"Report exported to {filename}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting report: {str(e)}")
