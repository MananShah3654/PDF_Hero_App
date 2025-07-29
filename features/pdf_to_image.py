from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from pdf2image import convert_from_path
import os

class PdfToImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.button = QPushButton("Select PDF to Convert to Images")
        self.button.clicked.connect(self.convert)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def convert(self):
        pdf_file, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if not pdf_file:
            return
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not output_folder:
            return
        try:
            images = convert_from_path(pdf_file)
            for i, image in enumerate(images):
                image.save(os.path.join(output_folder, f"page_{i+1}.jpg"), "JPEG")
            QMessageBox.information(self, "Success", f"Images saved to: {output_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to convert PDF: {e}")
