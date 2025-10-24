# Operational Notes: Concurrency & PyQt Integration

## Database Concurrency Handling

### Row-Level Locking

The system uses PostgreSQL's `SELECT FOR UPDATE` in critical sections:

```sql
-- In create_bill_with_items RPC
PERFORM 1 FROM inventory
WHERE id = v_inventory_id AND status = 'AVAILABLE'
FOR UPDATE; -- Locks the row until transaction completes
```

**Benefits:**

- Prevents race conditions when multiple users try to sell the same item
- Ensures atomic stock deduction
- Maintains data consistency under high concurrency

### Advisory Locks for Category Item Numbers

For high-concurrency scenarios, consider advisory locks:

```sql
-- Example: Lock category before assigning item numbers
SELECT pg_advisory_lock(hashtext(p_category_id::text));
-- ... assign category_item_no ...
SELECT pg_advisory_unlock(hashtext(p_category_id::text));
```

### Transaction Isolation

All RPC functions run in transaction context:

- Stock movements are atomic with inventory updates
- Bill creation either succeeds completely or fails completely
- No partial states possible

## PyQt Integration Best Practices

### 1. Database Connection Management

```python
# Use environment variables for configuration
load_dotenv()
supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_ANON_KEY")
)

# Test connection on startup
try:
    supabase.table('categories').select('*').limit(1).execute()
    print("✅ Database connected")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

### 2. Error Handling Patterns

```python
def create_bill_safe(self, bill_data):
    """Safe bill creation with proper error handling."""
    try:
        result = self.supabase.rpc('create_bill_with_items', bill_data).execute()

        # Check for RPC errors
        if hasattr(result, 'error') and result.error:
            raise Exception(result.error['message'])

        return result.data

    except Exception as e:
        # Log error for debugging
        print(f"Bill creation failed: {e}")

        # Show user-friendly message
        if "not available for sale" in str(e):
            QMessageBox.warning(self, "Item Unavailable",
                              "This item has already been sold.")
        else:
            QMessageBox.critical(self, "Error", f"Failed to create bill: {e}")

        return None
```

### 3. Realtime Updates

Since Supabase realtime requires additional setup, use polling for inventory updates:

```python
class InventoryPoller(QThread):
    inventory_changed = pyqtSignal(dict)

    def __init__(self, supabase_client):
        super().__init__()
        self.supabase = supabase_client
        self.running = True
        self.last_hash = None

    def run(self):
        while self.running:
            try:
                # Get current inventory summary
                result = self.supabase.table('total_summary_view').select('*').execute()
                current_hash = hash(str(result.data))

                # Only emit if data changed
                if current_hash != self.last_hash:
                    self.inventory_changed.emit(result.data[0])
                    self.last_hash = current_hash

                self.msleep(5000)  # Poll every 5 seconds
            except Exception as e:
                print(f"Polling error: {e}")
                self.msleep(10000)  # Wait longer on error
