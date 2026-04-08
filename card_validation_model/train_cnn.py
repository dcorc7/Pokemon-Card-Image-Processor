import os
import sys

import torch
import torch.nn as nn
import torch.optim as optim

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

from card_validation_model.data_preprocessing import train_test_split
from card_validation_model.cnn_model import ConvNeuralNet



# ----------------------------
# ----- TRAIN BEST MODEL -----
# ----------------------------

# Attempt to find GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Function to train the model and return training/validation losses
def train_model(training_dataloader, validation_dataloader, num_classes, best_params, epochs = 30, patience = 5):
    # Extract best parameters
    optimizer_name = best_params["optimizer"]
    dropout_rate = best_params["dropout_rate"]
    learning_rate = best_params["learning_rate"]

    # Initialize the model with the best hyperparameters
    model = ConvNeuralNet(num_classes, dropout_rate = dropout_rate).to(device)

    # Initialize the optimizer
    if optimizer_name == "adam":
        optimizer = optim.Adam(model.parameters(), lr = learning_rate)
    elif optimizer_name == "rmsprop":
        optimizer = optim.RMSprop(model.parameters(), lr = learning_rate)
    elif optimizer_name == "sgd":
        optimizer = optim.SGD(model.parameters(), lr = learning_rate, momentum = 0.9)

    # Initialize loss function
    cost = nn.CrossEntropyLoss()

    # Initialize lists to track training and validation loss for each epoch
    train_losses = []
    val_losses = []

    epochs_without_improvement = 0
    best_val_loss = float("inf")

    # Training loop through epochs
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        # Training phase
        for i, (images, labels) in enumerate(training_dataloader):  
            images = images.to(device)
            labels = labels.to(device)

            # Forward pass
            outputs = model(images)
            loss = cost(outputs, labels)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        # Calculate the average training loss for the epoch
        avg_train_loss = running_loss / len(training_dataloader)
        train_losses.append(avg_train_loss)

        # Validation phase
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, labels in validation_dataloader:
                images = images.to(device)
                labels = labels.to(device)

                # Forward pass
                outputs = model(images)
                loss = cost(outputs, labels)
                val_loss += loss.item()

        avg_val_loss = val_loss / len(validation_dataloader)
        val_losses.append(avg_val_loss)

        # Print loss for each epoch
        print(f"Epoch {epoch + 1}/{epochs} | Training Loss: {round(avg_train_loss, 3)} | Val Loss: {round(avg_val_loss, 3)} | Prev Best Val Loss {round(best_val_loss, 3)} | Patience #: {epochs_without_improvement}/{patience}")

        # Early stopping check
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            epochs_without_improvement = 0
            best_model_state = model.state_dict()
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement > patience:
                print(f"Early stopping triggered after {epoch+1} epochs.")
                break

    print(f"Best Validation Loss: {best_val_loss}")

    best_model = ConvNeuralNet(num_classes, dropout_rate = best_params["dropout_rate"]).to(device)
    best_model.load_state_dict(best_model_state)

    return best_model, train_losses, val_losses




def main():
    print(f"Downloading and splitting dataset...")
    training_dataloader, testing_dataloader, num_classes = train_test_split()



    print(f"\nObtaining best model and its parameters...")
    model_dir = "./card_validation_model/models"

    params_path = os.path.join(model_dir, "best_params.pth")
    best_params = torch.load(params_path)

    print(f"\nBest Model Parameters:\n"
        f"Optimizer - {best_params['optimizer']}\n "
        f"Dropout Rate - {best_params['dropout_rate']}\n "
        f"Learning Rate - {best_params['learning_rate']}")



    print(f"\nTraining model...")
    best_model, train_losses, val_losses = train_model(training_dataloader, testing_dataloader, num_classes, best_params, epochs = 30)



    print(f"\nSaving trained model...")
    model_path = os.path.join(model_dir, "best_model.pth")
    torch.save(best_model.state_dict(), model_path)



    print(f"\nPlotting and saving training and validation curves...")
    plot_dir = "./card_validation_model/plots"
    os.makedirs(plot_dir, exist_ok = True)

    plot_path = os.path.join(plot_dir, "training_validation_loss.png")

    plt.figure(figsize = (8, 6))
    plt.plot(range(1, len(train_losses) + 1), train_losses, label = "Training Loss", marker = "o")
    plt.plot(range(1, len(val_losses) + 1), val_losses, label = "Validation Loss", marker = "o")

    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Training and Validation Losses")
    plt.legend()

    plt.savefig(plot_path)
    plt.close()

    print(f"\nPlot saved to {plot_path}\n")



if __name__ == "__main__":
    sys.exit(main())


""" 
STEPS TO RUN:

python -m card_validation_model.train_cnn


"""