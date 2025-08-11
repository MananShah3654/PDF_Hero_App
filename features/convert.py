from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QSizePolicy
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt

CARD_INFO = [
    # (icon, title, subtitle, handler)
    ("word.png", "PDF to Word", "Convert your PDFs to DOC/DOCX for editing.", "open_pdf_to_word"),
    ("ppt.png", "PDF to PowerPoint", "PDFs to easy-to-edit PPT slides.", "open_pdf_to_ppt"),
    ("excel.png", "PDF to Excel", "Extract tables/data from PDFs to Excel.", "open_pdf_to_excel"),
    ("word.png", "Word to PDF", "DOC/DOCX to readable PDF.", "open_word_to_pdf"),
    ("ppt.png", "PowerPoint to PDF", "PPT to viewable PDF slides.", "open_ppt_to_pdf"),
    ("excel.png", "Excel to PDF", "Excel spreadsheets to PDF.", "open_excel_to_pdf"),
    ("jpg.png", "PDF to JPG", "Each PDF page as JPG or extract images.", "open_pdf_to_jpg"),
    ("jpg.png", "JPG to PDF", "JPG images into a single PDF.", "open_jpg_to_pdf"),
    ("html.png", "HTML to PDF", "Webpages to PDF with one click.", "open_html_to_pdf"),
    ("pdfa.png", "PDF to PDF/A", "ISO-standard archiving PDF.", "open_pdf_to_pdfa"),
]

class ConvertDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout()
        grid.setSpacing(24)
        for i, (icon, title, subtitle, handler) in enumerate(CARD_INFO):
            card = self.create_card(icon, title, subtitle, getattr(self, handler))
            row, col = divmod(i, 5)
            grid.addWidget(card, row, col)
        self.setLayout(grid)

    def create_card(self, icon_file, title, subtitle, handler):
        btn = QPushButton()
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setStyleSheet("""
            QPushButton {
                background: #fff;
                border-radius: 18px;
                border: 2px solid #f0f3f7;
                padding: 24px;
                text-align: left;
            }
            QPushButton:hover {
                border: 2px solid #4e82f1;
                background: #f7faff;
            }
        """)
        vbox = QVBoxLayout(btn)
        icon = QLabel()
        icon.setPixmap(QPixmap(f"resources/icons/{icon_file}").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        vbox.addWidget(icon, alignment=Qt.AlignLeft)
        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        vbox.addWidget(title_lbl, alignment=Qt.AlignLeft)
        subtitle_lbl = QLabel(subtitle)
        subtitle_lbl.setFont(QFont("Segoe UI", 11))
        subtitle_lbl.setStyleSheet("color: #8a8a9e;")
        subtitle_lbl.setWordWrap(True)
        vbox.addWidget(subtitle_lbl, alignment=Qt.AlignLeft)
        vbox.addStretch()
        btn.clicked.connect(handler)
        return btn

    # --- Handlers for each card ---
    def open_pdf_to_word(self):
        self.parent().open_converter("pdf_to_word")

    def open_pdf_to_ppt(self):
        self.parent().open_converter("pdf_to_ppt")

    def open_pdf_to_excel(self):
        self.parent().open_converter("pdf_to_excel")

    def open_word_to_pdf(self):
        self.parent().open_converter("word_to_pdf")

    def open_ppt_to_pdf(self):
        self.parent().open_converter("ppt_to_pdf")

    def open_excel_to_pdf(self):
        self.parent().open_converter("excel_to_pdf")

    def open_pdf_to_jpg(self):
        self.parent().open_converter("pdf_to_jpg")

    def open_jpg_to_pdf(self):
        self.parent().open_converter("jpg_to_pdf")

    def open_html_to_pdf(self):
        self.parent().open_converter("html_to_pdf")

    def open_pdf_to_pdfa(self):
        self.parent().open_converter("pdf_to_pdfa")
