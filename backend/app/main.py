from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

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

# Actions done on app startup
@app.on_event("startup")
async def startup_event():
    """Load models and indexes at startup."""
    app.state.embedding_service = EmbeddingService()
    app.state.similarity_service = SimilarityService()
    app.state.ocr_service = OCRService()
    print("Models and indexes loaded successfully.")


# Endpoint to signify API health
@app.get("/health")
def health():
    return {"status": "ok"}


# Endpoint to extract information from pokemon cards
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
    

# Endpoint to display a sample of cards in the database
@app.get("/cards")
def get_cards(limit: int = 100):
    try:
        cards = app.state.similarity_service.get_all_cards(limit=limit)
        return cards
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    

# Endpoint to display the original card and its OCR cropped boxes
@app.post("/visualize")
async def visualize(file: UploadFile = File(...)):
    try:
        # Read the raw bytes from the uploaded file
        image_bytes = await file.read()

        # Decode bytes into a Pillow Image and normalize to RGB color space
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Delegate to OCRService to draw colored bounding boxes over each crop region
        annotated = app.state.ocr_service.visualize_regions(image)

        # Write the annotated image into an in-memory buffer as PNG
        buf = io.BytesIO()
        annotated.save(buf, format="PNG")
        
        # Reset buffer position to the start before streaming
        buf.seek(0)  

        # Stream the PNG bytes directly back to the client
        return StreamingResponse(buf, media_type="image/png")

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=7860)



"""
ENDPOINT LOCATIONS:
https://dcorcoran-pokemon-card-image-processor-api.hf.space/docs
https://dcorcoran-pokemon-card-image-processor-api.hf.space/health
https://dcorcoran-pokemon-card-image-processor-api.hf.space/predict
https://dcorcoran-pokemon-card-image-processor-api.hf.space/cards
https://dcorcoran-pokemon-card-image-processor-api.hf.space/visualize

"""