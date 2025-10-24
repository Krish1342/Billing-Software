"""
Local SQLite Database Manager for Offline Operation
Provides the same interface as SupabaseDatabaseManager but uses local SQLite
"""

import sqlite3
import json
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Union, Any
from pathlib import Path


class LocalDatabaseManager:
    """Local SQLite database manager for offline operation."""

    def __init__(self, db_path: str = "jewelry_management.db"):
        """Initialize SQLite database."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")

        # Create tables
        schema_sql = """
        -- Categories table
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Suppliers table
        CREATE TABLE IF NOT EXISTS suppliers (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Inventory table (serialized items)
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            category_id TEXT NOT NULL REFERENCES categories(id),
            category_item_no INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            description TEXT,
            hsn_code TEXT,
            gross_weight DECIMAL(10,3) NOT NULL CHECK (gross_weight > 0),
            net_weight DECIMAL(10,3) NOT NULL CHECK (net_weight > 0 AND net_weight <= gross_weight),
            supplier_id TEXT REFERENCES suppliers(id),
            melting_percentage DECIMAL(5,2) DEFAULT 0.00,
            status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'SOLD', 'RESERVED')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(category_id, category_item_no)
        );

        -- Customers table
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            address TEXT,
            gstin TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Bills table
        CREATE TABLE IF NOT EXISTS bills (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            bill_number TEXT UNIQUE NOT NULL,
            customer_id TEXT REFERENCES customers(id),
            customer_name TEXT NOT NULL,
            customer_phone TEXT,
            customer_gstin TEXT,
            bill_date DATE NOT NULL DEFAULT (date('now')),
            subtotal DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            cgst_rate DECIMAL(5,2) NOT NULL DEFAULT 1.50,
            sgst_rate DECIMAL(5,2) NOT NULL DEFAULT 1.50,
            cgst_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            sgst_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            rounded_off DECIMAL(12,2) NOT NULL DEFAULT 0.00,
            status TEXT NOT NULL DEFAULT 'GENERATED' CHECK (status IN ('GENERATED', 'REVERSED')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Bill items table
        CREATE TABLE IF NOT EXISTS bill_items (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            bill_id TEXT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
            inventory_id TEXT REFERENCES inventory(id),
            product_name TEXT NOT NULL,
            description TEXT,
            hsn_code TEXT,
            quantity DECIMAL(10,3) NOT NULL DEFAULT 1.000,
            rate DECIMAL(12,2) NOT NULL,
            amount DECIMAL(12,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Stock movements table
        CREATE TABLE IF NOT EXISTS stock_movements (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            inventory_id TEXT REFERENCES inventory(id),
            movement_type TEXT NOT NULL CHECK (movement_type IN ('ADDED', 'SOLD', 'REVERSED', 'ADJUSTED')),
            reference_id TEXT,
            reference_type TEXT,
            quantity DECIMAL(10,3) NOT NULL DEFAULT 1.000,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Indexes
        CREATE INDEX IF NOT EXISTS idx_inventory_category_status ON inventory(category_id, status);
        CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory(status);
        CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id);
        CREATE INDEX IF NOT EXISTS idx_bill_items_inventory_id ON bill_items(inventory_id);
        CREATE INDEX IF NOT EXISTS idx_stock_movements_inventory_id ON stock_movements(inventory_id);

        -- Triggers for updated_at
        CREATE TRIGGER IF NOT EXISTS update_categories_updated_at 
            AFTER UPDATE ON categories FOR EACH ROW 
            BEGIN 
                UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
            END;

        CREATE TRIGGER IF NOT EXISTS update_suppliers_updated_at 
            AFTER UPDATE ON suppliers FOR EACH ROW 
            BEGIN 
                UPDATE suppliers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
            END;

        CREATE TRIGGER IF NOT EXISTS update_inventory_updated_at 
            AFTER UPDATE ON inventory FOR EACH ROW 
            BEGIN 
                UPDATE inventory SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
            END;

        CREATE TRIGGER IF NOT EXISTS update_customers_updated_at 
            AFTER UPDATE ON customers FOR EACH ROW 
            BEGIN 
                UPDATE customers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
            END;

        CREATE TRIGGER IF NOT EXISTS update_bills_updated_at 
            AFTER UPDATE ON bills FOR EACH ROW 
            BEGIN 
                UPDATE bills SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id; 
            END;
        """

        conn.executescript(schema_sql)
        conn.commit()
        conn.close()

        # Add sample data if database is empty
        self._add_sample_data()

    def _add_sample_data(self):
        """Add sample data if database is empty."""
        conn = sqlite3.connect(self.db_path)

        # Check if categories exist
        cursor = conn.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            # Add sample categories
            categories = [
                ("Ring", "Gold and silver rings"),
                ("Chain", "Gold and silver chains"),
                ("Necklace", "Traditional and modern necklaces"),
                ("Earrings", "Stud and drop earrings"),
                ("Bangles", "Gold and silver bangles"),
            ]

            conn.executemany(
                "INSERT INTO categories (name, description) VALUES (?, ?)", categories
            )

            # Add sample suppliers
            suppliers = [
                (
                    "Golden Crafts Ltd",
                    "GCL001",
                    "Rajesh Kumar",
                    "+91-9876543210",
                    "rajesh@goldencrafts.com",
                ),
                (
                    "Silver Palace",
                    "SP002",
                    "Priya Sharma",
                    "+91-9876543211",
                    "priya@silverpalace.com",
                ),
            ]

            conn.executemany(
                "INSERT INTO suppliers (name, code, contact_person, phone, email) VALUES (?, ?, ?, ?, ?)",
                suppliers,
            )

            conn.commit()

        conn.close()

    def close(self):
        """Close database connection."""
        pass  # SQLite connections are opened per operation

    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    # Categories
    def get_categories(self) -> List[Dict]:
        """Get all categories."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM categories ORDER BY name")
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories

    def add_category(self, name: str, description: str = None) -> str:
        """Add a new category."""
        category_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO categories (id, name, description) VALUES (?, ?, ?)",
            (category_id, name, description),
        )
        conn.commit()
        conn.close()
        return category_id

    # Suppliers
    def get_suppliers(self) -> List[Dict]:
        """Get all suppliers."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM suppliers ORDER BY name")
        suppliers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return suppliers

    def add_supplier(
        self,
        name: str,
        code: str,
        contact_person: str = None,
        phone: str = None,
        email: str = None,
        address: str = None,
    ) -> str:
        """Add a new supplier."""
        supplier_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO suppliers (id, name, code, contact_person, phone, email, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (supplier_id, name, code, contact_person, phone, email, address),
        )
        conn.commit()
        conn.close()
        return supplier_id

    # Products (Inventory)
    def get_products(self) -> List[Dict]:
        """Get all inventory items formatted as products."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT i.*, c.name as category_name, s.name as supplier_name, s.code as supplier_code
            FROM inventory i
            JOIN categories c ON i.category_id = c.id
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.status = 'AVAILABLE'
            ORDER BY c.name, i.category_item_no
        """
        )

        products = []
        for row in cursor.fetchall():
            products.append(
                {
                    "id": row["id"],
                    "name": row["product_name"],
                    "description": row["description"] or "",
                    "category_id": row["category_id"],
                    "category_name": row["category_name"],
                    "category_item_id": row["category_item_no"],
                    "hsn_code": row["hsn_code"] or "",
                    "gross_weight": float(row["gross_weight"]),
                    "net_weight": float(row["net_weight"]),
                    "quantity": 1,
                    "unit_price": 0.0,  # Default value for UI compatibility
                    "supplier_id": row["supplier_id"],
                    "supplier_name": row["supplier_name"] or "",
                    "supplier_code": row["supplier_code"] or "",
                    "melting_percentage": float(row["melting_percentage"] or 0),
                    "status": row["status"],
                    "created_at": row["created_at"],
                }
            )

        conn.close()
        return products

    def add_product(
        self,
        name: str,
        description: str = None,
        hsn_code: str = None,
        gross_weight: float = 0,
        net_weight: float = 0,
        quantity: int = 1,
        supplier_id: str = None,
        category_id: str = None,
        melting_percentage: float = 0,
        **kwargs,
    ) -> str:
        """Add inventory items."""
        conn = sqlite3.connect(self.db_path)
        last_item_id = None

        for i in range(quantity):
            # Get next category item number
            cursor = conn.execute(
                "SELECT COALESCE(MAX(category_item_no), 0) + 1 FROM inventory WHERE category_id = ?",
                (category_id,),
            )
            category_item_no = cursor.fetchone()[0]

            item_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO inventory (id, category_id, category_item_no, product_name, description, 
                                     hsn_code, gross_weight, net_weight, supplier_id, melting_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    category_id,
                    category_item_no,
                    name,
                    description,
                    hsn_code,
                    gross_weight,
                    net_weight,
                    supplier_id,
                    melting_percentage,
                ),
            )

            # Add stock movement
            movement_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO stock_movements (id, inventory_id, movement_type, quantity, notes)
                VALUES (?, ?, 'ADDED', 1.0, 'Initial inventory addition')
            """,
                (movement_id, item_id),
            )

            last_item_id = item_id

        conn.commit()
        conn.close()
        return last_item_id

    # Additional methods to match SupabaseDatabaseManager interface
    @property
    def db_path(self) -> str:
        """Return database path."""
        return f"Local SQLite Database: {self.db_path}"

    def get_next_invoice_number(self) -> str:
        """Get next invoice number."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT bill_number FROM bills ORDER BY created_at DESC LIMIT 1"
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            last_bill = result[0]
            try:
                parts = last_bill.split("-")
                if len(parts) >= 3:
                    prefix = "-".join(parts[:-1])
                    number = int(parts[-1]) + 1
                    return f"{prefix}-{number:03d}"
            except:
                pass

        # Default format
        current_year = datetime.now().year
        return f"RK-{current_year}-001"

    def get_sales_summary(self, from_date: str = None, to_date: str = None) -> Dict:
        """Get sales summary."""
        conn = sqlite3.connect(self.db_path)

        query = "SELECT * FROM bills WHERE status = 'GENERATED'"
        params = []

        if from_date:
            query += " AND bill_date >= ?"
            params.append(from_date)
        if to_date:
            query += " AND bill_date <= ?"
            params.append(to_date)

        cursor = conn.execute(query, params)
        bills = cursor.fetchall()

        total_sales = sum(float(bill[10]) for bill in bills)  # total_amount column
        total_bills = len(bills)

        # Get item count
        if bills:
            bill_ids = [bill[0] for bill in bills]
            placeholders = ",".join("?" * len(bill_ids))
            cursor = conn.execute(
                f"SELECT COUNT(*) FROM bill_items WHERE bill_id IN ({placeholders})",
                bill_ids,
            )
            total_items = cursor.fetchone()[0]
        else:
            total_items = 0

        conn.close()

        return {
            "total_sales": total_sales,
            "total_invoices": total_bills,
            "total_items_sold": total_items,
            "average_invoice_value": (
                total_sales / total_bills if total_bills > 0 else 0
            ),
        }

    def get_low_stock_products(self, threshold: int = 5) -> List[Dict]:
        """Get categories with low stock."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            """
            SELECT 
                c.id as category_id,
                c.name as category_name,
                COUNT(CASE WHEN i.status = 'AVAILABLE' THEN 1 END) as available_items,
                COUNT(i.id) as total_items,
                COUNT(CASE WHEN i.status = 'SOLD' THEN 1 END) as sold_items,
                COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.gross_weight END), 0) as available_gross_weight,
                COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.net_weight END), 0) as available_net_weight
            FROM categories c
            LEFT JOIN inventory i ON c.id = i.category_id
            GROUP BY c.id, c.name
            HAVING available_items <= ?
            ORDER BY c.name
        """,
            (threshold,),
        )

        low_stock = []
        for row in cursor.fetchall():
            low_stock.append(
                {
                    "id": row["category_id"],
                    "name": row["category_name"],
                    "category_name": row["category_name"],
                    "quantity": row["available_items"],
                    "available_quantity": row["available_items"],
                    "unit_price": 0.0,
                    "available_gross_weight": float(row["available_gross_weight"]),
                    "available_net_weight": float(row["available_net_weight"]),
                    "total_items": row["total_items"],
                    "sold_items": row["sold_items"],
                }
            )

        conn.close()
        return low_stock

    def generate_invoice_with_stock_deduction(
        self, invoice_data: Dict, line_items: List[Dict]
    ) -> tuple:
        """Generate invoice with stock deduction."""
        conn = sqlite3.connect(self.db_path)

        try:
            warnings = []

            # Create bill
            bill_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO bills (id, bill_number, customer_name, customer_phone, customer_gstin,
                                 bill_date, subtotal, cgst_rate, sgst_rate, cgst_amount, sgst_amount,
                                 total_amount, rounded_off)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    bill_id,
                    invoice_data["invoice_number"],
                    invoice_data["customer_name"],
                    invoice_data.get("customer_phone"),
                    invoice_data.get("customer_gstin"),
                    invoice_data.get("invoice_date", str(date.today())),
                    invoice_data.get("subtotal", 0),
                    invoice_data.get("cgst_rate", 1.5),
                    invoice_data.get("sgst_rate", 1.5),
                    invoice_data.get("cgst_amount", 0),
                    invoice_data.get("sgst_amount", 0),
                    invoice_data.get("total_amount", 0),
                    invoice_data.get("rounded_off", 0),
                ),
            )

            # Process line items
            for item in line_items:
                item_id = str(uuid.uuid4())
                product_id = item.get("product_id")

                # Add bill item
                conn.execute(
                    """
                    INSERT INTO bill_items (id, bill_id, inventory_id, product_name, description,
                                          hsn_code, quantity, rate, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item_id,
                        bill_id,
                        product_id,
                        item.get("name", ""),
                        item.get("description", ""),
                        item.get("hsn_code", ""),
                        item.get("quantity", 1),
                        item.get("rate", 0),
                        item.get("amount", 0),
                    ),
                )

                # Update inventory status if linked to product
                if product_id:
                    cursor = conn.execute(
                        "SELECT status FROM inventory WHERE id = ?", (product_id,)
                    )
                    result = cursor.fetchone()

                    if result and result[0] == "AVAILABLE":
                        conn.execute(
                            "UPDATE inventory SET status = 'SOLD' WHERE id = ?",
                            (product_id,),
                        )

                        # Add stock movement
                        movement_id = str(uuid.uuid4())
                        conn.execute(
                            """
                            INSERT INTO stock_movements (id, inventory_id, movement_type, reference_id,
                                                        reference_type, quantity, notes)
                            VALUES (?, ?, 'SOLD', ?, 'BILL', 1.0, ?)
                        """,
                            (
                                movement_id,
                                product_id,
                                bill_id,
                                f"Sold via bill {invoice_data['invoice_number']}",
                            ),
                        )
                    else:
                        warnings.append(
                            f"Item '{item.get('name')}' is not available for sale"
                        )
                else:
                    warnings.append(
                        f"Item '{item.get('name')}' is not linked to inventory"
                    )

            conn.commit()
            return str(bill_id), warnings

        except Exception as e:
            conn.rollback()
            raise Exception(f"Error generating invoice: {e}")
        finally:
            conn.close()

    # Additional required methods
    def get_invoices(self, limit: int = 100) -> List[Dict]:
        """Get recent invoices."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM bills ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        invoices = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return invoices


def get_database_manager():
    """Factory function to get appropriate database manager."""
    try:
        from logic.database_manager import SupabaseDatabaseManager

        return SupabaseDatabaseManager()
    except Exception:
        # Fallback to local database
        return LocalDatabaseManager()
