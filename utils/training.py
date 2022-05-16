"""libary for training functions and modularity"""
import torch
from torch import nn
import numpy as np
from torch_geometric.data import InMemoryDataset
from torch_geometric.loader import DataLoader

from utils.datasets import gen_expr_data
from .models import CustomCrossEntropy


def get_dataloader(dataset: InMemoryDataset, batch_size: int) -> DataLoader:
    """
    Helper function to get a dataloader for a given dataset
    
    Parameters:
        dataset: the dataset for which a dataloader should be created
        batch_size: the batch size of the dataloader

    Returns:
        A dataloader for the given dataset
    """
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def train_model(model: torch.nn.Module,
                dataset: InMemoryDataset,
                epochs: int,
                batch_size: int,
                device: str) -> None:
    """
    Helper function to train a given model on a given datasetmodel
    
    Parameters:
        model: the model which should be trained
        dataset: the dataset on which the model should be trained
        epochs: number of training epochs
        batch_size: batch size of the dataloader
        device: device string
    
    Returns:
        None

    """
    print("[[ Network Architecture ]]")
    print(model)

    #data_loader = get_dataloader(dataset, batch_size=batch_size)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.CrossEntropyLoss()

    print("\n[[ Training ]]")

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        data = next(gen_expr_data(batch_size)).to(device)
        prediction = model(data.x, data.edge_index)
        loss = loss_fn(prediction[data.train_mask], data.y[data.train_mask])
 
        # Backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # accuray calculation
        running_loss += loss.item()
        print(f"Epoch: {epoch} | Loss: {loss.item()}", end="\r")


    print("\n\n[[ Testing ]]")
    model.eval()
    true_preds = 0
    total_preds = 0

    with torch.no_grad():
        for _ in range(10):
            total_preds += 1
            data = next(gen_expr_data(1)).to(device)
            data = data.to(device)
            prediction = model(data.x, data.edge_index)
            prediced_op = prediction[data.test_mask].argmax()
            true_op = int(data.y[data.test_mask].item())

            if prediced_op == true_op:
                true_preds += 1
                print(f"✓ correct -> Pred: {prediced_op} | Real: {true_op}")
            else:
                print(f"× incorrect -> Pred: {prediced_op} | Real: {true_op}")


    print(f"\n[ test results ]\n"
          f"{true_preds}/{total_preds} correct predictions\n"
          f"{np.round((true_preds/total_preds)*100, 2)}% accuracy\n")
