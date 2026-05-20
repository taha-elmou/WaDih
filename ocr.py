# ══════════════════════════════════════════════════════════════
#  WADIH — backend/main.py
#  Point d'entrée FastAPI
#  Lancer : python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
# ══════════════════════════════════════════════════════════════

from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Modules internes WaDih
from ocr import extract_text_from_pdf, extract_text_from_image
# from ai import analyze_text        # à décommenter quand ai.py sera prêt
# from risk import compute_risk_score # à décommenter quand risk.py sera prêt

# ── Init app ──
app = FastAPI(
    title="WaDih API",
    description="API d'analyse de CGU — Loi 09-08",
    version="1.0.0",
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Types acceptés ──
ACCEPTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}


# ══════════════════════════════════════════════════════════════
#  Routes
# ══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    return {"status": "ok", "service": "WaDih API", "version": "1.0.0"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """
    Étape 1 : extraction du texte brut (OCR / PyMuPDF).
    Retourne le texte extrait + métadonnées.
    """
    filename = file.filename or ""
    file_ext = Path(filename).suffix.lower()

    if file_ext not in ACCEPTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Format non supporté : '{file_ext}'. Acceptés : PDF, PNG, JPG, JPEG, WEBP.",
        )

    try:
        file_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lecture fichier : {str(e)}")

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Fichier vide.")

    try:
        if file_ext == ".pdf":
            result = extract_text_from_pdf(file_bytes)
        else:
            result = extract_text_from_image(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'extraction du texte : {str(e)}")

    extracted = result["text"] or "[Aucun texte détecté dans ce fichier.]"

    return JSONResponse(content={
        "extracted_text": extracted,
        "method": result["method"],
        "pages": result["pages"],
        "filename": filename,
        "char_count": len(extracted),
    })


# ── Futur endpoint analyse complète ──
# @app.post("/analyze")
# async def analyze(file: UploadFile = File(...)):
#     """
#     Pipeline complet :
#     1. OCR / extraction texte
#     2. Analyse IA (ai.py)
#     3. Score de risque (risk.py)
#     4. Résumé Darija
#     """
#     pass