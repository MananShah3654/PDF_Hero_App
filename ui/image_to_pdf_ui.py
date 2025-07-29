from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt
import img2pdf
import os

class ImageToPdfUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title = QLabel("📁 Batch Image-to-PDF Converter")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title)

        self.progress = QLabel("Select a folder to start")
        self.progress.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.select_btn = QPushButton("📂 Select Base Folder")
        self.select_btn.clicked.connect(self.select_folder)
        layout.addWidget(self.select_btn)

        self.setLayout(layout)

    def select_folder(self):
        base_folder = QFileDialog.getExistingDirectory(self, "Select Folder with Subfolders of Images")
        if not base_folder:
            QMessageBox.information(self, "No Folder Selected", "You didn't select a folder.")
            return

        self.progress.setText("Processing... Please wait.")
        self.progress_bar.setVisible(True)
        self.process_folders(base_folder)

    def process_folders(self, base_folder):
        subfolders = [
            os.path.join(base_folder, folder)
            for folder in os.listdir(base_folder)
            if os.path.isdir(os.path.join(base_folder, folder))
        ]

        if not subfolders:
            self.progress.setText("No subfolders found in the selected folder.")
            return

        output_folder = os.path.join(base_folder, "output_pdfs")
        os.makedirs(output_folder, exist_ok=True)

        self.progress_bar.setMaximum(len(subfolders))
        self.progress_bar.setValue(0)

        for i, subfolder in enumerate(subfolders):
            folder_name = os.path.basename(subfolder)
            output_pdf = os.path.join(output_folder, f"{folder_name}.pdf")
            self.images_to_pdf_with_img2pdf(subfolder, output_pdf)
            self.progress_bar.setValue(i + 1)

        self.progress.setText(f"✅ All PDFs are saved in: {output_folder}")
        QMessageBox.information(self, "Success", f"PDFs created in:\n{output_folder}")

    def images_to_pdf_with_img2pdf(self, input_folder, output_pdf):
        image_files = [
            os.path.join(input_folder, file)
            for file in os.listdir(input_folder)
            if file.lower().endswith(('jpg', 'jpeg'))
        ]

        if not image_files:
            return

        image_files.sort()

        try:
            with open(output_pdf, "wb") as pdf_file:
                pdf_file.write(img2pdf.convert(image_files))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to convert images in {input_folder}: {e}")
