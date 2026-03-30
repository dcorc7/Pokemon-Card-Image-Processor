from pydantic import BaseModel
from typing import Optional

# --------------------------------
# ----- SIMILAR CARD -------------
# --------------------------------

class SimilarCard(BaseModel):
    id: str
    name: str
    set: Optional[str] = None
    types: Optional[list[str]] = None
    rarity: Optional[str] = None
    image_url: Optional[str] = None
    score: float



# --------------------------------
# ----- MOVE ---------------------
# --------------------------------

class Move(BaseModel):
    name: str
    damage: Optional[str] = None
    text: Optional[str] = None



# --------------------------------
# ----- CARD RESPONSE ------------
# --------------------------------

class CardResponse(BaseModel):
    name: Optional[str] = None
    hp: Optional[str] = None
    types: Optional[list[str]] = None
    moves: Optional[list[Move]] = None
    length: Optional[str] = None
    weight: Optional[str] = None
    is_evolved: Optional[bool] = None
    similar_cards: list[SimilarCard] = []