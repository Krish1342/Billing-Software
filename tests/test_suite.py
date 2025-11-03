"""
Comprehensive Test Suite for Roopkala Jewellers Billing System
Tests all major functionality without GUI interaction
"""

import sys
import os
from decimal import Decimal
from datetime import datetime

# Add paths (tests are in tests/ directory, so go up one level)
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, parent_dir)  # Add root for 'logic' imports
sys.path.insert(0, os.path.join(parent_dir, "ui"))
sys.path.insert(0, os.path.join(parent_dir, "logic"))

# Test results tracker
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def test_result(test_name, passed, error_msg=None):
    """Record test result."""
    if passed:
        test_results['passed'] += 1
        print(f"✅ {test_name}")
    else:
        test_results['failed'] += 1
        print(f"❌ {test_name}")
        if error_msg:
            print(f"   Error: {error_msg}")
            test_results['errors'].append(f"{test_name}: {error_msg}")

print("=" * 70)
print("Roopkala Jewellers Billing System - Comprehensive Test Suite")
print("=" * 70)
print()

# Test 1: Module Imports
print("Test Suite 1: Module Imports")
print("-" * 70)

try:
    from calculator import create_calculator
    test_result("Import calculator module", True)
except Exception as e:
    test_result("Import calculator module", False, str(e))

try:
    from database_config import create_database_manager
    test_result("Import database_config module", True)
except Exception as e:
    test_result("Import database_config module", False, str(e))

try:
    from pdf_generator import InvoicePDFGenerator
    test_result("Import pdf_generator module", True)
except Exception as e:
    test_result("Import pdf_generator module", False, str(e))

try:
    from label_printer import LabelPrinter
    test_result("Import label_printer module", True)
except Exception as e:
    test_result("Import label_printer module", False, str(e))

print()

# Test 2: Calculator Functionality
print("Test Suite 2: Calculator Functionality")
print("-" * 70)

try:
    calc = create_calculator('1.5', '1.5')
    
    # Test line item calculation
    result = calc.calculate_line_item(quantity='10', rate='100', amount=None)
    expected_amount = Decimal('1000.00')
    test_result(
        "Calculate line item (10 x 100)",
        result['amount'] == expected_amount,
        f"Expected {expected_amount}, got {result['amount']}"
    )
    
    # Test with amount provided
    result2 = calc.calculate_line_item(quantity='5', rate=None, amount='500')
    expected_rate = Decimal('100.00')
    test_result(
        "Calculate rate from amount (500 / 5)",
        result2['rate'] == expected_rate,
        f"Expected {expected_rate}, got {result2['rate']}"
    )
    
    # Test invoice totals
    line_items = [
        {'quantity': 10, 'rate': 100, 'amount': 1000},
        {'quantity': 5, 'rate': 200, 'amount': 1000}
    ]
    totals = calc.calculate_invoice_totals(line_items)
    expected_subtotal = Decimal('2000.00')
    test_result(
        "Calculate invoice subtotal",
        totals['subtotal'] == expected_subtotal,
        f"Expected {expected_subtotal}, got {totals['subtotal']}"
    )
    
    expected_cgst = Decimal('30.00')  # 1.5% of 2000
    test_result(
        "Calculate CGST (1.5%)",
        totals['cgst'] == expected_cgst,
        f"Expected {expected_cgst}, got {totals['cgst']}"
    )
    
    expected_sgst = Decimal('30.00')  # 1.5% of 2000
    test_result(
        "Calculate SGST (1.5%)",
        totals['sgst'] == expected_sgst,
        f"Expected {expected_sgst}, got {totals['sgst']}"
    )
    
except Exception as e:
    test_result("Calculator functionality", False, str(e))

print()

# Test 3: Database Operations
print("Test Suite 3: Database Operations")
print("-" * 70)

try:
    db = create_database_manager()
    
    # Test get categories
    categories = db.get_categories()
    test_result(
        "Get categories from database",
        isinstance(categories, list),
        f"Expected list, got {type(categories)}"
    )
    
    # Test get products
    products = db.get_products()
    test_result(
        "Get products from database",
        isinstance(products, list),
        f"Expected list, got {type(products)}"
    )
    
    # Test get suppliers
    suppliers = db.get_suppliers()
    test_result(
        "Get suppliers from database",
        isinstance(suppliers, list),
        f"Expected list, got {type(suppliers)}"
    )
    
    # Test next invoice number (check it returns a string, not specific prefix)
    next_invoice = db.get_next_invoice_number()
    test_result(
        "Get next invoice number",
        isinstance(next_invoice, str) and len(next_invoice) > 0,
        f"Expected non-empty string, got {next_invoice}"
    )
    
    # Test category summary
    summary = db.get_category_summary()
    test_result(
        "Get category summary",
        isinstance(summary, list),
        f"Expected list, got {type(summary)}"
    )
    
    # Test total summary
    total_summary = db.get_total_summary()
    test_result(
        "Get total summary",
        isinstance(total_summary, dict),
        f"Expected dict, got {type(total_summary)}"
    )
    
