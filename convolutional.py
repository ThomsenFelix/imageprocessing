# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 16:31:27 2021

@author: Gastón Vilches y Agustín Lapi
"""

import filters 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tkinter as tk
from scipy.signal import convolve2d

name = 'Convolutional'

def box(ksize=3):
    '''Returns a box blur kernel.'''
    return np.ones((ksize, ksize))/(ksize**2)

def circle(ksize=3):
    '''Returns a circle-shaped kernel. This can be improved by using the 
    mid-point algorithm to draw the circle.
    '''
    rad = ksize//2
    x, y = np.mgrid[-rad:rad+1, -rad:rad+1]
    kernel = np.zeros((ksize, ksize))
    kernel[x**2 + y**2 <= rad**2] = 1
    return kernel/kernel.sum()

def gauss(ksize=3, std=None):
    '''Returns a Gaussian kernel. If std=None, it calculates it proportionally 
    to the kernel radius such that for ksize=3 it matches the well-known 3x3 
    gaussian kernel. If std is a function, it applies that function to the 
    default std value.
    '''
    rad = ksize//2
    xx, yy = np.mgrid[-rad:rad+1, -rad:rad+1]
    if std == None or callable(std):
        std_temp = rad/np.sqrt(np.log(4))
        std = std(std_temp) if callable(std) else std_temp
    kernel = np.exp(-(xx**2 + yy**2)/(2*std**2))
    return kernel/kernel.sum()

def identity(ksize=3):
    '''Returns the identity kernel.'''
    kernel = np.zeros((ksize, ksize))
    kernel[ksize//2, ksize//2] = 1
    return kernel

def high_pass(kernel=gauss(3)):
    '''Calculates a high-pass kernel based on a low-pass input kernel.'''
    return identity(kernel.shape[0]) - kernel

def dog(ksize=5, std1=None, std2=lambda x:x*2):
    '''Returns a Difference of Gaussians kernel.'''
    return gauss(ksize,std1) - gauss(ksize,std2)

def normalize_filter(kernel):
    '''Normalizes the values of a kernel. If all the elements are positive, 
    the sum of the resultant kernel is 1. If the kernel has also negative 
    elements, the kernel is normalized so that the absolute value of the 
    convolution result is never greater than 0.5.
    '''
    if np.any(kernel < 0):
        max_negative = np.sum(np.clip(kernel, None, 0))
        max_positive = np.sum(np.clip(kernel, 0, None))
        max_val = np.maximum(-max_negative, max_positive)
        return kernel/(2*max_val)
    else:
        return kernel/kernel.sum()

class BasicFilters(filters.im_user_filter):
    name = 'Basic filters'
    
    def __init__(self, image, parent):
        super().__init__(image, parent)
        
    def _create_frame(self):
        self.filters = ['Box', 'Circle', 'Gaussian', 'Gaussian high pass', 'Difference of Gaussians']
        self.ksizes = ['3x3', '5x5', '7x7', '11x11', '15x15', '25x25']
        self.tools.config(text="Select filter")        
        self.cb_item = tk.StringVar()
        self.cb_item.trace_variable("w", self._adjust)
        self.makeCombobox(title="Filter", values=self.filters, var=self.cb_item)
        self.cb_item2 = tk.StringVar()
        self.cb_item2.trace_variable("w", self._adjust)
        self.makeCombobox(title="Kernel size", values=self.ksizes, var=self.cb_item2)
        
    def _reset(self):
        self.cb_item.set(self.filters[0])
        self.cb_item2.set(self.ksizes[0])
            
    def do(self):
        ksize = int(self.cb_item2.get().split('x')[0])
        filters = [box(ksize), circle(ksize), gauss(ksize), 
                   high_pass(gauss(ksize)), dog(ksize)]
        idx, = np.where(np.array(self.filters) == self.cb_item.get())
        kernel = normalize_filter(filters[idx[0]])
        img_filt = np.stack([convolve2d(self.image[:,:,ch], kernel, 'same', 'symm') 
                             for ch in range(self.image.ndim)], axis=2)
        return img_filt if not np.any(kernel < 0) else img_filt + 0.5

class ContrastEnhancement(filters.im_user_filter):
    name = 'Contrast enhancement'
    
    def _create_frame(self):
        self.ksizes = ['3x3', '5x5', '7x7', '11x11', '15x15', '25x25']
        self.tools.config(text="Select level of enhancement")
        self.scale = tk.DoubleVar()
        self.scale.trace_variable("w",self._adjust)
        self.makeSlider(title="Contrast enhancement", from_=0.0, to=5.0, 
                        resolution=0.05, variable=self.scale)
        self.cb_item2 = tk.StringVar()
        self.cb_item2.trace_variable("w", self._adjust)
        self.makeCombobox(title="Kernel size", values=self.ksizes, var=self.cb_item2)
    
    def _reset(self):
        self.scale.set(0)
    
    def do(self):
        ksize = int(self.cb_item2.get().split('x')[0])
        kernel = high_pass(gauss(ksize))
        img_hp = np.stack([convolve2d(self.image[:,:,ch], kernel, 'same', 'symm')
                             for ch in range(self.image.ndim)], axis=2)
        return np.clip(self.image + self.scale.get()*img_hp, 0, 1)
        
        
functions = [BasicFilters, ContrastEnhancement]       
