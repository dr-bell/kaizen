import os
from pathlib import Path
from typing import Callable, Optional, Tuple, Union
from torch.utils.data.dataset import Subset, ConcatDataset

import torchvision
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets import STL10, ImageFolder
from kaizen.utils.datasets import DomainNetDataset
from sklearn.model_selection import train_test_split
from kaizen.utils.pretrain_dataloader import split_dataset, split_dataset_subset

def build_custom_pipeline():
    """Builds augmentation pipelines for custom data.
    If you want to do exoteric augmentations, you can just re-write this function.
    Needs to return a dict with the same structure.
    """

    pipeline = {
        "T_train": transforms.Compose(
            [
                transforms.RandomResizedCrop(size=224, scale=(0.08, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.228, 0.224, 0.225)),
            ]
        ),
        "T_val": transforms.Compose(
            [
                transforms.Resize(256),  # resize shorter
                transforms.CenterCrop(224),  # take center crop
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.228, 0.224, 0.225)),
            ]
        ),
    }
    return pipeline


def prepare_transforms(dataset: str) -> Tuple[nn.Module, nn.Module]:
    """Prepares pre-defined train and test transformation pipelines for some datasets.

    Args:
        dataset (str): dataset name.

    Returns:
        Tuple[nn.Module, nn.Module]: training and validation transformation pipelines.
    """

    cifar_pipeline = {
        "T_train": transforms.Compose(
            [
                transforms.RandomResizedCrop(size=32, scale=(0.08, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
            ]
        ),
        "T_val": transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
            ]
        ),
    }

    stl_pipeline = {
        "T_train": transforms.Compose(
            [
                transforms.RandomResizedCrop(size=96, scale=(0.08, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4823, 0.4466), (0.247, 0.243, 0.261)),
            ]
        ),
        "T_val": transforms.Compose(
            [
                transforms.Resize((96, 96)),
                transforms.ToTensor(),
                transforms.Normalize((0.4914, 0.4823, 0.4466), (0.247, 0.243, 0.261)),
            ]
        ),
    }

    imagenet_pipeline = {
        "T_train": transforms.Compose(
            [
                transforms.RandomResizedCrop(size=224, scale=(0.08, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.228, 0.224, 0.225)),
            ]
        ),
        "T_val": transforms.Compose(
            [
                transforms.Resize(256),  # resize shorter
                transforms.CenterCrop(224),  # take center crop
                transforms.ToTensor(),
                transforms.Normalize(mean=(0.485, 0.456, 0.406), std=(0.228, 0.224, 0.225)),
            ]
        ),
    }

    custom_pipeline = build_custom_pipeline()

    pipelines = {
        "cifar10": cifar_pipeline,
        "cifar100": cifar_pipeline,
        "stl10": stl_pipeline,
        "imagenet100": imagenet_pipeline,
        "imagenet": imagenet_pipeline,
        "domainnet": imagenet_pipeline,
        "custom": custom_pipeline,
    }

    assert dataset in pipelines

    pipeline = pipelines[dataset]
    T_train = pipeline["T_train"]
    T_val = pipeline["T_val"]

    return T_train, T_val


def prepare_datasets(
    dataset: str,
    T_train: Callable,
    T_val: Callable,
    data_dir: Optional[Union[str, Path]] = None,
    train_dir: Optional[Union[str, Path]] = None,
    val_dir: Optional[Union[str, Path]] = None,
    train_domain: Optional[str] = None,
) -> Tuple[Dataset, Dataset]:
    """Prepares train and val datasets.

    Args:
        dataset (str): dataset name.
        T_train (Callable): pipeline of transformations for training dataset.
        T_val (Callable): pipeline of transformations for validation dataset.
        data_dir Optional[Union[str, Path]]: path where to download/locate the dataset.
        train_dir Optional[Union[str, Path]]: subpath where the training data is located.
        val_dir Optional[Union[str, Path]]: subpath where the validation data is located.

    Returns:
        Tuple[Dataset, Dataset]: training dataset and validation dataset.
    """

    if data_dir is None:
        sandbox_dir = Path(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        data_dir = sandbox_dir / "datasets"
    else:
        data_dir = Path(data_dir)

    if train_dir is None:
        train_dir = Path(f"{dataset}/train")
    else:
        train_dir = Path(train_dir)

    if val_dir is None:
        val_dir = Path(f"{dataset}/val")
    else:
        val_dir = Path(val_dir)

    assert dataset in [
        "cifar10",
        "cifar100",
        "stl10",
        "imagenet",
        "imagenet100",
        "domainnet",
        "custom",
    ]

    if dataset in ["cifar10", "cifar100"]:
        DatasetClass = vars(torchvision.datasets)[dataset.upper()]
        train_dataset = DatasetClass(
            data_dir / train_dir,
            train=True,
            download=True,
            transform=T_train,
        )

        val_dataset = DatasetClass(
            data_dir / val_dir,
            train=False,
            download=True,
            transform=T_val,
        )

    elif dataset == "stl10":
        train_dataset = STL10(
            data_dir / train_dir,
            split="train",
            download=True,
            transform=T_train,
        )
        val_dataset = STL10(
            data_dir / val_dir,
            split="test",
            download=True,
            transform=T_val,
        )

    elif dataset in ["imagenet", "imagenet100", "custom"]:
        train_dir = data_dir / train_dir
        val_dir = data_dir / val_dir

        train_dataset = ImageFolder(train_dir, T_train)
        val_dataset = ImageFolder(val_dir, T_val)

    elif dataset == "domainnet":
        train_dataset = DomainNetDataset(
            data_root=data_dir,
            image_list_root=data_dir,
            domain_names=train_domain,
            split="train",
            transform=T_train,
        )
        val_dataset = DomainNetDataset(
            data_root=data_dir,
            image_list_root=data_dir,
            domain_names=None,
            split="test",
            transform=T_val,
            return_domain=True,
        )

    return train_dataset, val_dataset


def prepare_dataloaders(
    train_dataset: Dataset, val_dataset: Dataset, batch_size: int = 64, num_workers: int = 4
) -> Tuple[DataLoader, DataLoader]:
    """Wraps a train and a validation dataset with a DataLoader.

    Args:
        train_dataset (Dataset): object containing training data.
        val_dataset (Dataset): object containing validation data.
        batch_size (int): batch size.
        num_workers (int): number of parallel workers.
    Returns:
        Tuple[DataLoader, DataLoader]: training dataloader and validation dataloader.
    """

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=False,
    )
    return train_loader, val_loader


