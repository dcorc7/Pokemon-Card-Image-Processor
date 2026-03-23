from pydantic_settings import BaseSettings
from pathlib import Path

# --------------------------------
# ----- PATHS --------------------
# --------------------------------

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):

    # Index paths
    FAISS_INDEX_PATH: str = str(BASE_DIR / "index" / "faiss_index.bin")
    METADATA_PATH: str = str(BASE_DIR / "index" / "metadata.json")

    # Model settings
    EMBEDDING_DIM: int = 2048
    TOP_K: int = 5

    # Tesseract path (Windows only)
    TESSERACT_PATH: str = "C:/Program Files/Tesseract-OCR/tesseract.exe"

    class Config:
        env_file = ".env"

settings = Settings()