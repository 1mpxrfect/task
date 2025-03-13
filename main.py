import os
import re
import json
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

FOLDER_PATH = "documents"
OUTPUT_JSON = "output.json"


def extract_text_from_pdf(pdf_path):
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(pdf_path).strip()

        if not text:
            images = convert_from_path(pdf_path)
            text = "\n".join(pytesseract.image_to_string(img, lang="rus+eng") for img in images)

        return text
    except Exception as e:
        print(f"Error to reading PDF {pdf_path}: {e}")
        return ""


def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        return pytesseract.image_to_string(img, lang="rus+eng")
    except Exception as e:
        print(f"Error to reading image {image_path}: {e}")
        return ""


def extract_data(text, file_name):
    invoice_number = re.search(r"\b\d{7,}\b", text)
    container_number = re.search(r"\b[A-Z]{2}[0-9]{7}\b", text)
    expeditor = re.search(r"(?:Экспедитор|Перевозчик|Отправитель|Expeditor|Carrier):?\s*([^\n,]+)", text)

    return {
        "invoice_number": invoice_number.group(0) if invoice_number else None,
        "container_number": container_number.group(0) if container_number else None,
        "expeditor": expeditor.group(1).strip() if expeditor else None,
        "file_name": file_name,
    }


def process_folder(folder_path):
    extracted_data = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)

        if file.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file.lower().endswith((".jpg", ".jpeg", ".png")):
            text = extract_text_from_image(file_path)
        else:
            continue

        if not text.strip():
            continue

        data = extract_data(text, file)
        extracted_data.append(data)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=4)

    print(f"Data is saved in {OUTPUT_JSON}")

process_folder(FOLDER_PATH)
