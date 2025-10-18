"""
Core calculation module for Roopkala Jewellers Billing System.

This module provides calculation logic with Decimal precision for monetary values.
Supports flexible input scenarios and GST-inclusive calculations.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Optional, Tuple


class CalculationError(Exception):
    """Custom exception for calculation errors."""
    pass


class BillingCalculator:
    """
    Calculator for billing operations with GST handling.
    
    All monetary calculations use Decimal to avoid floating-point errors.
    """
    
    # Precision constants
    QUANTITY_PRECISION = Decimal('0.001')
    MONEY_PRECISION = Decimal('0.01')
    
    def __init__(self, cgst_rate: Decimal, sgst_rate: Decimal):
        """
        Initialize calculator with tax rates.
        
        Args:
            cgst_rate: CGST rate as percentage (e.g., Decimal('1.5'))
            sgst_rate: SGST rate as percentage (e.g., Decimal('1.5'))
        """
        self.cgst_rate = Decimal(str(cgst_rate))
        self.sgst_rate = Decimal(str(sgst_rate))
        self.total_gst_rate = self.cgst_rate + self.sgst_rate
    
    @staticmethod
    def to_decimal(value) -> Decimal:
        """
        Convert various input types to Decimal safely.
        
        Args:
            value: Input value (str, int, float, Decimal)
            
        Returns:
            Decimal representation of the value
            
        Raises:
            CalculationError: If conversion fails
        """
        if value is None or value == "":
            return Decimal('0')
        
        try:
            if isinstance(value, Decimal):
                return value
            return Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            raise CalculationError(f"Invalid numeric value: {value}") from e
    
    @staticmethod
    def quantize_quantity(value: Decimal) -> Decimal:
        """Round quantity to 3 decimal places."""
        return value.quantize(BillingCalculator.QUANTITY_PRECISION, rounding=ROUND_HALF_UP)
    
    @staticmethod
    def quantize_money(value: Decimal) -> Decimal:
        """Round monetary value to 2 decimal places."""
        return value.quantize(BillingCalculator.MONEY_PRECISION, rounding=ROUND_HALF_UP)
    
    def calculate_from_two_params(
        self,
        quantity: Optional[Decimal] = None,
        rate: Optional[Decimal] = None,
        amount: Optional[Decimal] = None,
        total_inclusive: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate all billing parameters given any two inputs.
        
        Supports these input combinations:
        1. quantity + rate → calculate amount, total_inclusive
        2. quantity + amount → calculate rate, total_inclusive
        3. quantity + total_inclusive → calculate rate, amount
        4. rate + amount → calculate quantity, total_inclusive
        5. rate + total_inclusive → calculate quantity, amount
        6. amount + total_inclusive → calculate quantity, rate
        
        Args:
            quantity: Item quantity (optional)
            rate: Rate per unit excluding GST (optional)
            amount: Total amount excluding GST (optional)
            total_inclusive: Total amount including GST (optional)
            
        Returns:
            Dictionary with keys: quantity, rate, amount, taxable_amount,
                                 cgst, sgst, total_gst, total_inclusive, rounded_off
                                 
        Raises:
            CalculationError: If insufficient or invalid parameters provided
        """
        # Convert all inputs to Decimal
        qty = self.to_decimal(quantity) if quantity is not None else None
        rt = self.to_decimal(rate) if rate is not None else None
        amt = self.to_decimal(amount) if amount is not None else None
        total_inc = self.to_decimal(total_inclusive) if total_inclusive is not None else None
        
        # Count non-None parameters
        provided = sum(x is not None for x in [qty, rt, amt, total_inc])
        
        if provided < 2:
            raise CalculationError("At least two parameters must be provided")
        
        # Calculate missing values based on what's provided
        try:
            # Case 1: quantity + rate
            if qty is not None and rt is not None:
                amt = qty * rt
                total_inc = amt * (Decimal('1') + self.total_gst_rate / Decimal('100'))
            
            # Case 2: quantity + amount
            elif qty is not None and amt is not None:
                if qty == 0:
                    raise CalculationError("Quantity cannot be zero when calculating rate")
                rt = amt / qty
                total_inc = amt * (Decimal('1') + self.total_gst_rate / Decimal('100'))
            
            # Case 3: quantity + total_inclusive
            elif qty is not None and total_inc is not None:
                amt = total_inc / (Decimal('1') + self.total_gst_rate / Decimal('100'))
                if qty == 0:
                    raise CalculationError("Quantity cannot be zero when calculating rate")
                rt = amt / qty
            
            # Case 4: rate + amount
            elif rt is not None and amt is not None:
                if rt == 0:
                    raise CalculationError("Rate cannot be zero when calculating quantity")
                qty = amt / rt
                total_inc = amt * (Decimal('1') + self.total_gst_rate / Decimal('100'))
            
            # Case 5: rate + total_inclusive
            elif rt is not None and total_inc is not None:
                amt = total_inc / (Decimal('1') + self.total_gst_rate / Decimal('100'))
                if rt == 0:
                    raise CalculationError("Rate cannot be zero when calculating quantity")
                qty = amt / rt
            
            # Case 6: amount + total_inclusive
            elif amt is not None and total_inc is not None:
                # Verify consistency
                expected_total = amt * (Decimal('1') + self.total_gst_rate / Decimal('100'))
                # Allow small tolerance for rounding
                if abs(expected_total - total_inc) > Decimal('0.02'):
                    # Back-calculate from total_inclusive
                    amt = total_inc / (Decimal('1') + self.total_gst_rate / Decimal('100'))
                
                # Cannot determine quantity and rate uniquely, set defaults
                qty = Decimal('1')
                rt = amt
            
            else:
                raise CalculationError("Invalid parameter combination")
            
        except (ZeroDivisionError, InvalidOperation) as e:
            raise CalculationError(f"Calculation error: {str(e)}") from e
        
        # Calculate tax components
        taxable_amount = amt
        cgst = self.quantize_money(taxable_amount * self.cgst_rate / Decimal('100'))
        sgst = self.quantize_money(taxable_amount * self.sgst_rate / Decimal('100'))
        total_gst = cgst + sgst
        
        # Calculate final total with rounding
        calculated_total = self.quantize_money(taxable_amount + total_gst)
        
        # Calculate rounded off amount if total_inclusive was provided
        if total_inclusive is not None:
            target_total = self.quantize_money(total_inc)
            rounded_off = target_total - calculated_total
        else:
            target_total = calculated_total
            rounded_off = Decimal('0')
        
        return {
            'quantity': self.quantize_quantity(qty),
            'rate': self.quantize_money(rt),
            'amount': self.quantize_money(amt),
            'taxable_amount': self.quantize_money(taxable_amount),
            'cgst': cgst,
            'sgst': sgst,
            'total_gst': total_gst,
            'total_inclusive': target_total,
            'rounded_off': self.quantize_money(rounded_off)
        }
    
    def calculate_line_item(
        self,
        quantity: Optional[Decimal] = None,
        rate: Optional[Decimal] = None,
        amount: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate a single line item (quantity, rate, amount).
        
        Args:
            quantity: Item quantity
            rate: Rate per unit
            amount: Total amount for line
            
        Returns:
            Dictionary with calculated values
        """
        qty = self.to_decimal(quantity) if quantity is not None else None
        rt = self.to_decimal(rate) if rate is not None else None
        amt = self.to_decimal(amount) if amount is not None else None
        
        provided = sum(x is not None for x in [qty, rt, amt])
        
        if provided < 2:
            raise CalculationError("At least two parameters required for line item")
        
        # Calculate the missing value
        if qty is not None and rt is not None:
            amt = qty * rt
        elif qty is not None and amt is not None:
            if qty == 0:
                raise CalculationError("Quantity cannot be zero")
            rt = amt / qty
        elif rt is not None and amt is not None:
            if rt == 0:
                raise CalculationError("Rate cannot be zero")
            qty = amt / rt
        
        # All values should be calculated by now
        if qty is None or rt is None or amt is None:
            raise CalculationError("Failed to calculate all required values")
        
        return {
            'quantity': self.quantize_quantity(qty),
            'rate': self.quantize_money(rt),
            'amount': self.quantize_money(amt)
        }
    
    def calculate_invoice_totals(
        self,
        line_items: list,
        user_total_inclusive: Optional[Decimal] = None
    ) -> Dict[str, Decimal]:
        """
        Calculate invoice totals from multiple line items.
        
        Args:
            line_items: List of dicts with 'amount' key (pre-calculated line amounts)
            user_total_inclusive: Optional user-specified total (for rounded-off calculation)
            
        Returns:
            Dictionary with subtotal, taxes, and final total
        """
        subtotal = Decimal('0')
        
        for item in line_items:
            item_amount = self.to_decimal(item.get('amount', 0))
            subtotal += item_amount
        
        subtotal = self.quantize_money(subtotal)
        
        cgst = self.quantize_money(subtotal * self.cgst_rate / Decimal('100'))
        sgst = self.quantize_money(subtotal * self.sgst_rate / Decimal('100'))
        total_gst = cgst + sgst
        
        calculated_total = self.quantize_money(subtotal + total_gst)
        
        if user_total_inclusive is not None:
            target_total = self.quantize_money(self.to_decimal(user_total_inclusive))
            rounded_off = target_total - calculated_total
        else:
            target_total = calculated_total
            rounded_off = Decimal('0')
        
        return {
            'subtotal': subtotal,
            'cgst': cgst,
            'sgst': sgst,
            'total_gst': total_gst,
            'calculated_total': calculated_total,
            'rounded_off': self.quantize_money(rounded_off),
            'final_total': target_total
        }


# Factory function for easy calculator creation
def create_calculator(cgst_rate: str = "1.5", sgst_rate: str = "1.5") -> BillingCalculator:
    """
    Create a BillingCalculator instance with specified tax rates.
    
    Args:
        cgst_rate: CGST percentage as string (default "1.5")
        sgst_rate: SGST percentage as string (default "1.5")
        
    Returns:
        BillingCalculator instance
    """
    return BillingCalculator(Decimal(cgst_rate), Decimal(sgst_rate))
