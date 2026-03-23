import json
import os
import requests

def download_images(metadata_path="backend/app/index/metadata.json", output_dir="./data_collection/images"):
    #Make the images folder
    os.makedirs(output_dir, exist_ok=True)

    # Load the metadat.json file
    with open(metadata_path, "r") as f:
        cards = json.load(f)

    # Loo through all cards in json file
    for card in cards:
        # Get the card url and id
        image_url = card.get("image_url")
        card_id = card.get("id")

        # Skip the card if there is no image
        if not image_url or not card_id:
            continue

        # Use card id as filename ex). "base1-4.jpg"
        filename = os.path.join(output_dir, f"{card_id}.png")

        # Skip the image if it is already in the images folder
        if os.path.exists(filename):
            print(f"Skipping {card_id} — already downloaded")
            continue

        # Try to get the image
        try:
            response = requests.get(image_url, timeout=10)

            # Write the image to the images folder (f)
            with open(filename, "wb") as f:
                f.write(response.content)

                # Print success message
            print(f"Downloaded: {card_id}")

        # Show error message
        except Exception as e:
            print(f"Failed: {card_id} — {e}")

    # Print final message when done
    print("\nFinished downloading images.")

# Run the function
download_images()

"""
STEPS TO RUN:

python ./data_collection/download_card_images.py


"""