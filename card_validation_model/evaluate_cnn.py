import os
import sys

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

from card_validation_model.data_preprocessing import train_test_split
from card_validation_model.cnn_model import ConvNeuralNet



# -------------------------------
# ----- EVALUATE BEST MODEL -----
# -------------------------------

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def evaluate_model(testing_dataloader, model, class_names=None):
    # Initialize lists to store true and predicted labels
    all_preds = []
    all_labels = []

    correct = 0
    total = 0

    # Disable gradient calculation for testing set
    with torch.no_grad():
        for images, labels in testing_dataloader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy()) 
            
    # Print classification report
    print("Classification Report:\n")
    report = classification_report(all_labels, all_preds, target_names=class_names)
    print(report)

    # Optionally, compute and return confusion matrix
    conf_matrix = confusion_matrix(all_labels, all_preds)

    return all_labels, all_preds, conf_matrix



def main():
    print(f"Obtaining testing dataloader...")
    _, testing_dataloader, num_classes = train_test_split()



    print(f"\nObtaining trained model...")
    model_dir = "./card_validation_model/models"
    model_path = os.path.join(model_dir, "best_model.pth")

    params_path = os.path.join(model_dir, "best_params.pth")
    best_params = torch.load(params_path)
    dropout_rate = best_params['dropout_rate']
    
    # Initialize the model architecture
    model = ConvNeuralNet(num_classes, dropout_rate).to(device)

    # Load the saved weights
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()



    print(f"\nEvaluating model...")
    all_labels, all_preds, conf_matrix = evaluate_model(testing_dataloader, model)



    print(f"\nPlotting confusion matrix...")
    plot_dir = "./card_validation_model/plots"
    os.makedirs(plot_dir, exist_ok = True)

    plot_path = os.path.join(plot_dir, "confusion_matrix.png")

    # Plot confusion matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=range(num_classes))
    fig, ax = plt.subplots(figsize=(8, 6))
    disp.plot(ax=ax, cmap="Blues", colorbar=False, text_kw={"color": "black"})
    plt.title("Confusion Matrix")

    plt.savefig(plot_path)
    plt.close()

    print(f"\nConfusion matrix saved to {plot_path}\n")


if __name__ == "__main__":
    sys.exit(main())


"""
STEPS TO RUN:

python -m card_validation_model.evaluate_cnn


"""