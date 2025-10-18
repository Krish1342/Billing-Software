"""
Unit tests for calc.py calculation module.

Run with: python -m pytest test_calc.py -v
Or: python test_calc.py
"""

import unittest
from decimal import Decimal
from calc import BillingCalculator, create_calculator, CalculationError


class TestBillingCalculator(unittest.TestCase):
    """Test cases for BillingCalculator class."""
    
    def setUp(self):
        """Set up test calculator with 1.5% CGST and 1.5% SGST."""
        self.calc = create_calculator("1.5", "1.5")
    
    def test_calculator_initialization(self):
        """Test calculator initialization with tax rates."""
        self.assertEqual(self.calc.cgst_rate, Decimal('1.5'))
        self.assertEqual(self.calc.sgst_rate, Decimal('1.5'))
        self.assertEqual(self.calc.total_gst_rate, Decimal('3.0'))
    
    def test_to_decimal_conversion(self):
        """Test conversion of various types to Decimal."""
        self.assertEqual(self.calc.to_decimal(100), Decimal('100'))
        self.assertEqual(self.calc.to_decimal('100.50'), Decimal('100.50'))
        self.assertEqual(self.calc.to_decimal(Decimal('100.50')), Decimal('100.50'))
        self.assertEqual(self.calc.to_decimal(None), Decimal('0'))
        self.assertEqual(self.calc.to_decimal(''), Decimal('0'))
        
        with self.assertRaises(CalculationError):
            self.calc.to_decimal('invalid')
    
    def test_quantize_functions(self):
        """Test quantity and money quantization."""
        # Quantity (3 decimals)
        qty = Decimal('10.12345')
        self.assertEqual(
            self.calc.quantize_quantity(qty),
            Decimal('10.123')
        )
        
        # Money (2 decimals)
        money = Decimal('100.126')
        self.assertEqual(
            self.calc.quantize_money(money),
            Decimal('100.13')
        )
        
        # Rounding half up
        self.assertEqual(
            self.calc.quantize_money(Decimal('100.125')),
            Decimal('100.13')
        )
    
    def test_calculate_from_quantity_and_rate(self):
        """Test calculation with quantity and rate provided."""
        result = self.calc.calculate_from_two_params(
            quantity=10,
            rate=1000
        )
        
        self.assertEqual(result['quantity'], Decimal('10.000'))
        self.assertEqual(result['rate'], Decimal('1000.00'))
        self.assertEqual(result['amount'], Decimal('10000.00'))
        self.assertEqual(result['cgst'], Decimal('150.00'))  # 1.5% of 10000
        self.assertEqual(result['sgst'], Decimal('150.00'))  # 1.5% of 10000
        self.assertEqual(result['total_gst'], Decimal('300.00'))
        self.assertEqual(result['total_inclusive'], Decimal('10300.00'))
        self.assertEqual(result['rounded_off'], Decimal('0.00'))
    
    def test_calculate_from_quantity_and_amount(self):
        """Test calculation with quantity and amount provided."""
        result = self.calc.calculate_from_two_params(
            quantity=5,
            amount=5000
        )
        
        self.assertEqual(result['quantity'], Decimal('5.000'))
        self.assertEqual(result['rate'], Decimal('1000.00'))
        self.assertEqual(result['amount'], Decimal('5000.00'))
        self.assertEqual(result['total_inclusive'], Decimal('5150.00'))
    
    def test_calculate_from_quantity_and_total_inclusive(self):
        """Test calculation with quantity and total inclusive provided."""
        result = self.calc.calculate_from_two_params(
            quantity=10,
            total_inclusive=10300
        )
        
        self.assertEqual(result['quantity'], Decimal('10.000'))
        self.assertEqual(result['amount'], Decimal('10000.00'))
        self.assertEqual(result['rate'], Decimal('1000.00'))
        self.assertEqual(result['total_inclusive'], Decimal('10300.00'))
    
    def test_calculate_from_rate_and_amount(self):
        """Test calculation with rate and amount provided."""
        result = self.calc.calculate_from_two_params(
            rate=500,
            amount=5000
        )
        
        self.assertEqual(result['quantity'], Decimal('10.000'))
        self.assertEqual(result['rate'], Decimal('500.00'))
        self.assertEqual(result['amount'], Decimal('5000.00'))
    
    def test_calculate_from_rate_and_total_inclusive(self):
        """Test calculation with rate and total inclusive provided."""
        result = self.calc.calculate_from_two_params(
            rate=1000,
            total_inclusive=5150
        )
        
        self.assertEqual(result['rate'], Decimal('1000.00'))
        self.assertEqual(result['amount'], Decimal('5000.00'))
        self.assertEqual(result['quantity'], Decimal('5.000'))
        self.assertEqual(result['total_inclusive'], Decimal('5150.00'))
    
    def test_calculate_from_amount_and_total_inclusive(self):
        """Test calculation with amount and total inclusive provided."""
        result = self.calc.calculate_from_two_params(
            amount=10000,
            total_inclusive=10300
        )
        
        self.assertEqual(result['amount'], Decimal('10000.00'))
        self.assertEqual(result['total_inclusive'], Decimal('10300.00'))
        # When only amount and total given, defaults to qty=1, rate=amount
        self.assertEqual(result['quantity'], Decimal('1.000'))
        self.assertEqual(result['rate'], Decimal('10000.00'))
    
    def test_gst_inclusive_with_rounded_off(self):
        """Test rounded off calculation when user provides total."""
        # When user provides quantity + total_inclusive, system back-calculates
        result = self.calc.calculate_from_two_params(
            quantity=10,
            total_inclusive=10000  # User wants exactly 10000
        )
        
        # Total should match user input exactly
        self.assertEqual(result['total_inclusive'], Decimal('10000.00'))
        # Amount is back-calculated: 10000 / 1.03 = 9708.74 (approx)
        expected_amount = Decimal('10000') / (Decimal('1') + Decimal('3') / Decimal('100'))
        self.assertEqual(result['amount'], self.calc.quantize_money(expected_amount))
        # Rate = amount / quantity
        expected_rate = self.calc.quantize_money(expected_amount) / Decimal('10')
        self.assertEqual(result['rate'], self.calc.quantize_money(expected_rate))
    
    def test_decimal_precision(self):
        """Test that decimal precision is maintained correctly."""
        result = self.calc.calculate_from_two_params(
            quantity="10.123",  # 3 decimals
            rate="99.99"
        )
        
        self.assertEqual(result['quantity'], Decimal('10.123'))
        # 10.123 * 99.99 = 1012.19877, rounded to 1012.20
        expected_amount = Decimal('10.123') * Decimal('99.99')
        self.assertEqual(result['amount'], self.calc.quantize_money(expected_amount))
    
    def test_insufficient_parameters_error(self):
        """Test error when less than 2 parameters provided."""
        with self.assertRaises(CalculationError) as context:
            self.calc.calculate_from_two_params(quantity=10)
        
        self.assertIn("At least two parameters", str(context.exception))
    
    def test_zero_quantity_error(self):
        """Test error when quantity is zero and rate needs calculation."""
        with self.assertRaises(CalculationError) as context:
            self.calc.calculate_from_two_params(
                quantity=0,
                amount=1000
            )
        
        self.assertIn("Quantity cannot be zero", str(context.exception))
    
    def test_zero_rate_error(self):
        """Test error when rate is zero and quantity needs calculation."""
        with self.assertRaises(CalculationError) as context:
            self.calc.calculate_from_two_params(
                rate=0,
                amount=1000
            )
        
        self.assertIn("Rate cannot be zero", str(context.exception))
    
    def test_calculate_line_item(self):
        """Test line item calculation."""
        result = self.calc.calculate_line_item(
            quantity=5,
            rate=200
        )
        
        self.assertEqual(result['quantity'], Decimal('5.000'))
        self.assertEqual(result['rate'], Decimal('200.00'))
        self.assertEqual(result['amount'], Decimal('1000.00'))
    
    def test_calculate_line_item_from_qty_and_amount(self):
        """Test line item with quantity and amount."""
        result = self.calc.calculate_line_item(
            quantity=4,
            amount=800
        )
        
        self.assertEqual(result['quantity'], Decimal('4.000'))
        self.assertEqual(result['rate'], Decimal('200.00'))
        self.assertEqual(result['amount'], Decimal('800.00'))
    
    def test_calculate_invoice_totals(self):
        """Test invoice totals calculation."""
        line_items = [
            {'amount': Decimal('1000.00')},
            {'amount': Decimal('2000.00')},
            {'amount': Decimal('500.00')}
        ]
        
        totals = self.calc.calculate_invoice_totals(line_items)
        
        self.assertEqual(totals['subtotal'], Decimal('3500.00'))
        self.assertEqual(totals['cgst'], Decimal('52.50'))  # 1.5% of 3500
        self.assertEqual(totals['sgst'], Decimal('52.50'))  # 1.5% of 3500
        self.assertEqual(totals['total_gst'], Decimal('105.00'))
        self.assertEqual(totals['calculated_total'], Decimal('3605.00'))
        self.assertEqual(totals['final_total'], Decimal('3605.00'))
        self.assertEqual(totals['rounded_off'], Decimal('0.00'))
    
    def test_calculate_invoice_totals_with_override(self):
        """Test invoice totals with user-specified total."""
        line_items = [
            {'amount': Decimal('1000.00')},
            {'amount': Decimal('2000.00')}
        ]
        
        # User wants total to be exactly 3100
        totals = self.calc.calculate_invoice_totals(
            line_items,
            user_total_inclusive=3100
        )
        
        self.assertEqual(totals['subtotal'], Decimal('3000.00'))
        self.assertEqual(totals['final_total'], Decimal('3100.00'))
        # Calculated would be 3090 (3000 + 90), but user wants 3100
        self.assertEqual(totals['rounded_off'], Decimal('10.00'))
    
    def test_real_world_jewellery_example(self):
        """Test a real-world jewellery billing scenario."""
        # Customer buys 25.650 grams of gold at ₹6500/gram
        result = self.calc.calculate_from_two_params(
            quantity="25.650",
            rate="6500.00"
        )
        
        self.assertEqual(result['quantity'], Decimal('25.650'))
        self.assertEqual(result['rate'], Decimal('6500.00'))
        # 25.650 * 6500 = 166725
        self.assertEqual(result['amount'], Decimal('166725.00'))
        # CGST = 166725 * 1.5% = 2500.875 -> 2500.88
        self.assertEqual(result['cgst'], Decimal('2500.88'))
        # SGST = 166725 * 1.5% = 2500.875 -> 2500.88
        self.assertEqual(result['sgst'], Decimal('2500.88'))
        # Total GST = 5001.76
        self.assertEqual(result['total_gst'], Decimal('5001.76'))
        # Final = 166725 + 5001.76 = 171726.76
        self.assertEqual(result['total_inclusive'], Decimal('171726.76'))
    
    def test_float_inputs_accepted(self):
        """Test that float inputs are accepted and handled correctly."""
        # Even though we use Decimal internally, floats should be accepted
        result = self.calc.calculate_from_two_params(
            quantity=10.5,
            rate=100.25
        )
        
        self.assertEqual(result['quantity'], Decimal('10.500'))
        self.assertEqual(result['rate'], Decimal('100.25'))
        # Should handle the conversion correctly
        self.assertIsInstance(result['amount'], Decimal)


