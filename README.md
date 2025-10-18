# Roopkala Jewellers Billing System

A professional desktop billing application built with Python 3.10+, Tkinter, and SQLite designed specifically for Roopkala Jewellers. This system handles precise monetary calculations using `decimal.Decimal`, supports GST-inclusive billing, and generates professional PDF invoices.

## Features

### Core Features
- **Desktop GUI Application** - Built with Tkinter for a native desktop experience
- **Precise Money Calculations** - Uses `decimal.Decimal` internally to avoid floating-point errors
- **Flexible Input System** - Enter any 2 of: Quantity, Rate, Amount, or Total Inclusive
- **GST Support** - Automatic CGST (1.5%) and SGST (1.5%) calculation (configurable)
- **Rounding Control** - Proper rounding with ROUND_HALF_UP, rounded-off row for total adjustments
- **SQLite Database** - Persistent storage for all invoices
- **PDF Export** - Professional A4 invoice generation using ReportLab
- **No Authentication** - Designed for trusted admin users only

### Technical Highlights
- **Decimal Precision**: All monetary values use `Decimal` to ensure accuracy
- **Flexible Calculations**: Provide any two parameters and the system calculates the rest
- **Configurable Settings**: Easy-to-edit JSON file for company info and tax rates
- **Reusable Calculator Module**: `calc.py` can be used independently
- **Comprehensive Tests**: Unit tests included for calculation logic

## Project Structure

```
BillingSoftware/
│
├── main.py                 # Application entry point
├── calc.py                 # Core calculation module (reusable)
├── invoice_ui.py           # Tkinter GUI for invoice management
├── db_handler.py           # SQLite database operations
├── pdf_generator.py        # PDF invoice generation (ReportLab)
├── settings.json           # Configuration file (editable)
├── requirements.txt        # Python dependencies
├── test_calc.py           # Unit tests for calc.py
├── .gitignore             # Git ignore file
└── roopkala_billing.db    # SQLite database (auto-created)
```

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Step 1: Clone or Download
```bash
cd BillingSoftware
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

The required packages are:
- `reportlab>=4.0.0` - PDF generation
- `Pillow>=10.0.0` - Image handling for ReportLab

### Step 3: Verify Installation
Run the unit tests to ensure everything is working:
```bash
python test_calc.py
```

All tests should pass.

## Configuration

Edit `settings.json` to customize the application:

```json
{
  "company": {
    "name": "Roopkala Jewellers",
    "address_line1": "123 Main Street",
    "address_line2": "Jewellery Market, City - 400001",
    "phone": "+91 98765 43210",
    "email": "info@roopkalajewellers.com",
    "gstin": "27AAAAA0000A1Z5"
  },
  "tax": {
    "cgst_rate": "1.5",
    "sgst_rate": "1.5"
  },
  "invoice": {
    "prefix": "RKJ",
    "starting_number": 1001
  },
  "precision": {
    "quantity_decimals": 3,
    "money_decimals": 2
  }
}
```

### Configuration Options

- **company**: Your business details (appears on invoices)
- **tax**: GST rates (CGST + SGST percentages)
- **invoice**: Invoice numbering (prefix + starting number)
- **precision**: Decimal places for display

## Usage

### Starting the Application

```bash
python main.py
```

### Creating an Invoice

1. **Invoice Details Section**
   - Invoice number is auto-generated
   - Set the invoice date
   - Enter customer information (name, address, phone, GSTIN)

2. **Adding Line Items**
   - Enter item description (required)
   - Enter HSN code (optional)
   - Provide **any 2 of these 3**: Quantity, Rate, or Amount
   - Click "Add Item"
   - The system automatically calculates the missing value

3. **Viewing Totals**
   - Subtotal, CGST, SGST, and Final Total are calculated automatically
   - **Optional**: Use "Override Total" to specify exact final amount
   - System will add "Rounded Off" row to match your target total

4. **Saving and PDF**
   - Click "Save Invoice" to store in database
   - Click "Generate PDF" to create a printable invoice
   - Choose save location for PDF

### Loading Existing Invoices

1. Click "Load Invoice"
2. Enter the invoice number
3. Invoice will be loaded with all details

### Creating New Invoice

Click "New Invoice" to clear the form and start fresh. Invoice number will auto-increment.

## Calculation Examples

The calculation module supports flexible input scenarios:

### Example 1: Quantity + Rate
```python
from calc import create_calculator

calc = create_calculator("1.5", "1.5")  # CGST 1.5%, SGST 1.5%

result = calc.calculate_from_two_params(
    quantity=10.5,    # 10.5 grams
    rate=6500         # ₹6500 per gram
)

# Result:
# quantity: 10.500
# rate: 6500.00
# amount: 68250.00
# cgst: 1023.75 (1.5%)
# sgst: 1023.75 (1.5%)
# total_inclusive: 70297.50
```

### Example 2: Quantity + Total Inclusive
```python
result = calc.calculate_from_two_params(
    quantity=5,
    total_inclusive=5150  # Customer wants to pay exactly ₹5150
)

# System calculates:
# amount: 5000.00 (back-calculated from total)
# rate: 1000.00 (derived from amount/quantity)
# cgst: 75.00
# sgst: 75.00
```

### Example 3: With Rounded Off
```python
result = calc.calculate_from_two_params(
    quantity=10,
    rate=970.87,
    total_inclusive=10000  # Round to nice number
)

