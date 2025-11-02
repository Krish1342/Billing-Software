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

    def _migrate_if_needed(self):
        """Check if database migration is needed and perform migrations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if product_name column exists in inventory table
        cursor.execute("PRAGMA table_info(inventory)")
        columns = [col[1] for col in cursor.fetchall()]

        if "product_name" in columns:
            print("🔄 Migrating database: Removing product_name column...")
            try:
                # Create new inventory table without product_name
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS inventory_new (
                        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                        category_id TEXT NOT NULL REFERENCES categories(id),
                        category_item_no INTEGER NOT NULL,
                        description TEXT,
                        hsn_code TEXT,
                        gross_weight DECIMAL(10,3) NOT NULL CHECK (gross_weight > 0),
                        net_weight DECIMAL(10,3) NOT NULL CHECK (net_weight > 0 AND net_weight <= gross_weight),
                        supplier_id TEXT REFERENCES suppliers(id),
                        melting_percentage DECIMAL(5,2) DEFAULT 0.00,
                        status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'SOLD', 'RESERVED')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Copy data from old table to new (excluding product_name)
                cursor.execute(
                    """
                    INSERT INTO inventory_new 
                    SELECT id, category_id, category_item_no, description, hsn_code, 
                           gross_weight, net_weight, supplier_id, melting_percentage, 
                           status, created_at, updated_at
                    FROM inventory
                """
                )

                # Drop old table and rename new table
                cursor.execute("DROP TABLE inventory")
                cursor.execute("ALTER TABLE inventory_new RENAME TO inventory")

                print("✅ Inventory table migration completed")
            except Exception as e:
                print(f"⚠️ Migration failed: {e}")
                conn.rollback()
                conn.close()
                return

        # Check if product_name column exists in bill_items table
        cursor.execute("PRAGMA table_info(bill_items)")
        bill_columns = [col[1] for col in cursor.fetchall()]

        if "product_name" in bill_columns:
            print("🔄 Migrating database: Removing product_name from bill_items...")
            try:
                # Create new bill_items table without product_name
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bill_items_new (
                        id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
                        bill_id TEXT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
                        inventory_id TEXT REFERENCES inventory(id),
                        description TEXT NOT NULL,
                        hsn_code TEXT,
                        quantity DECIMAL(10,3) NOT NULL DEFAULT 1.000,
                        rate DECIMAL(12,2) NOT NULL,
                        amount DECIMAL(12,2) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Copy data from old table to new (excluding product_name)
                cursor.execute(
                    """
                    INSERT INTO bill_items_new 
                    SELECT id, bill_id, inventory_id, description, hsn_code, 
                           quantity, rate, amount, created_at
                    FROM bill_items
                """
                )

                # Drop old table and rename new table
                cursor.execute("DROP TABLE bill_items")
                cursor.execute("ALTER TABLE bill_items_new RENAME TO bill_items")

                print("✅ Bill items table migration completed")
            except Exception as e:
                print(f"⚠️ Bill items migration failed: {e}")
                conn.rollback()
                conn.close()
                return

        conn.commit()
        conn.close()

    def init_database(self):
        """Initialize SQLite database with complete schema (includes slot reuse)."""
        # First, check if we need to migrate existing database
        self._migrate_if_needed()

        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")

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

        -- Inventory table (removed product_name, using category as name)
        CREATE TABLE IF NOT EXISTS inventory (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            category_id TEXT NOT NULL REFERENCES categories(id),
            category_item_no INTEGER NOT NULL,
            description TEXT,
            hsn_code TEXT,
            gross_weight DECIMAL(10,3) NOT NULL CHECK (gross_weight > 0),
            net_weight DECIMAL(10,3) NOT NULL CHECK (net_weight > 0 AND net_weight <= gross_weight),
            supplier_id TEXT REFERENCES suppliers(id),
            melting_percentage DECIMAL(5,2) DEFAULT 0.00,
            status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'SOLD', 'RESERVED')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- HSN code history table
        CREATE TABLE IF NOT EXISTS hsn_code_history (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            hsn_code TEXT UNIQUE NOT NULL,
            description TEXT,
            last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        -- Bill items table (removed product_name field)
        CREATE TABLE IF NOT EXISTS bill_items (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
            bill_id TEXT NOT NULL REFERENCES bills(id) ON DELETE CASCADE,
            inventory_id TEXT REFERENCES inventory(id),
            description TEXT NOT NULL,
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

        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_inventory_category_status ON inventory(category_id, status);
        CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory(status);
        CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id);
        CREATE INDEX IF NOT EXISTS idx_bill_items_inventory_id ON bill_items(inventory_id);
        CREATE INDEX IF NOT EXISTS idx_stock_movements_inventory_id ON stock_movements(inventory_id);

        -- ✅ Conditional unique constraint (only for active items)
        CREATE UNIQUE INDEX IF NOT EXISTS unique_category_item_no_active 
        ON inventory (category_id, category_item_no)
        WHERE status IN ('AVAILABLE', 'RESERVED');

        -- Triggers for auto-updating 'updated_at'
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
        # Drop old index (if exists) to avoid unique constraint conflicts
        try:
            conn.execute("DROP INDEX IF EXISTS unique_category_item_no;")
        except Exception:
            pass

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

    def add_category(self, name: str, description: Optional[str] = None) -> str:
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

    def update_category(
        self, category_id: str, name: str, description: str = None
    ) -> bool:
        """Update a category."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "UPDATE categories SET name = ?, description = ? WHERE id = ?",
                (name, description, category_id),
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating category: {e}")
            return False

    def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        try:
            conn = sqlite3.connect(self.db_path)

            # Check if category is used by inventory
            cursor = conn.execute(
                "SELECT id FROM inventory WHERE category_id = ? LIMIT 1",
                (category_id,),
            )
            if cursor.fetchone():
                conn.close()
                raise ValueError(
                    "Cannot delete category that is being used by inventory items"
                )

            conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            conn.close()
            return True

        except ValueError:
            raise
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False

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
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
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

    def update_supplier(
        self,
        supplier_id: str,
        name: str,
        code: str,
        contact_person: str = None,
        phone: str = None,
        email: str = None,
        address: str = None,
    ) -> bool:
        """Update a supplier."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                "UPDATE suppliers SET name = ?, code = ?, contact_person = ?, phone = ?, email = ?, address = ? WHERE id = ?",
                (name, code, contact_person, phone, email, address, supplier_id),
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return False

    def delete_supplier(self, supplier_id: str) -> bool:
        """Delete a supplier."""
        try:
            conn = sqlite3.connect(self.db_path)

            # Check if supplier is used by inventory
            cursor = conn.execute(
                "SELECT id FROM inventory WHERE supplier_id = ? LIMIT 1",
                (supplier_id,),
            )
            if cursor.fetchone():
                conn.close()
                raise ValueError(
                    "Cannot delete supplier that is being used by inventory items"
                )

            conn.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            conn.commit()
            conn.close()
            return True

        except ValueError:
            raise
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            return False

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
                    "name": row["category_name"],  # Use category name as product name
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
        description: Optional[str] = None,
        hsn_code: Optional[str] = None,
        gross_weight: float = 0,
        net_weight: float = 0,
        quantity: int = 1,
        supplier_id: Optional[str] = None,
        category_id: Optional[str] = None,
        melting_percentage: float = 0,
        **kwargs,
    ) -> str:
        """Add inventory items with slot reuse. Name parameter is ignored, category is used as name."""
        conn = sqlite3.connect(self.db_path)
        last_item_id: str = ""

        # Save HSN code to history if provided
        if hsn_code:
            self.add_or_update_hsn_code_history(hsn_code, description)

        for i in range(quantity):
            # ✅ Find lowest available or reusable category_item_no
            cursor = conn.execute(
                """
                SELECT n FROM (
                    WITH RECURSIVE nums(n) AS (
                        SELECT 1
                        UNION ALL
                        SELECT n + 1 FROM nums WHERE n < 10000
                    )
                    SELECT nums.n
                    FROM nums
                    LEFT JOIN inventory i
                    ON i.category_id = ? AND i.category_item_no = nums.n
                    AND i.status IN ('AVAILABLE', 'RESERVED')
                    WHERE i.category_item_no IS NULL
                    LIMIT 1
                )
            """,
                (category_id,),
            )
            result = cursor.fetchone()
            category_item_no = result[0] if result and result[0] else 1

            # ✅ Insert new item (removed product_name)
            item_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO inventory (
                    id, category_id, category_item_no, description, 
                    hsn_code, gross_weight, net_weight, supplier_id, melting_percentage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    item_id,
                    category_id,
                    category_item_no,
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

    def update_product(
        self,
        product_id: str,
        name: str = None,
        description: str = None,
        hsn_code: str = None,
        gross_weight: float = None,
        net_weight: float = None,
        quantity: int = None,
        category_id: str = None,
        supplier_id: str = None,
        melting_percentage: float = None,
        **kwargs,
    ) -> bool:
        """Update an inventory item. Note: name parameter is ignored as we use category."""
        try:
            conn = sqlite3.connect(self.db_path)

            # Build update query dynamically
            update_fields = []
            update_values = []

            # Note: we don't update product_name as it's been removed from schema
            if description is not None:
                update_fields.append("description = ?")
                update_values.append(description)
            if hsn_code is not None:
                update_fields.append("hsn_code = ?")
                update_values.append(hsn_code)
                # Update HSN history if provided
                if hsn_code:
                    self.add_or_update_hsn_code_history(hsn_code, description)
            if gross_weight is not None:
                update_fields.append("gross_weight = ?")
                update_values.append(gross_weight)
            if net_weight is not None:
                update_fields.append("net_weight = ?")
                update_values.append(net_weight)
            if category_id is not None:
                update_fields.append("category_id = ?")
                update_values.append(category_id)
            if supplier_id is not None:
                update_fields.append("supplier_id = ?")
                update_values.append(supplier_id)
            if melting_percentage is not None:
                update_fields.append("melting_percentage = ?")
                update_values.append(melting_percentage)

            if not update_fields:
                return True  # Nothing to update

            # Add product_id to the end of values
            update_values.append(product_id)

            query = f"UPDATE inventory SET {', '.join(update_fields)} WHERE id = ?"
            conn.execute(query, update_values)
            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error updating product: {e}")
            return False

    def delete_product(self, product_id: str) -> bool:
        """Delete an inventory item."""
        try:
            conn = sqlite3.connect(self.db_path)

            # Check if item exists and get its status
            cursor = conn.execute(
                "SELECT status FROM inventory WHERE id = ?", (product_id,)
            )
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False

            if result[0] == "SOLD":
                conn.close()
                raise ValueError("Cannot delete sold inventory item")

            # Delete the inventory item
            conn.execute("DELETE FROM inventory WHERE id = ?", (product_id,))

            # Also delete related stock movements
            conn.execute(
                "DELETE FROM stock_movements WHERE inventory_id = ?", (product_id,)
            )

            conn.commit()
            conn.close()
            return True

        except ValueError:
            raise
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False

    # Additional methods to match SupabaseDatabaseManager interface
    def get_db_info(self) -> str:
        """Return database path information."""
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

    def get_sales_summary(
        self, from_date: Optional[str] = None, to_date: Optional[str] = None
    ) -> Dict:
        """Get sales summary."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

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

        # Columns in bills: see schema; use names for clarity
        total_sales = sum(float(bill[12]) for bill in bills)  # total_amount
        total_bills = len(bills)

        # Items sold count and top items
        total_items = 0
        top_items: List[Dict] = []
        if bills:
            bill_ids = [bill[0] for bill in bills]
            placeholders = ",".join("?" * len(bill_ids))

            # Total items
            cur2 = conn.execute(
                f"SELECT COUNT(*) FROM bill_items WHERE bill_id IN ({placeholders})",
                bill_ids,
            )
            total_items = cur2.fetchone()[0] or 0

            # Top items aggregated by description (fallback to product_name)
            cur3 = conn.execute(
                f"""
                SELECT 
                    COALESCE(NULLIF(description, ''), product_name) AS item_desc,
                    COUNT(*) AS total_sold,
                    COALESCE(SUM(amount), 0) AS total_revenue
                FROM bill_items
                WHERE bill_id IN ({placeholders})
                GROUP BY item_desc
                ORDER BY total_sold DESC, total_revenue DESC
                LIMIT 20
                """,
                bill_ids,
            )
            top_items = [
                {
                    "description": row[0],
                    "total_sold": float(row[1]),
                    "total_revenue": float(row[2]),
                }
                for row in cur3.fetchall()
            ]

        conn.close()

        # Return with aliases to match UI expectations
        average_sale = (total_sales / total_bills) if total_bills > 0 else 0.0
        return {
            "total_sales": total_sales,
            "total_invoices": total_bills,
            "invoice_count": total_bills,  # UI expects this key
            "total_items_sold": total_items,
            "average_invoice_value": average_sale,
            "average_sale": average_sale,  # UI expects this key
            "top_items": top_items,
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

                # Build description from item data
                item_description = item.get("description", "")
                if not item_description and item.get("name"):
                    item_description = item.get("name")

                # Add bill item (removed product_name)
                conn.execute(
                    """
                    INSERT INTO bill_items (id, bill_id, inventory_id, description,
                                          hsn_code, quantity, rate, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        item_id,
                        bill_id,
                        product_id,
                        item_description,
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

    def get_stock_movements(
        self, inventory_id: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """Get stock movements, optionally filtered by inventory ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        if inventory_id:
            cursor = conn.execute(
                "SELECT * FROM stock_movements WHERE inventory_id = ? ORDER BY created_at DESC LIMIT ?",
                (inventory_id, limit),
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM stock_movements ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )

        movements = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return movements

    def get_customers(self) -> List[Dict]:
        """Get all customers."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM customers ORDER BY name")
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return customers

    def add_customer(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        gstin: Optional[str] = None,
    ) -> str:
        """Add a new customer."""
        customer_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO customers (id, name, phone, email, address, gstin) VALUES (?, ?, ?, ?, ?, ?)",
            (customer_id, name, phone, email, address, gstin),
        )
        conn.commit()
        conn.close()
        return customer_id

    def get_category_summary(self) -> List[Dict]:
        """Get inventory summary by category."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            """
            SELECT 
                c.id as category_id,
                c.name as category_name,
                COUNT(CASE WHEN i.status = 'AVAILABLE' THEN 1 END) as available_count,
                COUNT(CASE WHEN i.status = 'SOLD' THEN 1 END) as sold_count,
                COUNT(CASE WHEN i.status = 'RESERVED' THEN 1 END) as reserved_count,
                COUNT(i.id) as total_count,
                COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.gross_weight END), 0) as available_gross_weight,
                COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.net_weight END), 0) as available_net_weight,
                COALESCE(SUM(i.gross_weight), 0) as total_gross_weight,
                COALESCE(SUM(i.net_weight), 0) as total_net_weight
            FROM categories c
            LEFT JOIN inventory i ON c.id = i.category_id
            GROUP BY c.id, c.name
            ORDER BY c.name
        """
        )

        summary = []
        for row in cursor.fetchall():
            # Provide both legacy "*_count" and UI-expected "*_items"/"total_items" keys
            item = {
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                # Counts
                "available_count": row["available_count"],
                "sold_count": row["sold_count"],
                "reserved_count": row["reserved_count"],
                "total_count": row["total_count"],
                # UI-expected aliases
                "available_items": row["available_count"],
                "sold_items": row["sold_count"],
                "total_items": row["total_count"],
                # Weights
                "available_gross_weight": float(row["available_gross_weight"]),
                "available_net_weight": float(row["available_net_weight"]),
                "total_gross_weight": float(row["total_gross_weight"]),
                "total_net_weight": float(row["total_net_weight"]),
            }
            summary.append(item)

        conn.close()
        return summary

    def get_total_summary(self) -> Dict:
        """Get overall inventory summary to match UI expectations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT 
                COUNT(CASE WHEN status = 'AVAILABLE' THEN 1 END) AS total_available_items,
                COUNT(CASE WHEN status = 'SOLD' THEN 1 END) AS total_sold_items,
                COALESCE(SUM(CASE WHEN status = 'AVAILABLE' THEN gross_weight END), 0) AS total_available_gross_weight,
                COALESCE(SUM(CASE WHEN status = 'AVAILABLE' THEN net_weight END), 0) AS total_available_net_weight
            FROM inventory
            """
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {
                "total_available_items": 0,
                "total_sold_items": 0,
                "total_available_gross_weight": 0.0,
                "total_available_net_weight": 0.0,
            }

        return {
            "total_available_items": int(row[0] or 0),
            "total_sold_items": int(row[1] or 0),
            "total_available_gross_weight": float(row[2] or 0.0),
            "total_available_net_weight": float(row[3] or 0.0),
        }

    def get_invoice_items(self, invoice_id: str) -> List[Dict]:
        """Get items for a specific invoice (local SQLite)."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM bill_items WHERE bill_id = ? ORDER BY created_at ASC",
            (invoice_id,),
        )
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def clear_all_data(self) -> bool:
        """Clear all data from the database while keeping the schema."""
        try:
            conn = sqlite3.connect(self.db_path)

            # Disable foreign key constraints temporarily
            conn.execute("PRAGMA foreign_keys = OFF")

            # Clear all tables in the correct order (respecting foreign key relationships)
            tables_to_clear = [
                "stock_movements",
                "bill_items",
                "bills",
                "inventory",
                "customers",
                "suppliers",
                "categories",
            ]

            for table in tables_to_clear:
                conn.execute(f"DELETE FROM {table}")
                print(f"Cleared table: {table}")

            # Re-enable foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")

            conn.commit()
            conn.close()

            print("✅ All database data cleared successfully!")
            print("📋 Database schema preserved.")
            return True

        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            return False

    def reset_database(self) -> bool:
        """Reset database by clearing all data and re-adding sample data."""
        if self.clear_all_data():
            self._add_sample_data()
            print("🔄 Database reset with sample data.")
            return True
        return False

    # HSN Code History Methods
    def get_hsn_code_history(self) -> List[Dict]:
        """Get all HSN codes from history."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM hsn_code_history ORDER BY last_used DESC LIMIT 100"
        )
        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history

    def add_or_update_hsn_code_history(
        self, hsn_code: str, description: Optional[str] = None
    ) -> None:
        """Add or update HSN code in history."""
        if not hsn_code or not hsn_code.strip():
            return

        conn = sqlite3.connect(self.db_path)
        try:
            # Check if HSN code already exists
            cursor = conn.execute(
                "SELECT id FROM hsn_code_history WHERE hsn_code = ?", (hsn_code,)
            )
            existing = cursor.fetchone()

            if existing:
                # Update last_used timestamp and description if provided
                if description:
                    conn.execute(
                        "UPDATE hsn_code_history SET last_used = CURRENT_TIMESTAMP, description = ? WHERE hsn_code = ?",
                        (description, hsn_code),
                    )
                else:
                    conn.execute(
                        "UPDATE hsn_code_history SET last_used = CURRENT_TIMESTAMP WHERE hsn_code = ?",
                        (hsn_code,),
                    )
            else:
                # Insert new HSN code
                hsn_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO hsn_code_history (id, hsn_code, description) VALUES (?, ?, ?)",
                    (hsn_id, hsn_code, description),
                )

            conn.commit()
        except Exception as e:
            print(f"Error adding/updating HSN history: {e}")
            conn.rollback()
        finally:
            conn.close()

    def export_category_wise_csv(self, category_id: str, file_path: str) -> bool:
        """Export category-wise inventory to CSV with sr.no, description, hsn code, supplier code."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Get category name
            cursor = conn.execute(
                "SELECT name FROM categories WHERE id = ?", (category_id,)
            )
            category_row = cursor.fetchone()
            if not category_row:
                conn.close()
                return False

            category_name = category_row["name"]

            # Get inventory items for this category
            cursor = conn.execute(
                """
                SELECT 
                    i.category_item_no,
                    i.description,
                    i.hsn_code,
                    i.gross_weight,
                    i.net_weight,
                    s.code as supplier_code,
                    i.status,
                    i.created_at
                FROM inventory i
                LEFT JOIN suppliers s ON i.supplier_id = s.id
                WHERE i.category_id = ?
                ORDER BY i.category_item_no
                """,
                (category_id,),
            )

            items = cursor.fetchall()
            conn.close()

            # Write to CSV
            import csv

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(
                    [
                        "Sr. No.",
                        "Category",
                        "Description",
                        "HSN Code",
                        "Supplier Code",
                        "Gross Weight (g)",
                        "Net Weight (g)",
                        "Status",
                        "Added Date",
                    ]
                )

                # Write data
                for idx, item in enumerate(items, 1):
                    writer.writerow(
                        [
                            idx,
                            category_name,
                            item["description"] or "",
                            item["hsn_code"] or "",
                            item["supplier_code"] or "",
                            f"{item['gross_weight']:.3f}",
                            f"{item['net_weight']:.3f}",
                            item["status"],
                            item["created_at"],
                        ]
                    )

            return True

        except Exception as e:
            print(f"Error exporting category-wise CSV: {e}")
            return False

    def export_total_summary_csv(self, file_path: str) -> bool:
        """Export total summary CSV with category, gross weight, net weight, no of items."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            # Get category summary
            cursor = conn.execute(
                """
                SELECT 
                    c.name as category_name,
                    COUNT(CASE WHEN i.status = 'AVAILABLE' THEN 1 END) as available_items,
                    COUNT(i.id) as total_items,
                    COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.gross_weight END), 0) as available_gross_weight,
                    COALESCE(SUM(CASE WHEN i.status = 'AVAILABLE' THEN i.net_weight END), 0) as available_net_weight,
                    COALESCE(SUM(i.gross_weight), 0) as total_gross_weight,
                    COALESCE(SUM(i.net_weight), 0) as total_net_weight
                FROM categories c
                LEFT JOIN inventory i ON c.id = i.category_id
                GROUP BY c.id, c.name
                ORDER BY c.name
                """
            )

            categories = cursor.fetchall()
            conn.close()

            # Write to CSV
            import csv

            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(
                    [
                        "Category",
                        "Total Items",
                        "Available Items",
                        "Total Gross Weight (g)",
                        "Total Net Weight (g)",
                        "Available Gross Weight (g)",
                        "Available Net Weight (g)",
                    ]
                )

                # Write data
                total_items = 0
                total_available = 0
                total_gross = 0.0
                total_net = 0.0
                available_gross = 0.0
                available_net = 0.0

                for cat in categories:
                    writer.writerow(
                        [
                            cat["category_name"],
                            cat["total_items"],
                            cat["available_items"],
                            f"{cat['total_gross_weight']:.3f}",
                            f"{cat['total_net_weight']:.3f}",
                            f"{cat['available_gross_weight']:.3f}",
                            f"{cat['available_net_weight']:.3f}",
                        ]
                    )

                    total_items += cat["total_items"]
                    total_available += cat["available_items"]
                    total_gross += float(cat["total_gross_weight"])
                    total_net += float(cat["total_net_weight"])
                    available_gross += float(cat["available_gross_weight"])
                    available_net += float(cat["available_net_weight"])

                # Write totals row
                writer.writerow([])
                writer.writerow(
                    [
                        "TOTAL",
                        total_items,
                        total_available,
                        f"{total_gross:.3f}",
                        f"{total_net:.3f}",
                        f"{available_gross:.3f}",
                        f"{available_net:.3f}",
                    ]
                )

            return True

        except Exception as e:
            print(f"Error exporting total summary CSV: {e}")
            return False


def get_database_manager():
    """Factory function to get appropriate database manager."""
    try:
        from logic.database_manager import SupabaseDatabaseManager

        return SupabaseDatabaseManager()
    except Exception:
        # Fallback to local database
        return LocalDatabaseManager()
