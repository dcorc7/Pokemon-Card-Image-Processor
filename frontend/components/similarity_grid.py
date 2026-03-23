import streamlit as st
import requests
from PIL import Image
import io

def render_similarity_grid(similar_cards: list):
    # Check if there are no similar cards returned
    if not similar_cards:
        st.info("No similar cards found.")
        return

    # Create however many columns as there are cards
    cols = st.columns(len(similar_cards))

    # Loop through list of similar cards
    for col, card in zip(cols, similar_cards):
        with col:
            # Load and display card image
            image_url = card.get("image_url")

            # Check if the card image url exists
            if image_url:
                # Attempt to get the image url and render the image
                try:
                    response = requests.get(image_url, timeout=5)
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, width="content")

                    # Write error message if image is unavailable
                except:
                    st.write("Image unavailable")

            # Display the card's name, ser, types, rarity, and similarity score
            st.header(f"**{card.get('name')}**")
            st.subheader(f"Set: {card.get('set') or 'Unknown'}")
            st.subheader(f"Types: {', '.join(card.get('types') or [])}")
            st.subheader(f"Rarity: {card.get('rarity') or 'Unknown'}")
            st.subheader(f"Similarity Score: {round(card.get('score', 0), 3)}")