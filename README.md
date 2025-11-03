# Roopkala Jewellers - Unified Billing & Management System

A comprehensive desktop application for jewelry shop management, built with Python and PyQt5.

## ✨ Features

### 🧾 Billing & Invoicing

- Professional invoice generation with PDF export
- Real-time GST calculation (CGST + SGST)
- Custom order support (non-inventory items)
- Automatic stock deduction on invoice generation
- Customer management with phone and GSTIN tracking
- Override total for custom pricing
- Print and save invoice functionality

### 📦 Stock Management

- Serialized inventory tracking (each item is unique)
- Category-wise organization
- Supplier management
- HSN code autocomplete from history
- Bulk label printing for inventory items
- CSV export for inventory data
- Category-wise and total inventory summaries
- Stock movement tracking

### 📊 Analytics & Reports

- Sales analytics with date range filtering
- Top-selling items tracking
- Inventory analytics and valuation
- Low stock alerts
- Category-wise breakdowns
- Export reports to CSV

### ⚙️ Settings & Configuration

- Company information management
- Tax rate configuration (CGST/SGST)
- Invoice preferences
- Database backup and restore
- Data export functionality

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Windows OS (for executable build)

### From Source

1. **Clone or download the repository**

   ```bash
   git clone https://github.com/Krish1342/Billing-Software.git
   cd Billing-Software
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**

   - Copy `.env.template` to `.env` (if using Supabase)
   - Update `settings.json` with your company details

4. **Run the application**
   ```bash
   python main.py
   ```

### Using Pre-built Executable

1. Download the latest release from the releases page
2. Extract the ZIP file
3. Ensure `settings.json` is in the same folder as the executable
4. Run `RoopkalaBillingSystem.exe`

## 🛠️ Building the Executable

### Quick Build

```bash
python build.bat
```

Or use the Python script directly:

```bash
python build_exe.py
```

See [BUILD_README.md](BUILD_README.md) for detailed build instructions.

## 📁 Project Structure

```
Billing-Software/
├── main.py                    # Application entry point
├── settings.json              # Configuration file
├── requirements.txt           # Python dependencies
├── build_exe.py              # Executable build script
├── build.bat                 # Windows build batch file
│
├── ui/                       # User interface modules
│   ├── main_window.py        # Main application window
│   ├── billing_tab.py        # Billing interface
│   ├── stock_tab.py          # Stock management
│   ├── analytics_tab.py      # Analytics & reports
│   ├── settings_tab.py       # Settings interface
│   └── keyboard_navigation.py # Keyboard shortcuts
│
├── logic/                    # Business logic modules
│   ├── database_manager.py   # Database operations (Supabase)
│   ├── local_database_manager.py # Local SQLite operations
│   ├── database_config.py    # Database configuration
│   ├── calculator.py         # Tax and totals calculation
│   ├── pdf_generator.py      # Invoice PDF generation
│   ├── label_printer.py      # Label printing
│   ├── validators.py         # Data validation
│   └── models.py             # Data models
│
├── tests/                    # Test suites (dev only)
│   ├── test_suite.py         # Comprehensive module tests
│   └── test_advanced.py      # Business logic tests
│
├── database/                 # Database schema and docs
│   ├── supabase_schema.sql   # Supabase database schema
│   ├── migration_guide.md    # Migration documentation
│   └── test_cases.sql        # Test data
│
├── invoices/                 # Generated invoice PDFs
├── labels/                   # Generated label PDFs
└── docs/                     # Additional documentation
```

## 💡 Usage Guide

### Creating an Invoice

1. **Start from Billing Tab** (Ctrl+1)
2. **Enter customer details**
   - Name (required)
   - Phone, address (optional)
3. **Add items**
   - Select category
   - Choose item by weight (for stock items)
   - OR check "Custom Order" for made-to-order items
   - Enter rate and quantity
4. **Review totals**
   - Automatic tax calculation
   - Optional: Override total for custom pricing
5. **Generate invoice** (Enter key or click button)
   - PDF is automatically saved
   - Stock is deducted for inventory items
   - Print or save as needed

### Managing Stock

1. **Go to Stock Management Tab** (Ctrl+2)
2. **Add Categories** (if needed)
3. **Add Suppliers** (if needed)
4. **Add Products**
   - Select category
   - Enter weights (gross and net)
   - Set supplier
   - Each item gets a unique serial number
5. **View inventory summary**
   - Category-wise breakdown
   - Export to CSV
   - Print labels

### Keyboard Shortcuts

- **Ctrl+N**: New Invoice
- **Ctrl+1 to Ctrl+4**: Switch between tabs
- **Ctrl+Shift+C**: Focus customer field
- **Ctrl+Q**: Exit application
- **F1**: Show help/shortcuts
- **Enter**: Move to next field or perform action

## 🔧 Configuration

### settings.json

```json
{
  "company": {
    "name": "Your Company Name",
    "address": "Your Address",
    "phone": "+91-XXXXXXXXXX",
    "email": "your@email.com",
    "gstin": "YOUR_GSTIN"
  },
  "tax": {
    "cgst_rate": "1.5",
    "sgst_rate": "1.5"
  },
  "invoice": {
    "prefix": "INV",
    "start_number": 1001,
    "default_save_path": "invoices",
    "require_confirmation": false,
    "show_success_dialog": false
  }
}
```

### Database Options

**Option 1: Local SQLite** (Default)

- No additional configuration needed
- Database file created automatically
- Suitable for single computer use

**Option 2: Supabase** (Cloud)

- Create `.env` file with Supabase credentials:
  ```
  SUPABASE_URL=your_supabase_url
  SUPABASE_KEY=your_supabase_key
  ```
- Suitable for multi-location access
- See `database/supabase_schema.sql` for schema

## 📝 PDF Invoice Features

The application generates professional PDF invoices with:

- **Enhanced company header** with decorative elements
- **Dual-bordered elegant layout** in maroon and gold
- **Comprehensive invoice details** box with customer info
- **Detailed items table** with alternating row colors
- **Professional totals section** with tax breakdown
- **Signature area** with company authorization
- **Terms and conditions** footer

## 🔐 Data Security

- Local database with file-level security
- Optional cloud backup with Supabase
- Built-in backup and restore functionality
- Export all data to CSV for external backup

## 🐛 Troubleshooting

### Application won't start

- Ensure Python 3.8+ is installed
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify `settings.json` exists

### PDF generation fails

- Check write permissions in the application directory
- Ensure `invoices` folder exists or can be created
- Verify reportlab is installed correctly

### Database errors

- For SQLite: Check write permissions
- For Supabase: Verify `.env` credentials
- Try database backup and restore from Settings tab

### Missing stock items

- Check if items were marked as "Sold" in previous invoices
- Verify category filter in Stock Management tab
- Use search functionality to locate items

## 🤝 Contributing

This is a production application for Roopkala Jewellers. For feature requests or bug reports, please contact the development team.

## 📜 License

Proprietary software for Roopkala Jewellers.

## 👥 Support

For technical support or questions:

- Check the documentation in the `docs/` folder
- Review this README and BUILD_README.md
- Contact the development team

## 🗓️ Version History

### Version 2.0.0 (2025-11-02)

- Enhanced PDF invoice formatting with professional styling
- Complete UI review and optimization
- Repository cleanup and organization
- Executable build system implementation
- Improved documentation

### Version 1.0.0

- Initial release with core functionality
- Billing, stock management, and analytics
- Local and cloud database support

---

**Developed with ❤️ for Roopkala Jewellers**
