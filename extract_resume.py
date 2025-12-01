import pdfplumber
from langdetect import detect

def process_resume(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() for page in pdf.pages]

    full_text = "\n".join(filter(None, pages))

    # detect the language (free)
    lang = detect(full_text)

    # return extracted text and language
    return {
        "text": full_text,
        "lang": lang
    }
