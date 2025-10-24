# Jewelry Management System - Supabase Edition

A production-ready jewelry billing and inventory management system built with PyQt5 and Supabase PostgreSQL backend.

## 🌟 Key Features

### 📦 Advanced Inventory Management

- **Serialized Inventory**: Each jewelry piece tracked individually with unique category item numbers
- **Category-based Organization**: Rings, chains, necklaces, etc. with reusable item numbering
- **Smart Slot Reuse**: When items are sold, their category numbers become available for new items
- **Real-time Stock Tracking**: Live updates across all connected clients

### 🧾 Professional Billing System

- **Atomic Bill Creation**: Thread-safe bill generation with automatic stock deduction
- **Bill Reversal**: Complete restoration of sold items back to available inventory
- **GST Compliance**: Automatic CGST/SGST calculation with HSN code support
- **Customer Management**: Integrated customer database with GSTIN support

### 📊 Business Intelligence

- **Category-wise Analytics**: Summary reports by jewelry type
- **Stock Movement Ledger**: Complete audit trail of all inventory changes
- **CSV Export**: Detailed category reports and summary data export
- **Real-time Dashboard**: Live inventory metrics and alerts

### 🔒 Enterprise-grade Backend

- **Supabase PostgreSQL**: Reliable cloud database with automatic backups
- **Concurrent Safety**: Row-level locking prevents double-selling
- **Immutable Ledger**: All stock movements permanently recorded
- **UUID Primary Keys**: Distributed system ready architecture

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Supabase account (free tier available)

### Installation

1. **Clone and Install**

   ```bash
   git clone <repository-url>
   cd Billing-Software
   pip install -r requirements.txt
   ```

2. **Setup Supabase**

   - Create project at [supabase.com](https://supabase.com)
   - Run `database/supabase_schema.sql` in SQL Editor
   - Copy your project URL and anon key

3. **Configure Environment**

   ```bash
   cp .env.template .env
   # Edit .env with your Supabase credentials
   ```

4. **Launch Application**
   ```bash
   python main.py
   ```

📖 **Detailed setup instructions in [SETUP.md](SETUP.md)**

## 💎 System Architecture

### Database Schema

```
├── categories (Rings, Chains, etc.)
├── suppliers (Vendor information)
├── inventory (Serialized items with category_item_no)
├── customers (Customer database)
├── bills (Invoice headers)
├── bill_items (Invoice line items)
└── stock_movements (Immutable audit ledger)
```

### Key Innovations

#### 🔄 Category Item Number Reuse

```sql
-- When Ring #37 is sold, the next added ring gets #37 (if available)
SELECT get_next_category_item_no('ring-category-uuid');
-- Returns: 37 (reuses sold item's slot)
```

#### ⚡ Atomic Bill Creation

```sql
-- Complete bill creation with stock deduction in single transaction
SELECT create_bill_with_items(
  'RK-2024-001',           -- Bill number
  'Customer Name',         -- Customer
  '{"items": [...]}',      -- Items array
  1.50, 1.50              -- Tax rates
);
```

#### 🔙 Intelligent Bill Reversal

```sql
-- Restore all items from a bill back to available inventory
SELECT reverse_bill('bill-uuid');
-- Items return to exact same category_item_no if possible
```

## 📱 User Interface

### Stock Management

- **Add Items**: Individual piece entry with weight tracking
- **Category Management**: Organize by jewelry types
- **Supplier Database**: Vendor information and contacts
- **Live Summary**: Real-time counts and weight totals

### Billing System

- **Item Selection**: Choose from available inventory
- **Automatic Calculations**: GST, rounding, totals
- **Customer Integration**: Link bills to customer database
- **Print-ready Invoices**: Professional PDF generation

### Analytics Dashboard

- **Category Reports**: Items count, weight, value by type
- **Stock Movements**: Complete transaction history
- **Export Tools**: CSV download for accounting systems
- **Live Metrics**: Real-time inventory updates

## 🔧 Advanced Features

### Concurrency Control

```python
# Row-level locking prevents race conditions
PERFORM 1 FROM inventory
WHERE id = item_id AND status = 'AVAILABLE'
FOR UPDATE;  -- Locks until transaction completes
```

### Real-time Updates

```python
# Background polling for inventory changes
class InventoryPoller(QThread):
    def run(self):
        # Monitor database for changes
        # Emit signals to update UI
```

### CSV Export Integration

```python
# Export category data via RPC
data = supabase.rpc('get_category_csv_data', {
    'p_category_id': category_id
}).execute()
```

## 📁 Project Structure

```
Billing-Software/
├── main.py                    # Application entry point
├── ui/                        # PyQt5 interface components
│   ├── main_window.py        # Main application window
│   ├── stock_tab.py          # Inventory management
│   ├── billing_tab.py        # Invoice creation
│   └── analytics_tab.py      # Reports and analytics
├── logic/                     # Business logic
│   ├── database_manager.py   # Supabase integration
│   ├── models.py             # Data models
│   └── calculator.py         # Tax calculations
├── database/                  # Database assets
│   ├── supabase_schema.sql   # Complete database schema
│   ├── test_cases.sql        # Validation tests
│   ├── migration_guide.md    # Data migration help
│   └── operational_notes.md  # Production guidance
└── examples/                  # Integration examples
    └── pyqt_supabase_example.py
```

## 🧪 Testing

### Database Validation

```bash
# Run in Supabase SQL Editor
\i database/test_cases.sql
```

### Application Testing

```bash
python examples/pyqt_supabase_example.py
```

### Migration Testing

```bash
# Follow database/migration_guide.md for existing data
```

## 🔐 Security & Production

### Environment Configuration

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
DEBUG=False
```

### Database Security

- Row Level Security (RLS) ready
- UUID primary keys for security
- Prepared statements prevent injection
- Audit trail for all changes

### Backup Strategy

- Automatic Supabase backups
- CSV export capabilities
- Complete schema versioning
- Point-in-time recovery available

## 📈 Performance Optimization

### Database Indexes

```sql
CREATE INDEX idx_inventory_category_status ON inventory(category_id, status);
CREATE INDEX idx_bill_items_inventory_id ON bill_items(inventory_id);
```

### UI Optimization

- Virtual scrolling for large datasets
- Background threading for database operations
- Efficient table population strategies
- Real-time update throttling

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Follow existing code style and patterns
4. Add tests for new functionality
5. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Documentation

- **Setup Guide**: [SETUP.md](SETUP.md)
- **Migration Help**: [database/migration_guide.md](database/migration_guide.md)
- **Operations Manual**: [database/operational_notes.md](database/operational_notes.md)
- **API Examples**: [examples/](examples/)

## 🏆 Production Ready Features

✅ **Concurrent Access**: Multi-user safe operations  
✅ **Data Integrity**: ACID transactions with rollback  
✅ **Audit Trail**: Complete change history  
✅ **Business Logic**: Industry-specific workflows  
✅ **Scalability**: Cloud-native architecture  
✅ **Backup/Recovery**: Automated data protection  
✅ **Export/Import**: Accounting system integration  
✅ **Real-time Updates**: Live inventory synchronization

---

**Built for modern jewelry businesses requiring reliable, scalable inventory and billing management.**
