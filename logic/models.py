"""
Data Models for Jewelry Management System
Supabase/PostgreSQL compatible models
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID


@dataclass
class Category:
    """Jewelry category model."""

    id: UUID
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Supplier:
    """Supplier model."""

    id: UUID
    name: str
    code: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class InventoryItem:
    """Serialized inventory item model (one row per physical piece)."""

    id: UUID
    category_id: UUID
    category_item_no: int  # Per-category sequential number (reusable)
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    gross_weight: Decimal = Decimal("0.000")
    net_weight: Decimal = Decimal("0.000")
    supplier_id: Optional[UUID] = None
    melting_percentage: Decimal = Decimal("0.00")
    status: str = "AVAILABLE"  # AVAILABLE, SOLD, RESERVED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Customer:
    """Customer model."""

    id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Bill:
    """Bill/Invoice model."""

    id: UUID
    bill_number: str
    customer_id: Optional[UUID] = None
    customer_name: str = ""
    customer_phone: Optional[str] = None
    customer_gstin: Optional[str] = None
    bill_date: date = date.today()
    subtotal: Decimal = Decimal("0.00")
    cgst_rate: Decimal = Decimal("1.50")
    sgst_rate: Decimal = Decimal("1.50")
    cgst_amount: Decimal = Decimal("0.00")
    sgst_amount: Decimal = Decimal("0.00")
    total_amount: Decimal = Decimal("0.00")
    rounded_off: Decimal = Decimal("0.00")
    status: str = "GENERATED"  # GENERATED, REVERSED
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class BillItem:
    """Bill item model."""

    id: UUID
    bill_id: UUID
    inventory_id: Optional[UUID] = None
    description: str = ""
    hsn_code: Optional[str] = None
    quantity: Decimal = Decimal("1.000")
    rate: Decimal = Decimal("0.00")
    amount: Decimal = Decimal("0.00")
    created_at: Optional[datetime] = None


@dataclass
class StockMovement:
    """Stock movement ledger model."""

    id: UUID
    inventory_id: Optional[UUID] = None
    movement_type: str = "ADDED"  # ADDED, SOLD, REVERSED, ADJUSTED
    reference_id: Optional[UUID] = None
    reference_type: Optional[str] = None  # BILL, ADJUSTMENT, etc.
    quantity: Decimal = Decimal("1.000")
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class CategorySummary:
    """Category summary model for analytics."""

    category_id: UUID
    category_name: str
    total_items: int
    available_items: int
    sold_items: int
    available_gross_weight: Decimal
    available_net_weight: Decimal


@dataclass
class TotalSummary:
    """Total inventory summary model."""

    total_available_items: int
    total_sold_items: int
    total_available_gross_weight: Decimal
    total_available_net_weight: Decimal


@dataclass
class CurrentStockItem:
    """Current stock view model for UI display."""

    id: UUID
    category_id: UUID
    category_name: str
    category_item_no: int
    product_name: str
    description: Optional[str]
    hsn_code: Optional[str]
    gross_weight: Decimal
    net_weight: Decimal
    supplier_name: Optional[str]
    supplier_code: Optional[str]
    melting_percentage: Decimal
    status: str
    created_at: datetime


@dataclass
class SoldItem:
    """Sold items view model."""

    id: UUID
    category_id: UUID
    category_name: str
    category_item_no: int
    product_name: str
    gross_weight: Decimal
    net_weight: Decimal
    bill_number: str
    bill_date: date
    customer_name: str
    sale_amount: Decimal
    sold_at: datetime


@dataclass
class CategoryCSVData:
    """Category CSV export data model."""

    category_item_no: int
    product_name: str
    gross_weight: Decimal
    net_weight: Decimal
    supplier_code: str
    added_at: datetime


# Legacy compatibility - map old product model to new inventory item
@dataclass
class Product:
    """Legacy product model for backward compatibility with existing UI."""

    id: UUID
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    category_item_id: Optional[int] = None  # Maps to category_item_no
    hsn_code: Optional[str] = None
    gross_weight: float = 0.0
    net_weight: float = 0.0
    quantity: int = 1  # Always 1 for serialized inventory
    supplier_id: Optional[UUID] = None
    supplier_name: Optional[str] = None
    supplier_code: Optional[str] = None
    melting_percentage: float = 0.0
    status: str = "AVAILABLE"
    created_at: Optional[datetime] = None

    @classmethod
    def from_inventory_item(
        cls,
        item: InventoryItem,
        category_name: str = "",
        supplier_name: str = "",
        supplier_code: str = "",
    ) -> "Product":
        """Convert InventoryItem to legacy Product model."""
        return cls(
            id=item.id,
            name=category_name,  # Use category_name as product name
            description=item.description,
            category_id=item.category_id,
            category_name=category_name,
            category_item_id=item.category_item_no,
            hsn_code=item.hsn_code,
            gross_weight=float(item.gross_weight),
            net_weight=float(item.net_weight),
            quantity=1,  # Always 1 for serialized items
            supplier_id=item.supplier_id,
            supplier_name=supplier_name,
            supplier_code=supplier_code,
            melting_percentage=float(item.melting_percentage),
            status=item.status,
            created_at=item.created_at,
        )
