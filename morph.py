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
import scipy.ndimage as sp

name = 'Morphology'
    
class Morph(filters.im_user_filter):
    name = 'Morph...'
    
    def __init__(self, image, parent):
        super().__init__(image, parent)
        
    def _create_frame(self):
        a = ['Erode','Dilate','Ext_Borders','Int_Borders','Gradient','TopHat','BottomHat','Open','Close','OC','CO']
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
#-------------------------------Dilate & Erode---------------------------------
        def _morph_erode(im, value2, r, gray):
            if is_gray:
                im = im.mean(axis=2)
                if value2 == 'Box':
                    #Box it's easier to process than other structures
                    result = sp.grey_erosion(im,size=(r,r))
                elif value2 == 'Circle':
                    threshold=0.5
                    vec = np.linspace(-r, r, r*2+1)
                    [x,y] = np.meshgrid(vec,vec) 
                    se = (x**2 + y**2)**0.5 < (r + threshold)
                    result = sp.grey_erosion(im,footprint=se,size=(r,r))
                result = result[:, :, np.newaxis].repeat(3,2)
            else:
                if value2 == 'Box':
                    se = np.ones((r*2+1,r*2+1),dtype=np.bool)
                elif value2 == 'Circle':
                    threshold=0.5
                    vec = np.linspace(-r, r, r*2+1)
                    [x,y] = np.meshgrid(vec,vec) 
                    se = (x**2 + y**2)**0.5 < (r + threshold)
                result = _morph_color(im,se,np.argmin)
            return result
        
        def _morph_dilation(im, value2, r, gray):
            if is_gray:
                im = im.mean(axis=2)
                if value2 == 'Box':
                    result = sp.grey_dilation(im,size=(r,r))
                elif value2 == 'Circle':
                    threshold=0.5
                    vec = np.linspace(-r, r, r*2+1)
                    [x,y] = np.meshgrid(vec,vec) 
                    se = (x**2 + y**2)**0.5 < (r + threshold)
                    result = sp.grey_dilation(im,footprint=se,size=(r,r))
                result = result[:, :, np.newaxis].repeat(3,2)
            else:
                if value2 == 'Box':
                    se = np.ones((r*2+1,r*2+1),dtype=np.bool)
                elif value2 == 'Circle':
                    threshold=0.5
                    vec = np.linspace(-r, r, r*2+1)
                    [x,y] = np.meshgrid(vec,vec) 
                    se = (x**2 + y**2)**0.5 < (r + threshold)
                result = _morph_color(im,se,np.argmax)
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
                
        data = self.image
        value = self.cb_item.get()
        value2 =  self.cb_item2.get()
        r = int(self.scaleperc.get())
        ep = 10**-5
        is_gray = data.var(axis=2).mean() < ep
        
#----------------------------Operation----------------------------
        
        if value=='Erode':
            #np.argmin
            return _morph_erode(data, value2, r, is_gray)
        elif value=='Dilate':
            #np.argmax
            return _morph_dilation(data, value2, r, is_gray)
        elif value=='Ext_Borders':
            return _morph_dilation(data, value2, r, is_gray) - data
        elif value=='Int_Borders':
            return data - _morph_erode(data, value2, r, is_gray)
        elif value=='Gradient':
            return _morph_dilation(data, value2, r, is_gray) - _morph_erode(data, value2, r, is_gray)
        elif value=='Open':
            return _morph_dilation(_morph_erode(data, value2, r, is_gray),value2, r, is_gray)
        elif value=='Close':
            return _morph_erode(_morph_dilation(data, value2, r, is_gray),value2, r, is_gray)
        elif value=='BottomHat':
            return _morph_erode(_morph_dilation(data, value2, r, is_gray),value2, r, is_gray) - data
        elif value=='TopHat':
            return data - _morph_dilation(_morph_erode(data, value2, r, is_gray),value2, r, is_gray)
        elif value=='OC':
            return _morph_erode(_morph_dilation(_morph_dilation(_morph_erode(data, value2, r, is_gray),value2, r, is_gray), value2, r, is_gray),value2, r, is_gray)
        elif value=='CO':
            return _morph_dilation(_morph_erode(_morph_erode(_morph_dilation(data, value2, r, is_gray),value2, r, is_gray), value2, r, is_gray),value2, r, is_gray)

        
        if is_gray:
            data = self.image
            return filters.yiq2rgb(_morph_gray(data,se,op))
        else:
            data = self.image
            return _morph_color(data,se,op)[:,:,:3]

functions = [Morph]       
