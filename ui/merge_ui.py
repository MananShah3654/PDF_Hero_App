from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox,
    QListView, QStatusBar, QProgressDialog, QAbstractItemView,
    QFrame, QStyle, QStyleOptionButton, QApplication, QToolButton
)
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt5.QtCore import Qt, QSize, QRect, QPropertyAnimation
from PyPDF2 import PdfMerger
from pdf2image import convert_from_path
import os
import sys
import tempfile
import subprocess

class MergeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_paths = []
        self.thumb_files = []
        self.full_preview_mode = False
        self.temp_dir = tempfile.mkdtemp()
        self.setAcceptDrops(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.instructions = QLabel("🖱️ Drag & drop PDF files here or click to select")
        self.instructions.setAlignment(Qt.AlignCenter)
        self.instructions.setStyleSheet("border: 2px dashed #888; padding: 40px; font-size: 16px;")
        layout.addWidget(self.instructions)

        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListView.IconMode)
        self.list_widget.setIconSize(QSize(120, 160))
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("+ Add PDFs")
        self.add_btn.clicked.connect(self.add_files)
        btn_layout.addWidget(self.add_btn)

        self.remove_all_btn = QPushButton("🗑 Remove All")
        self.remove_all_btn.clicked.connect(self.remove_all_files)
        btn_layout.addWidget(self.remove_all_btn)

        self.toggle_btn = QPushButton("🖼 Toggle Preview Mode")
        self.toggle_btn.clicked.connect(self.toggle_preview_mode)
        btn_layout.addWidget(self.toggle_btn)

        self.merge_btn = QPushButton("🔗 Merge Now")
        self.merge_btn.clicked.connect(self.merge_files)
        self.merge_btn.setStyleSheet("background-color: #2d89ef; color: white; padding: 10px;")
        btn_layout.addWidget(self.merge_btn)

        layout.addLayout(btn_layout)

        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files_added = False
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf") and path not in self.pdf_paths:
                self.add_to_list(path)
                files_added = True
        if files_added:
            self.instructions.hide()
        else:
            QMessageBox.information(self, "Invalid File", "Please drop only PDF files that are not already added.")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF files", "", "PDF Files (*.pdf)")
        for f in files:
            if f not in self.pdf_paths:
                self.add_to_list(f)
        self.instructions.setVisible(self.list_widget.count() == 0)

    def add_to_list(self, filepath):
        self.pdf_paths.append(filepath)
        try:
            images = convert_from_path(filepath, size=(120, 160) if not self.full_preview_mode else None)
            image_count = 1 if not self.full_preview_mode else len(images)
            for i in range(image_count):
                thumb_path = os.path.join(self.temp_dir, f"thumb_{os.path.basename(filepath)}_{i+1}.jpg")
                images[i].save(thumb_path, "JPEG")
                self.thumb_files.append(thumb_path)
                pixmap = QPixmap(thumb_path)

                frame = QWidget()
                h_layout = QVBoxLayout(frame)
                h_layout.setContentsMargins(5, 5, 5, 5)

                icon_label = QLabel()
                icon_label.setPixmap(pixmap.scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_label.setAlignment(Qt.AlignCenter)

                name_label = QLabel(os.path.basename(filepath))
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setFont(QFont("Arial", 8))
                name_label.setStyleSheet("color: #555;")

                remove_btn = QToolButton()
                remove_btn.setText("❌")
                remove_btn.setFixedSize(24, 24)
                remove_btn.setStyleSheet("QToolButton { border: none; } QToolButton:hover { color: red; }")
                remove_btn.clicked.connect(lambda _, fp=filepath: self.remove_by_path(fp))

                h_layout.addWidget(icon_label)
                h_layout.addWidget(name_label)
                h_layout.addWidget(remove_btn, alignment=Qt.AlignCenter)

                item = QListWidgetItem()
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, frame)
                item.setSizeHint(frame.sizeHint())
                item.setData(Qt.UserRole, filepath)
        except Exception as e:
            print(f"Thumbnail error: {e}")

        self.instructions.setVisible(self.list_widget.count() == 0)

    def remove_by_path(self, filepath):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == filepath:
                self.list_widget.takeItem(i)
                break
        if filepath in self.pdf_paths:
            self.pdf_paths.remove(filepath)
        for thumb in list(self.thumb_files):
            if filepath and filepath in thumb and os.path.exists(thumb):
                os.remove(thumb)
                self.thumb_files.remove(thumb)
        self.instructions.setVisible(self.list_widget.count() == 0)
        self.status_bar.showMessage(f"Removed {os.path.basename(filepath)}", 3000)

    def remove_all_files(self):
        self.list_widget.clear()
        self.pdf_paths.clear()
        for thumb in self.thumb_files:
            if os.path.exists(thumb):
                os.remove(thumb)
        self.thumb_files.clear()
        self.instructions.show()
        self.status_bar.showMessage("🗑 All files removed.", 3000)

    def toggle_preview_mode(self):
        self.full_preview_mode = not self.full_preview_mode
        current_pdfs = list(self.pdf_paths)
        self.remove_all_files()
        for f in current_pdfs:
            self.add_to_list(f)
        self.status_bar.showMessage("🖼 Full-page preview ON" if self.full_preview_mode else "🖼 Single-page preview ON", 3000)

    def merge_files(self):
        if self.list_widget.count() < 2:
            QMessageBox.warning(self, "Add PDFs", "Please add at least two PDF files.")
            return

        ordered_paths = []
        seen = set()
        for i in range(self.list_widget.count()):
            path = self.list_widget.item(i).data(Qt.UserRole)
            if path not in seen:
                ordered_paths.append(path)
                seen.add(path)

        merger = PdfMerger()
        progress = QProgressDialog("Merging PDFs...", None, 0, len(ordered_paths), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        for i, path in enumerate(ordered_paths):
            merger.append(path)
            progress.setValue(i + 1)

        out_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "merged.pdf", "PDF Files (*.pdf)")
        if out_path:
            merger.write(out_path)
            merger.close()
            self.remove_all_files()
            QMessageBox.information(self, "Success", f"PDFs merged and saved to:\n{out_path}")
            self.status_bar.showMessage(f"✅ Merged PDF saved to: {out_path}", 5000)
            self.open_file(out_path)

    def open_file(self, path):
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(("open", path))
            else:
                subprocess.call(("xdg-open", path))
        except Exception as e:
            print(f"Could not open file automatically: {e}")
