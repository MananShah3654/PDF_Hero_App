import os
from PIL import Image
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QListWidget, QMessageBox, QApplication, QProgressBar
)
from PyQt5.QtCore import Qt

class ImagesToPDFWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Images to PDF Converter")
        self.setMinimumSize(700, 500)

        self.image_files = []
        self.output_pdf = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top button bar
        top_btn_layout = QHBoxLayout()
        self.select_imgs_btn = QPushButton("📂 Select Images (JPG/JPEG)")
        self.select_imgs_btn.clicked.connect(self.select_images)
        top_btn_layout.addWidget(self.select_imgs_btn)

        self.select_output_btn = QPushButton("📄 Select Output PDF")
        self.select_output_btn.clicked.connect(self.select_output_pdf)
        top_btn_layout.addWidget(self.select_output_btn)

        self.convert_btn = QPushButton("▶️ Convert to PDF")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.convert_images_to_pdf)
        top_btn_layout.addWidget(self.convert_btn)

        layout.addLayout(top_btn_layout)

        self.status_label = QLabel("No images or output PDF selected.")
        layout.addWidget(self.status_label)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Progress bar and percentage label
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.percent_label = QLabel("0%")
        progress_layout.addWidget(self.percent_label)
        layout.addLayout(progress_layout)

        self.setLayout(layout)

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.jpg *.jpeg)")
        if files:
            self.image_files = files
            self.file_list.clear()
            for f in files:
                self.file_list.addItem(f)
            self.update_status()
        self.check_ready_state()

    def select_output_pdf(self):
        file, _ = QFileDialog.getSaveFileName(self, "Select Output PDF", "output.pdf", "PDF Files (*.pdf)")
        if file:
            self.output_pdf = file
            self.update_status()
        self.check_ready_state()

    def update_status(self):
        count = len(self.image_files)
        pdf_file = self.output_pdf or "[not selected]"
        self.status_label.setText(f"Images: {count}, Output PDF: {pdf_file}")

    def check_ready_state(self):
        if self.image_files and self.output_pdf:
            self.convert_btn.setEnabled(True)
        else:
            self.convert_btn.setEnabled(False)

    def convert_images_to_pdf(self):
        if not self.image_files or not self.output_pdf:
            QMessageBox.warning(self, "Missing", "Please select images and an output PDF.")
            return

        total = len(self.image_files)
        self.progress_bar.setValue(0)
        self.percent_label.setText("0%")

        try:
            image_list = []
            for idx, img_path in enumerate(self.image_files):
                image = Image.open(img_path)
                rgb_image = image.convert('RGB')
                image_list.append(rgb_image)
                progress = int(100 * (idx + 1) / total)
                self.progress_bar.setValue(progress)
                self.percent_label.setText(f"{progress}%")
                QApplication.processEvents()  # Allow UI to update

            # Save all images as a single PDF
            if image_list:
                image_list[0].save(self.output_pdf, save_all=True, append_images=image_list[1:])
            self.progress_bar.setValue(100)
            self.percent_label.setText("100%")
            QMessageBox.information(self, "Success", f"PDF created: {self.output_pdf}")
        except Exception as e:
            self.progress_bar.setValue(0)
            self.percent_label.setText("0%")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

# For standalone testing:
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ImagesToPDFWidget()
    window.show()
    sys.exit(app.exec())
