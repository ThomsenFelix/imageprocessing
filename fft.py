# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 15:12:46 2021

@author: agustring
"""

import filters 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import tkinter as tk

name = 'FFT'

class amp_FFT(filters.im_filter):
    name = 'to FFT amplitude'
    def do(self):
        def fft2_ap(im):
            im_f = np.fft.fftshift(np.fft.fft2(im))
            amp = np.abs(im_f)
            phase = np.angle(im_f)
            # normalize amplitude:
            s = np.array(im.shape).prod()
            amp /= s
            return amp
        a = np.log(fft2_ap(self.image))
        return a
    
class phase_FFT(filters.im_filter):
    name = 'to FFT phase'
    def do(self):
        def fft2_ap(im):
            im_f = np.fft.fftshift(np.fft.fft2(im))
            amp = np.abs(im_f)
            phase = np.angle(im_f)
            # normalize amplitude:
            s = np.array(im.shape).prod()
            amp /= s
            return phase
    
        return fft2_ap(self.image)
    
class resample(filters.im_filter):
    name = 'to RESAMPLE 500x500'
    def do(self): 
        def fft_resample(im, new_shape):
            fac = np.array(new_shape).prod() / np.array(im.shape).prod()
            im_f = np.fft.fftshift(np.fft.fft2(im * fac))
            # crop or pad:
            diff = (np.array(new_shape)-np.array(im.shape))//2
            crop = np.maximum(0, -diff)
            im_f = im_f[crop[0] : im.shape[0] - crop[0], crop[1] : im.shape[1] - crop[1]]
            pad = np.maximum(0, diff)
            im_f = np.pad(im_f,([pad[0], pad[0]], [pad[1], pad[1]]), 'empty')
            rec = np.clip(np.fft.ifft2(np.fft.ifftshift(im_f)).real, 0, 1)
            return rec

        return fft_resample(self.image,(500,500))
 
functions = [amp_FFT,phase_FFT,resample]       
