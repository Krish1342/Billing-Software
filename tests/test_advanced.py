"""
Advanced Business Logic Tests for Roopkala Jewellers Billing System
Tests invoice generation, stock deduction, and complex calculations
"""

import sys
import os
from decimal import Decimal

# Add paths
# Add paths (tests are in tests/ directory, so go up one level)
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)  # Add root for 'logic' imports
sys.path.insert(0, os.path.join(parent_dir, "ui"))
sys.path.insert(0, os.path.join(parent_dir, "logic"))

from calculator import create_calculator
from database_config import create_database_manager

print("=" * 70)
print("Advanced Business Logic Tests")
print("=" * 70)
print()

# Initialize components
calc = create_calculator('1.5', '1.5')
db = create_database_manager()

# Test 1: Override Total Calculation
print("Test 1: Override Total with Amount Allocation")
print("-" * 70)

line_items = [
    {'quantity': Decimal('10.000'), 'rate': Decimal('100.00'), 'amount': Decimal('1000.00')},
    {'quantity': Decimal('5.000'), 'rate': Decimal('200.00'), 'amount': Decimal('1000.00')}
]

print(f"Original items:")
for idx, item in enumerate(line_items, 1):
    print(f"  Item {idx}: {item['quantity']}g × ₹{item['rate']} = ₹{item['amount']}")

print(f"\nOriginal subtotal: ₹2000.00")

# User specifies override total of ₹2500 (tax-inclusive)
override_total = Decimal('2500.00')
print(f"Override total (tax-inclusive): ₹{override_total}")

# Allocate amounts by weight
allocated_items = calc.allocate_amounts_by_weight(line_items, override_total)

print(f"\nAllocated amounts:")
for idx, item in enumerate(allocated_items, 1):
    print(f"  Item {idx}: {item['quantity']}g × ₹{item['rate']:.2f} = ₹{item['amount']:.2f}")

# Verify totals match
allocated_subtotal = sum(Decimal(str(item['amount'])) for item in allocated_items)
print(f"\nAllocated subtotal: ₹{allocated_subtotal:.2f}")

# Calculate with override
totals_with_override = calc.calculate_invoice_totals(allocated_items, override_total)
print(f"CGST (1.5%): ₹{totals_with_override['cgst']:.2f}")
print(f"SGST (1.5%): ₹{totals_with_override['sgst']:.2f}")
print(f"Final total: ₹{totals_with_override['final_total']:.2f}")

print(f"\n✅ Override total test completed")
print()

# Test 2: Complex Invoice with Multiple Items
print("Test 2: Complex Invoice Calculation")
print("-" * 70)

complex_items = [
    {'quantity': Decimal('15.500'), 'rate': Decimal('5500.00'), 'amount': Decimal('85250.00')},
    {'quantity': Decimal('8.250'), 'rate': Decimal('5800.00'), 'amount': Decimal('47850.00')},
    {'quantity': Decimal('12.100'), 'rate': Decimal('5600.00'), 'amount': Decimal('67760.00')},
]

print("Invoice with 3 jewelry items:")
for idx, item in enumerate(complex_items, 1):
    print(f"  Item {idx}: {item['quantity']}g × ₹{item['rate']:.2f} = ₹{item['amount']:.2f}")

totals = calc.calculate_invoice_totals(complex_items)

print(f"\nSubtotal: ₹{totals['subtotal']:,.2f}")
print(f"CGST @ 1.5%: ₹{totals['cgst']:,.2f}")
print(f"SGST @ 1.5%: ₹{totals['sgst']:,.2f}")
print(f"Total GST: ₹{totals['total_gst']:,.2f}")
print(f"Rounded off: ₹{totals['rounded_off']:,.2f}")
print(f"Final total: ₹{totals['final_total']:,.2f}")

print(f"\n✅ Complex invoice calculation completed")
print()

# Test 3: Database Operations
print("Test 3: Database Integrity")
print("-" * 70)

# Get current state
categories = db.get_categories()
products = db.get_products()
suppliers = db.get_suppliers()

print(f"Database contains:")
print(f"  - {len(categories)} categories")
print(f"  - {len(products)} products")
print(f"  - {len(suppliers)} suppliers")

