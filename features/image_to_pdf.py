from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PIL import Image

class ImageToPdfWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.convert_button = QPushButton("Select Images and Convert to PDF")
        self.convert_button.clicked.connect(self.convert_images_to_pdf)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)

    def convert_images_to_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return

        out_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "output.pdf", "PDF Files (*.pdf)")
        if not out_path:
            return

        try:
            image_list = [Image.open(f).convert('RGB') for f in files]
            image_list[0].save(out_path, save_all=True, append_images=image_list[1:])
            QMessageBox.information(self, "Success", f"PDF created at: {out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create PDF: {e}")
