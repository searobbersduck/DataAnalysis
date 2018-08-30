#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/8/30 上午10:17
# @Author  : SeaRobbersAndDuck
# @Site    : 
# @File    : dataset.py
# @Software: PyCharm

import os
import sys
import numpy as np
from glob import glob

import torch
from torch.utils.data import DataLoader, Dataset
from torchvision.transforms import Compose, Scale, CenterCrop, Normalize, ToTensor

from PIL import Image
import cv2

class TGSDataset(Dataset):
    def __init__(self, root, input_trans=None, target_trans=None):
        self.root = root
        self.root_images = os.path.join(self.root, 'images')
        self.root_masks = os.path.join(self.root, 'masks')
        self.images_name = []
        images_list = glob(os.path.join(self.root_images, '*.png'))
        masks_list = glob(os.path.join(self.root_masks, '*.png'))
        for index in images_list:
            basename = os.path.basename(index)
            if os.path.join(self.root_masks, basename) in masks_list:
                self.images_name.append(basename)
        self.input_trans = input_trans
        self.target_trans = target_trans
    def __getitem__(self, item):
        basename = self.images_name[item]
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
        return len(self.images_name)


def test_TGSDataset():
    ds = TGSDataset('data')
    for index, (image, mask) in enumerate(ds):
        cv_image = np.array(image)
        cv2.imshow('img', cv_image)
        # cv2.waitKey(1000)
        cv_mask = np.array(mask)
        cv2.imshow('mask', cv_mask)
        cv2.waitKey(1000)


if __name__ == '__main__':
    test_TGSDataset()