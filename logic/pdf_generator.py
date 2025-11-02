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

        # Optimized margins for better layout
        margin_left = 12 * mm
        margin_right = 12 * mm
        margin_top = 12 * mm
        margin_bottom = 12 * mm

        # Draw decorative double border and compute inner content area
        inner = self._draw_double_border(
            c, margin_left, margin_bottom, width - margin_right, height - margin_top
        )

        # Main content area strictly inside the inner border
        content_padding = 6 * mm
        content_left = inner[0] + content_padding
        content_right = inner[2] - content_padding
        content_top = inner[3] - content_padding
        content_bottom = inner[1] + content_padding

        # Company header at top with name, address, GSTIN
        y_pos = content_top
        y_pos = self._draw_company_header(c, content_left, content_right, y_pos)

        # Tax Invoice title (centered with enhanced styling)
        y_pos -= 20 * mm

        # Draw enhanced background box for TAX INVOICE (clamped to inner width)
        title_text = "TAX INVOICE"
        c.setFont("Helvetica-Bold", 20)  # Larger font
        text_width = c.stringWidth(title_text, "Helvetica-Bold", 20)
        max_title_width = (content_right - content_left) * 0.9
        box_width = min(text_width + 30 * mm, max_title_width)
        box_height = 12 * mm  # Taller box
        box_x = ((content_left + content_right) / 2) - (box_width / 2)
        box_y = y_pos - 3 * mm

        # Shadow effect for depth
        shadow_offset = 1 * mm
        c.setFillColor(colors.HexColor("#660000"))  # Darker shadow
        c.rect(
            box_x + shadow_offset,
            box_y - shadow_offset,
            box_width,
            box_height,
            fill=1,
            stroke=0,
        )

        # Main gradient background for title
        c.setFillColor(colors.HexColor("#8B0000"))
        c.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)

        # Enhanced gold border with double effect
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(2.0)
        c.rect(box_x, box_y, box_width, box_height, fill=0, stroke=1)

        # Inner border for luxury effect
        c.setLineWidth(0.8)
        c.rect(
            box_x + 1 * mm,
            box_y + 1 * mm,
            box_width - 2 * mm,
            box_height - 2 * mm,
            fill=0,
            stroke=1,
        )

        # Draw text in white with enhanced positioning
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(
            (content_left + content_right) / 2, y_pos + 1.5 * mm, title_text
        )

        # Reset color to black for rest of content
        c.setFillColor(colors.black)

        # Invoice details box
        y_pos -= 10 * mm
        y_pos = self._draw_invoice_details_box(
            c, content_left, content_right, y_pos, invoice_data
        )

        # Items table - keep it within inner content and above footer area
        y_pos -= 5 * mm
        footer_reserved_h = 35 * mm  # reserved space for footer/signature
        bottom_limit = max(content_bottom, margin_bottom + 8 * mm) + footer_reserved_h
        y_pos = self._draw_items_table(
            c,
            content_left,
            content_right,
            y_pos,
            line_items,
            invoice_data,
            bottom_limit,
        )

        # Footer/signature anchored inside inner border
        footer_y = content_bottom + 6 * mm
        self._draw_footer(c, content_left, content_right, footer_y, invoice_data)

        # Save PDF
        c.save()

    def _draw_double_border(self, c, x1, y1, x2, y2):
        """Draw enhanced decorative triple-line border with elegant colors.

        Returns a tuple (inner_left, inner_bottom, inner_right, inner_top)
        representing the coordinates of the innermost border so callers can
        keep all content within it.
        """
        # Outer border (dark red/maroon) - thicker and more prominent
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(2.5)
        c.rect(x1, y1, x2 - x1, y2 - y1, fill=0, stroke=1)

        # Middle decorative line (gold) - enhanced thickness
        offset1 = 2 * mm
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(1.2)
        c.rect(
            x1 + offset1,
            y1 + offset1,
            (x2 - x1) - 2 * offset1,
            (y2 - y1) - 2 * offset1,
            fill=0,
            stroke=1,
        )

        # Inner border (dark red/maroon) - refined
        offset2 = 4 * mm
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(0.8)
        c.rect(
            x1 + offset2,
            y1 + offset2,
            (x2 - x1) - 2 * offset2,
            (y2 - y1) - 2 * offset2,
            fill=0,
            stroke=1,
        )

        # Add corner decorations for luxury feel
        corner_size = 3 * mm
        # Top-left corner
        c.setFillColor(colors.HexColor("#FFD700"))
        c.circle(x1 + offset1, y2 - offset1, corner_size / 2, fill=1, stroke=0)
        # Top-right corner
        c.circle(x2 - offset1, y2 - offset1, corner_size / 2, fill=1, stroke=0)
        # Bottom-left corner
        c.circle(x1 + offset1, y1 + offset1, corner_size / 2, fill=1, stroke=0)
        # Bottom-right corner
        c.circle(x2 - offset1, y1 + offset1, corner_size / 2, fill=1, stroke=0)

        # Return inner border rectangle
        return (x1 + offset2, y1 + offset2, x2 - offset2, y2 - offset2)

    def _draw_company_header(self, c, x1, x2, y_start):
        """Draw company header details with styling - now horizontal at top."""
        y = y_start

        # Company name in dark red - centered and MUCH larger
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor("#8B0000"))
        company_name = self.company["name"]
        c.drawCentredString((x1 + x2) / 2, y, company_name)

        # Decorative line under company name - longer and more prominent
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(2.0)
        line_center = (x1 + x2) / 2
        line_width = 120 * mm
        c.line(
            line_center - line_width / 2,
            y - 3 * mm,
            line_center + line_width / 2,
            y - 3 * mm,
        )

        y -= 10 * mm
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        # Use 'address' field from settings
        address_text = self.company.get("address", "")
        if address_text:
            c.drawCentredString((x1 + x2) / 2, y, address_text)

        y -= 5 * mm
        contact_text = (
            f"Phone: {self.company['phone']} | Email: {self.company['email']}"
        )
        c.drawCentredString((x1 + x2) / 2, y, contact_text)

        # GSTIN below contact info
        y -= 5 * mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#8B0000"))
        gstin_text = f"GSTIN: {self.company['gstin']}"
        c.drawCentredString((x1 + x2) / 2, y, gstin_text)

        return y - 8 * mm

    def _draw_invoice_details_box(self, c, x1, x2, y_start, invoice_data):
        """Draw invoice number, date, and customer details box with enhanced styling."""
        box_height = 38 * mm  # Slightly taller
        y_bottom = y_start - box_height

        # Enhanced box with shadow effect
        shadow_offset = 0.5 * mm
        c.setFillColor(colors.HexColor("#E0E0E0"))  # Light gray shadow
        c.rect(
            x1 + shadow_offset,
            y_bottom - shadow_offset,
            x2 - x1,
            box_height,
            fill=1,
            stroke=0,
        )

        # Draw main box with colored border
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(1.5)
        c.rect(x1, y_bottom, x2 - x1, box_height, fill=0, stroke=1)

        # Vertical divider (between invoice details and customer details)
        mid_x = x1 + (x2 - x1) * 0.35
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.setLineWidth(1.5)
        c.line(mid_x, y_bottom, mid_x, y_start)

        # Left side: Invoice details with enhanced background
        c.setFillColor(colors.HexColor("#FFF8DC"))  # Cornsilk
        c.rect(x1, y_bottom, mid_x - x1, box_height, fill=1, stroke=0)

        # Right side: Customer details with white background
        c.setFillColor(colors.white)
        c.rect(mid_x, y_bottom, x2 - mid_x, box_height, fill=1, stroke=0)

        # Redraw enhanced borders
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(1.5)
        c.rect(x1, y_bottom, x2 - x1, box_height, fill=0, stroke=1)
        c.setStrokeColor(colors.HexColor("#FFD700"))
        c.line(mid_x, y_bottom, mid_x, y_start)

        # Left side: Invoice details with better spacing
        y = y_start - 6 * mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(x1 + 4 * mm, y, "No.:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(x1 + 18 * mm, y, invoice_data.get("invoice_number", ""))

        y -= 6 * mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(x1 + 4 * mm, y, "Date:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(x1 + 18 * mm, y, invoice_data.get("invoice_date", ""))

        # Right side: Customer details with better spacing
        y = y_start - 6 * mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(mid_x + 4 * mm, y, "Name:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(mid_x + 20 * mm, y, invoice_data.get("customer_name", ""))

        y -= 6 * mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(mid_x + 4 * mm, y, "Address:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        # Better address wrapping
        address = invoice_data.get("customer_address", "")
        if len(address) > 35:
            c.drawString(mid_x + 20 * mm, y, address[:35])
            y -= 5 * mm
            c.drawString(mid_x + 20 * mm, y, address[35:])
        else:
            c.drawString(mid_x + 20 * mm, y, address)

        y -= 6 * mm
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(mid_x + 4 * mm, y, "Phone:")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 10)
        c.drawString(mid_x + 20 * mm, y, invoice_data.get("customer_phone", ""))

        return y_bottom - 5 * mm

    def _draw_items_table(
        self, c, x1, x2, y_start, line_items, invoice_data, bottom_limit
    ):
        """Draw items table with totals that ALWAYS fits inside the main border.

        Changes vs previous version:
        - Uses a safe inset on both sides so the table never touches the border
        - Dynamically computes column widths to exactly fit the available space
        - Slightly reduced font sizes and increased cell padding for readability
        """
        # Available width inside the content box
        available_width = x2 - x1
        # Keep a small inset so the table remains comfortably inside the box
        safe_inset = 4 * mm
        inner_width = max(10 * mm, available_width - 2 * safe_inset)

        # Compute how much vertical space we have for the table
        available_height = max(20 * mm, y_start - bottom_limit)
        # Start with a comfortable row height, shrink if needed
        row_height = 6.5 * mm

        # Prepare table data with size awareness
        table_data: List[List[str]] = []

        # Header row with better formatting
        headers = [
            "S.No.",
            "Description",
            "HSN Code",
            "Weight",
            "Rate\n(with making charges)",
            "Amount",
        ]
        table_data.append(headers)

        # Totals data sourced up-front (so we know totals row count)
        subtotal = invoice_data.get("subtotal", "0")
        cgst = invoice_data.get("cgst_amount", "0")
        sgst = invoice_data.get("sgst_amount", "0")
        final_total = invoice_data.get("total_amount", "0")
        rounded_off = invoice_data.get("rounded_off", "0")
        totals_rows_count = 4 if float(rounded_off) == 0 else 5

        # Determine how many data rows fit
        max_rows_total = max(6, int(available_height // row_height))
        # Keep at least header + totals
        available_for_data = max_rows_total - 1 - totals_rows_count
        if available_for_data < 1:
            # Shrink row height to squeeze minimum content
            for rh in [6.0 * mm, 5.5 * mm]:
                row_height = rh
                max_rows_total = max(6, int(available_height // row_height))
                available_for_data = max_rows_total - 1 - totals_rows_count
                if available_for_data >= 1:
                    break
            if available_for_data < 1:
                available_for_data = 1

        # Build data rows (truncate if necessary)
        items_to_show = line_items[:available_for_data]
        for idx, item in enumerate(items_to_show, start=1):
            description = item.get("description", "")
            if len(description) > 40:
                description = description[:37] + "..."
            row = [
                str(idx),
                description,
                item.get("hsn_code", ""),
                f"{float(item.get('quantity', 0)):.3f}",
                f"₹{float(item.get('rate', 0)):.2f}",
                f"₹{float(item.get('amount', 0)):.2f}",
            ]
            table_data.append(row)

        # If there are more items than can be shown, add a summary row
        remaining = max(0, len(line_items) - len(items_to_show))
        if remaining > 0 and len(table_data) < max_rows_total - totals_rows_count:
            table_data.append(
                [
                    "",
                    f"+{remaining} more item(s)",
                    "",
                    "",
                    "",
                    "",
                ]
            )

        # Fill remaining space with empty rows so totals align at bottom
        while len(table_data) < max_rows_total - totals_rows_count:
            table_data.append(["", "", "", "", "", ""])

        # Append totals rows at the end
        table_data.append(["", "", "", "", "TOTAL", f"₹{float(subtotal):.2f}"])
        table_data.append(
            [
                "",
                "",
                "",
                "",
                f"CGST {self.settings['tax']['cgst_rate']}%",
                f"₹{float(cgst):.2f}",
            ]
        )
        table_data.append(
            [
                "",
                "",
                "",
                "",
                f"SGST {self.settings['tax']['sgst_rate']}%",
                f"₹{float(sgst):.2f}",
            ]
        )
        if float(rounded_off) != 0:
            table_data.append(
                ["", "", "", "", "Rounded Off", f"₹{float(rounded_off):.2f}"]
            )
        table_data.append(["", "", "", "", "G.TOTAL", f"₹{float(final_total):.2f}"])

        # Dynamic column widths to fit inner_width precisely
        # Percentages sum to 1.0
        col_perc = [0.07, 0.37, 0.12, 0.12, 0.16, 0.16]
        col_widths = [inner_width * p for p in col_perc]

        # Create and style table
        table = Table(table_data, colWidths=col_widths)

        # Calculate totals row position
        num_totals_rows = totals_rows_count
        totals_start = len(table_data) - num_totals_rows

        # Enhanced table styling (reduced font sizes as requested)
        style = TableStyle(
            [
                # Header row with enhanced styling
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8B0000")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                # Data rows with better spacing
                ("FONTNAME", (0, 1), (-1, totals_start - 1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, totals_start - 1), 8),
                ("ALIGN", (0, 1), (0, totals_start - 1), "CENTER"),  # S.No. column
                ("ALIGN", (1, 1), (1, totals_start - 1), "LEFT"),  # Description column
                ("ALIGN", (2, 1), (2, totals_start - 1), "CENTER"),  # HSN
                ("ALIGN", (3, 1), (3, totals_start - 1), "CENTER"),  # Weight
                ("ALIGN", (4, 1), (4, totals_start - 1), "RIGHT"),  # Rate
                ("ALIGN", (5, 1), (5, totals_start - 1), "RIGHT"),  # Amount
                # Alternating row colors for better readability
                ("BACKGROUND", (0, 1), (-1, totals_start - 1), colors.white),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#F8F8F8")),
                ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#F8F8F8")),
                ("BACKGROUND", (0, 6), (-1, 6), colors.HexColor("#F8F8F8")),
                ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#F8F8F8")),
                # Totals rows with enhanced styling
                (
                    "BACKGROUND",
                    (0, totals_start),
                    (-1, -2),
                    colors.HexColor("#FFF8DC"),
                ),  # Light cream
                (
                    "BACKGROUND",
                    (0, -1),
                    (-1, -1),
                    colors.HexColor("#FFD700"),
                ),  # Gold for G.TOTAL
                ("FONTNAME", (0, totals_start), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, totals_start), (-1, -1), 9),
                ("ALIGN", (4, totals_start), (4, -1), "RIGHT"),
                ("ALIGN", (5, totals_start), (5, -1), "RIGHT"),
                # Grid and borders
                ("GRID", (0, 0), (-1, -1), 1.0, colors.HexColor("#8B0000")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                # Emphasized borders
                (
                    "LINEABOVE",
                    (0, totals_start),
                    (-1, totals_start),
                    2,
                    colors.HexColor("#8B0000"),
                ),
                ("LINEABOVE", (0, -1), (-1, -1), 3, colors.HexColor("#8B0000")),
                ("LINEBELOW", (0, -1), (-1, -1), 3, colors.HexColor("#8B0000")),
            ]
        )

        table.setStyle(style)

        # Calculate table dimensions
        table_width = sum(col_widths)
        table_height = len(table_data) * row_height

        # Position table - always draw with the inset so it stays inside the box
        table_x = x1 + safe_inset
        table_y = y_start - table_height

        # Wrap and draw table
        table.wrapOn(c, table_width, table_height)
        table.drawOn(c, table_x, table_y)

        return table_y - 8 * mm

    def _draw_footer(self, c, x1, x2, y, invoice_data):
        """Draw enhanced footer with professional signature area."""
        # Thank you message on the left
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(x1, y + 20 * mm, "Thank you for your business!")

        # Terms note
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.black)
        c.drawString(
            x1,
            y + 15 * mm,
            "• All items sold are subject to company terms and conditions",
        )
        c.drawString(
            x1, y + 12 * mm, "• Goods once sold will not be taken back or exchanged"
        )

        # Enhanced signature section on the right
        signature_x = x2 - 60 * mm

        # "For Roopkala Jewellers" text with styling
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.HexColor("#8B0000"))
        c.drawString(signature_x, y + 20 * mm, "For Roopkala Jewellers")

        # Signature box
        box_width = 50 * mm
        box_height = 15 * mm
        c.setStrokeColor(colors.HexColor("#8B0000"))
        c.setLineWidth(1.0)
        c.rect(signature_x, y + 5 * mm, box_width, box_height, fill=0, stroke=1)

        # Signature line inside box
        c.setLineWidth(0.5)
        c.line(
            signature_x + 5 * mm,
            y + 8 * mm,
            signature_x + box_width - 5 * mm,
            y + 8 * mm,
        )

        # Label
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.black)
        c.drawCentredString(
            signature_x + box_width / 2, y + 2 * mm, "Authorized Signatory"
        )

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
