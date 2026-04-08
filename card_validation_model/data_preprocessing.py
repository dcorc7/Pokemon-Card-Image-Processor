import torch
import torchvision
import torchvision.transforms as transforms


# ---------------------------------
# ----- TRAIN TEST SPLIT DATA -----
# ---------------------------------

def train_test_split():
    # Load CIFAR-10 dataset
    transform = transforms.Compose([transforms.ToTensor(), 
                                    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    # Load Training Set
    training_set = torchvision.datasets.CIFAR10(root = "./card_validation_model/data", 
                                            train = True, 
                                            download = True, 
                                            transform = transform)

    # Load Testing set
    testing_set = torchvision.datasets.CIFAR10(root = "./card_validation_model/data", 
                                            train = False, 
                                            download = True, 
                                            transform = transform)

    # Define dataloaders
    training_dataloader = torch.utils.data.DataLoader(training_set, batch_size = 64, shuffle = True)
    testing_dataloader = torch.utils.data.DataLoader(testing_set, batch_size = 64, shuffle = False)

    # Define number of classes
    num_classes = 10

    return training_dataloader, testing_dataloader, num_classes