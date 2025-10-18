# Quick Start Guide

## Installation (3 Steps)

1. **Install Python 3.10+** (if not already installed)
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python main.py
   ```

## First Invoice (5 Minutes)

1. **Launch** the app with `python main.py`

2. **Enter Customer Details**
   - Customer Name: (required)
   - Address, Phone, GSTIN: (optional)

3. **Add Items**
   - Description: "Gold Ring"
   - HSN: "7113" (optional)
   - Quantity: "25.5" (grams)
   - Rate: "6500" (per gram)
   - Click **Add Item**

4. **Review Totals**
   - Subtotal, CGST, SGST auto-calculated
   - Final total shown

5. **Save & Generate**
   - Click **Save Invoice**
   - Click **Generate PDF** to export

## Key Features

### Flexible Input
Enter **any 2 of 3**:
- ✅ Quantity + Rate → Calculates Amount
- ✅ Quantity + Amount → Calculates Rate
- ✅ Rate + Amount → Calculates Quantity

### Override Total
Want the total to be exactly ₹10,000?
1. Add items normally
2. In "Override Total" field, enter: `10000`
3. System adds "Rounded Off" to match

### Load Invoices
1. Click **Load Invoice**
2. Enter invoice number (e.g., "RKJ1001")
3. Edit or generate PDF

## Configuration

Edit `settings.json` to change:
- Company name & address
- GST rates (CGST/SGST)
- Invoice number prefix
- Starting invoice number

## Testing

Run tests to verify installation:
```bash
python test_calc.py
```

Should see: `OK` with all tests passing.

## Example Calculation

Try this in the app:
- Quantity: `10.5`
- Rate: `6500`
- Leave Amount blank
- Click "Add Item"

Result:
- Amount: ₹68,250.00
- CGST: ₹1,023.75
- SGST: ₹1,023.75
- Total: ₹70,297.50

## Common Tasks

### Backup Database
Copy `roopkala_billing.db` to safe location

### Reset Everything
Delete `roopkala_billing.db` and restart app

### Change Company Name
Edit `settings.json` → `company.name`

### Change Tax Rates
Edit `settings.json` → `tax.cgst_rate` and `tax.sgst_rate`

## Need Help?

1. Read `README.md` for full documentation
2. Run `python example_usage.py` for code examples
3. Check `test_calc.py` for calculation examples

## Troubleshooting

**Problem**: PDF generation fails
**Solution**: `pip install reportlab`

**Problem**: Database error
**Solution**: Close all app instances, restart

**Problem**: Wrong calculations
**Solution**: System uses Decimal precision - should be accurate. Check inputs.

---

**Ready to bill? Run:** `python main.py` 🚀
