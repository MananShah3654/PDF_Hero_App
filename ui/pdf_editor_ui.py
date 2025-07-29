
# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
#     QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QInputDialog, QColorDialog, QMessageBox
# )
# from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
# from PyQt5.QtCore import Qt, QPointF
# import fitz  # PyMuPDF

# class PdfEditorWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.doc = None
#         self.current_page = 0
#         self.zoom = 1.0
#         self.pen_color = Qt.red
#         self.drawing = False
#         self.last_point = QPointF()

#         self.init_ui()

#     def init_ui(self):
#         layout = QVBoxLayout(self)

#         # Toolbar buttons
#         toolbar = QHBoxLayout()

#         open_btn = QPushButton("📂 Open PDF")
#         open_btn.clicked.connect(self.open_pdf)
#         toolbar.addWidget(open_btn)

#         text_btn = QPushButton("🔤 Add Text")
#         text_btn.clicked.connect(self.add_text)
#         toolbar.addWidget(text_btn)

#         draw_btn = QPushButton("✏️ Draw")
#         draw_btn.clicked.connect(self.set_draw_mode)
#         toolbar.addWidget(draw_btn)

#         color_btn = QPushButton("🎨 Color")
#         color_btn.clicked.connect(self.pick_color)
#         toolbar.addWidget(color_btn)

#         save_btn = QPushButton("💾 Save")
#         save_btn.clicked.connect(self.save_pdf)
#         toolbar.addWidget(save_btn)

#         layout.addLayout(toolbar)

#         # Graphics view setup
#         self.view = QGraphicsView()
#         self.scene = QGraphicsScene()
#         self.view.setScene(self.scene)
#         layout.addWidget(self.view)

#     def open_pdf(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
#         if not file_path:
#             return
#         self.doc = fitz.open(file_path)
#         self.pdf_path = file_path
#         self.show_page()

#     def show_page(self):
#         if not self.doc:
#             return
#         page = self.doc[self.current_page]
#         pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
#         image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
#         self.scene.clear()
#         pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(image))
#         self.scene.addItem(pixmap_item)
#         self.view.setScene(self.scene)

#     def add_text(self):
#         if not self.doc:
#             return
#         text, ok = QInputDialog.getText(self, "Add Text", "Enter text:")
#         if ok and text:
#             page = self.doc[self.current_page]
#             page.insert_text((100, 100), text, fontsize=14, color=(1, 0, 0))
#             self.show_page()

#     def pick_color(self):
#         color = QColorDialog.getColor()
#         if color.isValid():
#             self.pen_color = color

#     def set_draw_mode(self):
#         self.view.viewport().installEventFilter(self)

#     def eventFilter(self, obj, event):
#         if event.type() == event.MouseButtonPress:
#             self.drawing = True
#             self.last_point = event.pos()
#             return True
#         elif event.type() == event.MouseMove and self.drawing:
#             painter = QPainter(self.view.viewport())
#             pen = QPen(self.pen_color, 2)
#             painter.setPen(pen)
#             painter.drawLine(self.last_point, event.pos())
#             self.last_point = event.pos()
#             return True
#         elif event.type() == event.MouseButtonRelease:
#             self.drawing = False
#             return True
#         return super().eventFilter(obj, event)

#     def save_pdf(self):
#         if not self.doc:
#             return
#         out_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", self.pdf_path, "PDF Files (*.pdf)")
#         if out_path:
#             self.doc.save(out_path, garbage=4, deflate=True)
#             QMessageBox.information(self, "Saved", f"PDF saved to: {out_path}")

import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QPushButton, QWidget, QInputDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint

class PdfEditorWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PDF Editor')
        self.setGeometry(100, 100, 800, 600)
        self.pdf_file = None
        self.page_number = 0
        self.pixmap = None
        self.annotations = []  # [(text, position)]
        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.label = QLabel("Open a PDF to start editing")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(600, 800)

        open_button = QPushButton('Open PDF')
        open_button.clicked.connect(self.open_pdf)

        add_text_button = QPushButton('Add Text Annotation')
        add_text_button.clicked.connect(self.add_text)

        save_button = QPushButton('Save Edited PDF')
        save_button.clicked.connect(self.save_pdf)

        layout.addWidget(self.label)
        layout.addWidget(open_button)
        layout.addWidget(add_text_button)
        layout.addWidget(save_button)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.pdf_file = fitz.open(file_path)
            self.page_number = 0
            self.show_page()

    def show_page(self):
        page = self.pdf_file[self.page_number]
        image = page.get_pixmap()
        qimage = QImage(image.samples, image.width, image.height, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimage)
        self.label.setPixmap(self.pixmap)
        self.annotations.clear()  # Clear previous session annotations

    def add_text(self):
        if not self.pdf_file:
            QMessageBox.warning(self, "No PDF", "Open a PDF first!")
            return
        # For demo: add text at fixed position (100,100). You could implement mouse click to choose position.
        text, ok = QInputDialog.getText(self, "Add Text", "Enter annotation:")
        if ok and text:
            self.annotations.append((text, (100, 100)))
            painter = QPainter(self.label.pixmap())
            painter.setPen(QPen(QColor('red'), 2))
            painter.drawText(100, 100, text)
            painter.end()
            self.label.repaint()

    def save_pdf(self):
        if not self.pdf_file or not self.annotations:
            QMessageBox.warning(self, "Nothing To Save", "No edits to save.")
            return
        # Apply all text annotations to PDF using PyMuPDF
        for text, pos in self.annotations:
            page = self.pdf_file[self.page_number]
            page.insert_text(pos, text, fontsize=14, color=(1,0,0))
        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "edited.pdf", "PDF Files (*.pdf)")
        if save_path:
            self.pdf_file.save(save_path)
            QMessageBox.information(self, "Saved", f"Edited PDF saved to: {save_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = PDFEditor()
    editor.show()
    sys.exit(app.exec_())
