import pytesseract
import re
from PIL import Image
import sys
import os


class OCRService:

    def __init__(self):
        # Auto-detect tesseract path
        if sys.platform.startswith("win"):
            pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "C:/Program Files/Tesseract-OCR/tesseract.exe")
        else:
            # Linux / Hugging Face Spaces
            pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        print(f"OCR service initialized. Using Tesseract at {pytesseract.pytesseract.tesseract_cmd}")

    def extract(self, image: Image.Image) -> dict:
        w, h = image.size

        # --------------------------------
        # ----- CROP REGIONS -------------
        # --------------------------------

        # Card name — top left area
        name_region = image.crop((0.15 * w, 0.02 * h, 0.75 * w, 0.10 * h))

        # HP — top right area
        hp_region = image.crop((0.60 * w, 0.02 * h, 0.95 * w, 0.10 * h))

        # Moves — lower middle section
        moves_region = image.crop((0.00 * w, 0.55 * h, 1.00 * w, 0.85 * h))

        # Full image for type detection
        full_text = pytesseract.image_to_string(image)

        # --------------------------------
        # ----- EXTRACT FIELDS -----------
        # --------------------------------

        return {
            "name": self._extract_name(name_region),
            "hp": self._extract_hp(hp_region),
            "types": self._extract_types(full_text),
            "moves": self._extract_moves(moves_region),
        }

    # --------------------------------
    # ----- EXTRACTORS ---------------
    # --------------------------------

    def _extract_name(self, region: Image.Image) -> str | None:
        # Upscale region for better OCR accuracy
        region = region.resize(
            (region.width * 3, region.height * 3),
            Image.LANCZOS
        )
        text = pytesseract.image_to_string(region, config="--psm 7").strip()
        return text if text else None

    def _extract_hp(self, region: Image.Image) -> str | None:
        region = region.resize(
            (region.width * 3, region.height * 3),
            Image.LANCZOS
        )
        text = pytesseract.image_to_string(region, config="--psm 7")
        match = re.search(r'(\d+)\s*HP|HP\s*(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2)
        return None

    def _extract_types(self, text: str) -> list[str] | None:
        types = [
            "Fire", "Water", "Grass", "Electric", "Psychic",
            "Fighting", "Darkness", "Metal", "Colorless",
            "Dragon", "Fairy", "Lightning", "Normal"
        ]
        found = [t for t in types if t.lower() in text.lower()]
        return found if found else None

    def _extract_moves(self, region: Image.Image) -> list[dict] | None:
        region = region.resize(
            (region.width * 2, region.height * 2),
            Image.LANCZOS
        )
        text = pytesseract.image_to_string(region)
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        moves = []
        i = 0
        while i < len(lines):
            # Match move name with damage e.g. "Lightning Flash 20"
            match = re.match(r'^([A-Z][a-zA-Z\s]+?)\s+(\d+\+?)$', lines[i])
            if match:
                moves.append({
                    "name": match.group(1).strip(),
                    "damage": match.group(2).strip(),
                    "text": lines[i + 1] if i + 1 < len(lines) else None
                })
                i += 2
            else:
                i += 1

        return moves if moves else None