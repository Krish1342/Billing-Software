"""
Supabase Database Manager for Jewelry Management System
Handles all database operations with Supabase PostgreSQL backend
"""

import os
import json
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Optional, Union, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SupabaseDatabaseManager:
    """Database manager for Supabase PostgreSQL backend."""

    def __init__(self):
        """Initialize Supabase client."""
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_ANON_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment"
            )

        self.supabase: Client = create_client(self.url, self.key)
        self._test_connection()

    def _test_connection(self):
        """Test the database connection."""
        try:
            # Test with a simple query
            result = self.supabase.table("categories").select("*").limit(1).execute()
            if result.data is not None:
                print("✅ Supabase connection successful")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {e}")

    def close(self):
        """Close database connection (no-op for Supabase)."""
        pass

    def get_connection(self):
        """Get database connection (returns self for Supabase compatibility)."""
        return self.supabase

    # Categories
    def get_categories(self) -> List[Dict]:
        """Get all categories."""
        try:
            result = (
                self.supabase.table("categories").select("*").order("name").execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    def add_category(self, name: str, description: str = None) -> str:
        """Add a new category."""
        try:
            result = (
                self.supabase.table("categories")
                .insert({"name": name, "description": description})
                .execute()
            )
            return result.data[0]["id"]
        except Exception as e:
            raise Exception(f"Error adding category: {e}")

    def update_category(
        self, category_id: str, name: str, description: str = None
    ) -> bool:
        """Update a category."""
        try:
            result = (
                self.supabase.table("categories")
                .update({"name": name, "description": description})
                .eq("id", category_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating category: {e}")
            return False

    def delete_category(self, category_id: str) -> bool:
        """Delete a category."""
        try:
            # Check if category is used by inventory
            inventory_check = (
                self.supabase.table("inventory")
                .select("id")
                .eq("category_id", category_id)
                .limit(1)
                .execute()
            )
            if inventory_check.data:
                raise ValueError(
                    "Cannot delete category that is being used by inventory items"
                )

            result = (
                self.supabase.table("categories")
                .delete()
                .eq("id", category_id)
                .execute()
            )
            return len(result.data) > 0
        except ValueError:
            raise
        except Exception as e:
            print(f"Error deleting category: {e}")
            return False

    # Suppliers
    def get_suppliers(self) -> List[Dict]:
        """Get all suppliers."""
        try:
            result = (
                self.supabase.table("suppliers").select("*").order("name").execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Error getting suppliers: {e}")
            return []

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
        try:
            result = (
                self.supabase.table("suppliers")
                .insert(
                    {
                        "name": name,
                        "code": code,
                        "contact_person": contact_person,
                        "phone": phone,
                        "email": email,
                        "address": address,
                    }
                )
                .execute()
            )
            return result.data[0]["id"]
        except Exception as e:
            raise Exception(f"Error adding supplier: {e}")

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
            result = (
                self.supabase.table("suppliers")
                .update(
                    {
                        "name": name,
                        "code": code,
                        "contact_person": contact_person,
                        "phone": phone,
                        "email": email,
                        "address": address,
                    }
                )
                .eq("id", supplier_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating supplier: {e}")
            return False

    def delete_supplier(self, supplier_id: str) -> bool:
        """Delete a supplier."""
        try:
            # Check if supplier is used by inventory
            inventory_check = (
                self.supabase.table("inventory")
                .select("id")
                .eq("supplier_id", supplier_id)
                .limit(1)
                .execute()
            )
            if inventory_check.data:
                raise ValueError(
                    "Cannot delete supplier that is being used by inventory items"
                )

            result = (
                self.supabase.table("suppliers")
                .delete()
                .eq("id", supplier_id)
                .execute()
            )
            return len(result.data) > 0
        except ValueError:
            raise
        except Exception as e:
            print(f"Error deleting supplier: {e}")
            return False

    # Inventory (Products)
    def get_products(self) -> List[Dict]:
        """Get all inventory items formatted as products for existing UI."""
        try:
            result = self.supabase.table("current_stock_view").select("*").execute()

            # Transform to match existing UI expectations
            products = []
            for item in result.data or []:
                products.append(
                    {
                        "id": item["id"],
                        "name": item["product_name"],
                        "description": item.get("description", ""),
                        "category_id": item["category_id"],
                        "category_name": item["category_name"],
                        "category_item_id": item[
                            "category_item_no"
                        ],  # Add this for UI display
                        "hsn_code": item.get("hsn_code", ""),
                        "gross_weight": float(item["gross_weight"]),
                        "net_weight": float(item["net_weight"]),
                        "quantity": 1,  # Each row is one piece in serialized inventory
                        "unit_price": 0.0,  # Default value since we don't store unit prices
                        "supplier_id": None,  # Will be added if needed
                        "supplier_name": item.get("supplier_name", ""),
                        "supplier_code": item.get("supplier_code", ""),
                        "melting_percentage": float(item.get("melting_percentage", 0)),
                        "status": item["status"],
                        "created_at": item["created_at"],
                    }
                )
            return products
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

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
        """Add a new inventory item using Supabase RPC."""
        try:
            # For serialized inventory, we create individual items
            last_item_id = None
            for i in range(quantity):
                result = self.supabase.rpc(
                    "add_inventory_item",
                    {
                        "p_category_id": category_id,
                        "p_product_name": name,
                        "p_gross_weight": gross_weight,
                        "p_net_weight": net_weight,
                        "p_description": description,
                        "p_hsn_code": hsn_code,
                        "p_supplier_id": supplier_id,
                        "p_melting_percentage": melting_percentage,
                    },
                ).execute()
                last_item_id = result.data

            return last_item_id
        except Exception as e:
            raise Exception(f"Error adding product: {e}")

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
        """Update an inventory item."""
        try:
            update_data = {}
            if name is not None:
                update_data["product_name"] = name
            if description is not None:
                update_data["description"] = description
            if hsn_code is not None:
                update_data["hsn_code"] = hsn_code
            if gross_weight is not None:
                update_data["gross_weight"] = gross_weight
            if net_weight is not None:
                update_data["net_weight"] = net_weight
            if category_id is not None:
                update_data["category_id"] = category_id
            if supplier_id is not None:
                update_data["supplier_id"] = supplier_id
            if melting_percentage is not None:
                update_data["melting_percentage"] = melting_percentage

            if not update_data:
                return True

            result = (
                self.supabase.table("inventory")
                .update(update_data)
                .eq("id", product_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            print(f"Error updating product: {e}")
            return False

    def delete_product(self, product_id: str) -> bool:
        """Delete an inventory item."""
        try:
            # Check if item is already sold
            item_check = (
                self.supabase.table("inventory")
                .select("status")
                .eq("id", product_id)
                .execute()
            )
            if not item_check.data:
                return False

            if item_check.data[0]["status"] == "SOLD":
                raise ValueError("Cannot delete sold inventory item")

            result = (
                self.supabase.table("inventory").delete().eq("id", product_id).execute()
            )
            return len(result.data) > 0
        except ValueError:
            raise
        except Exception as e:
            print(f"Error deleting product: {e}")
            return False

    # Customers
    def get_customers(self) -> List[Dict]:
        """Get all customers."""
        try:
            result = (
                self.supabase.table("customers").select("*").order("name").execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []

    def add_customer(
        self,
        name: str,
        phone: str = None,
        email: str = None,
        address: str = None,
        gstin: str = None,
    ) -> str:
        """Add a new customer."""
        try:
            result = (
                self.supabase.table("customers")
                .insert(
                    {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "gstin": gstin,
                    }
                )
                .execute()
            )
            return result.data[0]["id"]
        except Exception as e:
            raise Exception(f"Error adding customer: {e}")

    # Bills and Invoicing
    def create_invoice(self, invoice_data: Dict) -> Dict:
        """Create a new bill/invoice using Supabase RPC."""
        try:
            # Prepare items for RPC call
            items = []
            for item in invoice_data.get("items", []):
                items.append(
                    {
                        "inventory_id": item.get(
                            "product_id"
                        ),  # Map product_id to inventory_id
                        "product_name": item.get("product_name", ""),
                        "description": item.get("description", ""),
                        "hsn_code": item.get("hsn_code", ""),
                        "quantity": item.get("quantity", 1),
                        "rate": float(item.get("rate", 0)),
                        "amount": float(item.get("amount", 0)),
                    }
                )

            # Create bill using RPC
            result = self.supabase.rpc(
                "create_bill_with_items",
                {
                    "p_bill_number": invoice_data["invoice_number"],
                    "p_customer_name": invoice_data["customer_name"],
                    "p_items": items,  # Pass as Python list, not JSON string
                    "p_customer_phone": invoice_data.get("customer_phone"),
                    "p_customer_gstin": invoice_data.get("customer_gstin"),
                    "p_bill_date": invoice_data.get("invoice_date", str(date.today())),
                    "p_cgst_rate": float(invoice_data.get("cgst_rate", 1.5)),
                    "p_sgst_rate": float(invoice_data.get("sgst_rate", 1.5)),
                },
            ).execute()

            bill_id = result.data

            # Get the created bill details
            bill_result = (
                self.supabase.table("bills").select("*").eq("id", bill_id).execute()
            )
            return bill_result.data[0] if bill_result.data else {}

        except Exception as e:
            raise Exception(f"Error creating invoice: {e}")

    def generate_invoice_with_stock_deduction(
        self, invoice_data: Dict, line_items: List[Dict]
    ) -> tuple:
        """Generate invoice with automatic stock deduction using Supabase RPC.

        Args:
            invoice_data: Dictionary containing invoice information
            line_items: List of dictionaries containing line item information

        Returns:
            Tuple of (invoice_id, warnings) where warnings is a list of warning messages
        """
        try:
            warnings = []

            # Prepare items for the RPC call
            items = []
            for item in line_items:
                item_data = {
                    "inventory_id": item.get(
                        "product_id"
                    ),  # Map product_id to inventory_id
                    "product_name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "hsn_code": item.get("hsn_code", ""),
                    "quantity": item.get("quantity", 1),
                    "rate": item.get("rate", 0),
                    "amount": item.get("amount", 0),
                }

                # Add warning if product_id is None (custom item)
                if not item_data["inventory_id"]:
                    warnings.append(
                        f"Item '{item_data['product_name']}' is not linked to inventory"
                    )

                items.append(item_data)

            # Create bill using RPC - this handles stock deduction automatically
            result = self.supabase.rpc(
                "create_bill_with_items",
                {
                    "p_bill_number": invoice_data["invoice_number"],
                    "p_customer_name": invoice_data["customer_name"],
                    "p_items": items,  # Pass as Python list, not JSON string
                    "p_customer_phone": invoice_data.get("customer_phone"),
                    "p_customer_gstin": invoice_data.get("customer_gstin"),
                    "p_bill_date": invoice_data.get("invoice_date", str(date.today())),
                    "p_cgst_rate": float(invoice_data.get("cgst_rate", 1.5)),
                    "p_sgst_rate": float(invoice_data.get("sgst_rate", 1.5)),
                },
            ).execute()

            bill_id = result.data
            return str(bill_id), warnings

        except Exception as e:
            raise Exception(f"Error generating invoice with stock deduction: {e}")

    def get_invoices(self, limit: int = 100) -> List[Dict]:
        """Get recent invoices."""
        try:
            result = (
                self.supabase.table("bills")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Error getting invoices: {e}")
            return []

    def reverse_invoice(self, invoice_id: str) -> bool:
        """Reverse an invoice."""
        try:
            result = self.supabase.rpc(
                "reverse_bill", {"p_bill_id": invoice_id}
            ).execute()
            return result.data
        except Exception as e:
            print(f"Error reversing invoice: {e}")
            return False

    # Stock movements
    def get_stock_movements(
        self, product_id: str = None, limit: int = 200
    ) -> List[Dict]:
        """Get stock movements."""
        try:
            query = self.supabase.table("stock_ledger_view").select("*")

            if product_id:
                query = query.eq("inventory_id", product_id)

            result = query.order("created_at", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting stock movements: {e}")
            return []

    # Analytics and summaries
    def get_category_summary(self) -> List[Dict]:
        """Get category-wise summary."""
        try:
            result = self.supabase.table("category_summary_view").select("*").execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting category summary: {e}")
            return []

    def get_total_summary(self) -> Dict:
        """Get overall inventory summary."""
        try:
            result = self.supabase.table("total_summary_view").select("*").execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Error getting total summary: {e}")
            return {}

    def get_sold_items(self, limit: int = 100) -> List[Dict]:
        """Get recently sold items."""
        try:
            result = (
                self.supabase.table("sold_items_view")
                .select("*")
                .limit(limit)
                .execute()
            )
            return result.data or []
        except Exception as e:
            print(f"Error getting sold items: {e}")
            return []

    # CSV export functions
    def get_category_csv_data(self, category_id: str) -> List[Dict]:
        """Get category data for CSV export."""
        try:
            result = self.supabase.rpc(
                "get_category_csv_data", {"p_category_id": category_id}
            ).execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting category CSV data: {e}")
            return []

    def get_summary_csv_data(self) -> List[Dict]:
        """Get summary data for CSV export."""
        try:
            result = self.supabase.rpc("get_summary_csv_data").execute()
            return result.data or []
        except Exception as e:
            print(f"Error getting summary CSV data: {e}")
            return []

    # Legacy compatibility methods (for existing UI)
    def reduce_stock(self, product_id: str, quantity: int = 1):
        """Mark inventory item as sold (legacy method for UI compatibility)."""
        try:
            # In the new system, this is handled by create_invoice RPC
            # This method is kept for UI compatibility
            result = (
                self.supabase.table("inventory")
                .update({"status": "SOLD"})
                .eq("id", product_id)
                .eq("status", "AVAILABLE")
                .execute()
            )

            if result.data:
                # Create stock movement
                self.supabase.table("stock_movements").insert(
                    {
                        "inventory_id": product_id,
                        "movement_type": "SOLD",
                        "quantity": 1.0,
                        "notes": "Manual stock reduction",
                    }
                ).execute()
                return True
            return False
        except Exception as e:
            print(f"Error reducing stock: {e}")
            return False

    # Additional methods expected by UI components

    @property
    def db_path(self) -> str:
        """Return a descriptive path for Supabase connection (for UI display)."""
        return f"Supabase Database: {self.url}"

    def get_next_invoice_number(self) -> str:
        """Get the next invoice number."""
        try:
            from datetime import datetime

            current_year = datetime.now().year

            # Try to get the highest existing number for current year
            result = (
                self.supabase.table("bills")
                .select("bill_number")
                .like("bill_number", f"RK-{current_year}-%")
                .order("bill_number", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                last_bill = result.data[0]["bill_number"]
                try:
                    parts = last_bill.split("-")
                    if len(parts) >= 3 and parts[1] == str(current_year):
                        number = int(parts[-1]) + 1
                        new_number = f"RK-{current_year}-{number:03d}"

                        # Verify this number doesn't exist
                        check = (
                            self.supabase.table("bills")
                            .select("id")
                            .eq("bill_number", new_number)
                            .execute()
                        )
                        if not check.data:
                            return new_number
                except:
                    pass

            # Find next available number starting from 001
            for i in range(1, 10000):  # Support up to 9999 invoices per year
                new_number = f"RK-{current_year}-{i:03d}"
                check = (
                    self.supabase.table("bills")
                    .select("id")
                    .eq("bill_number", new_number)
                    .execute()
                )
                if not check.data:
                    return new_number

            # Fallback with timestamp if all numbers exhausted
            from datetime import datetime

            timestamp = datetime.now().strftime("%H%M%S")
            return f"RK-{current_year}-{timestamp}"

        except Exception as e:
            print(f"Error getting next invoice number: {e}")
            from datetime import datetime

            current_year = datetime.now().year
            timestamp = datetime.now().strftime("%H%M%S")
            return f"RK-{current_year}-{timestamp}"

    def get_sales_summary(self, from_date: str = None, to_date: str = None) -> Dict:
        """Get sales summary for given date range."""
        try:
            query = self.supabase.table("bills").select("*").eq("status", "GENERATED")

            if from_date:
                query = query.gte("bill_date", from_date)
            if to_date:
                query = query.lte("bill_date", to_date)

            result = query.execute()
            bills = result.data or []

            total_sales = sum(float(bill["total_amount"]) for bill in bills)
            total_bills = len(bills)

            # Get item count
            if bills:
                bill_ids = [bill["id"] for bill in bills]
                items_result = (
                    self.supabase.table("bill_items")
                    .select("*")
                    .in_("bill_id", bill_ids)
                    .execute()
                )
                total_items = len(items_result.data or [])
            else:
                total_items = 0

            return {
                "total_sales": total_sales,
                "total_invoices": total_bills,
                "total_items_sold": total_items,
                "average_invoice_value": (
                    total_sales / total_bills if total_bills > 0 else 0
                ),
            }

        except Exception as e:
            print(f"Error getting sales summary: {e}")
            return {
                "total_sales": 0,
                "total_invoices": 0,
                "total_items_sold": 0,
                "average_invoice_value": 0,
            }

    def get_low_stock_products(self, threshold: int = 5) -> List[Dict]:
        """Get products with low stock (for serialized inventory, this means categories with few available items)."""
        try:
            # Get category summary and filter by available items
            result = self.supabase.table("category_summary_view").select("*").execute()
            categories = result.data or []

            low_stock = []
            for category in categories:
                available_items = category.get("available_items", 0)
                if available_items <= threshold:
                    low_stock.append(
                        {
                            "id": category["category_id"],
                            "name": category["category_name"],
                            "category_name": category["category_name"],
                            "quantity": available_items,  # For UI compatibility
                            "available_quantity": available_items,
                            "unit_price": 0.0,  # Default value since we don't store unit prices
                            "available_gross_weight": float(
                                category.get("available_gross_weight", 0)
                            ),
                            "available_net_weight": float(
                                category.get("available_net_weight", 0)
                            ),
                            "total_items": category.get("total_items", 0),
                            "sold_items": category.get("sold_items", 0),
                        }
                    )

            return low_stock

        except Exception as e:
            print(f"Error getting low stock products: {e}")
            return []


# Alias for backward compatibility with existing UI
UnifiedDatabaseManager = SupabaseDatabaseManager
