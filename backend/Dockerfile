FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y tesseract-ocr

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Preload embedding model to avoid first request delay
RUN python -c "import torchvision.models as models; models.resnet50(weights = models.ResNet50_Weights.DEFAULT)"

# Copy backend code
COPY app ./app

# Expose the port your FastAPI app uses
EXPOSE 7860

# Docker health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]