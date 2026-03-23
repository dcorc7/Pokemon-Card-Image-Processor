import streamlit as st

def render_upload_section():
    uploaded_file = st.file_uploader(
        "Upload a Pokémon card image",
        type=["png", "jpg", "jpeg"],
        help="Supported formats: PNG, JPG, JPEG"
    )
    return uploaded_file