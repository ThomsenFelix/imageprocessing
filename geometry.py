#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 17:33:10 2021

@author: felix
"""
import numpy as np
import filters
import tkinter as tk
import skimage.transform as transform

name = 'rotate and flip' 

# example with explicite undo function
class Rotate90(filters.im_filter):
    name = 'Rotate 90'
    
    def do(self):
        image = self.image
        for i in range(3):
            image[:,:,i] = image[-1::-1,:,i].T
        return image
    
    def undo(self, new_image):
        for i in range(3):
            self.image[-1::-1,:,i] = new_image[:,:,i].T
        return self.image
    
class Flip(filters.im_filter):
    name = 'flip'
    
    def _flip(self, im):
        return im[:,-1::-1,:]
    
    def do(self): 
        return self._flip(self.image)
    
    def undo(self, new_image): 
        return self._flip(new_image)
    
    
class Rotate(filters.im_user_filter):
    name = 'Rotate...'
   
    def _create_frame(self):
        self.tools.config(text="Rotate")
        self.scaledeg = tk.IntVar()
        self.scaledeg.trace_variable("w",self._adjust)
        self.makeSlider(title="Angle",from_=-180,to=180,variable=self.scaledeg)
        self.crop = tk.StringVar()
        self.crop.trace_variable("w",self._adjust)
        self.makeCombobox(title="Resize",values = ['No','Yes'],var=self.crop)
        
    def _reset(self):
        self.scaledeg.set(0)
        self.crop.set('No')
    
    def do(self):
        angle = float(self.scaledeg.get())
        im_out= transform.rotate(self.image, angle, self.crop.get()=='Yes')
        return im_out


class Scale(filters.im_user_filter):
    name = 'Rescale...'

    def _create_frame(self):
        self.tools.config(text="Scale")
        self.scaleperc = tk.IntVar()
        self.scaleperc.trace_variable("w", self._adjust)
        self.makeSlider(title="Percent", from_ = 5, to = 1000, variable = self.scaleperc)

    def _reset(self):
        self.scaleperc.set(100)
    
    def do(self):
        scale = float(self.scaleperc.get())/100
        im_out= transform.rescale(self.image, scale, order = 3, multichannel = True)
        return im_out
    
functions = [Rotate, Scale, Rotate90, Flip]    