import os, sys, tempfile, subprocess
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog,
    QListWidget, QListWidgetItem, QAbstractItemView, QMessageBox, QProgressDialog,
    QToolButton, QSizePolicy, QStatusBar, QSpacerItem
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
from PyPDF2 import PdfMerger
from pdf2image import convert_from_path
from ui.success_dialog import SuccessDialog

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
        self.setStyleSheet("""
            QLabel#instructions {
                border: 2px dashed #b8c7e0;
                color: #6e7ca0;
                font-size: 16px; padding: 40px 8px; border-radius: 20px;
                background: #f9fbff;
            }
            QListWidget {
                background: #fff; border-radius: 12px;
                padding: 12px 6px 12px 6px; min-height: 180px;
            }
            QPushButton, QToolButton {
                border-radius: 9px; font-size: 15px;
                padding: 8px 18px;
            }
            QPushButton#merge {
                background: #4e82f1; color: #fff;
                font-weight: bold;
            }
            QPushButton#add { background: #f2f4f8; }
            QPushButton#removeall { background: #f2f4f8; }
            QPushButton#toggle { background: #f9e5c5; }
        """)

        layout = QVBoxLayout(self)
        self.instructions = QLabel("🖱️ <b>Drag & drop PDF files</b> here, or <span style='color:#4e82f1;'>click 'Add PDFs'</span>")
        self.instructions.setObjectName("instructions")
        self.instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.instructions)

        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setIconSize(QSize(110, 150))
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.setSpacing(12)
        self.list_widget.setSelectionMode(QAbstractItemView.NoSelection)
        layout.addWidget(self.list_widget)

        # Button row
        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("＋ Add PDFs")
        self.add_btn.setObjectName("add")
        self.add_btn.clicked.connect(self.add_files)
        btn_row.addWidget(self.add_btn)

        self.remove_all_btn = QPushButton("🗑 Remove All")
        self.remove_all_btn.setObjectName("removeall")
        self.remove_all_btn.clicked.connect(self.remove_all_files)
        btn_row.addWidget(self.remove_all_btn)

        self.toggle_btn = QPushButton("🖼 Toggle Preview")
        self.toggle_btn.setObjectName("toggle")
        self.toggle_btn.clicked.connect(self.toggle_preview_mode)
        btn_row.addWidget(self.toggle_btn)

        btn_row.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.merge_btn = QPushButton("🔗 Merge Now")
        self.merge_btn.setObjectName("merge")
        self.merge_btn.clicked.connect(self.merge_files)
        btn_row.addWidget(self.merge_btn)

        layout.addLayout(btn_row)
        self.status_bar = QStatusBar()
        layout.addWidget(self.status_bar)

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
            QMessageBox.information(self, "Invalid File", "Drop only PDF files not already added.")

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF files", "", "PDF Files (*.pdf)")
        for f in files:
            if f not in self.pdf_paths:
                self.add_to_list(f)
        if self.list_widget.count() > 0:
            self.instructions.hide()
        else:
            self.instructions.show()

    def add_to_list(self, filepath):
        self.pdf_paths.append(filepath)
        try:
            images = convert_from_path(filepath, size=(110, 150) if not self.full_preview_mode else None)
            image_count = 1 if not self.full_preview_mode else len(images)
            for i in range(image_count):
                thumb_path = os.path.join(self.temp_dir, f"thumb_{os.path.basename(filepath)}_{i+1}.jpg")
                images[i].save(thumb_path, "JPEG")
                self.thumb_files.append(thumb_path)
                pixmap = QPixmap(thumb_path)

                frame = QWidget()
                v_layout = QVBoxLayout(frame)
                v_layout.setContentsMargins(0, 0, 0, 0)
                icon_label = QLabel()
                icon_label.setPixmap(pixmap.scaled(110, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_label.setAlignment(Qt.AlignCenter)
                name_label = QLabel(os.path.basename(filepath))
                name_label.setAlignment(Qt.AlignCenter)
                name_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
                name_label.setStyleSheet("color: #6073a1;")

                remove_btn = QToolButton()
                remove_btn.setText("✖")
                remove_btn.setFixedSize(22, 22)
                remove_btn.setStyleSheet("QToolButton { border: none; } QToolButton:hover { color: #e84d4d; background:#fff2f2; }")
                remove_btn.clicked.connect(lambda _, fp=filepath: self.remove_by_path(fp))

                v_layout.addWidget(icon_label)
                v_layout.addWidget(name_label)
                v_layout.addWidget(remove_btn, alignment=Qt.AlignHCenter)

                item = QListWidgetItem()
                self.list_widget.addItem(item)
                self.list_widget.setItemWidget(item, frame)
                item.setSizeHint(QSize(124, 188))
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
            SuccessDialog(f"PDFs merged and saved to:\n{out_path}").exec_()
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

    def closeEvent(self, event):
        # Clean up thumbnails when the widget is closed
        for thumb in self.thumb_files:
            if os.path.exists(thumb):
                os.remove(thumb)
        super().closeEvent(event)
