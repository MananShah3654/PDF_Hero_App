from PyPDF2 import PdfReader, PdfWriter
from PyQt5.QtWidgets import QFileDialog, QInputDialog

def run():
    file, _ = QFileDialog.getOpenFileName(None, "Select PDF to Annotate", "", "PDF Files (*.pdf)")
    if not file:
        return
    reader = PdfReader(file)
    writer = PdfWriter()
    text, ok = QInputDialog.getText(None, "Annotation Text", "Enter annotation:")
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    out_path, _ = QFileDialog.getSaveFileName(None, "Save Annotated PDF", "annotated.pdf", "PDF Files (*.pdf)")
    if out_path:
        with open(out_path, "wb") as f:
            writer.write(f)
