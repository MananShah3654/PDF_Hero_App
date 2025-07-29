from PyPDF2 import PdfMerger
from PyQt5.QtWidgets import QFileDialog

def run():
    files, _ = QFileDialog.getOpenFileNames(None, "Select PDFs to Merge", "", "PDF Files (*.pdf)")
    if not files:
        return
    merger = PdfMerger()
    for f in files:
        merger.append(f)
    out_path, _ = QFileDialog.getSaveFileName(None, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)")
    if out_path:
        merger.write(out_path)
        merger.close()
