from pokemontcgsdk import Card, Set
import json
import os
import requests

# Function to collect Pokemon cards from pokemontcgsdk API
def get_cards(output_path="./data_collection/metadata.json"):
    all_cards = []
    
    # Option to collect every card
    #cards = Card.all()

    # Only original base1 cards
    #cards = Card.where(q="set.id:base1") 

    # Only original base 1-6 cards
    cards = Card.where(q="set.series:Base")

    
    # Loop through every card to collect/store relevant information in json file
    for card in cards:
        card_data = {
            "id": card.id,
            "name": card.name,
            "hp": getattr(card, "hp", None),
            "types": getattr(card, "types", None),
            "moves": [
                {
                    "name": move.name,
                    "damage": move.damage,
                    "text": move.text
                }
                for move in (card.attacks or [])
            ],
            "rarity": getattr(card, "rarity", None),
            "set": card.set.name if card.set else None,
            "image_url": card.images.large if card.images else None,
        }

        # Add current card data to the list
        all_cards.append(card_data)

        # Print validation message
        print(f"Fetched: {card.name} ({card.id})")
    
    # Save all_cards list as json file
    with open(output_path, "w") as f:
        json.dump(all_cards, f, indent=2)
    
    # Print validation message
    print(f"\nDone. {len(all_cards)} cards saved to {output_path}")

# Run the function
get_cards()

"""
STEPS TO RUN:

python ./data_collection/data_collection.py

"""