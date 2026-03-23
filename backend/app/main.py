from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from PIL import Image
import io

from app.services.embedding_service import EmbeddingService
from app.services.similarity_service import SimilarityService
from app.services.ocr_service import OCRService
from app.schemas import CardResponse
from app.config import settings

# --------------------
# ----- LIFESPAN -----
# --------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load all models and indexes once at startup
    app.state.embedding_service = EmbeddingService()
    app.state.similarity_service = SimilarityService()
    app.state.ocr_service = OCRService()
    print("Models and index loaded.")
    yield
    print("Shutting down.")



# ---------------
# ----- APP -----
# ---------------

app = FastAPI(
    title="Pokemon Card Image Processor",
    version="1.0.0",
    lifespan=lifespan
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

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=CardResponse)
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Generate embedding and find similar cards first
    embedding = app.state.embedding_service.embed(image)
    similar_cards = app.state.similarity_service.search(embedding, top_k=5)

    # Use OCR for extraction
    ocr_data = app.state.ocr_service.extract(image)

    # If top match is very confident, use its metadata to fill in OCR gaps
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
