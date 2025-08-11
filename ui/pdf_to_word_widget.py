import os
import fitz
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pdf2docx import Converter

# Conversion logic in a QThread for UI responsiveness
class PDFToWordWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, pdf_path, word_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.word_path = word_path

    def run(self):
        try:
           
            self.progress.emit(10)
            cv = Converter(self.pdf_path)
            self.progress.emit(30)
            cv.convert(self.word_path, start=0, end=None)
            self.progress.emit(100)
            cv.close()
            self.finished.emit(self.word_path)
        except Exception as e:
            self.error.emit(str(e))

class PDFToWordWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pdf_path = None
        self.word_path = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QLabel#title { font-size: 24px; font-weight: bold; }
            QLabel#subtitle { font-size: 13px; color: #7c7e8b; }
            QLabel#preview { border: 1px solid #e1e2ee; background: #fcfdff; min-height: 180px; }
            QPushButton { padding: 10px 24px; border-radius: 7px; font-size: 15px; }
            QPushButton#select { background: #4e82f1; color: #fff; }
            QPushButton#convert { background: #ffb73e; color: #393633; }
            QPushButton#open { background: #49d991; color: #fff; }
        """)

        layout = QVBoxLayout(self)
        title = QLabel("PDF to Word")
        title.setObjectName("title")
        layout.addWidget(title)
        subtitle = QLabel("Easily convert your PDF to a fully-editable Word document (DOCX).")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)

        # Controls row
        controls = QHBoxLayout()
        self.select_btn = QPushButton("📂 Select PDF")
        self.select_btn.setObjectName("select")
        self.select_btn.clicked.connect(self.select_pdf)
        controls.addWidget(self.select_btn)

        self.convert_btn = QPushButton("➡️ Convert to Word")
        self.convert_btn.setObjectName("convert")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.start_conversion)
        controls.addWidget(self.convert_btn)

        self.open_btn = QPushButton("📄 Open Word")
        self.open_btn.setObjectName("open")
        self.open_btn.setVisible(False)
        self.open_btn.clicked.connect(self.open_word_file)
        controls.addWidget(self.open_btn)

        controls.addStretch()
        layout.addLayout(controls)

        # PDF preview
        self.pdf_preview = QLabel()
        self.pdf_preview.setObjectName("preview")
        self.pdf_preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pdf_preview)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

    def select_pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if not file:
            return
        self.pdf_path = file
        # Preview first page
        try:
            doc = fitz.open(file)
            page = doc.load_page(0)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5))
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            pixmap = QPixmap.fromImage(qimg)
            self.pdf_preview.setPixmap(pixmap)
            doc.close()
        except Exception:
            self.pdf_preview.setText("Cannot preview PDF.")
        self.convert_btn.setEnabled(True)
        self.open_btn.setVisible(False)

    def start_conversion(self):
        if not self.pdf_path:
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "Save as Word Document", os.path.splitext(self.pdf_path)[0] + ".docx", "Word Files (*.docx)")
        if not save_path:
            return
        self.word_path = save_path
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.convert_btn.setEnabled(False)
        self.worker = PDFToWordWorker(self.pdf_path, self.word_path)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.conversion_done)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()

    def conversion_done(self, output_file):
        self.progress.setVisible(False)
        self.open_btn.setVisible(True)
        QMessageBox.information(self, "Success", f"PDF converted to Word successfully!\n\n{output_file}")

    def conversion_error(self, err):
        self.progress.setVisible(False)
        self.convert_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"Conversion failed:\n{err}")

    def open_word_file(self):
        if self.word_path and os.path.exists(self.word_path):
            os.startfile(self.word_path)  # Windows only; use subprocess otherwise

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = PDFToWordWidget()
    w.resize(650, 450)
    w.show()
    sys.exit(app.exec())
