import streamlit as st
import requests
from PIL import Image
import io

def render_similarity_grid(similar_cards: list):
    if not similar_cards:
        st.info("No similar cards found.")
        return

    cols = st.columns(len(similar_cards))

    for col, card in zip(cols, similar_cards):
        with col:
            # Load and display card image
            image_url = card.get("image_url")
            if image_url:
                try:
                    response = requests.get(image_url, timeout=5)
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, use_column_width=True)
                except:
                    st.write("Image unavailable")

            st.markdown(f"**{card.get('name')}**")
            st.caption(f"Set: {card.get('set') or 'Unknown'}")
            st.caption(f"Types: {', '.join(card.get('types') or [])}")
            st.caption(f"Rarity: {card.get('rarity') or 'Unknown'}")
            st.caption(f"Score: {round(card.get('score', 0), 3)}")