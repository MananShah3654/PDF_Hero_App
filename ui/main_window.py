from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
import os

from features import merge, split, annotate, compress, convert, ocr
from ui.merge_ui import MergeWidget
from ui.pdf_to_image_ui import PdfToImageUI
from ui.image_to_pdf_ui import ImageToPdfUI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Hero Pro")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(open("style.qss", "r").read())
        self.init_ui()

    def init_ui(self):
        # Sidebar with buttons
        sidebar = QVBoxLayout()
        tools = [
            ("Viewer", "view.png", lambda: print("Viewer clicked")),
            ("Merge", "merge.png", self.load_merge_ui),
            ("Split", "split.png", split.run),
            ("Annotate", "annotate.png", annotate.run),
            ("Compress", "compress.png", compress.run),
            ("Convert", "convert.png", convert.run),
            ("OCR", "ocr.png", ocr.run),
            ("PDF to Image", "convert.png", self.load_pdf_to_image_ui),
("Image to PDF", "convert.png", self.load_image_to_pdf_ui),
        ]

        for name, icon_file, func in tools:
            btn = QPushButton(name)
            icon_path = os.path.join("resources", "icons", icon_file)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setObjectName("sidebarButton")
            btn.clicked.connect(func)
            sidebar.addWidget(btn)

        sidebar.addStretch()

        # Placeholder stacked panel
        self.stack = QStackedWidget()
        self.viewer_placeholder = QLabel("PDF Viewer Placeholder")
        self.stack.addWidget(self.viewer_placeholder)

        # Layout setup
        main_layout = QHBoxLayout()
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar)
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addWidget(self.stack, 5)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_merge_ui(self):
        merge_widget = MergeWidget()
        self.stack.addWidget(merge_widget)
        self.stack.setCurrentWidget(merge_widget)

    def load_image_to_pdf_ui(self):
        widget = ImageToPdfUI()
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

    def load_pdf_to_image_ui(self):
        widget = PdfToImageUI()
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)

