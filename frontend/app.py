import streamlit as st
from PIL import Image
import io
import requests
import os

from api_client import predict, health_check, get_all_cards
from components.upload_section import render_upload_section
from components.display_structured_data import render_card_data
from components.similarity_grid import render_similarity_grid

BACKEND_URL = os.getenv("BACKEND_URL", "https://dcorcoran-pokemon-card-image-processor-api.hf.space")

# --------------------------------
# ----- PAGE CONFIG --------------
# --------------------------------

st.set_page_config(
    page_title="Pokemon Card Image Processor",
    page_icon="🃏",
    layout="wide"
)

# --------------------------------
# ----- HEADER -------------------
# --------------------------------

st.title("Pokemon Card Image Processor")
st.badge("Upload a Pokémon card image to extract its data and find similar cards.", color = "blue")


# --------------------------------
# ----- BACKEND STATUS -----------
# --------------------------------

if not health_check():
    st.error("⚠️ Backend is not reachable. Make sure the FastAPI Space is running.")
    st.stop()


# --------------------------------
# ----- UPLOAD -------------------
# --------------------------------

tab1, tab2 = st.tabs(["Upload Pokemon Card", "Card Database"])


with tab1:
    uploaded_file = render_upload_section()

    # Check if file was uploaded
    if uploaded_file:
        # Reading Pokemon Card
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))

        # Separate page into two columns
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(image, width="content")

        with col2:
            with st.spinner("Analyzing card..."):
                result = predict(image_bytes, uploaded_file.name)

            # Check if there was an error in the predict endpoint
            if "error_type" in result:
                st.error(f"Error ({result['error_type']}): {result.get('backend_response') or result.get('exception')}")

            # Display the rendered card data if there is no error
            else:
                render_card_data(result)

        # Add a divider between the uploaded card and the similar cards
        st.divider()

        # Add header for similar cards
        st.header("Similar Cards")

        if "error" not in result:
            render_similarity_grid(result.get("similar_cards", []))

with tab2: 
    st.header("Card Database")
    st.subheader("Showing a sample of available cards in the database.")

    with st.spinner("Loading cards..."):
        try:
            cards = get_all_cards()

        except Exception as e:
            st.error(f"Could not load card database: {e}")
            cards = []

    if cards:
        cols_per_row = 5
        rows = [cards[i:i+cols_per_row] for i in range(0, len(cards), cols_per_row)]

        for row in rows:
            cols = st.columns(cols_per_row)
            for col, card in zip(cols, row):
                with col:
                    if card.get("image_url"):
                        st.image(card["image_url"], width="content")
                    else:
                        st.markdown("🃏")
                    st.caption(card.get("name", "Unknown"))
    else:
        st.info("No cards to display.")