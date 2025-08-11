import fitz
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider,
    QScrollArea, QApplication, QFileDialog
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer

class VirtualizedPDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adobe-Like PDF Viewer")
        self.setMinimumSize(1100, 800)
        self.doc = None
        self.zoom = 1.0
        self.visible_window = 2

        # Layout
        main_layout = QVBoxLayout(self)

        # Controls
        ctrl = QHBoxLayout()
        self.open_btn = QPushButton("Open PDF")
        self.open_btn.clicked.connect(self.open_pdf)
        ctrl.addWidget(self.open_btn)
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(5, 30)
        self.zoom_slider.setValue(10)
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        ctrl.addWidget(QLabel("Zoom:"))
        ctrl.addWidget(self.zoom_slider)
        self.zoom_label = QLabel("100%")
        ctrl.addWidget(self.zoom_label)
        ctrl.addStretch()
        main_layout.addLayout(ctrl)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.page_layout = QVBoxLayout(self.container)
        self.scroll_area.setWidget(self.container)

        self.page_widgets = []
        self.current_page = 0
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return
        self.doc = fitz.open(file_path)
        self.zoom_slider.setValue(10)
        self.zoom = 1.0
        self.goto_page(0)

    def change_zoom(self, value):
        self.zoom = value / 10.0
        self.zoom_label.setText(f"{int(self.zoom*100)}%")
        self.goto_page(self.current_page)

    def goto_page(self, page_num):
        if not self.doc:
            return
        total_pages = len(self.doc)
        page_num = max(0, min(page_num, total_pages - 1))
        self.render_page_window(page_num)
        # QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(page_num * 1200 * self.zoom))
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(int(page_num * 1200 * self.zoom)))

        self.current_page = page_num

    def on_scroll(self):
        # Simple: get the closest visible page, trigger re-render if needed
        if not self.doc:
            return
        scrollbar = self.scroll_area.verticalScrollBar()
        value = scrollbar.value()
        # Assume page height ~1200px for scroll calculation
        page = int(round(value / (1200 * self.zoom)))
        page = max(0, min(page, len(self.doc)-1))
        if page != self.current_page:
            self.goto_page(page)

    def render_page_window(self, center_page):
        # Remove all widgets
        while self.page_layout.count():
            item = self.page_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                del item

        self.page_widgets = []
        if not self.doc:
            return

        total_pages = len(self.doc)
        window = self.visible_window
        start = max(0, center_page - window)
        end = min(total_pages, center_page + window + 1)
        scroll_area_width = self.scroll_area.viewport().width() - 48

        bg_color = QColor("#f7f7fa")
        paper_color = QColor("#fff")
        shadow_color = QColor(0, 0, 0, 40)

        for i in range(start, end):
            page = self.doc.load_page(i)
            page_width = page.rect.width
            fit_width_scale = scroll_area_width / page_width
            scale = fit_width_scale * self.zoom

            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            pixmap = QPixmap.fromImage(qimg)

            # -- Canvas with border, shadow, and background
            margin = 24
            shadow_offset = 10
            canvas_width = pixmap.width() + margin * 2 + shadow_offset
            canvas_height = pixmap.height() + margin * 2 + shadow_offset
            canvas = QPixmap(canvas_width, canvas_height)
            canvas.fill(bg_color)

            painter = QPainter(canvas)
            painter.setRenderHint(QPainter.Antialiasing)
            # Shadow
            painter.setBrush(QBrush(shadow_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(
                margin + shadow_offset, margin + shadow_offset,
                pixmap.width(), pixmap.height(), 12, 12)
            # White "paper"
            painter.setBrush(QBrush(paper_color))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(margin, margin, pixmap.width(), pixmap.height(), 8, 8)
            # PDF Page
            painter.drawPixmap(margin, margin, pixmap)
            painter.end()

            label = QLabel()
            label.setPixmap(canvas)
            label.setFixedSize(canvas.size())
            label.setAlignment(Qt.AlignCenter)
            self.page_layout.addWidget(label)
            self.page_widgets.append(label)

        self.page_layout.addStretch()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    viewer = VirtualizedPDFViewer()
    app.setStyleSheet("""
        QWidget { background: #f7f8fa; color: #2b2b2b; font-family: 'Segoe UI', sans-serif; }
        QLabel, QPushButton { color: #222; font-size: 16px; }
        QScrollArea { background: #f7f8fa; }
    """)
    viewer.showMaximized()
    sys.exit(app.exec())
