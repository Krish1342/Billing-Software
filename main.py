"""
Roopkala Jewellers Billing System
Main application entry point.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from invoice_ui import InvoiceUI


def main():
    """Main application entry point."""
    try:
        # Create root window
        root = tk.Tk()
        
        # Set icon (optional - would need an .ico file)
        # root.iconbitmap('icon.ico')
        
        # Initialize the application
        app = InvoiceUI(root)
        
        # Center window on screen
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Run the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
