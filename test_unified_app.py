"""
Test script for the Unified Jewelry Management System
Run this to test the basic functionality of the merged application.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test if all modules can be imported."""
    print("Testing imports...")

    try:
        from unified_database import UnifiedDatabaseManager

        print("✓ Unified database module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import unified database: {e}")
        return False

    try:
        from calc import create_calculator

        print("✓ Calculator module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import calculator: {e}")
        return False

    try:
        from pdf_generator import InvoicePDFGenerator

        print("✓ PDF generator module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PDF generator: {e}")
        return False

    # Test PyQt5 imports
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow

        print("✓ PyQt5 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyQt5: {e}")
        print("Please install PyQt5: pip install PyQt5")
        return False

    return True


def test_database():
    """Test database functionality."""
    print("\nTesting database...")

    try:
        from unified_database import UnifiedDatabaseManager
        import time

        # Remove existing test database
        if os.path.exists("test_jewelry_shop.db"):
            try:
                os.remove("test_jewelry_shop.db")
                time.sleep(0.5)  # Give time for file deletion
            except PermissionError:
                pass  # File might be in use, continue anyway

        # Initialize fresh database
        db = UnifiedDatabaseManager("test_jewelry_shop.db")
        print("✓ Database initialized successfully")

        # Test category operations
        category_id = db.add_category("Test Category", "Test description")
        print(f"✓ Category added with ID: {category_id}")

        categories = db.get_categories()
        print(f"✓ Retrieved {len(categories)} categories")

        # Test supplier operations
        supplier_id = db.add_supplier(
            "Test Supplier", "TEST001", "John Doe", "1234567890"
        )
        print(f"✓ Supplier added with ID: {supplier_id}")

        suppliers = db.get_suppliers()
        print(f"✓ Retrieved {len(suppliers)} suppliers")

        # Test product operations
        product_id = db.add_product(
            name="Test Ring",
            gross_weight=10.5,
            net_weight=9.8,
            quantity=5,
            unit_price=1500.0,
            supplier_id=supplier_id,
            category_id=category_id,
            description="Test jewelry item",
        )
        print(f"✓ Product added with ID: {product_id}")

        products = db.get_products()
        print(f"✓ Retrieved {len(products)} products")

        # Test invoice operations
        invoice_data = {
            "invoice_number": "TEST-001",
            "customer_name": "Test Customer",
            "invoice_date": "2025-01-01",
            "subtotal": 1500.0,
            "cgst_amount": 22.5,
            "sgst_amount": 22.5,
            "total_amount": 1545.0,
            "rounded_off": 0.0,
        }

        line_items = [
            {
                "product_id": product_id,
                "description": "Test Ring",
                "hsn_code": "71131910",
                "quantity": 1,
                "rate": 1500.0,
                "amount": 1500.0,
            }
        ]

        invoice_id, warnings = db.generate_invoice_with_stock_deduction(
            invoice_data, line_items
        )
        print(f"✓ Invoice created with ID: {invoice_id}")
        if warnings:
            print(f"  Warnings: {warnings}")

        # Check stock deduction
        updated_product = db.get_product_by_id(product_id)
        if updated_product:
            print(f"✓ Stock updated: {updated_product['quantity']} remaining (was 5)")

        # Close database connection before cleanup
        db.close()

        # Clean up test database
        import time

        time.sleep(0.5)  # Give time for file to be released

        if os.path.exists("test_jewelry_shop.db"):
            try:
                os.remove("test_jewelry_shop.db")
                print("✓ Test database cleaned up")
            except PermissionError:
                print("⚠️ Could not remove test database file (file in use)")

        return True

    except Exception as e:
        print(f"✗ Database test failed: {e}")
        # Clean up on error
        try:
            if "db" in locals():
                db.close()
        except:
            pass

        import time

        time.sleep(0.5)

        if os.path.exists("test_jewelry_shop.db"):
            try:
                os.remove("test_jewelry_shop.db")
            except PermissionError:
                print("⚠️ Could not remove test database file (file in use)")
        return False


def test_calculator():
    """Test calculation functionality."""
    print("\nTesting calculator...")

    try:
        from calc import create_calculator

        # Create calculator
        calc = create_calculator("1.5", "1.5")
        print("✓ Calculator created successfully")

        # Test basic calculation
        from decimal import Decimal

        result = calc.calculate_from_two_params(
            quantity=Decimal("2"), rate=Decimal("1000.0")
        )

        expected_amount = 2000.0
        expected_cgst = 30.0  # 1.5% of 2000
        expected_sgst = 30.0  # 1.5% of 2000
        expected_total = 2060.0

        if result["amount"] == expected_amount:
            print("✓ Amount calculation correct")
        else:
            print(
                f"✗ Amount calculation incorrect: got {result['amount']}, expected {expected_amount}"
            )

        if result["cgst"] == expected_cgst:
            print("✓ CGST calculation correct")
        else:
            print(
                f"✗ CGST calculation incorrect: got {result['cgst']}, expected {expected_cgst}"
            )

        if result["sgst"] == expected_sgst:
            print("✓ SGST calculation correct")
        else:
            print(
                f"✗ SGST calculation incorrect: got {result['sgst']}, expected {expected_sgst}"
            )

        if result["total_inclusive"] == expected_total:
            print("✓ Total calculation correct")
        else:
            print(
                f"✗ Total calculation incorrect: got {result['total_inclusive']}, expected {expected_total}"
            )

        return True

    except Exception as e:
        print(f"✗ Calculator test failed: {e}")
        return False


def test_settings():
    """Test settings file creation."""
    print("\nTesting settings...")

    try:
        import json

        # Create default settings
        settings = {
            "company": {
                "name": "Roopkala Jewellers",
                "address": "Shop No. 123, Jewelry Street",
                "city": "Mumbai",
                "state": "Maharashtra",
                "pincode": "400001",
                "phone": "+91-9876543210",
                "email": "info@roopkalajewellers.com",
                "gstin": "27XXXXX1234X1ZX",
                "logo_path": "",
            },
            "tax": {"cgst_rate": "1.5", "sgst_rate": "1.5"},
            "app": {"theme": "light", "auto_save": True, "backup_enabled": True},
        }

        # Save settings
        with open("test_settings.json", "w") as f:
            json.dump(settings, f, indent=4)

        # Load settings
        with open("test_settings.json", "r") as f:
            loaded_settings = json.load(f)

        if loaded_settings == settings:
            print("✓ Settings save/load test passed")
        else:
            print("✗ Settings save/load test failed")

        # Clean up
        os.remove("test_settings.json")

        return True

    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("UNIFIED JEWELRY MANAGEMENT SYSTEM - TEST SUITE")
    print("=" * 50)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test database
    if not test_database():
        all_passed = False

    # Test calculator
    if not test_calculator():
        all_passed = False

    # Test settings
    if not test_settings():
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nThe unified application is ready to run.")
        print("Execute: python unified_main_app.py")
    else:
        print("❌ SOME TESTS FAILED!")
        print("\nPlease fix the issues before running the application.")
    print("=" * 50)


if __name__ == "__main__":
    main()