except Exception as e:
    test_result("Database operations", False, str(e))

print()

# Test 4: PDF Generator
print("Test Suite 4: PDF Generator")
print("-" * 70)

try:
    pdf_gen = InvoicePDFGenerator()
    
    test_result(
        "PDF generator initialization",
        pdf_gen.company['name'] == 'Roopkala Jewellers',
        f"Expected 'Roopkala Jewellers', got {pdf_gen.company['name']}"
    )
    
    # Test PDF generation (just check method exists, don't create file)
    test_result(
        "PDF generator has generate method",
        hasattr(pdf_gen, 'generate_invoice_pdf'),
        "Method 'generate_invoice_pdf' not found"
    )
    
    # Create a test PDF
    test_invoice_data = {
        'invoice_number': 'TEST001',
        'invoice_date': '2025-11-02',
        'customer_name': 'Test Customer',
        'customer_address': '123 Test Street',
        'customer_phone': '+91-9876543210',
        'customer_gstin': '',
        'subtotal': '1000.00',
        'cgst_amount': '15.00',
        'sgst_amount': '15.00',
        'total_amount': '1030.00',
        'rounded_off': '0.00'
    }
    
    test_line_items = [
        {
            'description': 'Test Item',
            'hsn_code': '7113',
            'quantity': 10.000,
            'rate': 100.00,
            'amount': 1000.00
        }
    ]
    
    test_pdf_path = 'test_invoice.pdf'
    try:
        pdf_gen.generate_invoice_pdf(test_pdf_path, test_invoice_data, test_line_items)
        pdf_created = os.path.exists(test_pdf_path)
        test_result(
            "Generate test PDF invoice",
            pdf_created,
            "PDF file was not created"
        )
        
        # Clean up test file
        if pdf_created:
            os.remove(test_pdf_path)
            
    except Exception as e:
        test_result("Generate test PDF invoice", False, str(e))
        
except Exception as e:
    test_result("PDF generator", False, str(e))

print()

# Test 5: Label Printer
print("Test Suite 5: Label Printer")
print("-" * 70)

try:
    label_printer = LabelPrinter()
    
    test_result(
        "Label printer initialization",
        label_printer is not None,
        "Label printer failed to initialize"
    )
    
    test_result(
        "Label printer has generate method",
        hasattr(label_printer, 'generate_label_for_item'),
        "Method 'generate_label_for_item' not found"
    )
    
except Exception as e:
    test_result("Label printer", False, str(e))

print()

# Test 6: Settings File
print("Test Suite 6: Settings & Configuration")
print("-" * 70)

try:
    import json
    settings_path = os.path.join(parent_dir, 'settings.json')
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    test_result(
        "Load settings.json",
        'company' in settings,
        "Settings missing 'company' section"
    )
    
    test_result(
        "Settings has tax configuration",
        'tax' in settings,
        "Settings missing 'tax' section"
    )
    
    test_result(
        "Settings has invoice configuration",
        'invoice' in settings,
        "Settings missing 'invoice' section"
    )
    
    test_result(
        "CGST rate is configured",
        'cgst_rate' in settings['tax'],
        "CGST rate not found in settings"
    )
    
    test_result(
        "SGST rate is configured",
        'sgst_rate' in settings['tax'],
        "SGST rate not found in settings"
    )
    
except Exception as e:
    test_result("Settings file", False, str(e))

print()

# Test 8: Folder Structure
print("Test Suite 8: Folder Structure")
print("-" * 70)

# Check folders relative to parent directory
required_folders = ['ui', 'logic', 'database', 'invoices', 'labels']
for folder in required_folders:
    folder_path = os.path.join(parent_dir, folder)
    folder_exists = os.path.exists(folder_path)
    test_result(
        f"Folder '{folder}' exists",
        folder_exists,
        f"Required folder '{folder}' not found"
    )

print()

# Test 9: Required Files
print("Test Suite 9: Required Files")
print("-" * 70)

required_files = [
    'main.py',
    'settings.json',
    'requirements.txt',
    'README.md',
    'build_exe.py',
    'build.bat'
]

for file in required_files:
    file_path = os.path.join(parent_dir, file)
    file_exists = os.path.exists(file_path)
    test_result(
        f"File '{file}' exists",
        file_exists,
        f"Required file '{file}' not found"
    )

print()

# Final Summary
print("=" * 70)
print("Test Summary")
print("=" * 70)
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
print(f"Total Tests: {test_results['passed'] + test_results['failed']}")

if test_results['failed'] > 0:
    print("\nFailed Tests Details:")
    for error in test_results['errors']:
        print(f"  - {error}")
else:
    print("\n🎉 All tests passed!")

success_rate = (test_results['passed'] / (test_results['passed'] + test_results['failed'])) * 100
print(f"\nSuccess Rate: {success_rate:.1f}%")
print("=" * 70)
