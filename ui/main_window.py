import sys
import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QStackedWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

from features import merge, split, annotate, compress, convert, ocr
from ui.merge_ui import MergeWidget
from ui.pdf_to_image_ui import PdfToImageUI
from ui.image_to_pdf_ui import ImageToPdfUI

from ui.pdf_viewer_ui import PDFViewerWidget
from ui.pdf_editor_ui import PdfEditorWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Hero Pro")
        self.setMinimumSize(1000, 700)
        self.setMinimumSize(1000, 700)
        self.load_styles()
        self.init_ui()
    
    def load_styles(self):
        # This handles both dev mode and PyInstaller bundled mode
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # PyInstaller extracts temp folder
        else:
            base_path = os.path.abspath(".")

        style_path = os.path.join(base_path, "style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

    def init_ui(self):
        # Sidebar with buttons
        sidebar = QVBoxLayout()
        tools = [
            ("Viewer", "view.png", self.load_pdf_viewer),
            ("Editor PDF", "view.png", self.load_pdf_editor),
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
  
    def load_pdf_viewer(self, pdf_path=None):
        viewer_widget = PDFViewerWidget()
        self.stack.addWidget(viewer_widget)
        self.stack.setCurrentWidget(viewer_widget)

        if  pdf_path:
            viewer_widget.open_pdf_from_path(pdf_path)  # ✅ This loads the passed-in file
            
        self.stack.addWidget(viewer_widget)
        self.stack.setCurrentWidget(viewer_widget)


    def load_pdf_editor(self, checked=False):
        editor_widget = PdfEditorWidget()
        self.stack.addWidget(editor_widget)
        self.stack.setCurrentWidget(editor_widget)
