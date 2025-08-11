from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
import sys
import os

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    # Handle double-click or "Open with PDF Hero"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf'):
            window.load_pdf_viewer(pdf_path)

    window.showMaximized()
    sys.exit(app.exec_())

    
