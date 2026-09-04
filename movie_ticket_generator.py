"""
movie_ticket_generator.py

A terminal visitors' book. Each function below does exactly one job:

  get_visitor_details()  -> collects visitor info from the terminal
  generate_qr_code()     -> turns that info into a QR code image
  create_visitor_badge() -> draws a badge combining text + QR code
  save_badge_as_pdf()    -> exports the badge image as a PDF file

Notice the shape: each function's OUTPUT becomes the next function's
INPUT. That chain is the main reason to use functions here — main()
below reads almost like a sentence describing the whole program.
"""

from datetime import datetime
import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def get_visitor_details():
    """
    Ask the terminal user for visitor details and return them as a
    dictionary. Nothing is drawn or saved here — this function's only
    job is collecting data.
    """
    name = input("Visitor's full name: ")
    id_number = input("ID number: ")
    host = input("Who are they here to see: ")
    purpose = input("Purpose of visit: ")

    return {
        "name": name,
        "id_number": id_number,
        "host": host,
        "purpose": purpose,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

def generate_qr_code(visitor):
    """
    Take a visitor dictionary and return a QR code image encoding
    their details. This function doesn't know or care how the QR
    code will be displayed later — it just builds the image.
    """
    qr_text = (
        f"Name: {visitor['name']}\n"
        f"ID: {visitor['id_number']}\n"
        f"Host: {visitor['host']}\n"
        f"Purpose: {visitor['purpose']}\n"
        f"Time: {visitor['timestamp']}"
    )

    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(qr_text)
    qr.make(fit=True)

    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def load_font(size, bold=False):
    """
    Load a modern system font. Tries SF Pro (macOS), Helvetica Neue,
    then falls back to system defaults.
    """
    font_candidates = [
        "/System/Library/Fonts/SFNS.ttf" if not bold else "/System/Library/Fonts/SFNSBold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in font_candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_visitor_badge(visitor, qr_image):
    """
    Combine the visitor's details and their QR code into a modern,
    clean badge with improved typography and spacing.
    """
    width, height = 640, 380
    badge = Image.new("RGB", (width, height), "#FAFAFA")  # Light gray background
    draw = ImageDraw.Draw(badge)

    # Modern font stack with proper weights
    title_font = load_font(22, bold=True)
    label_font = load_font(11, bold=True)
    value_font = load_font(15)
    small_font = load_font(10)

    # Accent color
    accent = "#2563EB"  # Blue accent
    dark = "#111827"     # Near-black
    muted = "#6B7280"    # Gray-500
    light = "#F3F4F6"    # Gray-100

    # Header with accent bar
    draw.rectangle([(0, 0), (width, 4)], fill=accent)
    draw.rectangle([(0, 4), (width, 64)], fill=dark)
    draw.text((28, 20), "VISITOR PASS", font=title_font, fill="white")

    # Timestamp in header
    draw.text((width - 150, 24), visitor["timestamp"], font=small_font, fill="#9CA3AF")

    # Visitor details with better spacing
    fields = [
        ("NAME", visitor["name"]),
        ("ID NUMBER", visitor["id_number"]),
        ("HOST", visitor["host"]),
        ("PURPOSE", visitor["purpose"]),
    ]

    y = 88
    for label, value in fields:
        # Label
        draw.text((28, y), label, font=label_font, fill=muted)
        # Value with subtle background
        draw.rectangle([(24, y + 16), (width - 190, y + 42)], fill=light)
        draw.text((32, y + 19), value, font=value_font, fill=dark)
        y += 56

    # QR code with border
    qr_size = 150
    qr_x = width - qr_size - 28
    qr_y = 84
    # Light border around QR
    draw.rectangle([(qr_x - 4, qr_y - 4), (qr_x + qr_size + 4, qr_y + qr_size + 4)], fill="white", outline="#E5E7EB")
    qr_resized = qr_image.resize((qr_size, qr_size))
    badge.paste(qr_resized, (qr_x, qr_y))

    # Footer
    draw.rectangle([(0, height - 32), (width, height)], fill=light)
    draw.text((28, height - 24), "Scan QR code for details", font=small_font, fill=muted)

    return badge

def save_badge_as_pdf(badge_image, filename):
    """
    Export badge as a clean, centered PDF with proper margins.
    """
    temp_png = "temp_badge.png"
    badge_image.save(temp_png, quality=95)

    # A4-ish page with badge centered
    from reportlab.lib.pagesizes import A4
    page_w, page_h = A4
    
    img_w, img_h = badge_image.size
    # Scale badge to fit page width with margins
    margin = 40
    scale = min((page_w - 2 * margin) / img_w, (page_h - 2 * margin) / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    
    # Center on page
    x = (page_w - draw_w) / 2
    y = (page_h - draw_h) / 2

    pdf = canvas.Canvas(filename, pagesize=A4)
    pdf.drawImage(temp_png, x, y, width=draw_w, height=draw_h)
    pdf.save()

    os.remove(temp_png)

def main():
    visitor = get_visitor_details()
    qr_image = generate_qr_code(visitor)
    badge = create_visitor_badge(visitor, qr_image)

    filename = f"badge_{visitor['name'].replace(' ', '_')}.pdf"
    save_badge_as_pdf(badge, filename)

    print(f"\nBadge created: {filename}")


if __name__ == "__main__":
    main()