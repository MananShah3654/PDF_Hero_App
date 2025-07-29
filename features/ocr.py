import pytesseract
from PIL import Image
from PyQt5.QtWidgets import QFileDialog

def run():
    file, _ = QFileDialog.getOpenFileName(None, "Select Image for OCR", "", "Image Files (*.png *.jpg *.jpeg)")
    if not file:
        return
    text = pytesseract.image_to_string(Image.open(file))
    with open("ocr_output.txt", "w") as f:
        f.write(text)
