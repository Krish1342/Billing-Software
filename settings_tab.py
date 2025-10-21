"""
Settings Tab for Unified Jewelry Management System

This module provides settings management functionality including
company information, tax settings, and application preferences.
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
    QGroupBox,
    QTextEdit,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QCheckBox,
    QDoubleSpinBox,
    QTabWidget,
    QFrame,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import json
import os

from unified_database import UnifiedDatabaseManager


class SettingsTab(QWidget):
    """Settings management tab widget."""

    # Signals
    settings_updated = pyqtSignal(dict)

    def __init__(
        self,
        db: UnifiedDatabaseManager,
        settings: dict,
        settings_path: str = "settings.json",
    ):
        super().__init__()

        self.db = db
        self.settings = settings.copy()
        self.settings_path = settings_path

        # Setup UI
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """Initialize the settings UI."""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("⚙️ Settings")
        header_label.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #9932CC; margin: 10px;")
        layout.addWidget(header_label)

        # Create tab widget for different settings sections
        self.tab_widget = QTabWidget()

        # Company settings tab
        self.create_company_settings_tab()

        # Tax settings tab
        self.create_tax_settings_tab()

        # Application settings tab
        self.create_app_settings_tab()

        # Database settings tab
        self.create_database_settings_tab()

        layout.addWidget(self.tab_widget)

        # Action buttons
        self.create_action_buttons(layout)

    def create_company_settings_tab(self):
        """Create company settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Company information group
        company_group = QGroupBox("Company Information")
        company_layout = QGridLayout(company_group)

        # Row 0: Company name
        company_layout.addWidget(QLabel("Company Name:"), 0, 0)
        self.company_name_edit = QLineEdit()
        company_layout.addWidget(self.company_name_edit, 0, 1, 1, 3)

        # Row 1: Address
        company_layout.addWidget(QLabel("Address:"), 1, 0)
        self.company_address_edit = QLineEdit()
        company_layout.addWidget(self.company_address_edit, 1, 1, 1, 3)

        # Row 2: City and State
        company_layout.addWidget(QLabel("City:"), 2, 0)
        self.company_city_edit = QLineEdit()
        company_layout.addWidget(self.company_city_edit, 2, 1)

        company_layout.addWidget(QLabel("State:"), 2, 2)
        self.company_state_edit = QLineEdit()
        company_layout.addWidget(self.company_state_edit, 2, 3)

        # Row 3: Pincode and GSTIN
        company_layout.addWidget(QLabel("Pincode:"), 3, 0)
        self.company_pincode_edit = QLineEdit()
        company_layout.addWidget(self.company_pincode_edit, 3, 1)

        company_layout.addWidget(QLabel("GSTIN:"), 3, 2)
        self.company_gstin_edit = QLineEdit()
        company_layout.addWidget(self.company_gstin_edit, 3, 3)

        # Row 4: Phone and Email
        company_layout.addWidget(QLabel("Phone:"), 4, 0)
        self.company_phone_edit = QLineEdit()
        company_layout.addWidget(self.company_phone_edit, 4, 1)

        company_layout.addWidget(QLabel("Email:"), 4, 2)
        self.company_email_edit = QLineEdit()
        company_layout.addWidget(self.company_email_edit, 4, 3)

        # Row 5: Logo path
        company_layout.addWidget(QLabel("Logo Path:"), 5, 0)
        self.company_logo_edit = QLineEdit()
        company_layout.addWidget(self.company_logo_edit, 5, 1, 1, 2)

        logo_browse_btn = QPushButton("Browse...")
        logo_browse_btn.clicked.connect(self.browse_logo)
        company_layout.addWidget(logo_browse_btn, 5, 3)

        layout.addWidget(company_group)

        # Bank details group
        bank_group = QGroupBox("Bank Details (Optional)")
        bank_layout = QGridLayout(bank_group)

        bank_layout.addWidget(QLabel("Bank Name:"), 0, 0)
        self.bank_name_edit = QLineEdit()
        bank_layout.addWidget(self.bank_name_edit, 0, 1)

        bank_layout.addWidget(QLabel("Account Number:"), 0, 2)
        self.bank_account_edit = QLineEdit()
        bank_layout.addWidget(self.bank_account_edit, 0, 3)

        bank_layout.addWidget(QLabel("IFSC Code:"), 1, 0)
        self.bank_ifsc_edit = QLineEdit()
        bank_layout.addWidget(self.bank_ifsc_edit, 1, 1)

        bank_layout.addWidget(QLabel("Branch:"), 1, 2)
        self.bank_branch_edit = QLineEdit()
        bank_layout.addWidget(self.bank_branch_edit, 1, 3)

        layout.addWidget(bank_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "🏢 Company")

    def create_tax_settings_tab(self):
        """Create tax settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Tax rates group
        tax_group = QGroupBox("Tax Rates")
        tax_layout = QGridLayout(tax_group)

        tax_layout.addWidget(QLabel("CGST Rate (%):"), 0, 0)
        self.cgst_rate_spin = QDoubleSpinBox()
        self.cgst_rate_spin.setDecimals(2)
        self.cgst_rate_spin.setRange(0.0, 50.0)
        self.cgst_rate_spin.setSuffix("%")
        tax_layout.addWidget(self.cgst_rate_spin, 0, 1)

        tax_layout.addWidget(QLabel("SGST Rate (%):"), 0, 2)
        self.sgst_rate_spin = QDoubleSpinBox()
        self.sgst_rate_spin.setDecimals(2)
        self.sgst_rate_spin.setRange(0.0, 50.0)
        self.sgst_rate_spin.setSuffix("%")
        tax_layout.addWidget(self.sgst_rate_spin, 0, 3)

        # Total tax display
        total_tax_layout = QHBoxLayout()
        total_tax_layout.addWidget(QLabel("Total Tax Rate:"))
        self.total_tax_label = QLabel("0.00%")
        self.total_tax_label.setStyleSheet("font-weight: bold; color: #2E8B57;")
        total_tax_layout.addWidget(self.total_tax_label)
        total_tax_layout.addStretch()

        tax_layout.addLayout(total_tax_layout, 1, 0, 1, 4)

        # Connect spinboxes to update total
        self.cgst_rate_spin.valueChanged.connect(self.update_total_tax)
        self.sgst_rate_spin.valueChanged.connect(self.update_total_tax)

        layout.addWidget(tax_group)

        # Tax calculation settings
        calc_group = QGroupBox("Tax Calculation Settings")
        calc_layout = QVBoxLayout(calc_group)

        self.tax_inclusive_check = QCheckBox("Prices are tax-inclusive by default")
        calc_layout.addWidget(self.tax_inclusive_check)

        self.round_to_nearest_check = QCheckBox("Round total to nearest rupee")
        calc_layout.addWidget(self.round_to_nearest_check)

        layout.addWidget(calc_group)

        # HSN codes group
        hsn_group = QGroupBox("Default HSN Codes")
        hsn_layout = QVBoxLayout(hsn_group)

        hsn_note = QLabel(
            "Add commonly used HSN codes for quick selection during invoice creation.\n"
            "Enter one HSN code per line with optional description."
        )
        hsn_note.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        hsn_layout.addWidget(hsn_note)

        self.hsn_codes_edit = QTextEdit()
        self.hsn_codes_edit.setPlaceholderText(
            "Example:\n"
            "71131910 - Gold Jewelry\n"
            "71131920 - Silver Jewelry\n"
            "71162000 - Articles of precious stones"
        )
        self.hsn_codes_edit.setMaximumHeight(150)
        hsn_layout.addWidget(self.hsn_codes_edit)

        layout.addWidget(hsn_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "💰 Tax Settings")

    def create_app_settings_tab(self):
        """Create application settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)

        self.auto_save_check = QCheckBox("Auto-save invoices as drafts")
        general_layout.addWidget(self.auto_save_check)

        self.backup_enabled_check = QCheckBox("Enable automatic database backups")
        general_layout.addWidget(self.backup_enabled_check)

        self.show_notifications_check = QCheckBox("Show notifications for low stock")
        general_layout.addWidget(self.show_notifications_check)

        self.confirm_delete_check = QCheckBox("Confirm before deleting items")
        general_layout.addWidget(self.confirm_delete_check)

        layout.addWidget(general_group)

        # Display settings group
        display_group = QGroupBox("Display Settings")
        display_layout = QGridLayout(display_group)

        display_layout.addWidget(QLabel("Theme:"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        display_layout.addWidget(self.theme_combo, 0, 1)

        display_layout.addWidget(QLabel("Font Size:"), 0, 2)
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Small", "Medium", "Large"])
        display_layout.addWidget(self.font_size_combo, 0, 3)

        display_layout.addWidget(QLabel("Currency Symbol:"), 1, 0)
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["₹", "$", "€", "£"])
        display_layout.addWidget(self.currency_combo, 1, 1)

        display_layout.addWidget(QLabel("Date Format:"), 1, 2)
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        display_layout.addWidget(self.date_format_combo, 1, 3)

        layout.addWidget(display_group)

        # Backup settings group
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QGridLayout(backup_group)

        backup_layout.addWidget(QLabel("Backup Frequency:"), 0, 0)
        self.backup_frequency_combo = QComboBox()
        self.backup_frequency_combo.addItems(["Daily", "Weekly", "Monthly"])
        backup_layout.addWidget(self.backup_frequency_combo, 0, 1)

        backup_layout.addWidget(QLabel("Backup Location:"), 1, 0)
        self.backup_location_edit = QLineEdit()
        backup_layout.addWidget(self.backup_location_edit, 1, 1, 1, 2)

        backup_browse_btn = QPushButton("Browse...")
        backup_browse_btn.clicked.connect(self.browse_backup_location)
        backup_layout.addWidget(backup_browse_btn, 1, 3)

        layout.addWidget(backup_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "⚙️ Application")

    def create_database_settings_tab(self):
        """Create database settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Database info group
        info_group = QGroupBox("Database Information")
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("Database Type:"), 0, 0)
        self.db_type_label = QLabel("SQLite")
        info_layout.addWidget(self.db_type_label, 0, 1)

        info_layout.addWidget(QLabel("Database File:"), 1, 0)
        self.db_file_label = QLabel(self.db.db_path)
        info_layout.addWidget(self.db_file_label, 1, 1, 1, 3)

        # Database stats
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()

                # Get table counts
                cursor.execute("SELECT COUNT(*) FROM products")
                product_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM categories")
                category_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM suppliers")
                supplier_count = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM invoices")
                invoice_count = cursor.fetchone()[0]

                info_layout.addWidget(QLabel("Products:"), 2, 0)
                info_layout.addWidget(QLabel(str(product_count)), 2, 1)

                info_layout.addWidget(QLabel("Categories:"), 2, 2)
                info_layout.addWidget(QLabel(str(category_count)), 2, 3)

                info_layout.addWidget(QLabel("Suppliers:"), 3, 0)
                info_layout.addWidget(QLabel(str(supplier_count)), 3, 1)

                info_layout.addWidget(QLabel("Invoices:"), 3, 2)
                info_layout.addWidget(QLabel(str(invoice_count)), 3, 3)

        except Exception as e:
            info_layout.addWidget(QLabel("Error loading stats:"), 2, 0)
            info_layout.addWidget(QLabel(str(e)), 2, 1, 1, 3)

        layout.addWidget(info_group)

        # Database operations group
        operations_group = QGroupBox("Database Operations")
        operations_layout = QVBoxLayout(operations_group)

        # Backup button
        backup_btn = QPushButton("🗄️ Create Database Backup")
        backup_btn.clicked.connect(self.backup_database)
        operations_layout.addWidget(backup_btn)

        # Restore button
        restore_btn = QPushButton("📥 Restore from Backup")
        restore_btn.clicked.connect(self.restore_database)
        operations_layout.addWidget(restore_btn)

        # Export button
        export_btn = QPushButton("📊 Export All Data to CSV")
        export_btn.clicked.connect(self.export_all_data)
        operations_layout.addWidget(export_btn)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        operations_layout.addWidget(separator)

        # Warning label
        warning_label = QLabel(
            "⚠️ Warning: The operations below are destructive and cannot be undone!"
        )
        warning_label.setStyleSheet("color: red; font-weight: bold; margin: 10px;")
        operations_layout.addWidget(warning_label)

        # Clear data button
        clear_btn = QPushButton("🗑️ Clear All Data")
        clear_btn.setStyleSheet("background-color: #dc3545; color: white;")
        clear_btn.clicked.connect(self.clear_all_data)
        operations_layout.addWidget(clear_btn)

        layout.addWidget(operations_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "🗄️ Database")

    def create_action_buttons(self, layout):
        """Create action buttons."""
        button_layout = QHBoxLayout()

        # Reset to defaults
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)

        button_layout.addStretch()

        # Cancel
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.load_current_settings)
        button_layout.addWidget(cancel_btn)

        # Save
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """
        )
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def load_current_settings(self):
        """Load current settings into the form."""
        try:
            # Company settings
            company = self.settings.get("company", {})
            self.company_name_edit.setText(company.get("name", ""))
            self.company_address_edit.setText(company.get("address", ""))
            self.company_city_edit.setText(company.get("city", ""))
            self.company_state_edit.setText(company.get("state", ""))
            self.company_pincode_edit.setText(company.get("pincode", ""))
            self.company_gstin_edit.setText(company.get("gstin", ""))
            self.company_phone_edit.setText(company.get("phone", ""))
            self.company_email_edit.setText(company.get("email", ""))
            self.company_logo_edit.setText(company.get("logo_path", ""))

            # Bank details
            bank = company.get("bank", {})
            self.bank_name_edit.setText(bank.get("name", ""))
            self.bank_account_edit.setText(bank.get("account_number", ""))
            self.bank_ifsc_edit.setText(bank.get("ifsc_code", ""))
            self.bank_branch_edit.setText(bank.get("branch", ""))

            # Tax settings
            tax = self.settings.get("tax", {})
            self.cgst_rate_spin.setValue(float(tax.get("cgst_rate", 1.5)))
            self.sgst_rate_spin.setValue(float(tax.get("sgst_rate", 1.5)))
            self.update_total_tax()

            # HSN codes
            hsn_codes = tax.get("default_hsn_codes", [])
            if hsn_codes:
                self.hsn_codes_edit.setPlainText("\n".join(hsn_codes))

            # App settings
            app = self.settings.get("app", {})
            self.auto_save_check.setChecked(app.get("auto_save", True))
            self.backup_enabled_check.setChecked(app.get("backup_enabled", True))
            self.show_notifications_check.setChecked(
                app.get("show_notifications", True)
            )
            self.confirm_delete_check.setChecked(app.get("confirm_delete", True))

            # Set combo box values
            theme = app.get("theme", "Light")
            self.theme_combo.setCurrentText(theme.title())

            font_size = app.get("font_size", "Medium")
            self.font_size_combo.setCurrentText(font_size.title())

            currency = app.get("currency_symbol", "₹")
            self.currency_combo.setCurrentText(currency)

            date_format = app.get("date_format", "DD/MM/YYYY")
            self.date_format_combo.setCurrentText(date_format)

            backup_frequency = app.get("backup_frequency", "Weekly")
            self.backup_frequency_combo.setCurrentText(backup_frequency)

            backup_location = app.get("backup_location", "")
            self.backup_location_edit.setText(backup_location)

        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Error loading settings: {str(e)}")

    def update_total_tax(self):
        """Update total tax rate display."""
        cgst = self.cgst_rate_spin.value()
        sgst = self.sgst_rate_spin.value()
        total = cgst + sgst
        self.total_tax_label.setText(f"{total:.2f}%")

    def browse_logo(self):
        """Browse for company logo."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Company Logo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)",
        )
        if filename:
            self.company_logo_edit.setText(filename)

    def browse_backup_location(self):
        """Browse for backup location."""
        directory = QFileDialog.getExistingDirectory(self, "Select Backup Directory")
        if directory:
            self.backup_location_edit.setText(directory)

    def save_settings(self):
        """Save settings to file."""
        try:
            # Update settings dictionary
            self.settings["company"] = {
                "name": self.company_name_edit.text().strip(),
                "address": self.company_address_edit.text().strip(),
                "city": self.company_city_edit.text().strip(),
                "state": self.company_state_edit.text().strip(),
                "pincode": self.company_pincode_edit.text().strip(),
                "gstin": self.company_gstin_edit.text().strip(),
                "phone": self.company_phone_edit.text().strip(),
                "email": self.company_email_edit.text().strip(),
                "logo_path": self.company_logo_edit.text().strip(),
                "bank": {
                    "name": self.bank_name_edit.text().strip(),
                    "account_number": self.bank_account_edit.text().strip(),
                    "ifsc_code": self.bank_ifsc_edit.text().strip(),
                    "branch": self.bank_branch_edit.text().strip(),
                },
            }

            # HSN codes
            hsn_text = self.hsn_codes_edit.toPlainText().strip()
            hsn_codes = [line.strip() for line in hsn_text.split("\n") if line.strip()]

            self.settings["tax"] = {
                "cgst_rate": str(self.cgst_rate_spin.value()),
                "sgst_rate": str(self.sgst_rate_spin.value()),
                "tax_inclusive": self.tax_inclusive_check.isChecked(),
                "round_to_nearest": self.round_to_nearest_check.isChecked(),
                "default_hsn_codes": hsn_codes,
            }

            self.settings["app"] = {
                "theme": self.theme_combo.currentText().lower(),
                "font_size": self.font_size_combo.currentText().lower(),
                "currency_symbol": self.currency_combo.currentText(),
                "date_format": self.date_format_combo.currentText(),
                "auto_save": self.auto_save_check.isChecked(),
                "backup_enabled": self.backup_enabled_check.isChecked(),
                "show_notifications": self.show_notifications_check.isChecked(),
                "confirm_delete": self.confirm_delete_check.isChecked(),
                "backup_frequency": self.backup_frequency_combo.currentText(),
                "backup_location": self.backup_location_edit.text().strip(),
            }

            # Save to file
            with open(self.settings_path, "w") as f:
                json.dump(self.settings, f, indent=4)

            QMessageBox.information(self, "Success", "Settings saved successfully!")

            # Emit signal
            self.settings_updated.emit(self.settings)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")

    def reset_to_defaults(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Default settings
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
                    "bank": {
                        "name": "",
                        "account_number": "",
                        "ifsc_code": "",
                        "branch": "",
                    },
                },
                "tax": {
                    "cgst_rate": "1.5",
                    "sgst_rate": "1.5",
                    "tax_inclusive": False,
                    "round_to_nearest": True,
                    "default_hsn_codes": [],
                },
                "app": {
                    "theme": "light",
                    "font_size": "medium",
                    "currency_symbol": "₹",
                    "date_format": "DD/MM/YYYY",
                    "auto_save": True,
                    "backup_enabled": True,
                    "show_notifications": True,
                    "confirm_delete": True,
                    "backup_frequency": "Weekly",
                    "backup_location": "",
                },
            }

            self.load_current_settings()

    def backup_database(self):
        """Create database backup."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Database Backup",
                f"jewelry_shop_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                "SQLite Database (*.db)",
            )

            if filename:
                import shutil

                shutil.copy2(self.db.db_path, filename)
                QMessageBox.information(
                    self, "Success", f"Database backed up to {filename}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating backup: {str(e)}")

    def restore_database(self):
        """Restore database from backup."""
        reply = QMessageBox.warning(
            self,
            "Restore Database",
            "This will replace the current database with the backup. All current data will be lost!\n\nAre you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                filename, _ = QFileDialog.getOpenFileName(
                    self, "Select Database Backup", "", "SQLite Database (*.db)"
                )

                if filename:
                    import shutil

                    # Close current database connection
                    # self.db.close()  # Implement if needed

                    # Replace database file
                    shutil.copy2(filename, self.db.db_path)

                    QMessageBox.information(
                        self,
                        "Success",
                        "Database restored successfully!\nPlease restart the application.",
                    )

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Error restoring database: {str(e)}"
                )

    def export_all_data(self):
        """Export all data to CSV files."""
        try:
            directory = QFileDialog.getExistingDirectory(
                self, "Select Export Directory"
            )

            if directory:
                from datetime import datetime
                import csv
                import os

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Export products
                products = self.db.get_products()
                with open(
                    os.path.join(directory, f"products_{timestamp}.csv"),
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as f:
                    writer = csv.writer(f)
                    writer.writerow(
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
                        ]
                    )
                    for product in products:
                        writer.writerow(
                            [
                                product["id"],
                                product["name"],
                                product.get("description", ""),
                                product.get("category_name", ""),
                                product["gross_weight"],
                                product["net_weight"],
                                product["quantity"],
                                product["unit_price"],
                                product.get("supplier_name", ""),
                            ]
                        )

                # Export categories
                categories = self.db.get_categories()
                with open(
                    os.path.join(directory, f"categories_{timestamp}.csv"),
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as f:
                    writer = csv.writer(f)
                    writer.writerow(["ID", "Name", "Description"])
                    for category in categories:
                        writer.writerow(
                            [
                                category["id"],
                                category["name"],
                                category.get("description", ""),
                            ]
                        )

                # Export suppliers
                suppliers = self.db.get_suppliers()
                with open(
                    os.path.join(directory, f"suppliers_{timestamp}.csv"),
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "ID",
                            "Name",
                            "Code",
                            "Contact Person",
                            "Phone",
                            "Email",
                            "Address",
                        ]
                    )
                    for supplier in suppliers:
                        writer.writerow(
                            [
                                supplier["id"],
                                supplier["name"],
                                supplier["code"],
                                supplier.get("contact_person", ""),
                                supplier.get("phone", ""),
                                supplier.get("email", ""),
                                supplier.get("address", ""),
                            ]
                        )

                # Export invoices
                invoices = self.db.get_invoices(1000)  # Get more invoices for export
                with open(
                    os.path.join(directory, f"invoices_{timestamp}.csv"),
                    "w",
                    newline="",
                    encoding="utf-8",
                ) as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "ID",
                            "Invoice Number",
                            "Customer Name",
                            "Date",
                            "Subtotal",
                            "CGST",
                            "SGST",
                            "Total Amount",
                        ]
                    )
                    for invoice in invoices:
                        writer.writerow(
                            [
                                invoice["id"],
                                invoice["invoice_number"],
                                invoice["customer_name"],
                                invoice["invoice_date"],
                                invoice["subtotal"],
                                invoice["cgst_amount"],
                                invoice["sgst_amount"],
                                invoice["total_amount"],
                            ]
                        )

                QMessageBox.information(
                    self, "Success", f"All data exported to {directory}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting data: {str(e)}")

    def clear_all_data(self):
        """Clear all data from database."""
        reply = QMessageBox.warning(
            self,
            "Clear All Data",
            "⚠️ WARNING: This will permanently delete ALL data from the database!\n\n"
            "This includes:\n"
            "• All products and inventory\n"
            "• All invoices and sales records\n"
            "• All customers and suppliers\n"
            "• All categories and history\n\n"
            "This action CANNOT be undone!\n\n"
            "Are you absolutely sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Second confirmation
            reply2 = QMessageBox.critical(
                self,
                "Final Confirmation",
                "This is your final warning!\n\n"
                "All data will be permanently lost.\n"
                "Type 'DELETE ALL' in the next dialog to confirm.",
                QMessageBox.Ok | QMessageBox.Cancel,
            )

            if reply2 == QMessageBox.Ok:
                from PyQt5.QtWidgets import QInputDialog

                text, ok = QInputDialog.getText(
                    self, "Final Confirmation", "Type 'DELETE ALL' to confirm:"
                )

                if ok and text == "DELETE ALL":
                    try:
                        with self.db.get_connection() as conn:
                            cursor = conn.cursor()

                            # Drop and recreate all tables
                            tables = [
                                "invoice_items",
                                "invoices",
                                "stock_movements",
                                "products",
                                "customers",
                                "suppliers",
                                "categories",
                                "history",
                            ]

                            for table in tables:
                                cursor.execute(f"DELETE FROM {table}")

                            conn.commit()

                        QMessageBox.information(
                            self,
                            "Data Cleared",
                            "All data has been permanently deleted from the database.",
                        )

                    except Exception as e:
                        QMessageBox.critical(
                            self, "Error", f"Error clearing data: {str(e)}"
                        )
                else:
                    QMessageBox.information(
                        self, "Cancelled", "Operation cancelled. No data was deleted."
                    )