```

### 4. CSV Export Integration

```python
def export_category_csv_pyqt(self, category_id, filename):
    """Export category data to CSV with progress indication."""
    try:
        # Show progress dialog
        progress = QProgressDialog("Exporting data...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        progress.setValue(10)

        # Get data via RPC
        result = self.supabase.rpc('get_category_csv_data', {
            'p_category_id': category_id
        }).execute()
        progress.setValue(50)

        if not result.data:
            progress.close()
            QMessageBox.information(self, "No Data", "No items found in category")
            return False

        # Write CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Category Item No', 'Product Name', 'Gross Weight',
                           'Net Weight', 'Supplier Code', 'Added At'])

            for i, item in enumerate(result.data):
                writer.writerow([
                    item['category_item_no'], item['product_name'],
                    f"{item['gross_weight']:.3f}", f"{item['net_weight']:.3f}",
                    item['supplier_code'], item['added_at']
                ])

                # Update progress
                progress.setValue(50 + (i * 40 // len(result.data)))
                if progress.wasCanceled():
                    return False

        progress.setValue(100)
        progress.close()

        QMessageBox.information(self, "Success",
                              f"Exported {len(result.data)} items to {filename}")
        return True

    except Exception as e:
        progress.close()
        QMessageBox.critical(self, "Export Error", str(e))
        return False
```

## Performance Optimization

### 1. Database Indexes

The schema includes optimized indexes:

```sql
-- Existing indexes in schema
CREATE INDEX idx_inventory_category_status ON inventory(category_id, status);
CREATE INDEX idx_inventory_status ON inventory(status);
```

### 2. View Materialization

For large datasets, consider materialized views:

```sql
-- Create materialized view for category summary
CREATE MATERIALIZED VIEW category_summary_materialized AS
SELECT * FROM category_summary_view;

-- Refresh periodically
REFRESH MATERIALIZED VIEW category_summary_materialized;
```

### 3. PyQt Table Optimization

```python
def load_products_optimized(self):
    """Load products with pagination and virtual scrolling."""
    try:
        # Use pagination for large datasets
        offset = self.current_page * self.page_size

        result = self.supabase.table('current_stock_view')\
            .select('*')\
            .range(offset, offset + self.page_size - 1)\
            .execute()

        # Update table efficiently
        self.products_table.setRowCount(len(result.data))

        for row, item in enumerate(result.data):
            # Only create items for visible rows
            if self.products_table.isRowHidden(row):
                continue

            self.products_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            # ... other columns

    except Exception as e:
        print(f"Error loading products: {e}")
```

## Security Considerations

### 1. Environment Variables

Store sensitive credentials securely:

```bash
# .env file (never commit to git)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### 2. RPC Security

Supabase RPCs run with database user permissions:

- Use Row Level Security (RLS) policies if needed
- Validate inputs in RPC functions
- Use prepared statements (automatic in Supabase)

### 3. Input Validation

```python
def validate_inventory_input(self, data):
    """Validate inventory data before submission."""
    errors = []

    if not data.get('product_name', '').strip():
        errors.append("Product name is required")

    try:
        gross_weight = float(data['gross_weight'])
        net_weight = float(data['net_weight'])

        if gross_weight <= 0 or net_weight <= 0:
            errors.append("Weights must be positive")

        if net_weight > gross_weight:
            errors.append("Net weight cannot exceed gross weight")

    except (ValueError, KeyError):
        errors.append("Invalid weight values")

    return errors
```

## Deployment Checklist

### 1. Database Setup

- [ ] Run `supabase_schema.sql` in Supabase SQL editor
- [ ] Verify all RPC functions created successfully
- [ ] Run `test_cases.sql` to validate functionality
- [ ] Create database backups schedule

### 2. Application Configuration

- [ ] Set environment variables in production
- [ ] Test database connectivity
- [ ] Verify CSV export functionality
- [ ] Test bill creation and reversal

### 3. Monitoring

- [ ] Set up Supabase dashboard monitoring
- [ ] Monitor RPC function performance
- [ ] Track database storage usage
- [ ] Monitor concurrent connections

## Troubleshooting Common Issues

### 1. Connection Errors

```python
# Test connection health
def test_connection(self):
    try:
        result = self.supabase.table('categories').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
```

### 2. RPC Errors

```sql
-- Check RPC function exists
SELECT routine_name FROM information_schema.routines
WHERE routine_type = 'FUNCTION'
AND routine_name LIKE '%inventory%';
```

### 3. Performance Issues

```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
WHERE query LIKE '%inventory%'
ORDER BY total_time DESC;
```

## Integration with Existing UI

Your existing UI components will work with minimal changes:

1. **Stock Tab**: Already compatible - uses `get_products()` method
2. **Billing Tab**: Update to use new `create_invoice()` method
3. **Analytics**: Use new view-based summary methods
4. **Settings**: No changes needed

The new database manager maintains backward compatibility while adding enhanced features like serialized inventory and category item number reuse.
