import fitz
from PyQt5.QtWidgets import QFileDialog

def run():
    file, _ = QFileDialog.getOpenFileName(None, "Select PDF to Convert", "", "PDF Files (*.pdf)")
    if not file:
        return
    doc = fitz.open(file)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        pix.save(f"converted_page_{i+1}.png")
