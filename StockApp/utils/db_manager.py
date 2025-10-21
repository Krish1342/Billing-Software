"""
Database Manager for Jewelry Shop Stock Management System

This module provides comprehensive database operations using SQLite
with proper validation, error handling, and relationship management.
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, Any, Optional, List


class DBManager:
    """
    Database manager for the jewelry shop management system.

    Handles all database operations including CRUD operations for products,
    suppliers, and history tracking with proper validation and constraints.
    """

    def __init__(self, db_path: str = "db/jewelry_shop.db"):
        """
        Initialize database manager.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._create_tables()

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

            # Create products table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    gross_weight REAL NOT NULL,
                    net_weight REAL NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    unit_price REAL NOT NULL DEFAULT 0.0,
                    supplier_id INTEGER,
                    category TEXT DEFAULT 'General',
                    melting_percentage REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                    CHECK (gross_weight >= net_weight),
                    CHECK (gross_weight > 0),
                    CHECK (net_weight > 0),
                    CHECK (quantity >= 0),
                    CHECK (unit_price >= 0),
                    CHECK (melting_percentage >= 0 AND melting_percentage <= 100)
                )
            """
            )

            # Create history table for action logging
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

            # Add melting_percentage column to existing products table if it doesn't exist
            try:
                cursor.execute(
                    "ALTER TABLE products ADD COLUMN melting_percentage REAL DEFAULT 0.0"
                )
            except sqlite3.OperationalError:
                # Column already exists
                pass

            conn.commit()

    # Supplier operations
    def add_supplier(
        self,
        name: str,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
    ) -> int:
        """
        Add a new supplier to the database.

        Args:
            name (str): Supplier name
            contact_person (str, optional): Contact person name
            phone (str, optional): Phone number
            email (str, optional): Email address
            address (str, optional): Address

        Returns:
            int: ID of the newly created supplier

        Raises:
            ValueError: If supplier name already exists
        """
        code = self.generate_supplier_code(name)

        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO suppliers (name, code, contact_person, phone, email, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (name, code, contact_person, phone, email, address),
                )

                supplier_id = cursor.lastrowid
                conn.commit()
                return int(supplier_id or 0)

            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: suppliers.name" in str(e):
                    raise ValueError(f"Supplier '{name}' already exists")
                else:
                    raise ValueError(f"Database error: {str(e)}")

    def add_supplier_with_code(
        self,
        name: str,
        code: str,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
    ) -> int:
        """
        Add a new supplier to the database with a custom code.

        Args:
            name (str): Supplier name
            code (str): Custom supplier code
            contact_person (str, optional): Contact person name
            phone (str, optional): Phone number
            email (str, optional): Email address
            address (str, optional): Address

        Returns:
            int: ID of the newly created supplier

        Raises:
            ValueError: If supplier name or code already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO suppliers (name, code, contact_person, phone, email, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (name, code, contact_person, phone, email, address),
                )

                supplier_id = cursor.lastrowid
                conn.commit()
                return int(supplier_id or 0)

            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: suppliers.name" in str(e):
                    raise ValueError(f"Supplier '{name}' already exists")
                elif "UNIQUE constraint failed: suppliers.code" in str(e):
                    raise ValueError(f"Supplier code '{code}' already exists")
                else:
                    raise ValueError(f"Database error: {str(e)}")

    def clear_all_suppliers(self) -> int:
        """
        Remove all suppliers from the database.

        Returns:
            int: Number of suppliers removed
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # First, update any products that reference suppliers
            cursor.execute(
                "UPDATE products SET supplier_id = NULL WHERE supplier_id IS NOT NULL"
            )

            # Get count before deletion
            cursor.execute("SELECT COUNT(*) FROM suppliers")
            count = cursor.fetchone()[0]

            # Delete all suppliers
            cursor.execute("DELETE FROM suppliers")
            conn.commit()

            return count

    def clear_all_data(self) -> Dict[str, int]:
        """
        Remove ALL data from the database (products, suppliers, history).

        Returns:
            Dict[str, int]: Count of records removed from each table
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get counts before deletion
            cursor.execute("SELECT COUNT(*) FROM products")
            products_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM suppliers")
            suppliers_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM history")
            history_count = cursor.fetchone()[0]

            # Delete all data in proper order (respecting foreign keys)
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM suppliers")
            cursor.execute("DELETE FROM history")

            conn.commit()

            return {
                "products": products_count,
                "suppliers": suppliers_count,
                "history": history_count,
            }

    def reset_database(self) -> Dict[str, int]:
        """
        Complete database reset - removes all data and resets auto-increment counters.

        Returns:
            Dict[str, int]: Count of records removed from each table
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get counts before deletion
            cursor.execute("SELECT COUNT(*) FROM products")
            products_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM suppliers")
            suppliers_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM history")
            history_count = cursor.fetchone()[0]

            # Delete all data
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM suppliers")
            cursor.execute("DELETE FROM history")

            # Reset auto-increment counters
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name IN ('products', 'suppliers', 'history')"
            )

            conn.commit()

            return {
                "products": products_count,
                "suppliers": suppliers_count,
                "history": history_count,
            }

    def generate_supplier_code(self, name: str) -> str:
        """
        Generate a unique supplier code based on the name.

        Args:
            name (str): Supplier name

        Returns:
            str: Unique supplier code (3 letters + 3 digits)
        """
        # Extract first 3 letters and make uppercase
        base_code = "".join(c for c in name if c.isalpha())[:3].upper()
        if len(base_code) < 3:
            base_code = base_code.ljust(3, "X")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            counter = 1
            code = f"{base_code}{counter:03d}"

            while True:
                cursor.execute("SELECT id FROM suppliers WHERE code = ?", (code,))
                if not cursor.fetchone():
                    return code
                counter += 1
                code = f"{base_code}{counter:03d}"

    def get_suppliers(self) -> List[Dict[str, Any]]:
        """
        Get all suppliers from the database.

        Returns:
            List[Dict]: List of supplier records
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]

    def get_supplier_by_id(self, supplier_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a supplier by ID.

        Args:
            supplier_id (int): Supplier ID

        Returns:
            Dict or None: Supplier data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_supplier(
        self,
        supplier_id: int,
        name: Optional[str] = None,
        contact_person: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
    ) -> bool:
        """
        Update supplier information.

        Args:
            supplier_id (int): Supplier ID
            name (str, optional): New name
            contact_person (str, optional): New contact person
            phone (str, optional): New phone
            email (str, optional): New email
            address (str, optional): New address

        Returns:
            bool: True if update successful
        """
        updates = []
        values = []

        if name is not None:
            updates.append("name = ?")
            values.append(name)

        if contact_person is not None:
            updates.append("contact_person = ?")
            values.append(contact_person)

        if phone is not None:
            updates.append("phone = ?")
            values.append(phone)

        if email is not None:
            updates.append("email = ?")
            values.append(email)

        if address is not None:
            updates.append("address = ?")
            values.append(address)

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.append(supplier_id)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE suppliers SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_supplier(self, supplier_id: int) -> bool:
        """
        Delete a supplier from the database.

        Args:
            supplier_id (int): Supplier ID

        Returns:
            bool: True if deletion successful

        Raises:
            ValueError: If supplier has associated products
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if supplier has products
            cursor.execute(
                "SELECT COUNT(*) FROM products WHERE supplier_id = ?", (supplier_id,)
            )
            product_count = cursor.fetchone()[0]

            if product_count > 0:
                raise ValueError(
                    f"Cannot delete supplier: {product_count} products are associated with this supplier"
                )

            cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            conn.commit()
            return cursor.rowcount > 0

    # Product operations
    def add_product(
        self,
        name: str,
        gross_weight: float,
        net_weight: float,
        quantity: int = 0,
        unit_price: float = 0.0,
        supplier_id: Optional[int] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        melting_percentage: float = 0.0,
    ) -> int:
        """
        Add a new product to the database.

        Args:
            name (str): Product name
            gross_weight (float): Gross weight
            net_weight (float): Net weight
            quantity (int): Quantity in stock
            unit_price (float): Unit price
            supplier_id (int, optional): Supplier ID
            description (str, optional): Product description
            category (str, optional): Product category
            melting_percentage (float): Melting percentage (0-100)

        Returns:
            int: ID of the newly created product

        Raises:
            ValueError: If weight validation fails
        """
        if gross_weight <= 0 or net_weight <= 0:
            raise ValueError("Weights must be positive")
        if gross_weight < net_weight:
            raise ValueError("Gross weight cannot be less than net weight")
        if melting_percentage < 0 or melting_percentage > 100:
            raise ValueError("Melting percentage must be between 0 and 100")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO products 
                (name, description, gross_weight, net_weight, quantity, unit_price, supplier_id, category, melting_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    description,
                    gross_weight,
                    net_weight,
                    quantity,
                    unit_price,
                    supplier_id,
                    category,
                    melting_percentage,
                ),
            )
            product_id = cursor.lastrowid
            conn.commit()
            return int(product_id or 0)

    def update_product_full(
        self,
        product_id: int,
        name: str,
        gross_weight: float,
        net_weight: float,
        quantity: int,
        unit_price: float,
        supplier_id: Optional[int] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
        melting_percentage: float = 0.0,
    ) -> bool:
        """
        Update a product with full details.

        Args:
            product_id (int): Product ID to update
            name (str): Product name
            gross_weight (float): Gross weight
            net_weight (float): Net weight
            quantity (int): Quantity in stock
            unit_price (float): Unit price
            supplier_id (int, optional): Supplier ID
            description (str, optional): Product description
            category (str, optional): Product category
            melting_percentage (float): Melting percentage

        Returns:
            bool: True if update successful
        """
        if gross_weight <= 0 or net_weight <= 0:
            raise ValueError("Weights must be positive")
        if gross_weight < net_weight:
            raise ValueError("Gross weight cannot be less than net weight")
        if melting_percentage < 0 or melting_percentage > 100:
            raise ValueError("Melting percentage must be between 0 and 100")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE products 
                SET name=?, description=?, gross_weight=?, net_weight=?, quantity=?, 
                    unit_price=?, supplier_id=?, category=?, melting_percentage=?, 
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """,
                (
                    name,
                    description,
                    gross_weight,
                    net_weight,
                    quantity,
                    unit_price,
                    supplier_id,
                    category,
                    melting_percentage,
                    product_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_products(self) -> List[Dict[str, Any]]:
        """
        Get all products with supplier information.

        Returns:
            List[Dict]: List of product records with supplier details
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, s.name as supplier_name, s.code as supplier_code
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                ORDER BY p.name
            """
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a product by ID with supplier information.

        Args:
            product_id (int): Product ID

        Returns:
            Dict or None: Product data with supplier info or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, s.name as supplier_name, s.code as supplier_code
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.id = ?
            """,
                (product_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def delete_product(self, product_id: int) -> bool:
        """
        Delete a product from the database.

        Args:
            product_id (int): Product ID

        Returns:
            bool: True if deletion successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_product_categories_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary of all product categories with total weight and quantity.

        Returns:
            List[Dict]: List of category summaries with totals
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    COALESCE(category, 'General') as category,
                    COUNT(*) as product_count,
                    SUM(quantity) as total_quantity,
                    SUM(gross_weight * quantity) as total_gross_weight,
                    SUM(net_weight * quantity) as total_net_weight,
                    SUM(quantity * unit_price) as total_value,
                    AVG(melting_percentage) as avg_melting_percentage
                FROM products 
                WHERE quantity > 0
                GROUP BY COALESCE(category, 'General')
                ORDER BY category
            """
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all products in a specific category.

        Args:
            category (str): Category name

        Returns:
            List[Dict]: List of products in the category
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.*, s.name as supplier_name, s.code as supplier_code
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE COALESCE(p.category, 'General') = ?
                ORDER BY p.name
            """,
                (category,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_available_categories(self) -> List[str]:
        """
        Get list of all available product categories.

        Returns:
            List[str]: List of unique categories
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT DISTINCT COALESCE(category, 'General') as category
                FROM products 
                ORDER BY category
            """
            )
            return [row[0] for row in cursor.fetchall()]

    # History operations
    def add_history_record(
        self,
        action: str,
        table_name: str,
        record_id: Optional[int] = None,
        old_values: Optional[str] = None,
        new_values: Optional[str] = None,
        user_id: str = "admin",
    ) -> int:
        """
        Add a history record for audit trail.

        Args:
            action (str): Action performed (CREATE, UPDATE, DELETE)
            table_name (str): Table name
            record_id (int, optional): Record ID affected
            old_values (str, optional): JSON string of old values
            new_values (str, optional): JSON string of new values
            user_id (str): User who performed the action

        Returns:
            int: ID of the history record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO history (action, table_name, record_id, old_values, new_values, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (action, table_name, record_id, old_values, new_values, user_id),
            )
            history_id = cursor.lastrowid
            conn.commit()
            return int(history_id or 0)

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent action history.

        Args:
            limit (int): Maximum number of records to return

        Returns:
            List[Dict]: List of history records
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM history 
                ORDER BY timestamp DESC 
                LIMIT ?
            """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # Category operations
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories from the database.

        Returns:
            List[Dict]: List of all categories with their details
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, name, description, created_at, updated_at
                FROM categories
                ORDER BY name
            """
            )
            return [dict(row) for row in cursor.fetchall()]

    def add_category(self, name: str, description: Optional[str] = None) -> int:
        """
        Add a new category to the database.

        Args:
            name (str): Category name
            description (str, optional): Category description

        Returns:
            int: ID of the newly created category

        Raises:
            ValueError: If category name already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    INSERT INTO categories (name, description)
                    VALUES (?, ?)
                """,
                    (name.strip(), description.strip() if description else None),
                )

                category_id = cursor.lastrowid
                conn.commit()
                return int(category_id or 0)

            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: categories.name" in str(e):
                    raise ValueError(f"Category '{name}' already exists")
                else:
                    raise ValueError(f"Database error: {str(e)}")

    def update_category(
        self, category_id: int, name: str, description: Optional[str] = None
    ) -> bool:
        """
        Update an existing category.

        Args:
            category_id (int): Category ID to update
            name (str): New category name
            description (str, optional): New category description

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If category name already exists for a different category
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    """
                    UPDATE categories 
                    SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """,
                    (
                        name.strip(),
                        description.strip() if description else None,
                        category_id,
                    ),
                )

                conn.commit()
                return cursor.rowcount > 0

            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: categories.name" in str(e):
                    raise ValueError(f"Category '{name}' already exists")
                else:
                    raise ValueError(f"Database error: {str(e)}")

    def delete_category(self, category_id: int) -> bool:
        """
        Delete a category from the database.

        Args:
            category_id (int): Category ID to delete

        Returns:
            bool: True if successful, False otherwise

        Raises:
            ValueError: If category has associated products
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if category has products
            cursor.execute(
                "SELECT COUNT(*) FROM products WHERE category = (SELECT name FROM categories WHERE id = ?)",
                (category_id,),
            )
            product_count = cursor.fetchone()[0]

            if product_count > 0:
                raise ValueError(
                    f"Cannot delete category. It has {product_count} associated products."
                )

            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_category_names(self) -> List[str]:
        """
        Get list of all category names.

        Returns:
            List[str]: List of category names sorted alphabetically
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Close database connection (placeholder for consistency)."""
        # SQLite connections are handled in context managers
        pass


if __name__ == "__main__":
    # Test the database manager
    db = DBManager()
    print("Database manager initialized successfully!")

    # Test adding a supplier
    try:
        supplier_id = db.add_supplier("Test Supplier", "John Doe", "123-456-7890")
        print(f"Added supplier with ID: {supplier_id}")

        # Test adding a product
        product_id = db.add_product(
            "Test Ring",
            5.0,
            4.5,
            10,
            299.99,
            supplier_id,
            "Test ring description",
            "Rings",
            85.0,
        )
        print(f"Added product with ID: {product_id}")

        # Test getting categories summary
        categories = db.get_product_categories_summary()
        print(f"Categories summary: {categories}")

    except Exception as e:
        print(f"Error: {e}")
