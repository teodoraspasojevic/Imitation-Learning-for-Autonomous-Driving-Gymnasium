from data import CarDataset, ResizeWithLabels, RandomHorizontalFlipWithLabel, RandomVerticalFlipWithLabel, ChangeStreetColor, ToTensorWithLabel, ComposeTransformations
from model import Model, to_device, train_model, test_model, plot_history
from torch.utils.data import DataLoader, Subset
import torch.nn as nn
import torch.optim as optim

transforms = ComposeTransformations([
    ResizeWithLabels(),
    ToTensorWithLabel()
])

car_dataset = CarDataset(root='../../data', transform=transforms)

train_size = int(0.6 * len(car_dataset))
val_size = int(0.2 * len(car_dataset))
test_size = len(car_dataset) - train_size - val_size

train_indices = list(range(train_size))
val_indices = list(range(train_size, train_size + val_size))
test_indices = list(range(train_size + val_size, len(car_dataset)))

train_dataset = Subset(car_dataset, train_indices)
val_dataset = Subset(car_dataset, val_indices)
test_dataset = Subset(car_dataset, test_indices)

train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(dataset=val_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=64, shuffle=False)

model = Model()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)

model, history, best_epoch = train_model(model, train_loader, val_loader, criterion, optimizer, epochs=10)

plot_history(history, best_epoch)

test_model(model, test_loader)