# System adds rounded_off to match target total
```

## Database

The application uses SQLite for data persistence:

- **Database File**: `roopkala_billing.db` (auto-created)
- **Tables**: 
  - `invoices` - Invoice headers
  - `line_items` - Invoice line items

### Backing Up Data

Simply copy the `roopkala_billing.db` file to a safe location.

### Resetting Data

Delete `roopkala_billing.db` and restart the application. A fresh database will be created.

## Testing

Run the comprehensive unit tests:

```bash
# Run with unittest
python test_calc.py

# Or with pytest (if installed)
python -m pytest test_calc.py -v
```

### Test Coverage

The test suite includes:
- ✅ All calculation scenarios (6 different input combinations)
- ✅ Decimal precision and rounding
- ✅ GST calculations
- ✅ Rounded-off adjustments
- ✅ Error handling
- ✅ Edge cases (very small/large numbers)
- ✅ Real-world jewellery examples

## Key Design Decisions

### 1. No Authentication
Per requirements, no login page or admin settings UI. The app is designed for trusted admin users only. Settings are in `settings.json` which developers can edit directly.

### 2. Decimal Precision
All monetary calculations use `decimal.Decimal` to avoid floating-point arithmetic errors. This is critical for financial applications.

### 3. Flexible Input
Users can provide:
- Quantity + Rate (most common)
- Quantity + Amount
- Quantity + Total Inclusive
- Rate + Amount
- Rate + Total Inclusive
- Amount + Total Inclusive

The system calculates missing values automatically.

### 4. Rounding Strategy
- **Internal calculations**: Full precision with `Decimal`
- **Display/Storage**: Quantized with ROUND_HALF_UP
  - Quantity: 3 decimals (0.001)
  - Money: 2 decimals (0.01)
- **Rounded Off**: Adjusts calculated total to match user-specified total

### 5. GST Inclusive Deduction
When user provides `total_inclusive`, the system:
1. Deducts GST to get taxable amount
2. Calculates CGST and SGST separately
3. Adds "Rounded Off" row if needed to match exact total

## Troubleshooting

### Issue: PDF Generation Fails
**Solution**: Ensure ReportLab is installed:
```bash
pip install reportlab
```

### Issue: Database Locked
**Solution**: Close all instances of the application. Only one instance should access the database at a time.

### Issue: Decimal Precision Errors
**Solution**: This shouldn't happen as we use `Decimal`. If you see issues, ensure you're not mixing float arithmetic in custom code.

### Issue: Invoice Number Already Exists
**Solution**: The system auto-increments invoice numbers. If you manually edit the database, ensure uniqueness.

## Development

### Adding New Features

The codebase is modular:

- **Calculation Logic**: Modify `calc.py`
- **Database Schema**: Update `db_handler.py`
- **UI Changes**: Edit `invoice_ui.py`
- **PDF Layout**: Customize `pdf_generator.py`
- **Settings**: Add to `settings.json` and update relevant modules

### Running Tests During Development

```bash
# Run specific test class
python -m unittest test_calc.TestBillingCalculator

# Run specific test
python -m unittest test_calc.TestBillingCalculator.test_calculate_from_quantity_and_rate
```

## API Reference

### calc.py

```python
from calc import create_calculator, BillingCalculator

# Create calculator
calc = create_calculator(cgst_rate="1.5", sgst_rate="1.5")

# Calculate from parameters
result = calc.calculate_from_two_params(
    quantity=None,        # Optional
    rate=None,           # Optional
    amount=None,         # Optional
    total_inclusive=None # Optional
)
# Returns: dict with quantity, rate, amount, cgst, sgst, total_inclusive, rounded_off

# Calculate line item (no GST)
line = calc.calculate_line_item(quantity=10, rate=100)

# Calculate invoice totals
totals = calc.calculate_invoice_totals(
    line_items=[...],           # List of items with 'amount' key
    user_total_inclusive=None   # Optional override total
)
```

### db_handler.py

```python
from db_handler import DatabaseHandler

db = DatabaseHandler("roopkala_billing.db")

# Save invoice
invoice_id = db.save_invoice(
    invoice_number="RKJ1001",
    invoice_date="2025-10-18",
    customer_name="John Doe",
    line_items=[...],
    totals={...}
)

# Get invoice
invoice = db.get_invoice("RKJ1001")

# Search invoices
results = db.search_invoices("John", "customer_name")

# Get next invoice number
next_num = db.get_next_invoice_number("RKJ", 1001)
```

## License

This project is developed for Roopkala Jewellers. All rights reserved.

## Support

For issues or questions about the codebase:
1. Check this README
2. Review the unit tests for usage examples
3. Examine the inline code documentation
4. Modify `settings.json` for configuration changes

## Version History

### v1.0.0 (2025-10-18)
- Initial release
- Core billing functionality
- GST calculations with CGST/SGST
- SQLite database integration
- PDF export with ReportLab
- Comprehensive test suite
- Flexible calculation engine

---

**Built with Python 🐍 | Powered by Decimal Precision 💯 | Designed for Jewellers 💎**
