import fitz
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QListWidget, QListWidgetItem, QApplication, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QSize

class PDFPageWidget(QWidget):
    def __init__(self, pdf_path, page_num, scale=1.0):
        super().__init__()
        self.pdf_path = pdf_path
        self.page_num = page_num
        self.scale = scale
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        self.render_page()

    def render_page(self):
        doc = fitz.open(self.pdf_path)
        page = doc.load_page(self.page_num)
        mat = fitz.Matrix(self.scale, self.scale)
        pix = page.get_pixmap(matrix=mat)
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        pixmap = QPixmap.fromImage(qimg)
        pixmap = pixmap.scaledToHeight(800, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        doc.close()

class PDFViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Hero - Fast Viewer")
        self.setMinimumSize(1000, 700)
        self.pdf_path = None
        self.doc = None
        self.scale = 1.0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        open_btn = QPushButton("📂 Open PDF")
        open_btn.clicked.connect(self.open_pdf)
        btn_layout.addWidget(open_btn)

        layout.addLayout(btn_layout)

        self.list_widget = QListWidget()
        self.list_widget.setSpacing(18)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return
        self.open_pdf_from_path(file_path)

    def open_pdf_from_path(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = fitz.open(self.pdf_path)
        self.populate_pages()

    def populate_pages(self):
        self.list_widget.clear()
        for page_num in range(len(self.doc)):
            item = QListWidgetItem()
            item.setSizeHint(QSize(800, 900))
            widget = PDFPageWidget(self.pdf_path, page_num, scale=1.0)
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PDFViewerWidget()
    window.showMaximized()
    sys.exit(app.exec())
