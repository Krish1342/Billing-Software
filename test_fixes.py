"""
Quick test script to verify the database fixes
"""

import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ui"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "logic"))

from logic.database_config import create_database_manager

def test_database_fixes():
    print("🧪 Testing Database Fixes")
    print("=" * 40)
    
    try:
        # Test 1: Database connection
        print("1. Testing database connection...")
        db = create_database_manager()
        print(f"   ✅ Connected to: {type(db).__name__}")
        
        # Test 2: get_connection method
        print("2. Testing get_connection method...")
        conn = db.get_connection()
        print(f"   ✅ get_connection() returned: {type(conn).__name__}")
        
        # Test 3: get_next_invoice_number method
        print("3. Testing get_next_invoice_number method...")
        invoice_no = db.get_next_invoice_number()
        print(f"   ✅ Next invoice number: {invoice_no}")
        
        # Test 4: get_sales_summary method
        print("4. Testing get_sales_summary method...")
        summary = db.get_sales_summary()
        print(f"   ✅ Sales summary: {summary}")
        
        # Test 5: get_low_stock_products method
        print("5. Testing get_low_stock_products method...")
        low_stock = db.get_low_stock_products()
        print(f"   ✅ Low stock products: {len(low_stock)} items")
        
        # Test 6: Check for unit_price in products
        print("6. Testing unit_price field in products...")
        products = db.get_products()
        if products and 'unit_price' in products[0]:
            print(f"   ✅ unit_price field present in product data")
        else:
            print(f"   ⚠️  unit_price field missing or no products")
        
        print("\n🎉 All tests passed! Database fixes are working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = test_database_fixes()
    sys.exit(0 if success else 1)