import fitz  # PyMuPDF
from PIL import Image
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QListWidget, QMessageBox, QApplication, QProgressBar
)
from PyQt5.QtCore import Qt

class PDFToJPGWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to JPG Converter")
        self.setMinimumSize(700, 500)

        self.pdf_files = []
        self.output_folder = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top button bar
        top_btn_layout = QHBoxLayout()
        self.select_pdf_btn = QPushButton("📂 Select PDF(s)")
        self.select_pdf_btn.clicked.connect(self.select_pdfs)
        top_btn_layout.addWidget(self.select_pdf_btn)

        self.select_folder_btn = QPushButton("📁 Select Output Folder")
        self.select_folder_btn.clicked.connect(self.select_output_folder)
        top_btn_layout.addWidget(self.select_folder_btn)

        self.convert_btn = QPushButton("▶️ Convert to JPG")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.convert_pdfs)
        top_btn_layout.addWidget(self.convert_btn)

        layout.addLayout(top_btn_layout)

        self.status_label = QLabel("No PDF(s) or output folder selected.")
        layout.addWidget(self.status_label)

        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def select_pdfs(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if files:
            self.pdf_files = files
            self.file_list.clear()
            for f in files:
                self.file_list.addItem(f)
            self.update_status()
        self.check_ready_state()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder:
            self.output_folder = folder
            self.update_status()
        self.check_ready_state()

    def update_status(self):
        count = len(self.pdf_files)
        folder = self.output_folder or "[not selected]"
        self.status_label.setText(f"PDFs: {count}, Output: {folder}")

    def check_ready_state(self):
        if self.pdf_files and self.output_folder:
            self.convert_btn.setEnabled(True)
        else:
            self.convert_btn.setEnabled(False)

    def convert_pdfs(self):
        if not self.pdf_files or not self.output_folder:
            QMessageBox.warning(self, "Missing", "Please select PDF(s) and an output folder.")
            return

        total_pages = 0
        for pdf_path in self.pdf_files:
            pdf_document = fitz.open(pdf_path)
            total_pages += len(pdf_document)
            pdf_document.close()

        done_pages = 0
        self.progress_bar.setValue(0)

        try:
            for pdf_path in self.pdf_files:
                pdf_document = fitz.open(pdf_path)
                pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
                pdf_output_folder = os.path.join(self.output_folder, pdf_name)
                os.makedirs(pdf_output_folder, exist_ok=True)

                for page_num in range(len(pdf_document)):
                    page = pdf_document.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.25, 1.25))  # Good quality, adjust as needed
                    img_mode = "RGB" if pix.n < 5 else "RGBA"
                    image = Image.frombytes(img_mode, [pix.width, pix.height], pix.samples)
                    output_file = os.path.join(pdf_output_folder, f"{pdf_name}_page_{page_num + 1}.jpeg")
                    image = image.convert("RGB")
                    image.save(output_file, "JPEG", quality=85, optimize=True)

                    done_pages += 1
                    progress = int(100 * done_pages / total_pages)
                    self.progress_bar.setValue(progress)
                    QApplication.processEvents()  # Force UI update

                pdf_document.close()
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Success", "Conversion completed successfully!")
        except Exception as e:
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

# For testing standalone
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PDFToJPGWidget()
    window.show()
    sys.exit(app.exec())
