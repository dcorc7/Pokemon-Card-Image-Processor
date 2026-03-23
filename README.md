# Pokemon-Card-Image-Processor

An ML system that extracts structured data from Pokémon card images using optical character recognition (OCR) and retrieves similar cards using embedding-based similarity search.

---

## Features

- **OCR Pipeline** — Extracts card name, type, HP, moves, and other fields from uploaded card images
- **Embedding Model** — Fine-tuned ResNet/ViT model that encodes card images into vector representations
- **Similarity Search** — FAISS index enables fast retrieval of visually and structurally similar cards
- **REST API** — FastAPI backend exposes a `/predict` endpoint for image processing
- **Interactive UI** — Streamlit frontend for image upload, structured data display, and similar card recommendations
- **Containerized** — Fully Dockerized with Docker Compose for local development and Hugging Face Spaces for deployment

---

## Project Structure

```
Pokemon-Card-Image-Processor/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, model loading, /predict endpoint
│   │   ├── config.py                # Environment variables and paths
│   │   ├── schemas.py               # Pydantic request/response schemas
│   │   ├── utils.py                 # Shared utility functions
│   │   │
│   │   ├── models/
│   │   │   ├── embedding_model.py   # ResNet/ViT model definition
│   │   │   ├── ocr_model.py         # OCR model wrapper
│   │   │   ├── layout_detector.py   # Card region detection
│   │   │
│   │   ├── services/
│   │   │   ├── embedding_service.py # Image preprocessing and embedding generation
│   │   │   ├── ocr_service.py       # OCR text extraction and field parsing
│   │   │   ├── similarity_service.py# FAISS index querying and metadata retrieval
│   │   │
│   │   ├── index/
│   │   │   ├── faiss_index.bin      # Prebuilt FAISS index
│   │   │   ├── metadata.json        # Card metadata mapped to index positions
│   │
│   ├── training/
│   │   ├── train_embedding.py       # Fine-tune embedding model
│   │   ├── build_faiss_index.py     # Build FAISS index from trained model
│   │   ├── evaluate_similarity.py   # Evaluate retrieval quality
│   │   ├── ocr_validation.py        # Validate OCR field extraction accuracy
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── frontend/
│   ├── app.py                       # Main Streamlit app
│   ├── api_client.py                # HTTP client for backend communication
│   ├── components/
│   │   ├── upload_section.py        # Image upload widget
│   │   ├── display_structured_data.py # Extracted card data display
│   │   ├── similarity_grid.py       # Similar cards grid display
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── docker-compose.yml
└── README.md
```

---

## Quickstart

### Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Run Locally

```bash
git clone https://github.com/dcorc7/Pokemon-Card-Image-Processor.git
cd Pokemon-Card-Image-Processor
docker compose up --build
```

- Frontend: [http://localhost:8501](http://localhost:8501)
- Backend API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API

### `POST /predict`

Accepts a card image and returns extracted fields and similar cards.

**Request:** `multipart/form-data` with an image file

**Response:**
```json
{
  "card_name": "Charizard",
  "hp": 120,
  "type": "Fire",
  "moves": ["Fire Spin", "Slash"],
  "similar_cards": [
    { "id": "base1-4", "name": "Charizard", "score": 0.98 },
    { "id": "base1-5", "name": "Charmeleon", "score": 0.91 }
  ]
}
```

### `GET /health`

Returns service status.

---

## Development Order

1. Build and validate the embedding model locally
2. Build the FAISS index from card image dataset
3. Wrap the pipeline in FastAPI
4. Dockerize the backend
5. Build the Streamlit frontend
6. Dockerize the frontend
7. Test end-to-end with Docker Compose
8. Deploy backend and frontend to separate Hugging Face Spaces

---

## Deployment

Each service is deployed as a separate **Docker Space on Hugging Face**.

Update the backend URL in `frontend/api_client.py`:

```python
BACKEND_URL = "https://your-backend-space.hf.space/predict"
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| OCR | Tesseract / pytesseract |
| Embedding Model | ResNet / ViT (PyTorch) |
| Similarity Search | FAISS |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Containerization | Docker + Docker Compose |
| Deployment | Hugging Face Spaces |

---
