import os
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import random
import re


class RandomVerticalFlipWithLabel:
    """Randomly vertically flips an image with its label.

    Args:
            img (PIL.Image): The image to be transformed.
            label: The label associated with the image.

    Returns:
        Tuple: The (possibly) vertically flipped image and its label.
    """
    def __call__(self, img, label):
        if random.random() > 0.5:
            img = transforms.functional.vflip(img)
        return img, label


class RandomHorizontalFlipWithLabel:
    """Randomly horizontally flips an image with accordingly flipped label.

    Args:
            img (PIL.Image): The image to be transformed.
            label: The label associated with the image.

    Returns:
        Tuple: The (possibly) horizontally flipped image and its (possibly reversed) label.
    """
    def __call__(self, img, label):
        if random.random() > 0.5:
            img = transforms.functional.hflip(img)
            label = label[::-1]
        return img, label


class ChangeStreetColor:
    """Transforms grey areas in the image to brown.

    Args:
            img (PIL.Image): The image to be transformed.
            label: The label associated with the image.

    Returns:
        Tuple: The transformed image and its label.
    """
    def __init__(self):
        self.brown_color = (139, 69, 19)

    def __call__(self, image, label):
        image_np = np.array(image)

        # Define the grey color range.
        lower_grey = np.array([100, 100, 100])
        upper_grey = np.array([200, 200, 200])

        # Create a mask for grey areas.
        mask = np.all(image_np >= lower_grey, axis=-1) & np.all(image_np <= upper_grey, axis=-1)

        # Change grey areas to brown.
        image_np[mask] = self.brown_color

        image = Image.fromarray(image_np)

        return image, label


class ToTensorWithLabel:
    """Converts an image to a tensor.

    Args:
            img (PIL.Image): The image to be transformed.
            label: The label associated with the image.

    Returns:
        Tuple: The image tensor and its label.
    """
    def __call__(self, image, label):
        image = transforms.ToTensor()(image)
        return image, label


class ComposeTransformations:
    """Applies the composed transformations to the image and its label.

    Args:
            transformations (list): List of transformations to be composed.

    Returns:
        Tuple: The transformed image and its label.
    """
    def __init__(self, transformations):
        self.transformations = transformations

    def __call__(self, image, label):
        for transform in self.transformations:
            image, label = transform(image, label)
        return image, label


def visualize(dataset):
    # Visualize images from the dataset with labels.

    indices = np.random.choice(len(dataset), 30, replace=False)
    samples = [dataset[i] for i in indices]

    fig, axes = plt.subplots(5, 6, figsize=(15, 10))
    axes = axes.flatten()

    for ax, (img, label) in zip(axes, samples):
        ax.imshow(img)
        ax.set_title(label)
        ax.axis('off')

    plt.tight_layout()
    plt.show()


class CarDataset(Dataset):
    """Custom dataset for loading car images and their labels.

    Args:
        root (str): Root directory of the dataset.
        transform (callable, optional): Optional transformations to be applied on a sample.
    """

    def __init__(self, root, transform=None):
        self.root = root
        self.images_path = os.path.join(self.root, 'images')
        self.label_path = os.path.join(self.root, 'data_log.csv')
        self.labels = pd.read_csv(self.label_path, dtype={'image_filename': str, 'action': str})
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index):
        image_path = os.path.join(self.images_path, self.labels.iloc[index]['image_filename'])
        image = Image.open(image_path).convert("RGB")
        label = self.labels.iloc[index]['action']
        label = np.array(re.findall(r"[-+]?\d*\.\d+|\d+", label), dtype=float)

        if self.transform:
            image, label = self.transform(image, label)

        return image, label


if __name__ == '__main__':
    # Visualize original dataset.
    car_dataset = CarDataset(root='../../data', transform=None)
    visualize(car_dataset)

    # Visualize augmented dataset.
    augment1 = RandomHorizontalFlipWithLabel()
    augment2 = RandomVerticalFlipWithLabel()
    augment3 = ChangeStreetColor()
    to_tensor = ToTensorWithLabel()

    augmentations = ComposeTransformations([
        augment1,
        augment2,
        augment3
        # to_tensor
    ])

    car_dataset_augmented = CarDataset(root='../../data', transform=augmentations)
    visualize(car_dataset_augmented)