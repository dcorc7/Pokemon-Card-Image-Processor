import streamlit as st
from PIL import Image
import io
import requests
import os

from api_client import predict, health_check
from components.upload_section import render_upload_section
from components.display_structured_data import render_card_data
from components.similarity_grid import render_similarity_grid

# --------------------------------
# ----- PAGE CONFIG --------------
# --------------------------------

st.set_page_config(
    page_title="Pokemon Card Image Processor",
    page_icon="🃏",
    layout="wide"
)

BACKEND_URL = os.getenv("BACKEND_URL", "https://dcorcoran-Pokemon_Card_Image_Processor_API.hf.space")

# --------------------------------
# ----- HEADER -------------------
# --------------------------------

st.title("🃏 Pokemon Card Image Processor")
st.caption("Upload a Pokémon card image to extract its data and find similar cards.")



# --------------------------------
# ----- BACKEND STATUS -----------
# --------------------------------

if not health_check():
    st.error("⚠️ Backend is not reachable. Make sure the FastAPI Space is running.")
    st.stop()



# --------------------------------
# ----- UPLOAD -------------------
# --------------------------------

uploaded_file = render_upload_section()

if uploaded_file:
    image_bytes = uploaded_file.read()
    image = Image.open(io.BytesIO(image_bytes))

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Uploaded Card")
        st.image(image, use_column_width=True)

    with col2:
        with st.spinner("Analyzing card..."):
            result = predict(image_bytes, uploaded_file.name)

        if "error" in result:
            st.error(result["error"])
        else:
            render_card_data(result)

    st.divider()
    st.subheader("Similar Cards")

    if "error" not in result:
        render_similarity_grid(result.get("similar_cards", []))