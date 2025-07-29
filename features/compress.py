import fitz
from PyQt5.QtWidgets import QFileDialog

def run():
    file, _ = QFileDialog.getOpenFileName(None, "Select PDF to Compress", "", "PDF Files (*.pdf)")
    if not file:
        return
    doc = fitz.open(file)
    for page in doc:
        page.clean_contents()
    out_path, _ = QFileDialog.getSaveFileName(None, "Save Compressed PDF", "compressed.pdf", "PDF Files (*.pdf)")
    if out_path:
        doc.save(out_path, deflate=True)
