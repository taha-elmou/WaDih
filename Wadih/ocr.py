# ══════════════════════════════════════════════════════════════
#  WADIH — backend/ocr.py
#  Extraction de texte : PyMuPDF (PDF natif) + Tesseract (OCR)
#  Langues supportées : français + arabe (fra+ara)
# ══════════════════════════════════════════════════════════════

import io
from PIL import Image
import fitz          # PyMuPDF
import pytesseract

# ── Windows uniquement : chemin vers tesseract.exe ──
# Décommente si Tesseract n'est pas dans ton PATH :
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ── Langue OCR ──
OCR_LANG = "fra+ara"

# ── Résolution pour conversion PDF scanné → image ──
PDF_SCAN_DPI = 200


def extract_text_from_pdf(file_bytes: bytes) -> dict:
    """
    Extrait le texte d'un PDF.
    - Pages avec texte natif → PyMuPDF direct.
    - Pages scannées (texte vide) → conversion image + Tesseract OCR.

    Retourne : { "text": str, "method": str, "pages": int }
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    total_pages = len(doc)
    all_text = []
    method = "pymupdf_native"

    for page_num in range(total_pages):
        page = doc[page_num]
        page_text = page.get_text("text").strip()

        if page_text:
            all_text.append(page_text)
        else:
            # Page scannée → OCR
            method = "pymupdf_ocr_mixed"
            mat = fitz.Matrix(PDF_SCAN_DPI / 72, PDF_SCAN_DPI / 72)
            pix = page.get_pixmap(matrix=mat)
            pil_image = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(pil_image, lang=OCR_LANG, config="--psm 3")
            all_text.append(ocr_text.strip())

    doc.close()

    if all(not t for t in all_text):
        method = "pymupdf_ocr_full"

    return {
        "text": "\n\n---\n\n".join(filter(None, all_text)),
        "method": method,
        "pages": total_pages,
    }


def extract_text_from_image(file_bytes: bytes) -> dict:
    """
    Extrait le texte d'une image (PNG, JPG, JPEG, WEBP) via Tesseract OCR.

    Retourne : { "text": str, "method": str, "pages": int }
    """
    pil_image = Image.open(io.BytesIO(file_bytes))

    if pil_image.mode not in ("RGB", "L"):
        pil_image = pil_image.convert("RGB")

    ocr_text = pytesseract.image_to_string(pil_image, lang=OCR_LANG, config="--psm 3")

    return {
        "text": ocr_text.strip(),
        "method": "tesseract_ocr",
        "pages": 1,
    }