import requests
import os
import requests

#BACKEND_URL = "http://localhost:8000"
BACKEND_URL = os.getenv("BACKEND_URL", "https://dcorcoran-pokemon-card-image-processor-api.hf.space")

def predict(image_bytes: bytes, filename: str) -> dict:
    """Send image to backend /predict endpoint with detailed error info"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            files={"file": (filename, image_bytes, "image/png")},
            timeout=60
        )
        # Raise HTTPError for 4xx/5xx responses
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        # Capture status code and backend response
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
        return {
            "error_type": "ConnectionError",
            "exception": str(conn_err)
        }
    except requests.exceptions.Timeout as timeout_err:
        return {
            "error_type": "Timeout",
            "exception": str(timeout_err)
        }
    except Exception as e:
        return {
            "error_type": "Unexpected",
            "exception": str(e)
        }


def health_check() -> bool:
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout = 3)
        return response.status_code == 200
    except:
        return False

