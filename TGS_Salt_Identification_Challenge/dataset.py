import os
from glob import glob
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision.transforms import Compose, Scale, ToTensor, Normalize
from PIL import Image
import cv2

class ToLabel:
    def __call__(self, image):
        return torch.from_numpy(np.array(image)).long().unsqueeze(0)

class Relabel:
    def __init__(self, olabel, nlabel):
        self.olabel = olabel
        self.nlabel = nlabel
    def __call__(self, tensor):
        assert isinstance(tensor, torch.LongTensor), 'tensor type shoule be long'
        tensor[(tensor <= 10)] = 0
        tensor[tensor>10] = self.nlabel
        return tensor

image_transform = Compose([
    Scale(128),
    ToTensor(),
    Normalize([.485, .456, .406], [.229, .224, .225]),
])

label_transform = Compose([
    Scale(128),
    ToLabel(),
    Relabel(255, 1),
])

class TGSDS(Dataset):
    def __init__(self, root, input_trans=None, target_trans=None):
        self.root = root
        self.root_images = os.path.join(self.root, 'images')
        self.root_masks = os.path.join(self.root, 'masks')
        images_list = glob(os.path.join(self.root_images, '*.png'))
        masks_list = glob(os.path.join(self.root_masks, '*.png'))
        self.base_names = []
        for index in images_list:
            basename = os.path.basename(index)
            if os.path.join(self.root_masks, basename) in masks_list:
                self.base_names.append(basename)
        self.input_trans = input_trans
        self.target_trans = target_trans
    def __getitem__(self, item):
        basename = self.base_names[item]
        image_name = os.path.join(self.root_images, basename)
        mask_name = os.path.join(self.root_masks, basename)
        image = Image.open(image_name)
        mask = Image.open(mask_name)
        if self.input_trans is not None:
            image = self.input_trans(image)
        if self.target_trans is not None:
            mask = self.target_trans(mask)
        return image, mask

    def __len__(self):
        return len(self.base_names)

def test_TGSDS():
    ds = TGSDS('data')
    for index, (image, mask) in enumerate(ds):
        cv_image = np.array(image, dtype=np.uint8)
        stitching_image = np.zeros((cv_image.shape[0]*2, cv_image.shape[1], cv_image.shape[2]), dtype=np.uint8)
        cv_mask = np.array(mask, dtype=np.uint8)
        cv_mask_rgb = cv2.cvtColor(cv_mask, cv2.COLOR_GRAY2RGB)
        stitching_image[:cv_image.shape[0], :, :] = cv_image
        stitching_image[cv_image.shape[0]:, :, :] = cv_mask_rgb
        cv2.imshow('img', stitching_image)
        cv2.waitKey(1000)

if __name__ == '__main__':
    test_TGSDS()