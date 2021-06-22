#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 18:13:30 2021

@author: felix
"""
import tkinter as tk
import tkinter.ttk as ttk
#import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

RGB2YIQ = np.array([[0.299,0.595716,0.211456],[0.587,-0.274453,-0.522591], [0.114,-0.321263,0.311135]])

def _linear_map(data, matrix):
    return (data.reshape((-1, 3)) @ matrix).reshape(data.shape)

def rgb2yiq(data):
    return _linear_map(data, RGB2YIQ)

def yiq2rgb(data):
    return np.clip(_linear_map(data, np.linalg.inv(RGB2YIQ)),0,1)

class im_filter():
    name = ''
    image = None 
    accepted = True
    def __init__(self, image, parent = None):
        self.image = image
    
    def do(self):
        return self.image
    
    def undo(self, new_image):
        return self.image

class im_user_filter(im_filter):
    name = 'generic'
    def __init__(self, image, parent = None):
        super().__init__(image = image)
        self.accepted = False
        self.actual_row = 0
        
        self.win = tk.Toplevel(parent)
        self.makeGUI()
        self._create_frame()
        self._reset()
        
        self._show(image, 0)
        self._show(image, 1)
        self.do_preview.set(True)
        self._update()
        
        self.win.focus_set()       
        self.win.grab_set()           
        self.win.wait_window()
        
    def _reset(self):
        pass
    
    def _create_frame(self):
        pass
    
    def _show(self, im, subplot = 1):
        self.ax[subplot].clear()
        self.ax[subplot].imshow(im)
        self.ax[subplot].axis('off')
        self.canvas.draw()
        
    def _apply(self):        
        self.accepted = True
        self.win.destroy()
        
    def _cancel(self):
        self.win.destroy()
        
    def _adjust(self,*args):
        do_preview = self.do_preview.get()
        if do_preview:
            self.btn_update.config(state=tk.DISABLED)
            self._update()
        else:
            self.btn_update.config(state=tk.NORMAL)
    
    def _update(self):
        return self._show(self.do())            
    
    def makeCombobox(self, var, title='', values=None, state="readonly", **kwargs):
        self.tools.columnconfigure(1, weight=1)
        tk.Label(self.tools,text=title).grid(row=self.actual_row,column=0,sticky=tk.W)
        cb = ttk.Combobox(self.tools,values = values, state=state, textvariable=var, **kwargs)
        if not values is None:
            var.set(values[0])
        cb.grid(row=self.actual_row,column=1,sticky=tk.W)        
        self.actual_row +=1
        return cb
    
    def makeSlider(self, title='', **kwargs):
        self.tools.columnconfigure(1, weight=1)
        tk.Label(self.tools, text = title).grid(row = self.actual_row,column=0, sticky=tk.W)
        scale = tk.Scale(self.tools, orient=tk.HORIZONTAL, **kwargs)
        scale.grid(row = self.actual_row, column=1, sticky=tk.EW)        
        self.actual_row +=1
        return scale 
    
    def makeGUI(self, master=None):     
        self.win.title("Preview of filter: " + self.name)
        # Make Plot:
        self.matplotlib = tk.Frame(self.win)
        self.fig = Figure(figsize = (9,3))
        
        ax0 = self.fig.add_subplot(1,2,1)
        ax1 = self.fig.add_subplot(1,2,2)
        self.ax = [ax0, ax1]
        
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0,wspace=0,hspace=0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.matplotlib)
        self.canvas.get_tk_widget().pack(anchor=tk.N, fill=tk.BOTH, expand=1)
        self.matplotlib.pack(fill=tk.BOTH, expand=1)
 
        panel = tk.Frame(self.win,relief=tk.RAISED)
        self.tools = tk.LabelFrame(master=panel)
        self.tools.pack(fill=tk.X)

        panelBtn = tk.Frame(master=panel)
        tk.Button(master=panelBtn, text="cancel", command=self._cancel).pack(side=tk.LEFT)    
        ttk.Separator(panelBtn,orient=tk.VERTICAL).pack(padx=20,side=tk.LEFT)
        tk.Button(master=panelBtn, text="reset", command=self._reset).pack(side=tk.LEFT)
        ttk.Separator(panelBtn,orient=tk.VERTICAL).pack(padx=5,side=tk.LEFT)        
        self.btn_update = tk.Button(master=panelBtn, text="update", command=self._update)
        self.btn_update.pack(side=tk.LEFT)
        self.do_preview = tk.BooleanVar()
        self.do_preview.set(False)
        ttk.Checkbutton(master=panelBtn, text="live preview",
            variable=self.do_preview,command=self._adjust).pack(side = tk.LEFT)     
        tk.Button(master=panelBtn, text="apply", command=self._apply).pack(side=tk.RIGHT)     
        panelBtn.pack(fill=tk.X,expand=0)
        panel.pack(fill=tk.X,expand=0)