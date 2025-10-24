"""
PyQt + Supabase Integration Examples for Jewelry Management System
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Dict
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QMessageBox, QComboBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QDoubleSpinBox
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseRealtimeWorker(QThread):
    """Background worker for Supabase realtime updates."""
    
    inventory_updated = pyqtSignal(dict)
    
    def __init__(self, supabase_client: Client):
        super().__init__()
        self.supabase = supabase_client
        self.running = True
    
    def run(self):
        """Poll for inventory changes (realtime alternative)."""
        while self.running:
            try:
                # Get current stock summary
                result = self.supabase.table('total_summary_view').select('*').execute()
                if result.data:
                    self.inventory_updated.emit(result.data[0])
                
                self.msleep(5000)  # Poll every 5 seconds
            except Exception as e:
                print(f"Realtime polling error: {e}")
                self.msleep(10000)  # Wait longer on error
    
    def stop(self):
        """Stop the worker."""
        self.running = False


class BillCreationExample(QWidget):
    """Example widget for creating bills via Supabase RPC."""
    
    def __init__(self, supabase_client: Client):
        super().__init__()
        self.supabase = supabase_client
        self.init_ui()
        self.load_available_items()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Customer info
        layout.addWidget(QLabel("Customer Name:"))
        self.customer_name_edit = QLineEdit()
        layout.addWidget(self.customer_name_edit)
        
        layout.addWidget(QLabel("Customer Phone:"))
        self.customer_phone_edit = QLineEdit()
        layout.addWidget(self.customer_phone_edit)
        
        # Item selection
        layout.addWidget(QLabel("Select Item:"))
        self.item_combo = QComboBox()
        layout.addWidget(self.item_combo)
        
        layout.addWidget(QLabel("Rate (₹):"))
        self.rate_spin = QDoubleSpinBox()
        self.rate_spin.setMaximum(999999.99)
        layout.addWidget(self.rate_spin)
        
        # Create bill button
        self.create_bill_btn = QPushButton("Create Bill")
        self.create_bill_btn.clicked.connect(self.create_bill)
        layout.addWidget(self.create_bill_btn)
        
        # Status display
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)
    
    def load_available_items(self):
        """Load available inventory items."""
        try:
            result = self.supabase.table('current_stock_view').select('*').limit(50).execute()
            
            self.item_combo.clear()
            self.items = {}
            
            for item in result.data or []:
                display_name = f"{item['category_name']} #{item['category_item_no']} - {item['product_name']}"
                self.item_combo.addItem(display_name)
                self.items[display_name] = item
                
        except Exception as e:
            self.status_text.append(f"Error loading items: {e}")
    
    def create_bill(self):
        """Create a bill via Supabase RPC."""
        try:
            # Validate inputs
            customer_name = self.customer_name_edit.text().strip()
            if not customer_name:
                QMessageBox.warning(self, "Error", "Please enter customer name")
                return
            
            selected_item_name = self.item_combo.currentText()
            if not selected_item_name or selected_item_name not in self.items:
                QMessageBox.warning(self, "Error", "Please select an item")
                return
            
            rate = self.rate_spin.value()
            if rate <= 0:
                QMessageBox.warning(self, "Error", "Please enter a valid rate")
                return
            
            # Get item details
            item = self.items[selected_item_name]
            
            # Generate bill number
            bill_number = f"RK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare items array
            items = [{
                'inventory_id': item['id'],
                'product_name': item['product_name'],
                'description': item.get('description', ''),
                'hsn_code': item.get('hsn_code', ''),
                'quantity': 1,
                'rate': rate,
                'amount': rate
            }]
            
            # Create bill using RPC
            result = self.supabase.rpc('create_bill_with_items', {
                'p_bill_number': bill_number,
                'p_customer_name': customer_name,
                'p_items': items,  # Pass as Python list, not JSON string
                'p_customer_phone': self.customer_phone_edit.text().strip() or None,
                'p_customer_gstin': None,
                'p_bill_date': datetime.now().strftime('%Y-%m-%d'),
                'p_cgst_rate': 1.5,
                'p_sgst_rate': 1.5
            }).execute()
            
            bill_id = result.data
            
            # Get created bill details
            bill_result = self.supabase.table('bills').select('*').eq('id', bill_id).execute()
            bill = bill_result.data[0]
            
            # Display success message
            success_msg = f"""✅ Bill Created Successfully!
            
Bill Number: {bill['bill_number']}
Customer: {bill['customer_name']}
Total Amount: ₹{bill['total_amount']}
CGST: ₹{bill['cgst_amount']}
SGST: ₹{bill['sgst_amount']}

