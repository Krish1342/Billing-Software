"""
PDF Generator for Roopkala Jewellers Billing System.

Generates professional A4 invoice PDFs using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from decimal import Decimal
from datetime import datetime
from typing import Dict, List
import json


class InvoicePDFGenerator:
    """Generate PDF invoices with professional formatting."""
    
    def __init__(self, settings_path: str = "settings.json"):
        """
        Initialize PDF generator.
        
        Args:
            settings_path: Path to settings JSON file
        """
        with open(settings_path, 'r') as f:
            self.settings = json.load(f)
        
        self.company = self.settings['company']
        self.page_width, self.page_height = A4
    
    def generate_invoice_pdf(
        self,
        output_path: str,
        invoice_data: Dict,
        line_items: List[Dict]
    ):
        """
        Generate a PDF invoice.
        
        Args:
            output_path: Path where PDF will be saved
            invoice_data: Dictionary with invoice header information
            line_items: List of line item dictionaries
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#555555'),
            spaceAfter=1,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        # Company Header
        story.append(Paragraph(self.company['name'], title_style))
        story.append(Paragraph(self.company['address_line1'], subtitle_style))
        story.append(Paragraph(self.company['address_line2'], subtitle_style))
        story.append(Paragraph(
            f"Phone: {self.company['phone']} | Email: {self.company['email']}",
            subtitle_style
        ))
        story.append(Paragraph(f"GSTIN: {self.company['gstin']}", subtitle_style))
        story.append(Spacer(1, 15))
        
        # Invoice Title
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("TAX INVOICE", invoice_title_style))
        story.append(Spacer(1, 10))
        
        # Invoice details and customer info side by side
        invoice_info = [
            ['Invoice No:', invoice_data.get('invoice_number', 'N/A')],
            ['Invoice Date:', invoice_data.get('invoice_date', 'N/A')],
        ]
        
        customer_info = [
            ['Customer Name:', invoice_data.get('customer_name', 'N/A')],
            ['Address:', invoice_data.get('customer_address', 'N/A')],
            ['Phone:', invoice_data.get('customer_phone', 'N/A')],
            ['GSTIN:', invoice_data.get('customer_gstin', 'N/A')],
        ]
        
        # Create two-column layout for invoice and customer info
        info_table_data = []
        max_rows = max(len(invoice_info), len(customer_info))
        
        for i in range(max_rows):
            left_label = invoice_info[i][0] if i < len(invoice_info) else ''
            left_value = invoice_info[i][1] if i < len(invoice_info) else ''
            right_label = customer_info[i][0] if i < len(customer_info) else ''
            right_value = customer_info[i][1] if i < len(customer_info) else ''
            info_table_data.append([left_label, left_value, right_label, right_value])
        
        info_table = Table(info_table_data, colWidths=[80, 120, 80, 120])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a1a')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 15))
        
        # Line items table
        table_data = [['#', 'Description', 'HSN', 'Qty', 'Rate', 'Amount']]
        
        for idx, item in enumerate(line_items, start=1):
            table_data.append([
                str(idx),
                item.get('description', ''),
                item.get('hsn_code', ''),
                self._format_decimal(item.get('quantity', '0'), 3),
                self._format_decimal(item.get('rate', '0'), 2),
                self._format_decimal(item.get('amount', '0'), 2),
            ])
        
        # Create table
        items_table = Table(table_data, colWidths=[25, 200, 50, 50, 60, 65])
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # # column
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # HSN
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Qty
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Rate
            ('ALIGN', (5, 1), (5, -1), 'RIGHT'),   # Amount
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 10))
        
        # Totals section
        totals_data = [
            ['Subtotal:', self._format_decimal(invoice_data.get('subtotal', '0'), 2)],
            [f"CGST @ {self.settings['tax']['cgst_rate']}%:", 
             self._format_decimal(invoice_data.get('cgst', '0'), 2)],
            [f"SGST @ {self.settings['tax']['sgst_rate']}%:", 
             self._format_decimal(invoice_data.get('sgst', '0'), 2)],
        ]
        
        # Add rounded off if not zero
        rounded_off = Decimal(str(invoice_data.get('rounded_off', '0')))
        if rounded_off != Decimal('0'):
            totals_data.append([
                'Rounded Off:',
                self._format_decimal(str(rounded_off), 2)
            ])
        
        totals_data.append([
            'Final Total:',
            self._format_decimal(invoice_data.get('final_total', '0'), 2)
        ])
        
        # Right-align totals
        totals_table = Table(totals_data, colWidths=[100, 80])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Final total bold
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        # Create wrapper table to position totals on right
        wrapper_table = Table([[totals_table]], colWidths=[self.page_width - 40*mm])
        wrapper_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ]))
        
        story.append(wrapper_table)
        story.append(Spacer(1, 20))
        
        # Notes section
        notes = invoice_data.get('notes', '')
        if notes:
            story.append(Paragraph("Notes:", heading_style))
            notes_style = ParagraphStyle(
                'Notes',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#333333')
            )
            story.append(Paragraph(notes, notes_style))
            story.append(Spacer(1, 15))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Paragraph(
            f"This is a computer-generated invoice from {self.company['name']}",
            footer_style
        ))
        
        # Build PDF
        doc.build(story)
    
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
