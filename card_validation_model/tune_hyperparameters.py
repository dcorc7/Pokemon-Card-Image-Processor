import sys
import os

import torch
import torch.nn as nn
import torch.optim as optim

from card_validation_model.data_preprocessing import train_test_split
from card_validation_model.cnn_model import ConvNeuralNet


# --------------------------------
# ----- TUNE HYPERPARAMETERS -----
# --------------------------------

# Check for gpu
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Function to tune select hyperparameters
def tune_hyperparameters(training_dataloader, validation_dataloader, num_classes, epochs = 30, patience = 5):
    # Define the parameter grid for tuning
    
    """
    dropout_rates = [0.2, 0.5]
    learning_rates = [0.001, 0.01, 0.1]
    optimizers = ["adam", "sgd", "rmsprop"]
    """

    dropout_rates = [0.2, 0.5]
    learning_rates = [0.001]
    optimizers = ["adam"]

    # Initialize counter
    model_num = 1
    total_model_count = len(dropout_rates) * len(learning_rates) * len(optimizers)
    
    # Initialize training and validation loss lists for later plotting
    train_losses = []
    val_losses = []
    
    # Initialize best model, loss, and parameters
    best_params = {}
    
    # Loop through model hyperparameters
    for optimizer in optimizers:
        for dropout_rate in dropout_rates:
            for learning_rate in learning_rates:

                print(f"Model {model_num}/{total_model_count}: Optimizer - {optimizer} | Dropout Rate - {dropout_rate} | Learning_Rate - {learning_rate}\n")
                
                # Set model and optimizer
                model = ConvNeuralNet(num_classes, dropout_rate = dropout_rate).to(device)

                # Initialize best validation loss for the current model
                best_val_loss = float("inf")

                # Initialize the optmizer depending on the current model run
                if optimizer == "adam":
                    optimizer_choice = optim.Adam(model.parameters(), lr = learning_rate)
                elif optimizer == "rmsprop":
                        optimizer_choice = optim.RMSprop(model.parameters(), lr = learning_rate)  
                elif optimizer == "sgd":
                    optimizer_choice = optim.SGD(model.parameters(), lr = learning_rate, momentum = 0.9)
                else: 
                    continue
                

                cost = nn.CrossEntropyLoss()

                epochs_without_improvement = 0
                
                # Training loop through epochs
                for epoch in range(epochs):
                    model.train()
                    running_loss = 0.0

                    for i, (images, labels) in enumerate(training_dataloader):  
                        images = images.to(device)
                        labels = labels.to(device)
                        
                        # Forward pass
                        outputs = model(images)
                        loss = cost(outputs, labels)
                        
                        # Backward and optimize
                        optimizer_choice.zero_grad()
                        loss.backward()
                        optimizer_choice.step()

                        # Record the loss for the batch
                        running_loss += loss.item()

                    # Calculate the average training loss for the epoch
                    avg_train_loss = running_loss / len(training_dataloader)
                    train_losses.append(avg_train_loss)
                    
                    # Evaluate on validation set
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
                    print(f"Epoch {epoch + 1}/{epochs} | Training Loss: {round(avg_train_loss, 3)} | Val Loss: {round(avg_val_loss, 3)} | Prev Best Val Loss: {round(best_val_loss, 3)} | Patience #: {epochs_without_improvement}/{patience}")

                    # Early stopping check
                    if avg_val_loss < best_val_loss:
                        best_val_loss = avg_val_loss
                        epochs_without_improvement = 0

                        best_model_state = model.state_dict()
                        best_params = {"optimizer": optimizer,
                                    "dropout_rate": dropout_rate,
                                    "learning_rate": learning_rate}
                    else:
                        epochs_without_improvement += 1
                        if epochs_without_improvement > patience:
                            print(f"Early stopping triggered after {epoch+1} epochs.")
                            break

            print(f"Model {model_num}/{total_model_count} Best Validation Loss: {best_val_loss}\n")
            model_num += 1
                    
    best_model = ConvNeuralNet(num_classes, dropout_rate = best_params["dropout_rate"]).to(device)
    best_model.load_state_dict(best_model_state)
    
    return best_model, best_params




def main():
    print(f"Downloading and splitting dataset...")
    training_dataloader, testing_dataloader, num_classes = train_test_split()


    print(f"\nTuning hyperparameters...\n")
    best_model, best_params = tune_hyperparameters(
        training_dataloader,
        testing_dataloader,
        num_classes
    )

    # Create models directory if it does not exist
    model_dir = "./card_validation_model/models"
    os.makedirs(model_dir, exist_ok = True)

    # Save best model
    print(f"\nSaving best model...")
    model_path = os.path.join(model_dir, "best_model.pth")
    torch.save(best_model.state_dict(), model_path)

    # Save best hyperparameters
    print(f"\nSaving best parameters...")
    params_path = os.path.join(model_dir, "best_params.pth")
    torch.save(best_params, params_path)

    print(f"\nBest model saved to {model_path}")
    print(f"\nBest Model Parameters:\n"
        f"Optimizer - {best_params['optimizer']}\n "
        f"Dropout Rate - {best_params['dropout_rate']}\n "
        f"Learning Rate - {best_params['learning_rate']}")

if __name__ == "__main__":
    sys.exit(main())


"""
STEPS TO RUN:

python -m card_validation_model.tune_hyperparameters

"""