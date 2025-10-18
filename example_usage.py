"""
Example usage of the calc.py module.

This demonstrates how to use the calculation engine independently.
"""

from calc import create_calculator
from decimal import Decimal

def main():
    """Demonstrate calc.py usage with examples."""
    
    # Create calculator with 1.5% CGST and 1.5% SGST
    calc = create_calculator("1.5", "1.5")
    
    print("=" * 70)
    print("Roopkala Jewellers - Calculation Module Demo")
    print("=" * 70)
    
    # Example 1: Simple quantity × rate
    print("\nExample 1: Calculate from Quantity and Rate")
    print("-" * 70)
    result = calc.calculate_from_two_params(
        quantity=10.5,
        rate=6500
    )
    print(f"Input: 10.5 grams @ ₹6500/gram")
    print(f"Amount (excluding GST): ₹{result['amount']}")
    print(f"CGST (1.5%): ₹{result['cgst']}")
    print(f"SGST (1.5%): ₹{result['sgst']}")
    print(f"Total GST: ₹{result['total_gst']}")
    print(f"Final Total (inclusive): ₹{result['total_inclusive']}")
    
    # Example 2: Quantity + Amount
    print("\nExample 2: Calculate Rate from Quantity and Amount")
    print("-" * 70)
    result = calc.calculate_from_two_params(
        quantity=25,
        amount=50000
    )
    print(f"Input: 25 grams, Total Amount ₹50000")
    print(f"Calculated Rate: ₹{result['rate']}/gram")
    print(f"Final Total (inclusive): ₹{result['total_inclusive']}")
    
    # Example 3: GST Inclusive with target total
    print("\nExample 3: Calculate from Quantity with Target Total")
    print("-" * 70)
    result = calc.calculate_from_two_params(
        quantity=10,
        total_inclusive=50000  # Customer wants to pay exactly ₹50000
    )
    print(f"Input: 10 grams, Target Total ₹50000")
    print(f"Back-calculated Amount: ₹{result['amount']}")
    print(f"Rate per gram: ₹{result['rate']}")
    print(f"CGST: ₹{result['cgst']}")
    print(f"SGST: ₹{result['sgst']}")
    print(f"Final Total: ₹{result['total_inclusive']}")
    print(f"Rounded Off: ₹{result['rounded_off']}")
    
    # Example 4: Line item calculation
    print("\nExample 4: Simple Line Item (No GST)")
    print("-" * 70)
    line = calc.calculate_line_item(
        quantity=5,
        rate=1200
    )
    print(f"Input: 5 items @ ₹1200 each")
    print(f"Line Amount: ₹{line['amount']}")
    
    # Example 5: Invoice totals
    print("\nExample 5: Calculate Invoice Totals from Multiple Items")
    print("-" * 70)
    line_items = [
        {'amount': Decimal('10000')},
        {'amount': Decimal('25000')},
        {'amount': Decimal('15000')}
    ]
    totals = calc.calculate_invoice_totals(line_items)
    print(f"Line items: ₹10000, ₹25000, ₹15000")
    print(f"Subtotal: ₹{totals['subtotal']}")
    print(f"CGST (1.5%): ₹{totals['cgst']}")
    print(f"SGST (1.5%): ₹{totals['sgst']}")
    print(f"Total GST: ₹{totals['total_gst']}")
    print(f"Final Total: ₹{totals['final_total']}")
    
    # Example 6: Invoice with override total
    print("\nExample 6: Invoice with Override Total (Rounded Off)")
    print("-" * 70)
    totals = calc.calculate_invoice_totals(
        line_items,
        user_total_inclusive=51500  # Round to nice number
    )
    print(f"Calculated Total: ₹{totals['calculated_total']}")
    print(f"Override Total: ₹51500")
    print(f"Rounded Off: ₹{totals['rounded_off']}")
    print(f"Final Total: ₹{totals['final_total']}")
    
    # Example 7: Very precise quantity (jewellery use case)
    print("\nExample 7: High Precision Quantity (3 decimals)")
    print("-" * 70)
    result = calc.calculate_from_two_params(
        quantity="25.657",  # Very precise weight
        rate="7250.50"
    )
    print(f"Input: 25.657 grams @ ₹7250.50/gram")
    print(f"Quantity: {result['quantity']} (3 decimals)")
    print(f"Rate: ₹{result['rate']} (2 decimals)")
    print(f"Amount: ₹{result['amount']}")
    print(f"Total with GST: ₹{result['total_inclusive']}")
    
    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
