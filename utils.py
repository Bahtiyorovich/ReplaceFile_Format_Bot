from docx import Document
from reportlab.pdfgen import canvas
from PIL import Image
import os

# Word hujjatlarini PDF ga aylantirish
def convert_word_to_pdf(doc_path):
    pdf_path = doc_path.replace(".docx", ".pdf")
    doc = Document(doc_path)
    c = canvas.Canvas(pdf_path)

    for para in doc.paragraphs:
        c.drawString(100, 800, para.text)
    c.save()

    return pdf_path

# Rasmlarni qayta ishlash
def convert_image(image_path):
    formats = ["jpg", "jpeg", "webp", "png", "svg", "gif", "jfif", "hdr", "ico"]
    new_paths = []

    img = Image.open(image_path)
    for fmt in formats:
        new_path = image_path.replace(".jpg", f".{fmt}")
        img.save(new_path, fmt.upper())
        new_paths.append(new_path)

    return new_paths

# Fayl formatini aniqlash
def identify_format(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return ext
