import pytesseract
import re
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np
import sys
import os


class OCRService:

    def __init__(self):
        # On Windows, use the TESSERACT_PATH env var if set, otherwise fall back to the default installation path
        if sys.platform.startswith("win"):
            pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH", "C:/Program Files/Tesseract-OCR/tesseract.exe")

        # Look for tessaract OCR service in usr/bin folder
        else:
            pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    # Function to preprocess image to desired format
    def _preprocess(self, region: Image.Image, scale: int = 3) -> Image.Image:
        # Incrase size of image so that OCR performs better
        region = region.resize(
            (region.width * scale, region.height * scale),
            Image.LANCZOS
        )

        # Convert iamge to grayscale
        region = region.convert("L")

        # Increase contrast of image
        region = ImageEnhance.Contrast(region).enhance(2.0)

        # Threshold to black/white
        region = region.point(lambda x: 0 if x < 140 else 255, "1").convert("L")

        return region
    

    # Function to check top-left corner for 'STAGE' text indicating an evolved Pokémon.
    def _is_evolved(self, image: Image.Image) -> bool:
        # Get size of the image
        w, h = image.size

        # Crop to the top left of the card
        top_left = image.crop((0.07 * w, 0.04 * h, 0.19 * w, 0.07 * h))

        # Preprocesss the cropped region
        top_left = self._preprocess(top_left, scale=3)

        # Uses PSM 6 (block of text mode)
        text = pytesseract.image_to_string(top_left, config="--psm 6 --oem 3")
        print("IS_EVOLVED OCR RAW:", repr(text))

        if re.search(r'stage[\s.\-_]*[12|I]', text, re.IGNORECASE):
            return True

        # Fallback: check for "Evolves from" text which only appears on evolved cards
        evolved_region = image.crop((0, 0.02 * h, 0.80 * w, 0.07 * h))
        evolved_region = self._preprocess(evolved_region, scale=3)
        evolved_text = pytesseract.image_to_string(evolved_region, config="--psm 6 --oem 3")
        print("EVOLVES_FROM OCR RAW:", repr(evolved_text))  # remove once working

        if re.search(r'evolves\s+from', evolved_text, re.IGNORECASE):
            return True

        return False


    # Fuction to return all wanted card field texts
    def extract(self, image: Image.Image) -> dict:
        # Initialize width and height of image
        w, h = image.size

        # Detect whether this is an evolved card (Stage 1 or Stage 2)
        evolved = self._is_evolved(image)

        # Name field — skip "Basic Pokemon" line at very top, just grab name row
        # Evolved cards have an evolution picture in the top-left (~0–25% width), so the name starts further right. Basic cards start near the left edge.
        if evolved:
            name_region = image.crop((0.23 * w, 0.06 * h, 0.62 * w, 0.11 * h))
        else:
            name_region = image.crop((0.07 * w, 0.06 * h, 0.62 * w, 0.11 * h))

        # HP field — top right, large number + "HP" text
        hp_region = image.crop((0.64 * w, 0.06 * h, 0.85 * w, 0.11 * h))

        # Length/Weight —  bar sits just above the moves section
        length_weight_region = image.crop((0.125 * w, 0.53 * h, 0.86 * w, 0.57 * h))

        # Moves field — middle to lower section
        moves_region = image.crop((0.02 * w, 0.52 * h, 0.98 * w, 0.88 * h))

        # Full image for type detection
        full_text = pytesseract.image_to_string(image)

        # Return wanted fields using sepcific field extraction functions
        return {
            "name": self._extract_name(name_region),
            "hp": self._extract_hp(hp_region),
            "types": self._extract_types(full_text),
            "moves": self._extract_moves(moves_region),
            "length": self._extract_length(length_weight_region),
            "weight": self._extract_weight(length_weight_region),
            "is_evolved": evolved
        }


    # Function to get pokemon name
    def _extract_name(self, region: Image.Image) -> str | None:
        # prepocess region of card
        region = self._preprocess(region, scale=3)

        # Uses PM7 to get text (single line mode)
        text = pytesseract.image_to_string(region, config="--psm 7 --oem 3").strip()

        # Clean up noise — keep only lines that look like a name
        lines = [l.strip() for l in text.splitlines() if l.strip()]

        # Loop through all detected lines
        for line in lines:
            # Skip lines that are clearly not a name - looks for lines that start with a capital letter followed by lowercase letters and are under 30 characters
            if re.search(r'[A-Z][a-z]+', line) and len(line) < 30:
                return line
            
        return text if text else None


    # Function to get pokemon hp
    def _extract_hp(self, region: Image.Image) -> str | None:
        # prepocess region of card
        region = self._preprocess(region, scale=3)

        # Uses PSM 6 (block of text mode)
        text = pytesseract.image_to_string(region, config="--psm 6 --oem 3")

        # Look for a number near "HP"
        # First looks for a number adjacent to the letters "HP" in either order 
        match = re.search(r'(\d+)\s*HP|HP\s*(\d+)', text, re.IGNORECASE)

        if match:
            return match.group(1) or match.group(2)
        
        # Fallback: grabbing any standalone 2–3 digit number if the "HP" label wasn't recognized
        match = re.search(r'\b(\d{2,3})\b', text)

        return match.group(1) if match else None


    # Function to get pokemon types
    def _extract_types(self, text: str) -> list[str] | None:
        # All pokemon types for keywrods extraction
        types = [
            "Fire", "Water", "Grass", "Electric", "Psychic",
            "Fighting", "Darkness", "Metal", "Colorless",
            "Dragon", "Fairy", "Lightning", "Normal"
        ]

        # Checks whether any known Pokémon type name appears anywhere in the OCR output
        found = [t for t in types if t.lower() in text.lower()]
        return found if found else None


    # Extract length
    def _extract_length(self, region: Image.Image) -> str | None:
        # Preprocess the length region
        region = self._preprocess(region, scale=3)

        # Uses PSM 6 (block of text mode)
        text = pytesseract.image_to_string(region, config="--psm 6 --oem 3")

        # Find length match through regex patterns (after Length)
        match = re.search(r"Length[:\s]+([0-9]+'\s*[0-9]+\")", text, re.IGNORECASE)

        # Return a match or None
        return match.group(1).strip() if match else None


    # Extract weight
    def _extract_weight(self, region: Image.Image) -> str | None:
        # Preprocess the weight region
        region = self._preprocess(region, scale=3)

        # Uses PSM 6 (block of text mode)
        text = pytesseract.image_to_string(region, config="--psm 6 --oem 3")
        print("WEIGHT OCR RAW:", repr(text))

        # Primary: match "Weight: 76." with flexible spacing/punctuation
        match = re.search(r"Weight[:\s]+([\d.]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Fallback 1: find a number followed by lbs anywhere in the line
        match = re.search(r"([\d.]+)\s*lbs?\.?", text, re.IGNORECASE)
        if match:
            return match.group(1).strip() + " lbs"

        # Fallback 2: OCR sometimes reads "lbs" as "Ibs" (capital i) or "1bs"
        match = re.search(r"([\d.]+)\s*[Il1]bs?\.?", text)
        if match:
            return match.group(1).strip() + " lbs"

        return None
    

    # Function to get pokemon moves
    def _extract_moves(self, region: Image.Image) -> list[dict] | None:
        # prepocess region of card
        region = self._preprocess(region, scale=2)

        # Uses PSM 6 (block of text mode)
        text = pytesseract.image_to_string(region, config="--psm 6 --oem 3")

        #  Returns all dtected lines
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Empty list to store detected moves
        moves = []

        # Index starting at 0
        i = 0

        # Loop through all dtected lines
        while i < len(lines):
            # Match: "MoveName 10" or "MoveName 10+" or "MoveName" alone on a line (0 damage moves)
            match = re.match(r'^([A-Z][a-zA-Z\s]{2,25}?)\s{2,}(\d+\+?)$', lines[i])
            if not match:
                # Try looser match for lines like "Psychic                    10+"
                match = re.match(r'^([A-Z][a-zA-Z]+)\s+(\d+\+?)$', lines[i])

            # Separate move into names, damage, and etxt if a move is detected
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

            # Increase index to inspect to the next move
            else:
                i += 1

        return moves if moves else None
    

    def visualize_regions(self, image: Image.Image) -> Image.Image: 
        """Draw colored boxes over each OCR crop region and return the annotated image."""
        from PIL import ImageDraw, ImageFont
        
        w, h = image.size
        evolved = self._is_evolved(image)
        vis = image.copy()
        draw = ImageDraw.Draw(vis)

        regions = {
            "Name":           (0.23 * w if evolved else 0.07 * w, 0.06 * h, 0.62 * w, 0.11 * h),
            "HP":             (0.64 * w, 0.06 * h, 0.85 * w, 0.11 * h),
            "Length/Weight":  (0.125 * w, 0.53 * h, 0.86 * w, 0.57 * h),
            "Moves":          (0.02 * w, 0.57 * h, 0.98 * w, 0.88 * h),
            "is_evolved":     (0.07 * w, 0.04 * h, 0.19 * w, 0.07 * h),
            "evolves_from": (0, 0.02 * h, 0.80 * w, 0.07 * h)
        }
        colors = {
            "Name":          "red",
            "HP":            "blue",
            "Length/Weight": "orange",
            "Moves":         "green",
            "is_evolved":    "black",
            "evolves_from":  "white"
        }

        for label, box in regions.items():
            draw.rectangle(box, outline=colors[label], width=3)
            draw.text((box[0] + 4, box[1] + 4), label, fill=colors[label])

        return vis