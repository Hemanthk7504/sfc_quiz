import pytesseract


def ocr_image(image):
    return pytesseract.image_to_string(image)