def prepare_data(
    dataset: str,
    data_dir: Optional[Union[str, Path]] = None,
    train_dir: Optional[Union[str, Path]] = None,
    val_dir: Optional[Union[str, Path]] = None,
    batch_size: int = 64,
    num_workers: int = 4,
    train_domain: str = None,
    semi_supervised: float = None,
    training_data_source: str = "all_tasks",
    training_num_tasks: int = None,
    training_tasks = None,
    training_task_idx = None,
    training_split_strategy: str = None,
    training_split_seed: int = None,
    replay: bool = False,
    replay_proportion: float = 0.,
    replay_memory_bank_size: int = None
) -> Tuple[DataLoader, DataLoader]:
    """Prepares transformations, creates dataset objects and wraps them in dataloaders.

    Args:
        dataset (str): dataset name.
        data_dir (Optional[Union[str, Path]], optional): path where to download/locate the dataset.
            Defaults to None.
        train_dir (Optional[Union[str, Path]], optional): subpath where the
            training data is located. Defaults to None.
        val_dir (Optional[Union[str, Path]], optional): subpath where the
            validation data is located. Defaults to None.
        batch_size (int, optional): batch size. Defaults to 64.
        num_workers (int, optional): number of parallel workers. Defaults to 4.

    Returns:
        Tuple[DataLoader, DataLoader]: prepared training and validation dataloader;.
    """

    T_train, T_val = prepare_transforms(dataset)
    train_dataset, val_dataset = prepare_datasets(
        dataset,
        T_train,
        T_val,
        data_dir=data_dir,
        train_dir=train_dir,
        val_dir=val_dir,
        train_domain=train_domain,
    )

    if training_data_source == "all_tasks":
        split_train_dataset = train_dataset
    elif training_data_source == "current_task":
        split_train_dataset, _ = split_dataset(
            train_dataset,
            tasks=training_tasks,
            task_idx=training_task_idx,
            num_tasks=training_num_tasks,
            split_strategy=training_split_strategy,
            split_seed=training_split_seed
        )
    elif training_data_source == "seen_tasks":
        task_idxs = [i for i in range(training_task_idx + 1)]
        split_train_dataset, _ = split_dataset(
            train_dataset,
            tasks=training_tasks,
            task_idx=task_idxs,
            num_tasks=training_num_tasks,
            split_strategy=training_split_strategy,
            split_seed=training_split_seed
        )
    
    if training_data_source == "all_tasks" and replay:
        raise Exception("replay is not supported when training_data_source is set to 'all_tasks'")
    elif replay:
        replay_dataset = split_dataset_subset(
            train_dataset,
            tasks=training_tasks,
            replay_task_idxs=[i for i in range(training_task_idx)],
            num_tasks=training_num_tasks,
            split_strategy=training_split_strategy,
            split_seed=training_split_seed,
            proportion=replay_proportion,
            num_samples=replay_memory_bank_size
        )
        if replay_dataset is not None:
            split_train_dataset = ConcatDataset([split_train_dataset, replay_dataset])
    print(len(split_train_dataset), len(split_train_dataset))
    if semi_supervised is not None:
        idxs = train_test_split(
            range(len(split_train_dataset)),
            train_size=semi_supervised,
            stratify=split_train_dataset.targets,
            random_state=training_split_seed,
        )[0]
        split_train_dataset = Subset(split_train_dataset, idxs)

    train_loader, val_loader = prepare_dataloaders(
        split_train_dataset,
        val_dataset,
        batch_size=batch_size,
        num_workers=num_workers,
    )
    return train_loader, val_loader
