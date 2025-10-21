"""
Unified Database Manager for Merged Billing and Stock Management System

This module provides comprehensive database operations combining both
billing and stock management functionality with automatic stock deduction
when bills are generated.
"""

import sqlite3
import os
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple


class UnifiedDatabaseManager:
    """
    Unified database manager for billing and stock management system.

    Handles all database operations including CRUD operations for products,
    suppliers, customers, invoices, and history tracking with proper validation.
    """

    def __init__(self, db_path: str = "unified_jewelry_shop.db"):
        """
        Initialize unified database manager.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._create_tables()
        self._migrate_database()

    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a database connection.

        Returns:
            sqlite3.Connection: Database connection object
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn

    def _create_tables(self):

                    # Ensure stock_movements has a simple 'quantity' column for new code paths
                        cursor.execute("PRAGMA table_info(stock_movements)")
                    sm_columns = [col[1] for col in cursor.fetchall()]
                    if 'quantity' not in sm_columns:
                        try:
                            cursor.execute("ALTER TABLE stock_movements ADD COLUMN quantity REAL")
                            print("Database migration: Added 'quantity' column to stock_movements")
                        except Exception:
                            # Table may be immutable or migration not needed; continue gracefully
                            pass
        """Create all required tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Create suppliers table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    code TEXT NOT NULL UNIQUE,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create categories table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create products table (stock management)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    hsn_code TEXT,
                    gross_weight REAL NOT NULL,
                    net_weight REAL NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit_price REAL NOT NULL DEFAULT 0.0,
                    supplier_id INTEGER,
                    category_id INTEGER,
                    melting_percentage REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                    FOREIGN KEY (category_id) REFERENCES categories (id),
                    CHECK (gross_weight >= net_weight),
                    CHECK (gross_weight > 0),
                    CHECK (net_weight > 0),
                    CHECK (quantity >= 0),
                    CHECK (unit_price >= 0),
                    CHECK (melting_percentage >= 0 AND melting_percentage <= 100)
                )
            """
            )

            # Create customers table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    gstin TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create invoices table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT NOT NULL UNIQUE,
                    customer_id INTEGER,
                    customer_name TEXT NOT NULL,
                    invoice_date DATE NOT NULL,
                    subtotal REAL NOT NULL,
                    cgst_amount REAL NOT NULL,
                    sgst_amount REAL NOT NULL,
                    total_amount REAL NOT NULL,
                    rounded_off REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'GENERATED',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """
            )

            # Create invoice_items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    product_id INTEGER,
                    description TEXT NOT NULL,
                    hsn_code TEXT,
                    quantity REAL NOT NULL,
                    rate REAL NOT NULL,
                    amount REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (id),
                    CHECK (quantity > 0),
                    CHECK (rate >= 0),
                    CHECK (amount >= 0)
                )
            """
            )

            # Create stock_movements table for tracking inventory changes
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    movement_type TEXT NOT NULL, -- 'IN', 'OUT', 'ADJUSTMENT'
                    quantity REAL NOT NULL,
                    reference_type TEXT, -- 'INVOICE', 'PURCHASE', 'ADJUSTMENT'
                    reference_id INTEGER,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """
            )

            # Create history table for audit trail
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    old_values TEXT,
                    new_values TEXT,
                    user_id TEXT DEFAULT 'admin',
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Insert default categories if table is empty
            cursor.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            if count == 0:
                default_categories = [
                    ("Rings", "Wedding rings, engagement rings, and fashion rings"),
                    ("Necklaces", "Gold, silver, and diamond necklaces"),
                    ("Earrings", "Studs, hoops, and drop earrings"),
                    ("Bracelets", "Tennis bracelets, charm bracelets, and bangles"),
                    ("Pendants", "Decorative pendants and charms"),
                    ("Brooches", "Vintage and modern brooches"),
                    ("Chains", "Gold and silver chains of various lengths"),
                    ("Bangles", "Traditional and contemporary bangles"),
                    ("Anklets", "Delicate ankle jewelry"),
                    ("Cufflinks", "Formal and casual cufflinks"),
                ]
                cursor.executemany(
                    "INSERT INTO categories (name, description) VALUES (?, ?)",
                    default_categories,
                )

            conn.commit()

    # ==================== PRODUCT MANAGEMENT ====================

    def add_product(
        self,
        name: str,
        gross_weight: float,
        net_weight: float,
        quantity: int = 1,
        unit_price: float = 0.0,
        supplier_id: Optional[int] = None,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        hsn_code: Optional[str] = None,
        melting_percentage: float = 0.0,
    ) -> int:
        """Add a new product to inventory."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO products (name, description, hsn_code, gross_weight, net_weight, 
                                    quantity, unit_price, supplier_id, category_id, melting_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    description,
                    hsn_code,
                    gross_weight,
                    net_weight,
                    quantity,
                    unit_price,
                    supplier_id,
                    category_id,
                    melting_percentage,
                ),
            )

            product_id = cursor.lastrowid

            # Record initial stock movement
            if quantity > 0:
                cursor.execute(
                    """
                    INSERT INTO stock_movements (product_id, movement_type, quantity, reference_type, notes)
                    VALUES (?, 'IN', ?, 'INITIAL', 'Initial stock entry')
                """,
                    (product_id, quantity),
                )

            conn.commit()
            return product_id

    def get_products(self) -> List[Dict]:
        """Get all products with supplier and category details."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT p.*, s.name as supplier_name, s.code as supplier_code,
                       c.name as category_name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.name
            """
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a product by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT p.*, s.name as supplier_name, c.name as category_name
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = ?
            """,
                (product_id,),
            )

            row = cursor.fetchone()
            return dict(row) if row else None

    def update_product_stock(
        self,
        product_id: int,
        new_quantity: int,
        movement_type: str = "ADJUSTMENT",
        reference_type: str = "ADJUSTMENT",
        reference_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> bool:
        """Update product stock quantity with movement tracking."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get current quantity
            cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if not row:
                return False

            current_quantity = row[0]
            quantity_change = new_quantity - current_quantity

            # Update product quantity
            cursor.execute(
                """
                UPDATE products SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (new_quantity, product_id),
            )

            # Record stock movement
            if quantity_change != 0:
                cursor.execute(
                    """
                    INSERT INTO stock_movements (product_id, movement_type, quantity, 
                                               reference_type, reference_id, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        product_id,
                        movement_type,
                        abs(quantity_change),
                        reference_type,
                        reference_id,
                        notes,
                    ),
                )

            conn.commit()
            return True

    def deduct_stock(
        self, product_id: int, quantity: float, invoice_id: Optional[int] = None
    ) -> bool:
        """Deduct stock when a product is sold."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get current quantity
            cursor.execute("SELECT quantity FROM products WHERE id = ?", (product_id,))
            row = cursor.fetchone()
            if not row:
                return False

            current_quantity = row[0]
            if current_quantity < quantity:
                return False  # Insufficient stock

            new_quantity = current_quantity - quantity

            # Update product quantity
            cursor.execute(
                """
                UPDATE products SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (new_quantity, product_id),
            )

            # Record stock movement
            cursor.execute(
                """
                INSERT INTO stock_movements (product_id, movement_type, quantity, 
                                           reference_type, reference_id, notes)
                VALUES (?, 'OUT', ?, 'INVOICE', ?, 'Stock deducted for sale')
            """,
                (product_id, quantity, invoice_id),
            )

            conn.commit()
            return True

    # ==================== CATEGORY MANAGEMENT ====================

    def add_category(self, name: str, description: Optional[str] = None) -> int:
        """Add a new category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            """,
                (name, description),
            )

            conn.commit()
            return cursor.lastrowid

    def get_categories(self) -> List[Dict]:
        """Get all categories."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM categories ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    # ==================== SUPPLIER MANAGEMENT ====================

    def add_supplier(
        self,
        name: str,
        code: str,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
    ) -> int:
        """Add a new supplier."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO suppliers (name, code, contact_person, phone, email, address)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (name, code, contact_person, phone, email, address),
            )

            conn.commit()
            return cursor.lastrowid

    def get_suppliers(self) -> List[Dict]:
        """Get all suppliers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM suppliers ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    # ==================== CUSTOMER MANAGEMENT ====================

    def add_customer(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        gstin: Optional[str] = None,
    ) -> int:
        """Add a new customer."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO customers (name, phone, email, address, gstin)
                VALUES (?, ?, ?, ?, ?)
            """,
                (name, phone, email, address, gstin),
            )

            conn.commit()
            return cursor.lastrowid

    def get_customers(self) -> List[Dict]:
        """Get all customers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM customers ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    # ==================== INVOICE MANAGEMENT ====================

    def create_invoice(
        self,
        invoice_number: str,
        customer_name: str,
        invoice_date: str,
        subtotal: float,
        cgst_amount: float,
        sgst_amount: float,
        total_amount: float,
        rounded_off: float = 0.0,
        customer_id: Optional[int] = None,
    ) -> int:
        """Create a new invoice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO invoices (invoice_number, customer_id, customer_name, invoice_date,
                                    subtotal, cgst_amount, sgst_amount, total_amount, rounded_off)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    invoice_number,
                    customer_id,
                    customer_name,
                    invoice_date,
                    subtotal,
                    cgst_amount,
                    sgst_amount,
                    total_amount,
                    rounded_off,
                ),
            )

            conn.commit()
            return cursor.lastrowid

    def add_invoice_item(
        self,
        invoice_id: int,
        product_id: Optional[int],
        description: str,
        hsn_code: Optional[str],
        quantity: float,
        rate: float,
        amount: float,
    ) -> int:
        """Add an item to an invoice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO invoice_items (invoice_id, product_id, description, hsn_code,
                                         quantity, rate, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (invoice_id, product_id, description, hsn_code, quantity, rate, amount),
            )

            conn.commit()
            return cursor.lastrowid

    def generate_invoice_with_stock_deduction(
        self, invoice_data: Dict, line_items: List[Dict]
    ) -> Tuple[int, List[str]]:
        """
        Generate invoice and automatically deduct stock for linked products.

        Returns:
            Tuple of (invoice_id, list of warnings/errors)
        """
        warnings = []

        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                # Begin transaction
                conn.execute("BEGIN TRANSACTION")

                # Create invoice
                cursor.execute(
                    """
                    INSERT INTO invoices (invoice_number, customer_id, customer_name, invoice_date,
                                        subtotal, cgst_amount, sgst_amount, total_amount, rounded_off)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        invoice_data["invoice_number"],
                        invoice_data.get("customer_id"),
                        invoice_data["customer_name"],
                        invoice_data["invoice_date"],
                        invoice_data["subtotal"],
                        invoice_data["cgst_amount"],
                        invoice_data["sgst_amount"],
                        invoice_data["total_amount"],
                        invoice_data.get("rounded_off", 0.0),
                    ),
                )

                invoice_id = cursor.lastrowid

                # Add invoice items and deduct stock
                for item in line_items:
                    # Add invoice item
                    cursor.execute(
                        """
                        INSERT INTO invoice_items (invoice_id, product_id, description, hsn_code,
                                                 quantity, rate, amount)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            invoice_id,
                            item.get("product_id"),
                            item["description"],
                            item.get("hsn_code"),
                            item["quantity"],
                            item["rate"],
                            item["amount"],
                        ),
                    )

                    # Deduct stock if product_id is provided
                    if item.get("product_id"):
                        cursor.execute(
                            "SELECT name, quantity FROM products WHERE id = ?",
                            (item["product_id"],),
                        )
                        product_row = cursor.fetchone()

                        if product_row:
                            product_name, current_stock = product_row
                            required_qty = item["quantity"]

                            if current_stock >= required_qty:
                                # Deduct stock
                                new_quantity = current_stock - required_qty
                                cursor.execute(
                                    """
                                    UPDATE products SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                                    WHERE id = ?
                                """,
                                    (new_quantity, item["product_id"]),
                                )

                                # Record stock movement
                                cursor.execute(
                                    """
                                    INSERT INTO stock_movements (product_id, movement_type, quantity,
                                                               reference_type, reference_id, notes)
                                    VALUES (?, 'OUT', ?, 'INVOICE', ?, 'Stock deducted for sale')
                                """,
                                    (item["product_id"], required_qty, invoice_id),
                                )
                            else:
                                warnings.append(
                                    f"Insufficient stock for {product_name}. Required: {required_qty}, Available: {current_stock}"
                                )
                        else:
                            warnings.append(
                                f"Product with ID {item['product_id']} not found"
                            )

                # Commit transaction
                conn.commit()
                return invoice_id, warnings

            except Exception as e:
                # Rollback on error
                conn.execute("ROLLBACK")
                raise e

    def get_invoices(self, limit: int = 100) -> List[Dict]:
        """Get recent invoices."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT * FROM invoices
                ORDER BY created_at DESC
                LIMIT ?
            """,
                (limit,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_invoice_items(self, invoice_id: int) -> List[Dict]:
        """Get items for a specific invoice."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT ii.*, p.name as product_name
                FROM invoice_items ii
                LEFT JOIN products p ON ii.product_id = p.id
                WHERE ii.invoice_id = ?
                ORDER BY ii.id
            """,
                (invoice_id,),
            )

            return [dict(row) for row in cursor.fetchall()]

    # ==================== ANALYTICS AND REPORTING ====================

    def get_low_stock_products(self, threshold: int = 5) -> List[Dict]:
        """Get products with stock below threshold."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT p.*, c.name as category_name, s.name as supplier_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.quantity <= ?
                ORDER BY p.quantity ASC
            """,
                (threshold,),
            )

            return [dict(row) for row in cursor.fetchall()]

    def get_stock_movements(
        self, product_id: Optional[int] = None, limit: int = 100
    ) -> List[Dict]:
        """Get stock movement history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if product_id:
                cursor.execute(
                    """
                    SELECT sm.*, p.name as product_name
                    FROM stock_movements sm
                    JOIN products p ON sm.product_id = p.id
                    WHERE sm.product_id = ?
                    ORDER BY sm.created_at DESC
                    LIMIT ?
                """,
                    (product_id, limit),
                )
            else:
                cursor.execute(
                    """
                    SELECT sm.*, p.name as product_name
                    FROM stock_movements sm
                    JOIN products p ON sm.product_id = p.id
                    ORDER BY sm.created_at DESC
                    LIMIT ?
                """,
                    (limit,),
                )

            return [dict(row) for row in cursor.fetchall()]

    def get_sales_summary(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict:
        """Get sales summary for a date range."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            where_clause = ""
            params = []

            if start_date and end_date:
                where_clause = "WHERE invoice_date BETWEEN ? AND ?"
                params = [start_date, end_date]
            elif start_date:
                where_clause = "WHERE invoice_date >= ?"
                params = [start_date]
            elif end_date:
                where_clause = "WHERE invoice_date <= ?"
                params = [end_date]

            # Total sales
            cursor.execute(
                f"""
                SELECT COUNT(*) as invoice_count, 
                       SUM(total_amount) as total_sales,
                       AVG(total_amount) as average_sale
                FROM invoices {where_clause}
            """,
                params,
            )

            summary = dict(cursor.fetchone())

            # Top selling items
            cursor.execute(
                f"""
                SELECT ii.description, SUM(ii.quantity) as total_sold, SUM(ii.amount) as total_revenue
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.id
                {where_clause}
                GROUP BY ii.description
                ORDER BY total_sold DESC
                LIMIT 10
            """,
                params,
            )

            summary["top_items"] = [dict(row) for row in cursor.fetchall()]

            return summary

    def get_next_invoice_number(self) -> str:
        """Get the next invoice number."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(invoice_number) FROM invoices")
            row = cursor.fetchone()
            last_number = row[0] if row[0] else None

            if last_number:
                try:
                    # Extract numeric part and increment
                    num_part = int(last_number.split("-")[-1])
                    return f"INV-{num_part + 1:04d}"
                except:
                    pass

            # Default starting number
            return "INV-0001"

    def _migrate_database(self):
        """Perform database migrations for schema updates."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                # Check if invoices table needs migration (total -> total_amount)
                cursor.execute("PRAGMA table_info(invoices)")
                columns = [col[1] for col in cursor.fetchall()]

                if "total_amount" not in columns and "total" in columns:
                    print(
                        "Migrating database: Adding total_amount and rounded_off columns..."
                    )

                    # Add the missing columns
                    cursor.execute("ALTER TABLE invoices ADD COLUMN total_amount REAL")
                    cursor.execute(
                        "ALTER TABLE invoices ADD COLUMN rounded_off REAL DEFAULT 0.0"
                    )

                    # Copy data from total to total_amount
                    cursor.execute("UPDATE invoices SET total_amount = total")

                    print("Database migration completed successfully!")

            except Exception as e:
                print(f"Migration error (non-critical): {e}")

    def close(self):
        """Close database connections (placeholder for cleanup if needed)."""
        pass
