# 🏪 Unified Jewelry Management System

A comprehensive PyQt5-based application that combines billing and inventory management for jewelry shops. This unified system automatically manages stock levels when bills are generated and provides complete business management functionality.

## 🚀 Quick Start

### Option 1: Use the Launcher (Recommended)

```bash
python launch_unified_app.py
```

The launcher will:

- Check system requirements
- Install missing dependencies automatically
- Verify all files are present
- Create default settings if needed
- Launch the application

### Option 2: Direct Launch

```bash
python unified_main_app.py
```

## 📋 Prerequisites

- **Python 3.7+** (Tested with Python 3.12.1)
- **Windows OS** (Optimized for Windows PowerShell)

## 📦 Dependencies

All dependencies are automatically handled by the launcher, or install manually:

```bash
pip install PyQt5==5.15.10
pip install reportlab==4.0.8
pip install Pillow==10.1.0
```

Or use the requirements file:

```bash
pip install -r requirements_unified.txt
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_unified_app.py
```

The test suite validates:

- ✅ All module imports
- ✅ Database operations and stock deduction
- ✅ Calculator functionality
- ✅ Settings management
- ✅ System integration

## 🏗️ System Architecture

### Core Components

1. **unified_main_app.py** - Main application window with tabbed interface
2. **unified_database.py** - Database manager with automatic stock deduction
3. **billing_tab.py** - Invoice creation and billing functionality
4. **stock_tab.py** - Inventory and product management
5. **analytics_tab.py** - Sales reports and analytics
6. **settings_tab.py** - Application configuration
7. **calc.py** - High-precision calculation engine

### Key Features

#### 🧾 Billing System

- **Invoice Generation** with automatic PDF creation
- **Customer Management** with history tracking
- **Tax Calculations** (CGST/SGST) with configurable rates
- **Multiple Payment Methods** support
- **Automatic Stock Deduction** when bills are generated

#### 📦 Inventory Management

- **Product Management** with categories and suppliers
- **Stock Tracking** with movement history
- **Low Stock Alerts** for inventory monitoring
- **Batch Operations** for bulk updates
- **Real-time Stock Updates** during billing

#### 📊 Analytics & Reporting

- **Sales Analytics** with date range filtering
- **Inventory Reports** with stock levels
- **Customer Analytics** and purchase history
- **Export Functionality** to CSV/Excel
- **Visual Charts** for sales trends

#### ⚙️ Configuration Management

- **Company Settings** (Name, Address, GST details)
- **Tax Configuration** (CGST/SGST rates)
- **Application Preferences** (Theme, Auto-save)
- **Database Backup/Restore** functionality

## 🗄️ Database Schema

The system uses SQLite with the following main tables:

- **products** - Product catalog with stock quantities
- **categories** - Product categorization
- **suppliers** - Vendor information
- **customers** - Customer database
- **invoices** - Bill records
- **invoice_items** - Line items for each bill
- **stock_movements** - Stock change history
- **settings** - Configuration storage

## 💡 Key Innovation: Automatic Stock Deduction

When a bill is generated, the system:

1. ✅ Validates stock availability for all items
2. ✅ Deducts quantities from inventory automatically
3. ✅ Records stock movements with timestamps
4. ✅ Updates product quantities in real-time
5. ✅ Prevents overselling with stock checks

## 🎯 Usage Examples

### Creating an Invoice with Stock Deduction

1. Navigate to **Billing** tab
2. Add customer details
3. Add products to the invoice
   - System automatically checks stock availability
   - Shows current stock levels
4. Generate invoice
   - PDF is created automatically
   - Stock is deducted immediately
   - Stock movements are logged

### Managing Inventory

1. Navigate to **Stock Management** tab
2. Add/Edit products with quantities
3. Organize by categories and suppliers
4. Monitor stock levels and movements
5. Set up low stock alerts

### Viewing Analytics

1. Navigate to **Analytics** tab
2. Select date ranges for reports
3. View sales summaries and trends
4. Export data for external analysis
5. Monitor top products and customers

## 🔧 Configuration

The system uses `settings.json` for configuration:

```json
{
  "company": {
    "name": "Roopkala Jewellers",
    "address": "Shop No. 123, Jewelry Street",
    "gstin": "27XXXXX1234X1ZX"
  },
  "tax": {
    "cgst_rate": "1.5",
    "sgst_rate": "1.5"
  },
  "app": {
    "theme": "light",
    "auto_save": true
  }
}
```

## 📁 File Structure

```
Billing-Software/
├── unified_main_app.py          # Main application entry point
├── unified_database.py          # Database manager
├── billing_tab.py               # Billing interface
├── stock_tab.py                 # Inventory management
├── analytics_tab.py             # Reports and analytics
├── settings_tab.py              # Configuration management
├── calc.py                      # Calculation engine
├── pdf_generator.py             # PDF generation
├── launch_unified_app.py        # Application launcher
├── test_unified_app.py          # Test suite
├── requirements_unified.txt     # Dependencies
├── settings.json                # Configuration file
└── jewelry_shop.db              # SQLite database
```

## 🛠️ Development Notes

### Precision Calculations

- All monetary calculations use `Decimal` class
- Prevents floating-point precision errors
- Ensures accurate tax and total calculations

### Database Design

- Foreign key constraints for data integrity
- Indexed fields for performance
- Transaction support for atomic operations

### UI Framework

- PyQt5 for native desktop experience
- Tabbed interface for organized functionality
- Signal-slot architecture for real-time updates

## 🐛 Troubleshooting

### Common Issues

1. **"PyQt5 not found"**

   ```bash
   pip install PyQt5==5.15.10
   ```

2. **"Database locked"**

   - Ensure no other instances are running
   - Restart the application

3. **"PDF generation failed"**

   ```bash
   pip install reportlab==4.0.8
   ```

4. **Permission errors on Windows**
   - Run as administrator if needed
   - Check file permissions in the application directory

### Debug Mode

Set environment variable for detailed logging:

```bash
set JEWELRY_DEBUG=1
python unified_main_app.py
```

## 📞 Support

For technical support or feature requests:

1. Check the test suite output for specific errors
2. Review the application logs in the console
3. Ensure all dependencies are properly installed
4. Verify file permissions and disk space

## 🔄 Migration from Separate Apps

This unified system combines:

- **Previous Tkinter Billing App** → Now integrated in Billing tab
- **Previous Streamlit Stock App** → Now integrated in Stock Management tab
- **Enhanced with automatic stock deduction** during billing
- **Added analytics and reporting** capabilities
- **Unified database** for better data consistency

## 🎉 Success Indicators

✅ **All tests pass** in `test_unified_app.py`
✅ **Stock deduction works** automatically during billing
✅ **PDF invoices generate** correctly
✅ **Real-time stock updates** across all tabs
✅ **Settings persist** between sessions
✅ **Database operations** complete successfully

---

**🏪 Ready to manage your jewelry business efficiently!**
