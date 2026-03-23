import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import numpy as np

class EmbeddingService:

    def __init__(self):
        print("Loading embedding model...")

        # Load pretrained ResNet50
        model = models.resnet50(pretrained=True)

        # Remove final classification layer
        self.model = torch.nn.Sequential(*list(model.children())[:-1])
        self.model.eval()

        # Preprocessing pipeline, must match what was used to build the index (in data_collection/build_faiss_index.py)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        print("Embedding model loaded.")

    def embed(self, image: Image.Image) -> np.ndarray:
        # Preprocess
        tensor = self.transform(image).unsqueeze(0)

        # Forward pass
        with torch.no_grad():
            embedding = self.model(tensor)

        # Flatten to 1D and normalize
        embedding = embedding.squeeze().numpy().astype("float32")
        embedding = embedding / np.linalg.norm(embedding)

        return embedding