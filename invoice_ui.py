"""
Invoice UI for Roopkala Jewellers Billing System.

Main Tkinter interface for creating and managing invoices.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from decimal import Decimal
import json
from typing import List, Dict, Optional

from calc import create_calculator, CalculationError
from db_handler import DatabaseHandler
from pdf_generator import InvoicePDFGenerator


class InvoiceUI:
    """Main invoice creation and management UI."""
    
    def __init__(self, root: tk.Tk, settings_path: str = "settings.json"):
        """
        Initialize the invoice UI.
        
        Args:
            root: Tkinter root window
            settings_path: Path to settings JSON file
        """
        self.root = root
        self.settings_path = settings_path
        
        # Load settings
        with open(settings_path, 'r') as f:
            self.settings = json.load(f)
        
        # Initialize components
        self.calculator = create_calculator(
            self.settings['tax']['cgst_rate'],
            self.settings['tax']['sgst_rate']
        )
        self.db = DatabaseHandler()
        self.pdf_generator = InvoicePDFGenerator(settings_path)
        
        # Data storage
        self.line_items: List[Dict] = []
        
        # Setup UI
        self.setup_ui()
        
        # Load next invoice number
        self.load_next_invoice_number()
    
    def setup_ui(self):
        """Setup the main UI components."""
        self.root.title(f"{self.settings['company']['name']} - Billing System")
        self.root.geometry("1200x800")
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=self.settings['company']['name'],
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Invoice Header Section
        header_frame = ttk.LabelFrame(main_frame, text="Invoice Details", padding="10")
        header_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        header_frame.columnconfigure(3, weight=1)
        
        # Row 0: Invoice Number and Date
        ttk.Label(header_frame, text="Invoice No:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.invoice_number_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.invoice_number_var, width=20).grid(
            row=0, column=1, sticky=tk.W, padx=(0, 20)
        )
        
        ttk.Label(header_frame, text="Date:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.invoice_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(header_frame, textvariable=self.invoice_date_var, width=20).grid(
            row=0, column=3, sticky=tk.W
        )
        
        # Row 1: Customer Name
        ttk.Label(header_frame, text="Customer Name:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.customer_name_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.customer_name_var, width=40).grid(
            row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0)
        )
        
        # Row 2: Customer Address
        ttk.Label(header_frame, text="Address:").grid(row=2, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.customer_address_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.customer_address_var, width=40).grid(
            row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0)
        )
        
        # Row 3: Phone and GSTIN
        ttk.Label(header_frame, text="Phone:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.customer_phone_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.customer_phone_var, width=20).grid(
            row=3, column=1, sticky=tk.W, padx=(0, 20), pady=(5, 0)
        )
        
        ttk.Label(header_frame, text="GSTIN:").grid(row=3, column=2, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.customer_gstin_var = tk.StringVar()
        ttk.Entry(header_frame, textvariable=self.customer_gstin_var, width=20).grid(
            row=3, column=3, sticky=tk.W, pady=(5, 0)
        )
        
        # Line Items Section
        items_frame = ttk.LabelFrame(main_frame, text="Line Items", padding="10")
        items_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(1, weight=1)
        
        # Input row for adding items
        input_frame = ttk.Frame(items_frame)
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(input_frame, text="Description:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.item_desc_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_desc_var, width=25).grid(
            row=0, column=1, padx=(0, 10)
        )
        
        ttk.Label(input_frame, text="HSN:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.item_hsn_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_hsn_var, width=10).grid(
            row=0, column=3, padx=(0, 10)
        )
        
        ttk.Label(input_frame, text="Qty:").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.item_qty_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_qty_var, width=10).grid(
            row=0, column=5, padx=(0, 10)
        )
        
        ttk.Label(input_frame, text="Rate:").grid(row=0, column=6, sticky=tk.W, padx=(0, 5))
        self.item_rate_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_rate_var, width=10).grid(
            row=0, column=7, padx=(0, 10)
        )
        
        ttk.Label(input_frame, text="Amount:").grid(row=0, column=8, sticky=tk.W, padx=(0, 5))
        self.item_amount_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_amount_var, width=10).grid(
            row=0, column=9, padx=(0, 10)
        )
        
        ttk.Button(input_frame, text="Add Item", command=self.add_line_item).grid(
            row=0, column=10
        )
        
        # Items table
        table_frame = ttk.Frame(items_frame)
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create Treeview
        columns = ('description', 'hsn', 'quantity', 'rate', 'amount')
        self.items_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        
        self.items_tree.heading('description', text='Description')
        self.items_tree.heading('hsn', text='HSN Code')
        self.items_tree.heading('quantity', text='Quantity')
        self.items_tree.heading('rate', text='Rate')
        self.items_tree.heading('amount', text='Amount')
        
        self.items_tree.column('description', width=300)
        self.items_tree.column('hsn', width=100)
        self.items_tree.column('quantity', width=100, anchor=tk.E)
        self.items_tree.column('rate', width=100, anchor=tk.E)
        self.items_tree.column('amount', width=100, anchor=tk.E)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Item controls
        item_controls = ttk.Frame(items_frame)
        item_controls.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(item_controls, text="Remove Selected", command=self.remove_line_item).grid(
            row=0, column=0, padx=(0, 5)
        )
        ttk.Button(item_controls, text="Clear All", command=self.clear_all_items).grid(
            row=0, column=1
        )
        
        # Totals and Actions Section
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        bottom_frame.columnconfigure(0, weight=1)
        
        # Notes
        notes_frame = ttk.LabelFrame(bottom_frame, text="Notes", padding="5")
        notes_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.notes_text = tk.Text(notes_frame, height=3, width=50)
        self.notes_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        notes_frame.columnconfigure(0, weight=1)
        
        # Totals
        totals_frame = ttk.LabelFrame(bottom_frame, text="Totals", padding="10")
        totals_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))
        
        self.subtotal_var = tk.StringVar(value="0.00")
        self.cgst_var = tk.StringVar(value="0.00")
        self.sgst_var = tk.StringVar(value="0.00")
        self.total_gst_var = tk.StringVar(value="0.00")
        self.rounded_off_var = tk.StringVar(value="0.00")
        self.final_total_var = tk.StringVar(value="0.00")
        
        ttk.Label(totals_frame, text="Subtotal:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(totals_frame, textvariable=self.subtotal_var, font=('Arial', 10)).grid(
            row=0, column=1, sticky=tk.E, padx=(10, 0)
        )
        
        ttk.Label(totals_frame, text=f"CGST @ {self.settings['tax']['cgst_rate']}%:").grid(
            row=1, column=0, sticky=tk.W
        )
        ttk.Label(totals_frame, textvariable=self.cgst_var).grid(
            row=1, column=1, sticky=tk.E, padx=(10, 0)
        )
        
        ttk.Label(totals_frame, text=f"SGST @ {self.settings['tax']['sgst_rate']}%:").grid(
            row=2, column=0, sticky=tk.W
        )
        ttk.Label(totals_frame, textvariable=self.sgst_var).grid(
            row=2, column=1, sticky=tk.E, padx=(10, 0)
        )
        
        ttk.Label(totals_frame, text="Total GST:").grid(row=3, column=0, sticky=tk.W)
        ttk.Label(totals_frame, textvariable=self.total_gst_var, font=('Arial', 10)).grid(
            row=3, column=1, sticky=tk.E, padx=(10, 0)
        )
        
        ttk.Label(totals_frame, text="Rounded Off:").grid(row=4, column=0, sticky=tk.W)
        ttk.Label(totals_frame, textvariable=self.rounded_off_var).grid(
            row=4, column=1, sticky=tk.E, padx=(10, 0)
        )
        
        ttk.Separator(totals_frame, orient=tk.HORIZONTAL).grid(
            row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5
        )
        
        ttk.Label(totals_frame, text="Final Total:", font=('Arial', 11, 'bold')).grid(
            row=6, column=0, sticky=tk.W
        )
        ttk.Label(
            totals_frame,
            textvariable=self.final_total_var,
            font=('Arial', 12, 'bold')
        ).grid(row=6, column=1, sticky=tk.E, padx=(10, 0))
        
        # Optional: User-specified total
        ttk.Label(totals_frame, text="Override Total:").grid(row=7, column=0, sticky=tk.W, pady=(10, 0))
        self.override_total_var = tk.StringVar()
        override_entry = ttk.Entry(totals_frame, textvariable=self.override_total_var, width=15)
        override_entry.grid(row=7, column=1, sticky=tk.E, padx=(10, 0), pady=(10, 0))
        override_entry.bind('<FocusOut>', lambda e: self.recalculate_totals())
        override_entry.bind('<Return>', lambda e: self.recalculate_totals())
        
        # Action buttons
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(
            actions_frame,
            text="Save Invoice",
            command=self.save_invoice,
            width=15
        ).grid(row=0, column=0, padx=(0, 5))
        
        ttk.Button(
            actions_frame,
            text="Generate PDF",
            command=self.generate_pdf,
            width=15
        ).grid(row=0, column=1, padx=(0, 5))
        
        ttk.Button(
            actions_frame,
            text="New Invoice",
            command=self.new_invoice,
            width=15
        ).grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(
            actions_frame,
            text="Load Invoice",
            command=self.load_invoice,
            width=15
        ).grid(row=0, column=3, padx=(0, 5))
    
    def load_next_invoice_number(self):
        """Load the next invoice number from database."""
        next_number = self.db.get_next_invoice_number(
            self.settings['invoice']['prefix'],
            self.settings['invoice']['starting_number']
        )
        self.invoice_number_var.set(next_number)
    
    def add_line_item(self):
        """Add a line item to the invoice."""
        desc = self.item_desc_var.get().strip()
        if not desc:
            messagebox.showwarning("Validation", "Description is required")
            return
        
        hsn = self.item_hsn_var.get().strip()
        qty_str = self.item_qty_var.get().strip()
        rate_str = self.item_rate_var.get().strip()
        amount_str = self.item_amount_var.get().strip()
        
        # Count provided values
        provided = sum(bool(x) for x in [qty_str, rate_str, amount_str])
        
        if provided < 2:
            messagebox.showwarning(
                "Validation",
                "Please provide at least 2 of: Quantity, Rate, Amount"
            )
            return
        
        try:
            # Calculate line item
            result = self.calculator.calculate_line_item(
                quantity=qty_str if qty_str else None,
                rate=rate_str if rate_str else None,
                amount=amount_str if amount_str else None
            )
            
            # Store item
            item = {
                'description': desc,
                'hsn_code': hsn,
                'quantity': result['quantity'],
                'rate': result['rate'],
                'amount': result['amount']
            }
            
            self.line_items.append(item)
            
            # Update tree
            self.items_tree.insert('', tk.END, values=(
                desc,
                hsn,
                f"{result['quantity']:.3f}",
                f"₹ {result['rate']:.2f}",
                f"₹ {result['amount']:.2f}"
            ))
            
            # Clear inputs
            self.item_desc_var.set('')
            self.item_hsn_var.set('')
            self.item_qty_var.set('')
            self.item_rate_var.set('')
            self.item_amount_var.set('')
            
            # Recalculate totals
            self.recalculate_totals()
            
        except CalculationError as e:
            messagebox.showerror("Calculation Error", str(e))
    
    def remove_line_item(self):
        """Remove selected line item."""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select an item to remove")
            return
        
        # Get index
        item_id = selection[0]
        index = self.items_tree.index(item_id)
        
        # Remove from data
        del self.line_items[index]
        
        # Remove from tree
        self.items_tree.delete(item_id)
        
        # Recalculate
        self.recalculate_totals()
    
    def clear_all_items(self):
        """Clear all line items."""
        if messagebox.askyesno("Confirm", "Clear all line items?"):
            self.line_items.clear()
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            self.recalculate_totals()
    
    def recalculate_totals(self):
        """Recalculate invoice totals."""
        if not self.line_items:
            self.subtotal_var.set("0.00")
            self.cgst_var.set("0.00")
            self.sgst_var.set("0.00")
            self.total_gst_var.set("0.00")
            self.rounded_off_var.set("0.00")
            self.final_total_var.set("0.00")
            return
        
        # Check if user provided override total
        override_str = self.override_total_var.get().strip()
        override_total = override_str if override_str else None
        
        try:
            totals = self.calculator.calculate_invoice_totals(
                self.line_items,
                override_total
            )
            
            self.subtotal_var.set(f"₹ {totals['subtotal']:.2f}")
            self.cgst_var.set(f"₹ {totals['cgst']:.2f}")
            self.sgst_var.set(f"₹ {totals['sgst']:.2f}")
            self.total_gst_var.set(f"₹ {totals['total_gst']:.2f}")
            self.rounded_off_var.set(f"₹ {totals['rounded_off']:.2f}")
            self.final_total_var.set(f"₹ {totals['final_total']:.2f}")
            
        except CalculationError as e:
            messagebox.showerror("Calculation Error", str(e))
    
    def save_invoice(self):
        """Save invoice to database."""
        # Validate
        if not self.customer_name_var.get().strip():
            messagebox.showwarning("Validation", "Customer name is required")
            return
        
        if not self.line_items:
            messagebox.showwarning("Validation", "Please add at least one line item")
            return
        
        try:
            # Calculate totals
            override_str = self.override_total_var.get().strip()
            override_total = override_str if override_str else None
            
            totals = self.calculator.calculate_invoice_totals(
                self.line_items,
                override_total
            )
            
            # Save to database
            invoice_id = self.db.save_invoice(
                invoice_number=self.invoice_number_var.get(),
                invoice_date=self.invoice_date_var.get(),
                customer_name=self.customer_name_var.get(),
                customer_address=self.customer_address_var.get(),
                customer_phone=self.customer_phone_var.get(),
                customer_gstin=self.customer_gstin_var.get(),
                line_items=self.line_items,
                totals=totals,
                notes=self.notes_text.get("1.0", tk.END).strip()
            )
            
            messagebox.showinfo(
                "Success",
                f"Invoice saved successfully!\nInvoice ID: {invoice_id}"
            )
            
            # Ask if user wants to create new invoice
            if messagebox.askyesno("New Invoice", "Create a new invoice?"):
                self.new_invoice()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice: {str(e)}")
    
    def generate_pdf(self):
        """Generate PDF for current invoice."""
        if not self.line_items:
            messagebox.showwarning("Validation", "Please add line items first")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Invoice_{self.invoice_number_var.get()}.pdf"
        )
        
        if not filename:
            return
        
        try:
            # Prepare invoice data
            override_str = self.override_total_var.get().strip()
            override_total = override_str if override_str else None
            
            totals = self.calculator.calculate_invoice_totals(
                self.line_items,
                override_total
            )
            
            invoice_data = {
                'invoice_number': self.invoice_number_var.get(),
                'invoice_date': self.invoice_date_var.get(),
                'customer_name': self.customer_name_var.get(),
                'customer_address': self.customer_address_var.get(),
                'customer_phone': self.customer_phone_var.get(),
                'customer_gstin': self.customer_gstin_var.get(),
                'subtotal': str(totals['subtotal']),
                'cgst': str(totals['cgst']),
                'sgst': str(totals['sgst']),
                'total_gst': str(totals['total_gst']),
                'rounded_off': str(totals['rounded_off']),
                'final_total': str(totals['final_total']),
                'notes': self.notes_text.get("1.0", tk.END).strip()
            }
            
            # Convert line items to string format
            line_items_str = []
            for item in self.line_items:
                line_items_str.append({
                    'description': item['description'],
                    'hsn_code': item['hsn_code'],
                    'quantity': str(item['quantity']),
                    'rate': str(item['rate']),
                    'amount': str(item['amount'])
                })
            
            # Generate PDF
            self.pdf_generator.generate_invoice_pdf(
                filename,
                invoice_data,
                line_items_str
            )
            
            messagebox.showinfo("Success", f"PDF generated successfully!\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF: {str(e)}")
    
    def new_invoice(self):
        """Clear form for new invoice."""
        # Clear all fields
        self.customer_name_var.set('')
        self.customer_address_var.set('')
        self.customer_phone_var.set('')
        self.customer_gstin_var.set('')
        self.notes_text.delete("1.0", tk.END)
        self.override_total_var.set('')
        
        # Clear items
        self.line_items.clear()
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Reset date and invoice number
        self.invoice_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.load_next_invoice_number()
        
        # Reset totals
        self.recalculate_totals()
    
    def load_invoice(self):
        """Load an existing invoice."""
        # Simple dialog to get invoice number
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Invoice")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Enter Invoice Number:").pack(pady=10)
        
        invoice_num_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=invoice_num_var, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def do_load():
            invoice_num = invoice_num_var.get().strip()
            if not invoice_num:
                messagebox.showwarning("Validation", "Please enter invoice number")
                return
            
            invoice = self.db.get_invoice(invoice_num)
            
            if not invoice:
                messagebox.showwarning("Not Found", f"Invoice {invoice_num} not found")
                return
            
            # Load data
            self.invoice_number_var.set(invoice['invoice_number'])
            self.invoice_date_var.set(invoice['invoice_date'])
            self.customer_name_var.set(invoice['customer_name'])
            self.customer_address_var.set(invoice['customer_address'] or '')
            self.customer_phone_var.set(invoice['customer_phone'] or '')
            self.customer_gstin_var.set(invoice['customer_gstin'] or '')
            self.notes_text.delete("1.0", tk.END)
            self.notes_text.insert("1.0", invoice['notes'] or '')
            
            # Clear and load items
            self.line_items.clear()
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            for db_item in invoice['line_items']:
                item = {
                    'description': db_item['description'],
                    'hsn_code': db_item['hsn_code'] or '',
                    'quantity': Decimal(db_item['quantity']),
                    'rate': Decimal(db_item['rate']),
                    'amount': Decimal(db_item['amount'])
                }
                self.line_items.append(item)
                
                self.items_tree.insert('', tk.END, values=(
                    item['description'],
                    item['hsn_code'],
                    f"{item['quantity']:.3f}",
                    f"₹ {item['rate']:.2f}",
                    f"₹ {item['amount']:.2f}"
                ))
            
            # Recalculate totals
            self.recalculate_totals()
            
            dialog.destroy()
            messagebox.showinfo("Success", "Invoice loaded successfully")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Load", command=do_load).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: do_load())


def main():
    """Main entry point for invoice UI."""
    root = tk.Tk()
    app = InvoiceUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
