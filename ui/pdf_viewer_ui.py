from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QScrollArea, QMessageBox, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from pdf2image import convert_from_path
from PIL import Image
from PyQt5.QtWidgets import QScrollArea

class PDFViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.pdf_path = None
        self.images = []
        self.zoom_factor = 1.0
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Button Panel
        btn_layout = QHBoxLayout()

        open_btn = QPushButton("📂 Open PDF")
        open_btn.clicked.connect(self.open_pdf)
        btn_layout.addWidget(open_btn)

        zoom_in_btn = QPushButton("➕ Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        btn_layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("➖ Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        btn_layout.addWidget(zoom_out_btn)

        layout.addLayout(btn_layout)

        # Scrollable PDF display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)

        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return

        try:
            self.pdf_path = file_path
            self.images = convert_from_path(file_path, dpi=150)
            self.zoom_factor = 1.0
            self.render_all_pages()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load PDF:\n{str(e)}")
            self.images = []

    def render_all_pages(self):
        # Clear previous content
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for image in self.images:
            zoomed = image.resize((
                int(image.width * self.zoom_factor),
                int(image.height * self.zoom_factor)
            )).convert("RGBA")

            qimage = QImage(zoomed.tobytes("raw", "RGBA"), zoomed.width, zoomed.height, QImage.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)

            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            self.content_layout.addWidget(label)

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.render_all_pages()

    def zoom_out(self):
        if self.zoom_factor > 0.2:
            self.zoom_factor -= 0.1
            self.render_all_pages()
            
def eventFilter(self, obj, event):
    from PyQt5.QtCore import QEvent

    if obj == self.scroll_area and event.type() == QEvent.Wheel:
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            return True  # Event handled
    return super().eventFilter(obj, event)