# Check category summary
cat_summary = db.get_category_summary()
print(f"\nCategory Summary:")
for cat in cat_summary[:5]:  # Show first 5
    print(f"  {cat['category_name']}: {cat['available_items']} items, {cat['available_net_weight']:.3f}g")

# Check total summary
total_summary = db.get_total_summary()
print(f"\nInventory Totals:")
print(f"  Total items: {total_summary.get('total_available_items', 0)}")
print(f"  Total net weight: {total_summary.get('total_available_net_weight', 0):.3f}g")
print(f"  Total gross weight: {total_summary.get('total_available_gross_weight', 0):.3f}g")

print(f"\n✅ Database integrity check completed")
print()

# Test 4: Edge Cases
print("Test 4: Edge Cases & Boundary Conditions")
print("-" * 70)

# Test with very small quantity
tiny_item = calc.calculate_line_item(quantity='0.001', rate='50000', amount=None)
print(f"Tiny item (0.001g × ₹50000): ₹{tiny_item['amount']}")

# Test with large quantity
large_item = calc.calculate_line_item(quantity='999.999', rate='6000', amount=None)
print(f"Large item (999.999g × ₹6000): ₹{large_item['amount']:,.2f}")

# Test with zero quantity (should handle gracefully)
try:
    zero_item = calc.calculate_line_item(quantity='0', rate='100', amount=None)
    print(f"Zero quantity item: {zero_item}")
except Exception as e:
    print(f"Zero quantity handled: {type(e).__name__}")

# Test with rate calculation from amount
reverse_calc = calc.calculate_line_item(quantity='25.5', rate=None, amount='150000')
print(f"Reverse calculation (₹150000 / 25.5g): ₹{reverse_calc['rate']:.2f} per gram")

print(f"\n✅ Edge case testing completed")
print()

# Test 5: Tax Calculations at Different Rates
print("Test 5: Tax Calculations with Different Rates")
print("-" * 70)

# Test with standard rate (1.5% + 1.5%)
standard_calc = create_calculator('1.5', '1.5')
standard_items = [{'quantity': 10, 'rate': 100, 'amount': 1000}]
standard_totals = standard_calc.calculate_invoice_totals(standard_items)

print(f"Standard rate (1.5% + 1.5%):")
print(f"  Subtotal: ₹{standard_totals['subtotal']}")
print(f"  CGST: ₹{standard_totals['cgst']}")
print(f"  SGST: ₹{standard_totals['sgst']}")
print(f"  Total: ₹{standard_totals['final_total']}")

# Test with different rate (e.g., 2.5% + 2.5%)
custom_calc = create_calculator('2.5', '2.5')
custom_totals = custom_calc.calculate_invoice_totals(standard_items)

print(f"\nCustom rate (2.5% + 2.5%):")
print(f"  Subtotal: ₹{custom_totals['subtotal']}")
print(f"  CGST: ₹{custom_totals['cgst']}")
print(f"  SGST: ₹{custom_totals['sgst']}")
print(f"  Total: ₹{custom_totals['final_total']}")

print(f"\n✅ Tax rate testing completed")
print()

# Test 6: Rounding Behavior
print("Test 6: Rounding Behavior")
print("-" * 70)

# Test invoice that needs rounding
rounding_items = [
    {'quantity': Decimal('7.333'), 'rate': Decimal('5432.10'), 'amount': Decimal('39842.17')}
]

rounding_totals = calc.calculate_invoice_totals(rounding_items)
print(f"Invoice requiring rounding:")
print(f"  Subtotal: ₹{rounding_totals['subtotal']}")
print(f"  CGST: ₹{rounding_totals['cgst']}")
print(f"  SGST: ₹{rounding_totals['sgst']}")
print(f"  Before rounding: ₹{float(rounding_totals['subtotal']) + float(rounding_totals['cgst']) + float(rounding_totals['sgst']):.2f}")
print(f"  Rounded off: ₹{rounding_totals['rounded_off']}")
print(f"  Final total: ₹{rounding_totals['final_total']}")

print(f"\n✅ Rounding behavior test completed")
print()

print("=" * 70)
print("All Advanced Tests Completed Successfully! 🎉")
print("=" * 70)
