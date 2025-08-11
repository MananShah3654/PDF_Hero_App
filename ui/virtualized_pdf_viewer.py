import fitz
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider,
    QLineEdit, QScrollArea, QSizePolicy, QListWidget, QListWidgetItem, QApplication, QSpacerItem, QFileDialog
)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QTimer, QEvent


class PDFPageWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal, Qt

class PageInputLineEdit(QLineEdit):
    editingFinishedOrTab = pyqtSignal()

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
            self.editingFinishedOrTab.emit()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.editingFinishedOrTab.emit()


# import fitz
# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider,
#     QLineEdit, QScrollArea, QSizePolicy, QSpacerItem,
#     QListWidget, QListWidgetItem, QApplication
# )
# from PyQt5.QtGui import QPixmap, QImage, QIcon
# from PyQt5.QtCore import Qt, QTimer

class PDFPageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

class VirtualizedPDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 800)
        self.doc = None
        self.page_height = 1200
        self.zoom = 1.0
        self.visible_window = 2

        # --- LAYOUT: Thumbnails | Viewer ---
        main_layout = QHBoxLayout(self)

        # ---- Thumbnail sidebar ----
        self.thumb_list = QListWidget()
        self.thumb_list.setFixedWidth(100)
        self.thumb_list.itemClicked.connect(self.goto_page_from_thumb)
        main_layout.addWidget(self.thumb_list)

        # ---- PDF controls + scroll viewer ----
        viewer_panel = QVBoxLayout()

        # Top controls bar
        controls = QHBoxLayout()
        self.open_btn = QPushButton("📂 Open PDF")
        self.open_btn.clicked.connect(self.open_pdf)
        controls.addWidget(self.open_btn)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(5, 30)
        self.zoom_slider.setValue(10)
        self.zoom_slider.valueChanged.connect(self.change_zoom)
        controls.addWidget(QLabel("Zoom:"))
        controls.addWidget(self.zoom_slider)
        self.zoom_label = QLabel("100%")
        controls.addWidget(self.zoom_label)

        self.page_input = PageInputLineEdit("1")
        self.page_input.setFixedWidth(50)
        self.page_input.returnPressed.connect(self.goto_page_input)
        controls.addWidget(QLabel("Go to:"))
        controls.addWidget(self.page_input)

        self.page_count_label = QLabel("/ ?")
        controls.addWidget(self.page_count_label)
        self.current_page_label = QLabel("Page: 1")
        controls.addWidget(self.current_page_label)
        controls.addStretch()
        viewer_panel.addLayout(controls)

        # Scroll area for infinite scroll pages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        viewer_panel.addWidget(self.scroll_area)
        main_layout.addLayout(viewer_panel, 1)

        self.container = QWidget()
        self.page_layout = QVBoxLayout()
        self.page_layout.setSpacing(24)
        self.container.setLayout(self.page_layout)
        self.scroll_area.setWidget(self.container)

        self.page_widgets = []
        self.top_spacer = None
        self.bottom_spacer = None
        self.current_page = 0
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)

    # ----- File open and thumbnail logic -----
    def open_pdf(self):
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if not file_path:
            return
        self.doc = fitz.open(file_path)
        self.page_count_label.setText(f"/ {len(self.doc)}")
        self.zoom_slider.setValue(10)
        self.zoom = 1.0
        self.render_thumbnails()
        self.goto_page(0)
        self.update_current_page()

    def render_thumbnails(self):
        self.thumb_list.clear()
        if not self.doc:
            return
        for i in range(len(self.doc)):
            page = self.doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.10, 0.10))
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            thumb = QPixmap.fromImage(qimg)
            item = QListWidgetItem()
            item.setIcon(QIcon(thumb))
            item.setText(str(i + 1))
            self.thumb_list.addItem(item)

    def goto_page_from_thumb(self, item):
        page_num = int(item.text()) - 1
        self.goto_page(page_num)

    # ----- Controls -----
    def change_zoom(self, value):
        old_page = self.current_page
        self.zoom = value / 10.0
        self.zoom_label.setText(f"{int(self.zoom*100)}%")
        self.goto_page(old_page)

    def goto_page_input(self):
        try:
            page_num = int(self.page_input.text()) - 1
            self.goto_page(page_num)
        except Exception:
            pass

    def goto_page(self, page_num):
        if not self.doc:
            return
        total_pages = len(self.doc)
        page_num = max(0, min(page_num, total_pages - 1))
        scroll_y = int(page_num * self.page_height * self.zoom)
        self.render_page_window(page_num)
        QTimer.singleShot(0, lambda: self.scroll_area.verticalScrollBar().setValue(scroll_y))
        self.current_page = page_num
        self.update_current_page()

    def get_current_page(self):
        if not self.doc:
            return 0
        scroll = self.scroll_area.verticalScrollBar().value()
        page = int(round(scroll / (self.page_height * self.zoom)))
        page = max(0, min(page, len(self.doc) - 1))
        return page

    def on_scroll(self):
        if not self.doc:
            return
        page = self.get_current_page()
        if page != self.current_page:
            self.current_page = page
            self.render_page_window(page)
            self.thumb_list.setCurrentRow(page)
        self.update_current_page()

    def render_page_window(self, center_page):
        while self.page_layout.count():
            item = self.page_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                del item

        self.page_widgets = []
        total_pages = len(self.doc)
        window = self.visible_window
        start = max(0, center_page - window)
        end = min(total_pages, center_page + window + 1)
        pages_above = start
        pages_below = total_pages - end

        if pages_above > 0:
            self.top_spacer = QSpacerItem(
                20,
                int(pages_above * self.page_height * self.zoom),
                QSizePolicy.Minimum,
                QSizePolicy.Fixed
            )
            self.page_layout.addSpacerItem(self.top_spacer)

        for i in range(start, end):
            label = PDFPageLabel()
            page = self.doc.load_page(i)
            target_height = int(self.page_height * self.zoom)
            scale = target_height / page.rect.height
            mat = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
            qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            pixmap = QPixmap.fromImage(qimg)
            label.setPixmap(pixmap)
            self.page_layout.addWidget(label)
            self.page_widgets.append(label)

        if pages_below > 0:
            self.bottom_spacer = QSpacerItem(
                20,
                int(pages_below * self.page_height * self.zoom),
                QSizePolicy.Minimum,
                QSizePolicy.Fixed
            )
            self.page_layout.addSpacerItem(self.bottom_spacer)

        self.page_layout.addStretch()

    def update_current_page(self):
        if not self.doc:
            return
        page = self.get_current_page()
        self.current_page_label.setText(f"Page: {page + 1}")
        self.page_input.setText(str(page + 1))
        # Highlight thumbnail
        self.thumb_list.setCurrentRow(page)
        self.thumb_list.scrollToItem(self.thumb_list.currentItem(), hint=QListWidget.PositionAtCenter)

    def open_pdf_from_path(self, file_path):
        self.doc = fitz.open(file_path)
        self.page_count_label.setText(f"/ {len(self.doc)}")
        self.zoom_slider.setValue(10)
        self.zoom = 1.0
        self.render_thumbnails()
        self.goto_page(0)
        self.update_current_page()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    viewer = VirtualizedPDFViewer()
    # Light modern style:
    app.setStyleSheet("""
        QWidget { background: #f7f8fa; color: #2b2b2b; font-family: 'Segoe UI', sans-serif; }
        QLabel, QLineEdit, QPushButton { color: #222; font-size: 16px; }
        QSlider { background: #e6e8ea; }
        QLineEdit { background: #fff; border: 1px solid #aab5c6; border-radius: 4px; padding: 4px; }
        QScrollArea { background: #f7f8fa; }
        QListWidget { background: #f3f4f6; border: 1px solid #e2e6ec; }
        QListWidget::item:selected { background: #d0e2ff; }
    """)
    viewer.showMaximized()
    sys.exit(app.exec())
