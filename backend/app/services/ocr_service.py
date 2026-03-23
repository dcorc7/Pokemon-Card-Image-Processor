import pytesseract
import re
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import sys
import os


class OCRService:

    def __init__(self):
        if sys.platform.startswith("win"):
            pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "C:/Program Files/Tesseract-OCR/tesseract.exe")
        else:
            pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    def _preprocess(self, region: Image.Image, scale: int = 3) -> Image.Image:
        """Upscale, convert to grayscale, and threshold for better OCR."""
        region = region.resize(
            (region.width * scale, region.height * scale),
            Image.LANCZOS
        )
        region = region.convert("L")  # grayscale
        # Increase contrast
        region = ImageEnhance.Contrast(region).enhance(2.0)
        # Threshold to black/white
        region = region.point(lambda x: 0 if x < 140 else 255, "1").convert("L")
        return region

    def extract(self, image: Image.Image) -> dict:
        w, h = image.size

        # Name — skip "Basic Pokemon" line at very top, just grab name row
        name_region = image.crop((0.05 * w, 0.06 * h, 0.72 * w, 0.13 * h))

        # HP — top right, large number + "HP" text
        hp_region = image.crop((0.55 * w, 0.04 * h, 0.97 * w, 0.13 * h))

        # Moves — middle to lower section
        moves_region = image.crop((0.02 * w, 0.52 * h, 0.98 * w, 0.88 * h))

        # Full image for type detection
        full_text = pytesseract.image_to_string(image)

        return {
            "name": self._extract_name(name_region),
            "hp": self._extract_hp(hp_region),
            "types": self._extract_types(full_text),
            "moves": self._extract_moves(moves_region),
        }

    def _extract_name(self, region: Image.Image) -> str | None:
        region = self._preprocess(region, scale=3)
        text = pytesseract.image_to_string(region, config="--psm 7 --oem 3").strip()
        # Clean up noise — keep only lines that look like a name
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        for line in lines:
            # Skip lines that are clearly not a name
            if re.search(r'[A-Z][a-z]+', line) and len(line) < 30:
                return line
        return text if text else None

    def _extract_hp(self, region: Image.Image) -> str | None:
        region = self._preprocess(region, scale=3)
        text = pytesseract.image_to_string(region, config="--psm 6 --oem 3")
        # Look for a number near "HP"
        match = re.search(r'(\d+)\s*HP|HP\s*(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2)
        # Fallback: just grab any standalone number (the HP value)
        match = re.search(r'\b(\d{2,3})\b', text)
        return match.group(1) if match else None

    def _extract_types(self, text: str) -> list[str] | None:
        types = [
            "Fire", "Water", "Grass", "Electric", "Psychic",
            "Fighting", "Darkness", "Metal", "Colorless",
            "Dragon", "Fairy", "Lightning", "Normal"
        ]
        found = [t for t in types if t.lower() in text.lower()]
        return found if found else None

    def _extract_moves(self, region: Image.Image) -> list[dict] | None:
        region = self._preprocess(region, scale=2)
        text = pytesseract.image_to_string(region, config="--psm 6 --oem 3")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        moves = []
        i = 0
        while i < len(lines):
            # Match: "MoveName 10" or "MoveName 10+" or "MoveName" alone on a line (0 damage moves)
            match = re.match(r'^([A-Z][a-zA-Z\s]{2,25}?)\s{2,}(\d+\+?)$', lines[i])
            if not match:
                # Try looser match for lines like "Psychic                    10+"
                match = re.match(r'^([A-Z][a-zA-Z]+)\s+(\d+\+?)$', lines[i])

            if match:
                # Collect any following lines as move description until next move or end
                desc_lines = []
                j = i + 1
                while j < len(lines) and not re.match(r'^[A-Z][a-zA-Z\s]+\s+\d+', lines[j]):
                    desc_lines.append(lines[j])
                    j += 1

                moves.append({
                    "name": match.group(1).strip(),
                    "damage": match.group(2).strip(),
                    "text": " ".join(desc_lines) if desc_lines else None
                })
                i = j
            else:
                i += 1

        return moves if moves else None