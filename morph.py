# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 11:41:08 2021

@author: agustring
"""

import filters 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tkinter as tk

name = 'Morphology'
    
class Morph(filters.im_user_filter):
    name = 'Morph...'
    
    def __init__(self, image, parent):
        super().__init__(image, parent)
        
    def _create_frame(self):
        a = ['Erode','Dilate','Median','Ext_Borders','Int_Borders','Gradient','TopHat','BottomHat','Open','Close','OC','CO']
        self.values = sorted(a)    
        self.tools.config(text="Change Settings")        
        self.cb_item = tk.StringVar()
        self.cb_item.trace_variable("w",self._adjust)  
        self.makeCombobox(title="Operation", values=self.values, var = self.cb_item)
        
        se = ['Circle','Box']
        self.values2 = sorted(se)    
        # self.tools.config(text="Change Structural Element")        
        self.cb_item2 = tk.StringVar()
        self.cb_item2.trace_variable("w",self._adjust)  
        self.makeCombobox(title="Structural Element", values=self.values2, var = self.cb_item2)
        
        self.tools.config(text="Scale")
        self.scaleperc = tk.IntVar()
        self.scaleperc.trace_variable("w", self._adjust)
        self.makeSlider(title="Structure size", from_ = 1, to = 15, variable = self.scaleperc)
        
    def _reset(self):
        self.cb_item.set(self.values[0])
        self.cb_item2.set(self.values[0])
        self.scaleperc.set(1)
        
    def do(self):       
        def _morph_gray(im, se, op):
            result = np.zeros(im.shape)
            offset = (np.array(se.shape)-1)//2
            im = np.pad(im,[(offset[0],offset[0]),(offset[1],offset[1])],'edge')
            for y, x in np.ndindex(result.shape):
                pixels = im[y: y + se.shape[0], x: x + se.shape[1]][se]
                result[y, x] = op(pixels)
            return result
        
        def _morph_color(im, se, op):
            def _morph_multiband(im, se, op):
                result = np.zeros(im.shape)
                offset = (np.array(se.shape)-1)//2
                im = np.pad(im,[(offset[0],offset[0]),(offset[1],offset[1]),(0,0)],'edge')
                for y, x in np.ndindex(result.shape[:2]):
                    pixels = im[y:y+se.shape[0], x:x+se.shape[1]][se]
                    result[y, x] = pixels[op(pixels[:,0])]
                return result
            im2 = (filters.rgb2yiq(im)[:, :, 0])[:, :, np.newaxis]
            im2 = np.concatenate((im2, im),axis=2)
            result = _morph_multiband(im2, se, op)[:, :, 1:]
            return result
                

        value = self.cb_item.get()
        value2 =  self.cb_item2.get()
        r = int(self.scaleperc.get())
        
#-------------------------------SE options---------------------------------
        if value2 == 'Box':
            se = np.ones((r*2+1,r*2+1),dtype=np.bool)
        elif value2 == 'Circle':
            threshold=0.5
            vec = np.linspace(-r, r, r*2+1)
            [x,y] = np.meshgrid(vec,vec) 
            se = (x**2 + y**2)**0.5 < (r + threshold)
#----------------------------Operation----------------------------
        data = self.image
        if value=='Erode':
            op=np.argmin
            if len(data.shape)==2: op=np.min
        elif value=='Dilate':
            op=np.argmax
            if len(data.shape)==2: op=np.max
        elif value=='Median':
            op= lambda px: np.argsort(px)[len(px)//2]
            if len(data.shape)==2: op=np.median
        elif value=='Ext_Borders':
            return _morph_color(data,se,np.argmax)[:,:,:3] - data
        elif value=='Int_Borders':
            return data - _morph_color(data,se,np.argmin)[:,:,:3] 
        elif value=='Gradient':
            return _morph_color(data,se,np.argmax)[:,:,:3] - _morph_color(data,se,np.argmin)[:,:,:3] 
        elif value=='Open':
            return _morph_color(_morph_color(data,se,np.argmin)[:,:,:3],se,np.argmax)[:,:,:3]
        elif value=='Close':
            return _morph_color(_morph_color(data,se,np.argmax)[:,:,:3],se,np.argmin)[:,:,:3]
        elif value=='BottomHat':
            return _morph_color(_morph_color(data,se,np.argmax)[:,:,:3],se,np.argmin)[:,:,:3] - data
        elif value=='TopHat':
            return data - _morph_color(_morph_color(data,se,np.argmin)[:,:,:3],se,np.argmax)[:,:,:3]
        elif value=='OC':
            return _morph_color(_morph_color(_morph_color(_morph_color(data,se,np.argmax)[:,:,:3],se,np.argmin)[:,:,:3],se,np.argmin)[:,:,:3],se,np.argmax)[:,:,:3]
        elif value=='CO':
            return _morph_color(_morph_color( _morph_color(_morph_color(data,se,np.argmin)[:,:,:3],se,np.argmax)[:,:,:3],se,np.argmax)[:,:,:3],se,np.argmin)[:,:,:3]
        
        if len(self.image.shape)==2:
            data = self.image
            return filters.yiq2rgb(_morph_gray(data,se,op))
        else:
            data = self.image
            return _morph_color(data,se,op)[:,:,:3]

functions = [Morph]       
