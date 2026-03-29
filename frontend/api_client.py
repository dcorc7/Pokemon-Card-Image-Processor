import requests
import os
import requests
import base64
import streamlit as st
import io
from PIL import Image

#BACKEND_URL = "http://localhost:8000"
BACKEND_URL = os.getenv("BACKEND_URL", "https://dcorcoran-pokemon-card-image-processor-api.hf.space")


#headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}


def predict(image_bytes: bytes, filename: str) -> dict:
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            files={"file": (filename, image_bytes, "image/jpeg")},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        try:
            error_content = response.json()
        except Exception:
            error_content = response.text
        return {
            "error_type": "HTTPError",
            "status_code": response.status_code,
            "backend_response": error_content,
            "exception": str(http_err)
        }
    except requests.exceptions.ConnectionError as conn_err:
        return {"error_type": "ConnectionError", "exception": str(conn_err)}
    except requests.exceptions.Timeout as timeout_err:
        return {"error_type": "Timeout", "exception": str(timeout_err)}
    except Exception as e:
        return {"error_type": "Unexpected", "exception": str(e)}


def health_check() -> bool:
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout = 3)
        return response.status_code == 200
    except:
        return False


@st.cache_data(ttl=300) 
def get_all_cards(limit: int = 100) -> list:
    try:
        response = requests.get(f"{BACKEND_URL}/cards", params={"limit": limit}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise  


def visualize_regions(image_bytes: bytes, filename: str) -> Image.Image | None:
    try:
        response = requests.post(
            f"{BACKEND_URL}/visualize",
            files={"file": (filename, image_bytes, "image/jpeg")},
            timeout=30
        )
        response.raise_for_status()

        # Decode the returned PNG bytes into a Pillow Image
        return Image.open(io.BytesIO(response.content))

    except requests.exceptions.HTTPError as http_err:
        st.error(f"Visualization failed (HTTP {response.status_code}): {http_err}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        st.error(f"Connection error during visualization: {conn_err}")
        return None
    except requests.exceptions.Timeout:
        st.error("Visualization request timed out.")
        return None
    except Exception as e:
        st.error(f"Unexpected error during visualization: {e}")
        return None