"""
PDF Generator for Roopkala Jewellers Billing System.

Generates professional A4 invoice PDFs matching the exact template format.
Uses ReportLab's canvas for precise positioning to match the handwritten template.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from decimal import Decimal
from typing import Dict, List
import json


class InvoicePDFGenerator:
    """Generate PDF invoices with professional formatting matching the exact template."""

    def __init__(self, settings_path: str = "settings.json"):
        """
        Initialize PDF generator.

        Args:
            settings_path: Path to settings JSON file
        """
        with open(settings_path, "r") as f:
            self.settings = json.load(f)

        self.company = self.settings["company"]
        self.page_width, self.page_height = A4

    def generate_invoice_pdf(
        self, output_path: str, invoice_data: Dict, line_items: List[Dict]
    ):
        """
        Generate a PDF invoice matching the exact template format.

        Args:
            output_path: Path where PDF will be saved
            invoice_data: Dictionary with invoice header information
            line_items: List of line item dictionaries
        """
        # Create canvas
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        # Margins
        margin_left = 15 * mm
        margin_right = 15 * mm
        margin_top = 15 * mm
        margin_bottom = 15 * mm

        # Draw decorative double border
        self._draw_double_border(
            c, margin_left, margin_bottom, width - margin_right, height - margin_top
        )

        # Main content area (no left sidebar now)
        content_left = margin_left + 10 * mm
        content_right = width - margin_right - 10 * mm
        content_top = height - margin_top - 10 * mm

        # Company header at top with name, address, GSTIN
        y_pos = content_top
        y_pos = self._draw_company_header(c, content_left, content_right, y_pos)

        # Tax Invoice title (centered with color and box)
        y_pos -= 15 * mm

        # Draw background box for TAX INVOICE
        title_text = "TAX INVOICE"
        c.setFont("Helvetica-Bold", 16)
        text_width = c.stringWidth(title_text, "Helvetica-Bold", 16)
        box_width = text_width + 20 * mm
        box_height = 8 * mm
        box_x = ((content_left + content_right) / 2) - (box_width / 2)
        box_y = y_pos - 2 * mm

        # Gradient background for title
        c.setFillColor(colors.HexColor("#8B0000"))
        c.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)

        # Gold border
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(1.5)
        c.rect(box_x, box_y, box_width, box_height, fill=0, stroke=1)

        # Draw text in white
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString((content_left + content_right) / 2, y_pos, title_text)

        # Reset color to black for rest of content
        c.setFillColor(colors.black)

        # Invoice details box
        y_pos -= 10 * mm
        y_pos = self._draw_invoice_details_box(
            c, content_left, content_right, y_pos, invoice_data
        )

        # Items table
        y_pos -= 5 * mm
        y_pos = self._draw_items_table(
            c, content_left, content_right, y_pos, line_items, invoice_data
        )

        # Footer with GSTIN
        self._draw_footer(
            c, content_left, content_right, margin_bottom + 10 * mm, invoice_data
        )

        # Save PDF
        c.save()

    def _draw_double_border(self, c, x1, y1, x2, y2):
        """Draw decorative double-line border with colors."""
        # Outer border (dark red/maroon)
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(2)
        c.rect(x1, y1, x2 - x1, y2 - y1, fill=0, stroke=1)

        # Middle decorative line (gold)
        offset1 = 1.5 * mm
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(0.8)
        c.rect(
            x1 + offset1,
            y1 + offset1,
            (x2 - x1) - 2 * offset1,
            (y2 - y1) - 2 * offset1,
            fill=0,
            stroke=1,
        )

        # Inner border (dark red/maroon)
        offset2 = 3 * mm
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(0.5)
        c.rect(
            x1 + offset2,
            y1 + offset2,
            (x2 - x1) - 2 * offset2,
            (y2 - y1) - 2 * offset2,
            fill=0,
            stroke=1,
        )

    def _draw_company_header(self, c, x1, x2, y_start):
        """Draw company header details with styling - now horizontal at top."""
        y = y_start

        # Company name in dark red - centered and large
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#8B0000"))
        company_name = self.company["name"]
        c.drawCentredString((x1 + x2) / 2, y, company_name)

        # Decorative line under company name
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(1.5)
        line_center = (x1 + x2) / 2
        line_width = 80 * mm
        c.line(
            line_center - line_width / 2,
            y - 2 * mm,
            line_center + line_width / 2,
            y - 2 * mm,
        )

        y -= 7 * mm
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        address_text = (
            f"{self.company['address_line1']}, {self.company['address_line2']}"
        )
        c.drawCentredString((x1 + x2) / 2, y, address_text)

        y -= 4 * mm
        contact_text = (
            f"Phone: {self.company['phone']} | Email: {self.company['email']}"
        )
        c.drawCentredString((x1 + x2) / 2, y, contact_text)

        # GSTIN below contact info
        y -= 4 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#8B0000"))
        gstin_text = f"GSTIN: {self.company['gstin']}"
        c.drawCentredString((x1 + x2) / 2, y, gstin_text)

        return y - 5 * mm

    def _draw_invoice_details_box(self, c, x1, x2, y_start, invoice_data):
        """Draw invoice number, date, and customer details box with styling."""
        box_height = 35 * mm
        y_bottom = y_start - box_height

        # Draw box with colored border
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(1)
        c.rect(x1, y_bottom, x2 - x1, box_height, fill=0, stroke=1)

        # Vertical divider (between invoice details and customer details)
        mid_x = x1 + (x2 - x1) * 0.35
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(1)
        c.line(mid_x, y_bottom, mid_x, y_start)

        # Left side: Invoice details with light background
        c.setFillColor(colors.HexColor("#FFF8DC"))  # Cornsilk
        c.rect(x1, y_bottom, mid_x - x1, box_height, fill=1, stroke=0)

        # Right side: Customer details with white background
        c.setFillColor(colors.white)
        c.rect(mid_x, y_bottom, x2 - mid_x, box_height, fill=1, stroke=0)

        # Redraw borders
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(1)
        c.rect(x1, y_bottom, x2 - x1, box_height, fill=0, stroke=1)
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.line(mid_x, y_bottom, mid_x, y_start)

        # Left side: Invoice details
        y = y_start - 5 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(x1 + 3 * mm, y, "No.:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(x1 + 15 * mm, y, invoice_data.get("invoice_number", ""))

        y -= 5 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(x1 + 3 * mm, y, "Date:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(x1 + 15 * mm, y, invoice_data.get("invoice_date", ""))

        # Right side: Customer details
        y = y_start - 5 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(mid_x + 3 * mm, y, "Name:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(mid_x + 15 * mm, y, invoice_data.get("customer_name", ""))

        y -= 5 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(mid_x + 3 * mm, y, "Address:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        # Wrap address if needed
        address = invoice_data.get("customer_address", "")
        if len(address) > 40:
            c.drawString(mid_x + 15 * mm, y, address[:40])
            y -= 4 * mm
            c.drawString(mid_x + 15 * mm, y, address[40:])
        else:
            c.drawString(mid_x + 15 * mm, y, address)

        y -= 5 * mm
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(mid_x + 3 * mm, y, "Phone:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(mid_x + 15 * mm, y, invoice_data.get("customer_phone", ""))

        return y_bottom - 3 * mm

    def _draw_items_table(self, c, x1, x2, y_start, line_items, invoice_data):
        """Draw items table with totals."""
        # Prepare table data
        table_data = []

        # Header row
        headers = [
            "Name",
            "Description",
            "HSN Code",
            "Weight",
            "Rate\n(with making charges)",
            "Amount",
        ]
        table_data.append(headers)

        # Item rows
        for idx, item in enumerate(line_items, start=1):
            row = [
                f"{idx}",
                item.get("description", ""),
                item.get("hsn_code", ""),
                f"{float(item.get('quantity', 0)):.3f}",
                f"₹ {float(item.get('rate', 0)):.2f}",
                f"₹ {float(item.get('amount', 0)):.2f}",
            ]
            table_data.append(row)

        # Add empty rows to fill space if needed
        min_rows = 5
        while len(table_data) < min_rows + 1:  # +1 for header
            table_data.append(["", "", "", "", "", ""])

        # Totals rows
        subtotal = invoice_data.get("subtotal", "0")
        cgst = invoice_data.get("cgst_amount", "0")  # Fixed key
        sgst = invoice_data.get("sgst_amount", "0")  # Fixed key
        final_total = invoice_data.get("total_amount", "0")  # Fixed key
        rounded_off = invoice_data.get("rounded_off", "0")

        table_data.append(["", "", "", "TOTAL", "", f"₹ {float(subtotal):.2f}"])
        table_data.append(
            [
                "",
                "",
                "",
                f"CGST {self.settings['tax']['cgst_rate']}%",
                "",
                f"₹ {float(cgst):.2f}",
            ]
        )
        table_data.append(
            [
                "",
                "",
                "",
                f"SGST {self.settings['tax']['sgst_rate']}%",
                "",
                f"₹ {float(sgst):.2f}",
            ]
        )

        # Only add rounded off if non-zero
        if float(rounded_off) != 0:
            table_data.append(
                ["", "", "", "Rounded Off", "", f"₹ {float(rounded_off):.2f}"]
            )

        table_data.append(["", "", "", "G.TOTAL", "", f"₹ {float(final_total):.2f}"])

        # Column widths (adjusted to fit within page borders)
        # Total available width = content_right - content_left ≈ 175mm
        col_widths = [
            12 * mm,
            55 * mm,
            22 * mm,
            22 * mm,
            32 * mm,
            32 * mm,
        ]  # Total = 175mm

        # Create and style table
        table = Table(table_data, colWidths=col_widths)

        # Calculate totals row position
        num_totals_rows = 4 if float(rounded_off) == 0 else 5
        totals_start = len(table_data) - num_totals_rows

        # Style the table
        style = TableStyle(
            [
                # Header row with gradient-like color
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8B0000")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                # Data rows
                ("FONTNAME", (0, 1), (-1, totals_start - 1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, totals_start - 1), 8),
                ("ALIGN", (0, 1), (0, totals_start - 1), "CENTER"),  # Name column
                ("ALIGN", (1, 1), (1, totals_start - 1), "LEFT"),  # Description column
                ("ALIGN", (2, 1), (2, totals_start - 1), "CENTER"),  # HSN
                ("ALIGN", (3, 1), (3, totals_start - 1), "CENTER"),  # Weight
                ("ALIGN", (4, 1), (4, totals_start - 1), "RIGHT"),  # Rate
                ("ALIGN", (5, 1), (5, totals_start - 1), "RIGHT"),  # Amount
                # Totals rows with light background
                (
                    "BACKGROUND",
                    (0, totals_start),
                    (-1, -2),
                    colors.HexColor("#FFF8DC"),
                ),  # Cornsilk
                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    colors.HexColor("#FFD700"),
                ),  # Gold for G.TOTAL
                ("FONTNAME", (0, totals_start), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, totals_start), (-1, -1), 9),
                ("ALIGN", (3, totals_start), (3, -1), "RIGHT"),
                ("ALIGN", (5, totals_start), (5, -1), "RIGHT"),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8B0000")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                # Bold line before totals
                (
                    "LINEABOVE",
                    (0, totals_start),
                    (-1, totals_start),
                    2,
                    colors.HexColor("#8B0000"),
                ),
                # Extra bold line before G.TOTAL
                ("LINEABOVE", (0, -1), (-1, -1), 2, colors.HexColor("#8B0000")),
            ]
        )

        table.setStyle(style)

        # Calculate table dimensions and draw
        table_width = sum(col_widths)
        table_height = len(table_data) * 6 * mm  # Approximate row height

        # Position table
        table.wrapOn(c, table_width, table_height)
        table_x = x1
        table_y = y_start - table_height

        table.drawOn(c, table_x, table_y)

        return table_y - 5 * mm

    def _draw_footer(self, c, x1, x2, y, invoice_data):
        """Draw footer with signature area."""
        # "For Roopkala Jewellers" text (top right)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawRightString(x2, y + 15 * mm, "For Roopkala Jewellers")

        # Add a signature line
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.5)
        c.line(x2 - 50 * mm, y + 5 * mm, x2, y + 5 * mm)
        c.setFont("Helvetica", 8)
        c.drawRightString(x2, y + 2 * mm, "Authorized Signatory")

    def _format_decimal(self, value: str, decimals: int = 2) -> str:
        """
        Format decimal value for display.

        Args:
            value: String representation of decimal
            decimals: Number of decimal places

        Returns:
            Formatted string
        """
        try:
            dec_value = Decimal(str(value))
            if decimals == 2:
                return f"₹ {dec_value:,.2f}"
            elif decimals == 3:
                return f"{dec_value:.3f}"
            else:
                return str(dec_value)
        except:
            return str(value)
