from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox,
    QListView, QAbstractItemView
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from pdf2image import convert_from_path
import os
import tempfile

class PdfToImageUI(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_paths = []
        self.temp_dir = tempfile.mkdtemp()
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.instructions = QLabel("📄 Drag & drop PDFs here or click to select")
        self.instructions.setAlignment(Qt.AlignCenter)
        self.instructions.setStyleSheet("border: 2px dashed #888; padding: 40px; font-size: 16px;")
        layout.addWidget(self.instructions)

        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListView.IconMode)
        self.list_widget.setIconSize(QSize(120, 160))
        self.list_widget.setAcceptDrops(False)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("+ Add PDFs")
        self.add_btn.clicked.connect(self.add_pdfs)
        btn_layout.addWidget(self.add_btn)

        self.convert_btn = QPushButton("🖼 Convert to Images")
        self.convert_btn.clicked.connect(self.convert_to_images)
        btn_layout.addWidget(self.convert_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def add_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF files", "", "PDF Files (*.pdf)")
        for f in files:
            if f not in self.pdf_paths:
                self.pdf_paths.append(f)
                item = QListWidgetItem(QIcon("resources/icons/pdf.png"), os.path.basename(f))
                item.setData(Qt.UserRole, f)
                self.list_widget.addItem(item)
        self.instructions.setVisible(self.list_widget.count() == 0)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf") and path not in self.pdf_paths:
                self.pdf_paths.append(path)
                item = QListWidgetItem(QIcon("resources/icons/pdf.png"), os.path.basename(path))
                item.setData(Qt.UserRole, path)
                self.list_widget.addItem(item)
        self.instructions.setVisible(self.list_widget.count() == 0)

    def convert_to_images(self):
        if not self.pdf_paths:
            QMessageBox.warning(self, "No PDFs", "Please add PDF files first.")
            return

        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not out_dir:
            return

        try:
            for file in self.pdf_paths:
                images = convert_from_path(file)
                base_name = os.path.splitext(os.path.basename(file))[0]
                for i, image in enumerate(images):
                    img_path = os.path.join(out_dir, f"{base_name}_page_{i+1}.jpg")
                    image.save(img_path, "JPEG")
            QMessageBox.information(self, "Success", f"Images saved to: {out_dir}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to convert PDFs: {e}")
