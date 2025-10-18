"""
Database handler for Roopkala Jewellers Billing System.

Manages SQLite database for storing invoices and line items.
"""

import sqlite3
import json
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class DatabaseHandler:
    """Handles all database operations for the billing system."""
    
    def __init__(self, db_path: str = "roopkala_billing.db"):
        """
        Initialize database handler.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection."""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema if not exists."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                invoice_date TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_address TEXT,
                customer_phone TEXT,
                customer_gstin TEXT,
                subtotal TEXT NOT NULL,
                cgst TEXT NOT NULL,
                sgst TEXT NOT NULL,
                total_gst TEXT NOT NULL,
                rounded_off TEXT NOT NULL,
                final_total TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create line items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS line_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                item_number INTEGER NOT NULL,
                description TEXT NOT NULL,
                hsn_code TEXT,
                quantity TEXT NOT NULL,
                rate TEXT NOT NULL,
                amount TEXT NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
            )
        ''')
        
        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_invoice_number 
            ON invoices(invoice_number)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_invoice_date 
            ON invoices(invoice_date)
        ''')
        
        conn.commit()
        conn.close()
    
    def save_invoice(
        self,
        invoice_number: str,
        invoice_date: str,
        customer_name: str,
        line_items: List[Dict],
        totals: Dict[str, Decimal],
        customer_address: str = "",
        customer_phone: str = "",
        customer_gstin: str = "",
        notes: str = ""
    ) -> int:
        """
        Save a new invoice to the database.
        
        Args:
            invoice_number: Unique invoice number
            invoice_date: Invoice date (YYYY-MM-DD format)
            customer_name: Customer name
            line_items: List of line item dictionaries
            totals: Dictionary with totals (subtotal, cgst, sgst, etc.)
            customer_address: Customer address (optional)
            customer_phone: Customer phone (optional)
            customer_gstin: Customer GSTIN (optional)
            notes: Additional notes (optional)
            
        Returns:
            Invoice ID (database row ID)
            
        Raises:
            sqlite3.IntegrityError: If invoice number already exists
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert invoice header
            cursor.execute('''
                INSERT INTO invoices (
                    invoice_number, invoice_date, customer_name, customer_address,
                    customer_phone, customer_gstin, subtotal, cgst, sgst,
                    total_gst, rounded_off, final_total, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_number,
                invoice_date,
                customer_name,
                customer_address,
                customer_phone,
                customer_gstin,
                str(totals['subtotal']),
                str(totals['cgst']),
                str(totals['sgst']),
                str(totals['total_gst']),
                str(totals['rounded_off']),
                str(totals['final_total']),
                notes
            ))
            
            invoice_id = cursor.lastrowid
            if invoice_id is None:
                raise Exception("Failed to create invoice")
            
            # Insert line items
            for idx, item in enumerate(line_items, start=1):
                cursor.execute('''
                    INSERT INTO line_items (
                        invoice_id, item_number, description, hsn_code,
                        quantity, rate, amount
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    invoice_id,
                    idx,
                    item['description'],
                    item.get('hsn_code', ''),
                    str(item['quantity']),
                    str(item['rate']),
                    str(item['amount'])
                ))
            
            conn.commit()
            return invoice_id
            
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_invoice(self, invoice_number: str) -> Optional[Dict]:
        """
        Retrieve an invoice by invoice number.
        
        Args:
            invoice_number: Invoice number to search
            
        Returns:
            Dictionary with invoice data and line items, or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get invoice header
        cursor.execute('''
            SELECT * FROM invoices WHERE invoice_number = ?
        ''', (invoice_number,))
        
        invoice_row = cursor.fetchone()
        
        if not invoice_row:
            conn.close()
            return None
        
        invoice = dict(invoice_row)
        
        # Get line items
        cursor.execute('''
            SELECT * FROM line_items 
            WHERE invoice_id = ?
            ORDER BY item_number
        ''', (invoice['id'],))
        
        line_items = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        invoice['line_items'] = line_items
        return invoice
    
    def get_all_invoices(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "invoice_date DESC"
    ) -> List[Dict]:
        """
        Get all invoices with pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: SQL ORDER BY clause
            
        Returns:
            List of invoice dictionaries (headers only, no line items)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = f'''
            SELECT * FROM invoices 
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        '''
        
        cursor.execute(query, (limit, offset))
        invoices = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return invoices
    
    def search_invoices(
        self,
        search_term: str,
        search_field: str = "customer_name"
    ) -> List[Dict]:
        """
        Search invoices by field.
        
        Args:
            search_term: Term to search for
            search_field: Field to search in (customer_name, invoice_number, etc.)
            
        Returns:
            List of matching invoice dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        valid_fields = [
            'invoice_number', 'customer_name', 'customer_phone',
            'customer_gstin', 'invoice_date'
        ]
        
        if search_field not in valid_fields:
            search_field = 'customer_name'
        
        query = f'''
            SELECT * FROM invoices 
            WHERE {search_field} LIKE ?
            ORDER BY invoice_date DESC
        '''
        
        cursor.execute(query, (f'%{search_term}%',))
        invoices = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return invoices
    
    def get_next_invoice_number(self, prefix: str = "RKJ", starting_number: int = 1001) -> str:
        """
        Generate next invoice number.
        
        Args:
            prefix: Invoice number prefix
            starting_number: Starting number if no invoices exist
            
        Returns:
            Next invoice number (e.g., "RKJ1001")
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get the last invoice number with this prefix
        cursor.execute('''
            SELECT invoice_number FROM invoices 
            WHERE invoice_number LIKE ?
            ORDER BY id DESC
            LIMIT 1
        ''', (f'{prefix}%',))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            last_number = row['invoice_number']
            # Extract numeric part
            try:
                numeric_part = int(last_number.replace(prefix, ''))
                next_number = numeric_part + 1
            except ValueError:
                next_number = starting_number
        else:
            next_number = starting_number
        
        return f"{prefix}{next_number}"
    
    def delete_invoice(self, invoice_number: str) -> bool:
        """
        Delete an invoice and its line items.
        
        Args:
            invoice_number: Invoice number to delete
            
        Returns:
            True if deleted, False if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM invoices WHERE invoice_number = ?
        ''', (invoice_number,))
        
        rows_deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_deleted > 0
    
    def get_invoice_count(self) -> int:
        """Get total number of invoices."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM invoices')
        count = cursor.fetchone()['count']
        
        conn.close()
        return count
