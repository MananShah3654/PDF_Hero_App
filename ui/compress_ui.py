import fitz  # PyMuPDF
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QScrollArea, QMessageBox, QSizePolicy, QApplication
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import io
from PIL import Image

class PDFCompressorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Compressor Viewer Page")
        self.setMinimumSize(900, 700)

        self.doc = None
        self.file_path = None
        self.page_widgets = []

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top button bar
        top_btn_layout = QHBoxLayout()
        self.open_btn = QPushButton("📂 Select PDF")
        self.open_btn.clicked.connect(self.select_pdf)
        top_btn_layout.addWidget(self.open_btn)

        self.compress_btn = QPushButton("🗜️ Compress & Save")
        self.compress_btn.clicked.connect(self.compress_and_save)
        self.compress_btn.setEnabled(False)
        top_btn_layout.addWidget(self.compress_btn)

        layout.addLayout(top_btn_layout)

        # Status label
        self.status_label = QLabel("No PDF loaded.")
        layout.addWidget(self.status_label)

        # Scroll area to view pages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

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
            self.render_pages()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load PDF:\n{str(e)}")

    def render_pages(self):
        # Clear existing page widgets
        for widget in self.page_widgets:
            widget.setParent(None)
        self.page_widgets.clear()

        # Render each page to image and display
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            pixmap = QPixmap.fromImage(image)

            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            self.content_layout.addWidget(label)
            self.page_widgets.append(label)

    def compress_and_save(self):
        if not self.doc:
            return

        try:
            for page in self.doc:
                page.clean_contents()
                for img in page.get_images(full=True):
                    xref = img[0]
                    try:
                        pix = fitz.Pixmap(self.doc, xref)
                        if pix.n > 4:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        # Convert pixmap to PIL Image for aggressive compression
                        pil_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        # Resize to 70% (you can adjust this)
                        pil_img = pil_img.resize((int(pix.width * 0.7), int(pix.height * 0.7)), Image.LANCZOS)
                        # Save to JPEG buffer with quality 60 (aggressive)
                        img_buffer = io.BytesIO()
                        pil_img.save(img_buffer, format="JPEG", quality=60)
                        img_buffer.seek(0)
                        # Replace image in PDF
                        new_xref = self.doc.insert_image(
                            page.rect, stream=img_buffer.getvalue(), keep_proportion=True
                        )
                        page._wrapContents()  # Needed in some PyMuPDF versions
                        pix = None
                    except Exception as img_error:
                        print(f"Skipping image {xref}: {img_error}")

            out_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", "compressed.pdf", "PDF Files (*.pdf)")
            if out_path:
                self.doc.save(out_path, garbage=4, deflate_images=True, clean=True)
                QMessageBox.information(self, "Success", f"Compressed PDF saved to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Compression failed:\n{str(e)}")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PDFCompressorUI()
    window.show()
    sys.exit(app.exec())
