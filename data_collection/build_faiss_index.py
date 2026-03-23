import os
import json
import numpy as np
import faiss
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image

# --------------------------------
# ----- CONFIG -------------------
# --------------------------------

IMAGES_DIR = "./data_collection/images"
METADATA_PATH = "./data_collection/metadata.json"
INDEX_OUTPUT = "./backend/app/index/faiss_index.bin"
METADATA_OUTPUT = "./backend/app/index/metadata.json"



# --------------------------------
# ----- LOAD MODEL ---------------
# --------------------------------

# Loads the resnet model (without the classificatrion part) required for feature extraction
def load_model():
    model = models.resnet50(pretrained=True)

    # Remove the final classification layer, only want the embedding not the class
    model = torch.nn.Sequential(*list(model.children())[:-1])
    model.eval()

    return model



# --------------------------------
# ----- PREPROCESS IMAGE ---------
# --------------------------------

# Reshape the images to a standardized size
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# Function to get pokemon card image embeddings
def get_embedding(model, image_path):
    # convert to RGB
    image = Image.open(image_path).convert("RGB")
    # Unsqueeze image tensor
    tensor = transform(image).unsqueeze(0)

    # Get image embedding
    with torch.no_grad():
        embedding = model(tensor)

    # Flatten to 1D vector
    return embedding.squeeze().numpy()



# --------------------------------
# ----- BUILD INDEX --------------
# --------------------------------

# Fnction to build mebdding index
def build_index():
    # Create the new embedddings file
    os.makedirs(os.path.dirname(INDEX_OUTPUT), exist_ok=True)

    # Load the metadata json file
    with open(METADATA_PATH, "r") as f:
        metadata = json.load(f)

    # Load the resnet model
    model = load_model()

    # Initialize empty list to store embeddings dna metadata
    embeddings = []
    valid_metadata = []

    # Loop through each entry in the metadata
    for card in metadata:
        # Get card id
        card_id = card.get("id")

        # Find the image path using the card id
        image_path = os.path.join(IMAGES_DIR, f"{card_id}.png")

        # Skip the card if the iomage file doesnt exist
        if not os.path.exists(image_path):
            print(f"Skipping {card_id} — image not found")
            continue

        # Attempt to get image embedding using the resnet model
        try:
            # Calcualte mebedding
            embedding = get_embedding(model, image_path)

            # Add embedding to the mebeddings list
            embeddings.append(embedding)

            # Add metadata to the valid_metadata list
            valid_metadata.append(card)

            # Success message
            print(f"Embedded: {card_id}")

        # Print error if the card can't be added
        except Exception as e:
            print(f"Failed: {card_id} — {e}")

    # Stack into matrix
    embeddings_matrix = np.array(embeddings).astype("float32")

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings_matrix)

    # Build flat index
    dim = embeddings_matrix.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings_matrix)

    # Save index and metadata
    faiss.write_index(index, INDEX_OUTPUT)
    with open(METADATA_OUTPUT, "w") as f:
        json.dump(valid_metadata, f, indent=2)

    print(f"\nDone. Index built with {index.ntotal} cards.")

build_index()

"""
STEPS TO RUN:

python ./data_collection/build_faiss_index.py

"""