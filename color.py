#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 17:30:18 2021

@author: felix
"""

import filters 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tkinter as tk

name = 'Color conversion'

class Gray(filters.im_filter):
    name = 'to grayscale'
    def do(self):
        image = self.image
        g = image.mean(axis=2) 
        im = np.zeros(image.shape)
        for i in range(3):
            im[:,:,i] = g
        return im
    
class Invert(filters.im_filter):
    name = 'invert'
    def do(self): return 1-self.image
    
class BGR(filters.im_filter):
    name = 'to BGR'
    def do(self): return self.image[:,:,[2,1,0]]
                
class GBR(filters.im_filter):
    name = 'to GBR'
    def do(self): return self.image[:,:,[1,2,0]]
    
    
class Colormaps(filters.im_user_filter):
    name = 'Colormaps...'
    
    def __init__(self, image, parent):
        super().__init__(image, parent)
        
    def _create_frame(self):
        deprecated = ['Vega10','Vega10_r','Vega20_r','Vega20b',
                      'Vega20b_r','Vega20c','Vega20c_r','spectral','spectral_r']
        self.values = sorted(m for m in plt.cm.datad if m not in deprecated)    
        self.tools.config(text="Change Colormap")        
        self.cb_item = tk.StringVar()
        self.cb_item.trace_variable("w",self._adjust)  
        self.makeCombobox(title="Colormap", values=self.values, var = self.cb_item)
        
    def _reset(self):
        self.cb_item.set(self.values[0])
            
    def do(self):
        value = self.cb_item.get()
        cm = matplotlib.cm.ScalarMappable(cmap=value)
        if len(self.image.shape)==2:
            data = self.image
        else:
            yiq = filters.rgb2yiq(self.image)
            data = yiq[:,:,0]
        return cm.to_rgba(data)[:,:,:3]
    
class Luminance(filters.im_user_filter):
    name = 'Luminance...'
    
    def _create_frame(self):
        self.tools.config(text="Change YIQ")
        self.scaleY = tk.IntVar()
        self.scaleY.trace_variable("w",self._adjust)
        self.makeSlider(title="Luminance", from_=-50, to=50, variable=self.scaleY)
        self.scaleIQ = tk.IntVar()
        self.scaleIQ.trace_variable("w",self._adjust)
        self.makeSlider(title="Chrominance", from_=0, to=40, variable=self.scaleIQ)
    
    def _reset(self):
        self.scaleY.set(0)
        self.scaleIQ.set(10)
    
    def do(self):
        alpha = 2**(self.scaleY.get() / 10)
        beta = (self.scaleIQ.get() / 10)
        yiq = filters.rgb2yiq(self.image)
        yiq[:,:,0] *= alpha
        yiq[:,:,1:3] *= beta
        return filters.yiq2rgb(yiq)

functions = [Gray, Invert, BGR, GBR, Colormaps, Luminance]       
