from PyPDF2 import PdfReader, PdfWriter
from PyQt5.QtWidgets import QFileDialog, QInputDialog

def run():
    file, _ = QFileDialog.getOpenFileName(None, "Select PDF to Split", "", "PDF Files (*.pdf)")
    if not file:
        return
    start, ok1 = QInputDialog.getInt(None, "Start Page", "Start Page (1-based):")
    end, ok2 = QInputDialog.getInt(None, "End Page", "End Page (1-based):")
    if ok1 and ok2:
        reader = PdfReader(file)
        writer = PdfWriter()
        for i in range(start - 1, end):
            writer.add_page(reader.pages[i])
        out_path, _ = QFileDialog.getSaveFileName(None, "Save Split PDF", "split.pdf", "PDF Files (*.pdf)")
        if out_path:
            with open(out_path, "wb") as f:
                writer.write(f)