class TestCalculatorFactory(unittest.TestCase):
    """Test the calculator factory function."""
    
    def test_create_calculator_default(self):
        """Test creating calculator with default rates."""
        calc = create_calculator()
        self.assertEqual(calc.cgst_rate, Decimal('1.5'))
        self.assertEqual(calc.sgst_rate, Decimal('1.5'))
    
    def test_create_calculator_custom_rates(self):
        """Test creating calculator with custom rates."""
        calc = create_calculator("2.5", "2.5")
        self.assertEqual(calc.cgst_rate, Decimal('2.5'))
        self.assertEqual(calc.sgst_rate, Decimal('2.5'))
        self.assertEqual(calc.total_gst_rate, Decimal('5.0'))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        self.calc = create_calculator()
    
    def test_very_small_quantities(self):
        """Test calculations with very small quantities."""
        result = self.calc.calculate_from_two_params(
            quantity="0.001",
            rate="50000"
        )
        
        self.assertEqual(result['quantity'], Decimal('0.001'))
        self.assertEqual(result['amount'], Decimal('50.00'))
    
    def test_very_large_amounts(self):
        """Test calculations with very large amounts."""
        result = self.calc.calculate_from_two_params(
            quantity=1000,
            rate=100000
        )
        
        self.assertEqual(result['amount'], Decimal('100000000.00'))
        # Should handle large numbers correctly
        self.assertIsInstance(result['total_inclusive'], Decimal)
    
    def test_rounding_half_up(self):
        """Test ROUND_HALF_UP behavior."""
        # 0.125 should round to 0.13
        result = self.calc.quantize_money(Decimal('0.125'))
        self.assertEqual(result, Decimal('0.13'))
        
        # 0.124 should round to 0.12
        result = self.calc.quantize_money(Decimal('0.124'))
        self.assertEqual(result, Decimal('0.12'))
        
        # 0.135 should round to 0.14
        result = self.calc.quantize_money(Decimal('0.135'))
        self.assertEqual(result, Decimal('0.14'))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
