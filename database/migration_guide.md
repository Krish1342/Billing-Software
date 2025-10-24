# Migration Guide: SQLite to Supabase

This document provides step-by-step guidance for migrating from existing SQLite database to the new Supabase PostgreSQL schema.

## Prerequisites

1. **Supabase Project Setup**

   - Create a new Supabase project
   - Note down your project URL and anon key
   - Run the `supabase_schema.sql` in the Supabase SQL Editor

2. **Required Python Packages**
   ```bash
   pip install supabase python-dotenv
   ```

## Migration Steps

### Step 1: Export SQLite Data to CSV

If you have existing SQLite data, export tables to CSV files:

```sql
-- Export categories
.mode csv
.headers on
.output categories.csv
SELECT id, name, description FROM categories;

-- Export suppliers
.output suppliers.csv
SELECT id, name, code, contact_person, phone, email, address FROM suppliers;

-- Export products/inventory
.output inventory.csv
SELECT id, name, description, category_id, hsn_code,
       gross_weight, net_weight, supplier_id,
       melting_percentage, quantity FROM products;

-- Export customers
.output customers.csv
SELECT id, name, phone, email, address, gstin FROM customers;

-- Reset output
.output stdout
```

### Step 2: Data Transformation Scripts

Create Python scripts to transform and import data:

**transform_data.py:**

```python
import csv
import uuid
from typing import Dict, List

def transform_categories(csv_file: str) -> List[Dict]:
    """Transform categories CSV to Supabase format."""
    categories = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories.append({
                'id': str(uuid.uuid4()),
                'name': row['name'],
                'description': row.get('description', '')
            })
    return categories

def transform_suppliers(csv_file: str) -> List[Dict]:
    """Transform suppliers CSV to Supabase format."""
    suppliers = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            suppliers.append({
                'id': str(uuid.uuid4()),
                'name': row['name'],
                'code': row['code'],
                'contact_person': row.get('contact_person'),
                'phone': row.get('phone'),
                'email': row.get('email'),
                'address': row.get('address')
            })
    return suppliers

def transform_inventory(csv_file: str, category_map: Dict, supplier_map: Dict) -> List[Dict]:
    """Transform inventory CSV to Supabase serialized format."""
    inventory = []
    category_counters = {}  # Track category_item_no per category

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category_id = category_map.get(row['category_id'])
            if not category_id:
                continue

            # Get next category_item_no
            if category_id not in category_counters:
                category_counters[category_id] = 1
            else:
                category_counters[category_id] += 1

            # Create individual items based on quantity
            quantity = int(row.get('quantity', 1))
            for i in range(quantity):
                inventory.append({
                    'id': str(uuid.uuid4()),
                    'category_id': category_id,
                    'category_item_no': category_counters[category_id],
                    'product_name': row['name'],
                    'description': row.get('description'),
                    'hsn_code': row.get('hsn_code'),
                    'gross_weight': float(row['gross_weight']),
                    'net_weight': float(row['net_weight']),
                    'supplier_id': supplier_map.get(row.get('supplier_id')),
                    'melting_percentage': float(row.get('melting_percentage', 0)),
                    'status': 'AVAILABLE'
                })
                category_counters[category_id] += 1

    return inventory
```

### Step 3: Import to Supabase

**import_to_supabase.py:**

```python
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from transform_data import transform_categories, transform_suppliers, transform_inventory

load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def import_data():
    try:
        # Import categories
        categories = transform_categories('categories.csv')
        category_result = supabase.table('categories').insert(categories).execute()
        print(f"Imported {len(categories)} categories")

        # Create category mapping for inventory
        category_map = {old_id: new_cat['id'] for old_id, new_cat in zip(
            [c['old_id'] for c in categories], category_result.data)}

        # Import suppliers
        suppliers = transform_suppliers('suppliers.csv')
        supplier_result = supabase.table('suppliers').insert(suppliers).execute()
        print(f"Imported {len(suppliers)} suppliers")

        # Create supplier mapping
        supplier_map = {old_id: new_sup['id'] for old_id, new_sup in zip(
            [s['old_id'] for s in suppliers], supplier_result.data)}

        # Import inventory using RPC function for proper category_item_no assignment
        inventory_items = transform_inventory('inventory.csv', category_map, supplier_map)

        for item in inventory_items:
            try:
                result = supabase.rpc('add_inventory_item', {
                    'p_category_id': item['category_id'],
                    'p_product_name': item['product_name'],
                    'p_description': item['description'],
                    'p_hsn_code': item['hsn_code'],
                    'p_gross_weight': item['gross_weight'],
                    'p_net_weight': item['net_weight'],
                    'p_supplier_id': item['supplier_id'],
                    'p_melting_percentage': item['melting_percentage']
                }).execute()
                print(f"Added inventory item: {item['product_name']}")
            except Exception as e:
                print(f"Error adding item {item['product_name']}: {e}")

        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    import_data()
```

### Step 4: Environment Configuration

Create `.env` file:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Step 5: Validation

After migration, validate the data:

```sql
-- Check category summary
SELECT * FROM category_summary_view;

-- Check total summary
SELECT * FROM total_summary_view;

-- Verify category_item_no uniqueness
SELECT category_id, category_item_no, COUNT(*)
FROM inventory
WHERE status = 'AVAILABLE'
GROUP BY category_id, category_item_no
HAVING COUNT(*) > 1;

-- Check stock movements
SELECT * FROM stock_ledger_view LIMIT 10;
```

## Key Changes in New Schema

1. **Serialized Inventory**: Each physical piece has its own row
2. **Category Item Numbers**: Reusable per-category sequential IDs
3. **No Unit Price**: Pricing handled at bill level
4. **Immutable Ledger**: All stock movements tracked
5. **Status-based**: Items marked as AVAILABLE/SOLD/RESERVED
6. **UUID Primary Keys**: For better distributed system support
7. **RPC Functions**: Atomic operations for stock management

## Rollback Plan

Keep SQLite backups until migration is fully validated:

```bash
# Backup original SQLite database
cp original_database.db backup_$(date +%Y%m%d).db

# Export Supabase data back to CSV if needed
# Use Supabase dashboard export features
```
