from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from contextlib import asynccontextmanager
from PIL import Image
import io

from app.services.embedding_service import EmbeddingService
from app.services.similarity_service import SimilarityService
from app.services.ocr_service import OCRService
from app.schemas import CardResponse

import base64


# ---------------
# ----- APP -----
# ---------------

app = FastAPI(
    title="Pokemon Card Image Processor"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



# --------------------
# ----- ROUTES -------
# --------------------

@app.on_event("startup")
async def startup_event():
    """Load models and indexes at startup."""
    app.state.embedding_service = EmbeddingService()
    app.state.similarity_service = SimilarityService()
    app.state.ocr_service = OCRService()
    print("Models and indexes loaded successfully.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=CardResponse)
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        embedding = app.state.embedding_service.embed(image)
        similar_cards = app.state.similarity_service.search(embedding, top_k=5)
        ocr_data = app.state.ocr_service.extract(image)

        if similar_cards and similar_cards[0]["score"] > 0.99:
            top_match = similar_cards[0]
            ocr_data["name"] = ocr_data["name"] or top_match["name"]
            ocr_data["types"] = ocr_data["types"] or top_match["types"]

        return CardResponse(
            name=ocr_data.get("name"),
            hp=ocr_data.get("hp"),
            types=ocr_data.get("types"),
            moves=ocr_data.get("moves"),
            similar_cards=similar_cards
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@app.get("/cards")
def get_cards(limit: int = 100):
    try:
        cards = app.state.similarity_service.get_all_cards(limit=limit)
        return cards
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860)