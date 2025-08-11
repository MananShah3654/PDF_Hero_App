from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class SuccessDialog(QDialog):
    def __init__(self, message="Operation completed!", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Success")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(340, 180)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fff, stop:1 #f6e7ff);
                border-radius: 18px;
            }
            QLabel#title {
                font-size: 22px; font-weight: bold; color: #35c86a;
            }
            QLabel#msg {
                font-size: 15px; color: #595B6E; padding: 4px 0 0 0;
            }
            QPushButton {
                background: #35c86a;
                color: #fff;
                border: none;
                font-size: 15px;
                border-radius: 8px;
                padding: 9px 28px;
            }
            QPushButton:hover { background: #39e47b; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        # Checkmark or custom SVG/icon
        icon = QLabel()
        icon.setAlignment(Qt.AlignCenter)
        # Use your brand checkmark PNG/SVG or emoji
        icon.setText("✅")
        icon.setFont(QFont("Segoe UI Emoji", 36))
        layout.addWidget(icon)

        title = QLabel("Success!")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        msg = QLabel(message)
        msg.setObjectName("msg")
        msg.setWordWrap(True)
        msg.setAlignment(Qt.AlignCenter)
        layout.addWidget(msg)

        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
