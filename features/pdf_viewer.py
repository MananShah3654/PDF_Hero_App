import fitz  # PyMuPDF
import os
from PIL import Image

def render_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    image_paths = []
    output_dir = "rendered_pages"
    os.makedirs(output_dir, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        output = os.path.join(output_dir, f"page_{page_num + 1}.png")
        pix.save(output)
        image_paths.append(output)

    return image_paths