import requests
import os

#BACKEND_URL = "http://localhost:8000"
BACKEND_URL = os.getenv("BACKEND_URL", "https://dcorcoran-Pokemon_Card_Image_Processor_API.hf.space")

def predict(image_bytes: bytes, filename: str) -> dict:
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            files={"file": (filename, image_bytes, "image/png")}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to backend. Make sure it is running."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Backend error: {e}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def health_check() -> bool:
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout = 3)
        return response.status_code == 200
    except:
        return False