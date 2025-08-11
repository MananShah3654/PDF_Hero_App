import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QHBoxLayout, QApplication, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class PDFCompressorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Compressor with Preview")
        self.setMinimumSize(800, 600)

        self.doc = None
        self.file_path = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()

        self.open_btn = QPushButton("📂 Select PDF")
        self.open_btn.clicked.connect(self.select_pdf)
        btn_layout.addWidget(self.open_btn)

        self.compress_btn = QPushButton("🗜️ Compress & Save")
        self.compress_btn.clicked.connect(self.compress_and_save)
        self.compress_btn.setEnabled(False)
        btn_layout.addWidget(self.compress_btn)

        layout.addLayout(btn_layout)

        self.status_label = QLabel("No PDF loaded.")
        layout.addWidget(self.status_label)

        self.thumbnail_list = QListWidget()
        layout.addWidget(self.thumbnail_list)

        self.setLayout(layout)

    def select_pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF to Compress", "", "PDF Files (*.pdf)")
        if not file:
            return

        try:
            self.doc = fitz.open(file)
            self.file_path = file
            self.status_label.setText(f"Loaded: {file} ({len(self.doc)} pages)")
            self.compress_btn.setEnabled(True)
            self.load_thumbnails()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF:\n{str(e)}")

    def load_thumbnails(self):
        self.thumbnail_list.clear()
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGBA8888)
            item = QListWidgetItem(f"Page {page_num + 1}")
            item.setIcon(QPixmap.fromImage(image))
            self.thumbnail_list.addItem(item)

    def compress_and_save(self):
        if not self.doc:
            return

        try:
            for page in self.doc:
                page.clean_contents()

            out_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "compressed.pdf", "PDF Files (*.pdf)")
            if out_path:
                self.doc.save(out_path, deflate=True)
                QMessageBox.information(self, "Success", f"Compressed PDF saved to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Compression failed:\n{str(e)}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PDFCompressorUI()
    window.show()
    sys.exit(app.exec())
    
def run():
    import sys
    app = QApplication(sys.argv)
    window = PDFCompressorUI()
    window.show()
    app.exec()