Item sold: {item['category_name']} #{item['category_item_no']}
This item is now marked as SOLD and removed from available inventory.
"""
            
            self.status_text.append(success_msg)
            QMessageBox.information(self, "Success", f"Bill {bill['bill_number']} created successfully!")
            
            # Refresh available items
            self.load_available_items()
            
            # Clear form
            self.customer_name_edit.clear()
            self.customer_phone_edit.clear()
            self.rate_spin.setValue(0)
            
        except Exception as e:
            error_msg = f"❌ Error creating bill: {e}"
            self.status_text.append(error_msg)
            QMessageBox.critical(self, "Error", str(e))


class CategoryCSVExporter(QWidget):
    """Example widget for downloading category CSV data."""
    
    def __init__(self, supabase_client: Client):
        super().__init__()
        self.supabase = supabase_client
        self.init_ui()
        self.load_categories()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Export Category Data to CSV"))
        
        # Category selection
        layout.addWidget(QLabel("Select Category:"))
        self.category_combo = QComboBox()
        layout.addWidget(self.category_combo)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_category_btn = QPushButton("Export Selected Category")
        self.export_category_btn.clicked.connect(self.export_category_csv)
        export_layout.addWidget(self.export_category_btn)
        
        self.export_summary_btn = QPushButton("Export All Categories Summary")
        self.export_summary_btn.clicked.connect(self.export_summary_csv)
        export_layout.addWidget(self.export_summary_btn)
        
        layout.addLayout(export_layout)
        
        # Status display
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)
    
    def load_categories(self):
        """Load categories for selection."""
        try:
            result = self.supabase.table('categories').select('*').order('name').execute()
            
            self.category_combo.clear()
            self.categories = {}
            
            for category in result.data or []:
                self.category_combo.addItem(category['name'])
                self.categories[category['name']] = category['id']
                
        except Exception as e:
            self.status_text.append(f"Error loading categories: {e}")
    
    def export_category_csv(self):
        """Export selected category data to CSV."""
        try:
            category_name = self.category_combo.currentText()
            if not category_name:
                QMessageBox.warning(self, "Error", "Please select a category")
                return
            
            category_id = self.categories[category_name]
            
            # Get CSV data using RPC
            result = self.supabase.rpc('get_category_csv_data', {
                'p_category_id': category_id
            }).execute()
            
            if not result.data:
                QMessageBox.information(self, "No Data", f"No items found in category '{category_name}'")
                return
            
            # Save file dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                f"Export {category_name} Category Data",
                f"{category_name.lower()}_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                # Write CSV file
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        'Category Item No', 'Product Name', 'Gross Weight (g)', 
                        'Net Weight (g)', 'Supplier Code', 'Added At'
                    ])
                    
                    # Write data
                    for item in result.data:
                        writer.writerow([
                            item['category_item_no'],
                            item['product_name'],
                            f"{item['gross_weight']:.3f}",
                            f"{item['net_weight']:.3f}",
                            item['supplier_code'],
                            item['added_at']
                        ])
                
                success_msg = f"✅ Exported {len(result.data)} items from '{category_name}' to {filename}"
                self.status_text.append(success_msg)
                QMessageBox.information(self, "Success", f"Category data exported to {filename}")
            
        except Exception as e:
            error_msg = f"❌ Error exporting category CSV: {e}"
            self.status_text.append(error_msg)
            QMessageBox.critical(self, "Error", str(e))
    
    def export_summary_csv(self):
        """Export summary of all categories to CSV."""
        try:
            # Get summary data using RPC
            result = self.supabase.rpc('get_summary_csv_data').execute()
            
            if not result.data:
                QMessageBox.information(self, "No Data", "No summary data available")
                return
            
            # Save file dialog
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Categories Summary",
                f"categories_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV Files (*.csv)"
            )
            
            if filename:
                # Write CSV file
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        'Category Name', 'Total Items', 'Available Items', 
                        'Sold Items', 'Available Gross Weight (g)', 'Available Net Weight (g)'
                    ])
                    
                    # Write data
                    total_items = 0
                    total_available = 0
                    total_sold = 0
                    total_gross_weight = 0
                    total_net_weight = 0
                    
                    for category in result.data:
                        writer.writerow([
                            category['category_name'],
                            category['total_items'],
                            category['available_items'],
                            category['sold_items'],
                            f"{category['available_gross_weight']:.3f}",
                            f"{category['available_net_weight']:.3f}"
                        ])
                        
                        total_items += category['total_items']
                        total_available += category['available_items']
                        total_sold += category['sold_items']
                        total_gross_weight += float(category['available_gross_weight'])
                        total_net_weight += float(category['available_net_weight'])
                    
                    # Write totals row
                    writer.writerow([])
                    writer.writerow([
                        'TOTAL', total_items, total_available, total_sold,
                        f"{total_gross_weight:.3f}", f"{total_net_weight:.3f}"
                    ])
                
                success_msg = f"✅ Exported summary for {len(result.data)} categories to {filename}"
                self.status_text.append(success_msg)
                QMessageBox.information(self, "Success", f"Summary data exported to {filename}")
            
        except Exception as e:
            error_msg = f"❌ Error exporting summary CSV: {e}"
            self.status_text.append(error_msg)
            QMessageBox.critical(self, "Error", str(e))


class InventoryRealtimeWidget(QWidget):
    """Example widget showing realtime inventory updates."""
    
    def __init__(self, supabase_client: Client):
        super().__init__()
        self.supabase = supabase_client
        self.init_ui()
        self.setup_realtime()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 Live Inventory Summary"))
        
        # Summary labels
        self.total_items_label = QLabel("Total Items: Loading...")
        self.available_items_label = QLabel("Available Items: Loading...")
        self.sold_items_label = QLabel("Sold Items: Loading...")
        self.total_weight_label = QLabel("Total Weight: Loading...")
        
        for label in [self.total_items_label, self.available_items_label, 
                     self.sold_items_label, self.total_weight_label]:
            label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 5px;")
            layout.addWidget(label)
        
        # Manual refresh button
        refresh_btn = QPushButton("🔄 Refresh Now")
        refresh_btn.clicked.connect(self.refresh_summary)
        layout.addWidget(refresh_btn)
        
        # Activity log
        layout.addWidget(QLabel("Recent Activity:"))
        self.activity_log = QTextEdit()
        self.activity_log.setMaximumHeight(200)
        layout.addWidget(self.activity_log)
        
        self.setLayout(layout)
        
        # Initial refresh
        self.refresh_summary()
    
    def setup_realtime(self):
        """Setup realtime updates (using polling as alternative to Supabase realtime)."""
        # Start background worker for realtime updates
        self.realtime_worker = SupabaseRealtimeWorker(self.supabase)
        self.realtime_worker.inventory_updated.connect(self.on_inventory_updated)
        self.realtime_worker.start()
        
        # Also use a timer for periodic refresh
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_summary)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def refresh_summary(self):
        """Refresh inventory summary."""
        try:
            result = self.supabase.table('total_summary_view').select('*').execute()
            if result.data:
                self.on_inventory_updated(result.data[0])
        except Exception as e:
            self.activity_log.append(f"❌ Error refreshing: {e}")
    
    def on_inventory_updated(self, summary: Dict):
        """Handle inventory update."""
        try:
            total_items = summary.get('total_available_items', 0) + summary.get('total_sold_items', 0)
            available_items = summary.get('total_available_items', 0)
            sold_items = summary.get('total_sold_items', 0)
            total_weight = float(summary.get('total_available_net_weight', 0))
            
            self.total_items_label.setText(f"Total Items: {total_items}")
            self.available_items_label.setText(f"Available Items: {available_items}")
            self.sold_items_label.setText(f"Sold Items: {sold_items}")
            self.total_weight_label.setText(f"Available Weight: {total_weight:.3f}g")
            
            # Log update
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.activity_log.append(f"[{timestamp}] Updated: {available_items} available, {sold_items} sold")
            
        except Exception as e:
            self.activity_log.append(f"❌ Error updating display: {e}")
    
    def closeEvent(self, event):
        """Clean up when widget is closed."""
        if hasattr(self, 'realtime_worker'):
            self.realtime_worker.stop()
            self.realtime_worker.wait()
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        event.accept()


class SupabaseExampleApp(QMainWindow):
    """Main example application demonstrating Supabase integration."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize Supabase client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        
        if not url or not key:
            QMessageBox.critical(self, "Configuration Error", 
                               "Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
            return
        
        self.supabase = create_client(url, key)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main UI."""
        self.setWindowTitle("Supabase PyQt Integration Examples")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Bill creation example
        bill_widget = BillCreationExample(self.supabase)
        layout.addWidget(bill_widget)
        
        # CSV export example
        csv_widget = CategoryCSVExporter(self.supabase)
        layout.addWidget(csv_widget)
        
        # Realtime inventory widget
        realtime_widget = InventoryRealtimeWidget(self.supabase)
        layout.addWidget(realtime_widget)


if __name__ == "__main__":
    app = QApplication([])
    window = SupabaseExampleApp()
    window.show()
    app.exec_()