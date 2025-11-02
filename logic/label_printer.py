"""
Label Printer for Jewelry Inventory Items
Generates small printable labels with SR.NO, Net Weight, and Supplier Code
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from datetime import datetime
from typing import List, Dict, Optional
import os


class LabelPrinter:
    """Generate small printable labels for inventory items."""

    # Label dimensions (in mm) - Tag/Tie label size for jewelry
    LABEL_WIDTH = 55 * mm  # 55mm width (includes tie hole area)
    LABEL_HEIGHT = 30 * mm  # 30mm height

    # Tag design elements
    TIE_HOLE_AREA_WIDTH = 8 * mm  # Small area for hole punch/tie
    TIE_HOLE_RADIUS = 2 * mm  # Radius of the hole for string/tie

    # Margins and spacing
    LABEL_MARGIN = 2 * mm
    LABELS_PER_ROW = 3  # 3 labels per row on A4 (wider tags)
    LABELS_PER_COL = 9  # 9 rows on A4
    HORIZONTAL_GAP = 4 * mm
    VERTICAL_GAP = 3 * mm

    # Page margins
    PAGE_MARGIN_LEFT = 5 * mm
    PAGE_MARGIN_TOP = 5 * mm

    def __init__(self, output_folder: str = "labels"):
        """Initialize label printer."""
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def generate_label_sheet(
        self, items: List[Dict], filename: Optional[str] = None, page_size=A4
    ) -> str:
        """
        Generate a sheet of labels for multiple items.

        Args:
            items: List of dictionaries with keys: sr_no, net_weight, supplier_code, category_name
            filename: Optional output filename
            page_size: Page size (default A4)

        Returns:
            Path to generated PDF file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"labels_{timestamp}.pdf"

        filepath = os.path.join(self.output_folder, filename)

        # Create PDF
        c = canvas.Canvas(filepath, pagesize=page_size)
        page_width, page_height = page_size

        # Calculate positions for labels
        current_item = 0
        total_items = len(items)

        while current_item < total_items:
            # Draw labels on current page
            labels_on_page = 0

            for row in range(self.LABELS_PER_COL):
                for col in range(self.LABELS_PER_ROW):
                    if current_item >= total_items:
                        break

                    # Calculate label position
                    x = self.PAGE_MARGIN_LEFT + col * (
                        self.LABEL_WIDTH + self.HORIZONTAL_GAP
                    )
                    y = (
                        page_height
                        - self.PAGE_MARGIN_TOP
                        - (row + 1) * (self.LABEL_HEIGHT + self.VERTICAL_GAP)
                    )

                    # Draw label
                    self._draw_label(c, items[current_item], x, y)

                    current_item += 1
                    labels_on_page += 1

                if current_item >= total_items:
                    break

            # Create new page if more items remain
            if current_item < total_items:
                c.showPage()

        c.save()
        return filepath

    def _draw_label(self, canvas_obj: canvas.Canvas, item: Dict, x: float, y: float):
        """
        Draw a single tag-style label with tie hole at specified position.

        Args:
            canvas_obj: ReportLab canvas object
            item: Item dictionary with sr_no, net_weight, supplier_code, category_name
            x: X position (bottom-left corner)
            y: Y position (bottom-left corner)
        """
        # Draw main label border (excluding tie hole area)
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.rect(
            x + self.TIE_HOLE_AREA_WIDTH,
            y,
            self.LABEL_WIDTH - self.TIE_HOLE_AREA_WIDTH,
            self.LABEL_HEIGHT,
        )

        # Draw tie hole area (small tab on the left)
        canvas_obj.setFillColorRGB(0.95, 0.95, 0.95)  # Light gray background
        canvas_obj.rect(
            x, y, self.TIE_HOLE_AREA_WIDTH, self.LABEL_HEIGHT, stroke=1, fill=1
        )

        # Draw tie hole (circle for punching)
        hole_center_x = x + self.TIE_HOLE_AREA_WIDTH / 2
        hole_center_y = y + self.LABEL_HEIGHT / 2
        canvas_obj.setFillColorRGB(1, 1, 1)  # White for hole
        canvas_obj.circle(
            hole_center_x, hole_center_y, self.TIE_HOLE_RADIUS, stroke=1, fill=1
        )

        # Draw decorative corner cuts (optional - makes it look like a tag)
        canvas_obj.setStrokeColor(colors.grey)
        canvas_obj.setLineWidth(0.3)
        corner_size = 2 * mm
        # Top right corner cut
        canvas_obj.line(
            x + self.LABEL_WIDTH - corner_size,
            y + self.LABEL_HEIGHT,
            x + self.LABEL_WIDTH,
            y + self.LABEL_HEIGHT - corner_size,
        )
        # Bottom right corner cut
        canvas_obj.line(
            x + self.LABEL_WIDTH - corner_size, y, x + self.LABEL_WIDTH, y + corner_size
        )

        # Reset colors for text
        canvas_obj.setFillColorRGB(0, 0, 0)  # Black text
        canvas_obj.setStrokeColor(colors.black)

        # Text starting position (after tie hole area)
        text_x = x + self.TIE_HOLE_AREA_WIDTH + self.LABEL_MARGIN + 1 * mm
        text_y = y + self.LABEL_HEIGHT - self.LABEL_MARGIN - 9

        # Draw category name (top, bold)
        canvas_obj.setFont("Helvetica-Bold", 8)
        category = item.get("category_name", "")[:18]  # Truncate if too long
        canvas_obj.drawString(text_x, text_y, category.upper())
        text_y -= 11

        # Draw decorative line under category
        canvas_obj.setLineWidth(0.3)
        canvas_obj.setStrokeColorRGB(0.7, 0.7, 0.7)
        canvas_obj.line(
            text_x,
            text_y + 2,
            x + self.LABEL_WIDTH - self.LABEL_MARGIN - 2 * mm,
            text_y + 2,
        )
        text_y -= 2

        # Draw SR.NO (larger, prominent)
        canvas_obj.setStrokeColor(colors.black)
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(text_x, text_y, f"#{item.get('sr_no', 'N/A')}")
        text_y -= 12

        # Draw Net Weight with icon
        canvas_obj.setFont("Helvetica-Bold", 9)
        canvas_obj.drawString(text_x, text_y, "⚖")
        canvas_obj.setFont("Helvetica", 9)
        net_weight = item.get("net_weight", 0)
        canvas_obj.drawString(text_x + 4 * mm, text_y, f"{net_weight:.3f}g")
        text_y -= 10

        # Draw Supplier Code
        canvas_obj.setFont("Helvetica", 7)
        supplier_code = item.get("supplier_code", "N/A")
        if supplier_code:
            canvas_obj.setFillColorRGB(0.4, 0.4, 0.4)  # Gray text for supplier
            canvas_obj.drawString(text_x, text_y, f"Supplier: {supplier_code}")
            canvas_obj.setFillColorRGB(0, 0, 0)  # Reset to black

    def generate_single_label(
        self,
        sr_no: str,
        net_weight: float,
        supplier_code: str,
        category_name: str = "",
        filename: Optional[str] = None,
    ) -> str:
        """
        Generate a single label.

        Args:
            sr_no: Serial number (e.g., "Ring #5")
            net_weight: Net weight in grams
            supplier_code: Supplier code
            category_name: Category name
            filename: Optional output filename

        Returns:
            Path to generated PDF file
        """
        item = {
            "sr_no": sr_no,
            "net_weight": net_weight,
            "supplier_code": supplier_code,
            "category_name": category_name,
        }
        return self.generate_label_sheet([item], filename)

    def generate_labels_for_category(
        self, db_manager, category_id: str, filename: Optional[str] = None
    ) -> str:
        """
        Generate labels for all items in a category.

        Args:
            db_manager: Database manager instance
            category_id: Category ID
            filename: Optional output filename

        Returns:
            Path to generated PDF file
        """
        import sqlite3

        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            """
            SELECT 
                c.name as category_name,
                i.category_item_no,
                i.net_weight,
                s.code as supplier_code,
                i.status
            FROM inventory i
            JOIN categories c ON i.category_id = c.id
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.category_id = ? AND i.status = 'AVAILABLE'
            ORDER BY i.category_item_no
            """,
            (category_id,),
        )

        items = []
        for row in cursor.fetchall():
            items.append(
                {
                    "sr_no": f"{row['category_name']} #{row['category_item_no']}",
                    "net_weight": float(row["net_weight"]),
                    "supplier_code": row["supplier_code"] or "N/A",
                    "category_name": row["category_name"],
                }
            )

        conn.close()

        if not items:
            raise ValueError("No items found in this category")

        return self.generate_label_sheet(items, filename)

    def generate_labels_for_all_inventory(
        self, db_manager, filename: Optional[str] = None
    ) -> str:
        """
        Generate labels for all available inventory items.

        Args:
            db_manager: Database manager instance
            filename: Optional output filename

        Returns:
            Path to generated PDF file
        """
        import sqlite3

        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            """
            SELECT 
                c.name as category_name,
                i.category_item_no,
                i.net_weight,
                s.code as supplier_code,
                i.status
            FROM inventory i
            JOIN categories c ON i.category_id = c.id
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.status = 'AVAILABLE'
            ORDER BY c.name, i.category_item_no
            """
        )

        items = []
        for row in cursor.fetchall():
            items.append(
                {
                    "sr_no": f"{row['category_name']} #{row['category_item_no']}",
                    "net_weight": float(row["net_weight"]),
                    "supplier_code": row["supplier_code"] or "N/A",
                    "category_name": row["category_name"],
                }
            )

        conn.close()

        if not items:
            raise ValueError("No items found in inventory")

        return self.generate_label_sheet(items, filename)

    def generate_label_for_item(
        self, db_manager, item_id: str, filename: Optional[str] = None
    ) -> str:
        """
        Generate a label for a specific inventory item.

        Args:
            db_manager: Database manager instance
            item_id: Inventory item ID
            filename: Optional output filename

        Returns:
            Path to generated PDF file
        """
        import sqlite3

        conn = sqlite3.connect(db_manager.db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            """
            SELECT 
                c.name as category_name,
                i.category_item_no,
                i.net_weight,
                s.code as supplier_code,
                i.status,
                i.id
            FROM inventory i
            JOIN categories c ON i.category_id = c.id
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.id = ?
            """,
            (item_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Item with ID '{item_id}' not found")

        item = {
            "sr_no": f"{row['category_name']} #{row['category_item_no']}",
            "net_weight": float(row["net_weight"]),
            "supplier_code": row["supplier_code"] or "N/A",
            "category_name": row["category_name"],
        }

        return self.generate_label_sheet([item], filename)


# Example usage
if __name__ == "__main__":
    # Test label generation
    printer = LabelPrinter()

    # Test with sample data
    test_items = [
        {
            "sr_no": "Ring #1",
            "net_weight": 5.250,
            "supplier_code": "GCL001",
            "category_name": "Gold Ring",
        },
        {
            "sr_no": "Ring #2",
            "net_weight": 7.100,
            "supplier_code": "GCL001",
            "category_name": "Gold Ring",
        },
        {
            "sr_no": "Chain #1",
            "net_weight": 12.500,
            "supplier_code": "SP002",
            "category_name": "Gold Chain",
        },
    ]

    output_file = printer.generate_label_sheet(test_items, "test_labels.pdf")
    print(f"Labels generated: {output_file}")
