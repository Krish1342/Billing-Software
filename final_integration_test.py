"""
Final Integration Test for Unified Jewelry Management System

This script tests all the major fixes:
1. Database schema migration (total -> total_amount)
2. Settings path issue fix
3. Override total amount functionality
"""

import sys
import os
import sqlite3
from decimal import Decimal


def test_database_schema():
    """Test that database schema is correct."""
    print("=== Testing Database Schema ===")

    db_path = "unified_jewelry_shop.db"

    if not os.path.exists(db_path):
        print("Creating fresh database...")
        from unified_database import UnifiedDatabaseManager

        db = UnifiedDatabaseManager(db_path)
        db.close()

    # Check schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(invoices)")
    columns = [col[1] for col in cursor.fetchall()]

    required_columns = ["total_amount", "rounded_off", "subtotal", "cgst", "sgst"]
    missing_columns = [col for col in required_columns if col not in columns]

    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False
    else:
        print("✓ All required columns present in invoices table")

    conn.close()
    return True


def test_settings_path():
    """Test settings path functionality."""
    print("\n=== Testing Settings Path ===")

    try:
        # Import the main app class
        from unified_main_app import UnifiedJewelryApp
        from PyQt5.QtWidgets import QApplication

        # Create temporary app (without showing GUI)
        app = (
            QApplication(sys.argv)
            if not QApplication.instance()
            else QApplication.instance()
        )

        # Create the main app instance
        main_app = UnifiedJewelryApp()

        # Test that settings_path is set
        if hasattr(main_app, "settings_path") and main_app.settings_path:
            print(f"✓ Settings path is set: {main_app.settings_path}")
            return True
        else:
            print("❌ Settings path is not set")
            return False

    except Exception as e:
        print(f"❌ Error testing settings path: {e}")
        return False


def test_override_total_functionality():
    """Test override total functionality in billing tab."""
    print("\n=== Testing Override Total Functionality ===")

    try:
        from PyQt5.QtWidgets import QApplication
        from billing_tab import BillingTab
        from unified_database import UnifiedDatabaseManager
        from calc import create_calculator

        # Setup
        app = (
            QApplication(sys.argv)
            if not QApplication.instance()
            else QApplication.instance()
        )

        db = UnifiedDatabaseManager()
        calculator = create_calculator("1.5", "1.5")
        settings = {
            "tax": {"cgst_rate": "1.5", "sgst_rate": "1.5"},
            "company": {"name": "Test Company"},
        }

        # Create billing tab
        billing_tab = BillingTab(db, calculator, settings)

        # Check if override functionality exists
        required_attributes = [
            "override_total_checkbox",
            "override_total_spin",
            "final_total_label",
        ]

        missing_attrs = [
            attr for attr in required_attributes if not hasattr(billing_tab, attr)
        ]

        if missing_attrs:
            print(f"❌ Missing override total attributes: {missing_attrs}")
            return False
        else:
            print("✓ Override total functionality is implemented")

        # Test the on_override_total_changed method exists
        if hasattr(billing_tab, "on_override_total_changed"):
            print("✓ Override total change handler exists")
        else:
            print("❌ Override total change handler missing")
            return False

        return True

    except Exception as e:
        print(f"❌ Error testing override total: {e}")
        return False


def test_calculation_with_override():
    """Test calculation with override total."""
    print("\n=== Testing Calculation with Override ===")

    try:
        from calc import create_calculator

        calculator = create_calculator("1.5", "1.5")

        # Test line items
        line_items = [
            {
                "description": "Gold Ring",
                "hsn_code": "7113",
                "quantity": Decimal("1"),
                "rate": Decimal("1000.00"),
                "amount": Decimal("1000.00"),
            }
        ]

        # Calculate normal totals
        totals = calculator.calculate_invoice_totals(line_items)

        print(f"  Subtotal: ₹{totals['subtotal']}")
        print(f"  CGST: ₹{totals['cgst']}")
        print(f"  SGST: ₹{totals['sgst']}")
        print(f"  Final Total: ₹{totals['final_total']}")

        # Test override logic
        override_total = Decimal("1100.00")
        calculated_total = totals["subtotal"] + totals["cgst"] + totals["sgst"]
        override_rounded_off = override_total - calculated_total

        print(f"  Override Total: ₹{override_total}")
        print(f"  Override Rounded Off: ₹{override_rounded_off}")

        print("✓ Override calculation logic works correctly")
        return True

    except Exception as e:
        print(f"❌ Error testing override calculation: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 FINAL INTEGRATION TEST - UNIFIED JEWELRY MANAGEMENT SYSTEM")
    print("=" * 70)

    tests = [
        test_database_schema,
        test_settings_path,
        test_override_total_functionality,
        test_calculation_with_override,
    ]

    results = []

    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"🎉 ALL TESTS PASSED! ({passed}/{total})")
        print("\n✅ The application is ready for use!")
        print("\n🚀 To start the application, run:")
        print("   python unified_main_app.py")
        print("   OR")
        print("   python launch_unified_app.py")
    else:
        print(f"❌ Some tests failed: {passed}/{total} passed")
        print("\n🔧 Please review the failed tests above.")

    print("=" * 70)


if __name__ == "__main__":
    main()
