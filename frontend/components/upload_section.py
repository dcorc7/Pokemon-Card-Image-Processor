import streamlit as st

def render_upload_section(key="file_uploader"):
    uploaded_file = st.file_uploader(
        "Upload a Pokémon card image",
        type=["png", "jpg", "jpeg"],
        help="Supported formats: PNG, JPG, JPEG",
        key=key,
        label_visibility="collapsed"
    )
    return uploaded_file