# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 13:22:12 2019

@author: Felix
"""

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import imageio
import numpy as np

# functions
import color, geometry, convolutional

TITLE = "UNS - Image processing"
SIZE = (600, 400)
TB_Y = 26

class Main():
    def __init__(self):
        self.history= []
        self.hist_pointer = -1
        
        self.image = None
        self.fn = ''
        self.zoom = 1.0
        self.root = tk.Tk()
        self.root.title(TITLE)
        self.menubar = tk.Menu(self.root)
        self.make_menus()
        self.root.config(menu=self.menubar)
        
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RIDGE, height=TB_Y) 
        self.make_toolbars()
        
        self.canvas=tk.Canvas(self.root,bg='#FFFFFF',width=SIZE[0],height=SIZE[1],scrollregion=(0,0,SIZE[0],SIZE[1]))
        hbar=tk.Scrollbar(self.root,orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM,fill=tk.X)
        hbar.config(command=self.canvas.xview)
        vbar=tk.Scrollbar(self.root,orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT,fill=tk.Y)
        vbar.config(command=self.canvas.yview)
        self.canvas.config(width=SIZE[0],height=SIZE[1])
        self.canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.canvas.pack(side=tk.LEFT,expand=True,fill=tk.BOTH)
        
        self.root.mainloop()
        
    def make_toolbars(self):
        
        files = tk.Frame(self.toolbar,relief=tk.RIDGE)
        
        img = Image.open("icons/load.png")
        img = img.resize((TB_Y,TB_Y), Image.ANTIALIAS)
        self.eimg1 = ImageTk.PhotoImage(img)  
        button = tk.Button(files,image=self.eimg1, relief=tk.FLAT,command=self._read)
        button.pack(side=tk.LEFT)
        img = Image.open("icons/save.png")
        img = img.resize((TB_Y,TB_Y), Image.ANTIALIAS)
        self.eimg2 = ImageTk.PhotoImage(img)  
        button = tk.Button(files,image=self.eimg2, relief=tk.FLAT,command=self._write_as)
        button.pack(side=tk.LEFT)
        files.pack(side=tk.LEFT,fill=tk.X,padx = 5)
        
        undo_redo = tk.Frame(self.toolbar,relief=tk.RIDGE)
        img = Image.open("icons/undo.png")
        img = img.resize((TB_Y,TB_Y), Image.ANTIALIAS)
        self.eimg5 = ImageTk.PhotoImage(img)  
        button = tk.Button(undo_redo,image=self.eimg5, relief=tk.FLAT,command=self._undo)
        button.pack(side=tk.LEFT)
        img = Image.open("icons/redo.png")
        img = img.resize((TB_Y,TB_Y), Image.ANTIALIAS)
        self.eimg6 = ImageTk.PhotoImage(img)  
        button = tk.Button(undo_redo,image=self.eimg6, relief=tk.FLAT,command=self._redo)
        button.pack(side=tk.LEFT)
        undo_redo.pack(side=tk.LEFT,fill=tk.X,padx = 5)
           
        zoom = tk.Frame(self.toolbar,relief=tk.RIDGE)
        img = Image.open("icons/zoom-in.png")
        img = img.resize((TB_Y,TB_Y), Image.ANTIALIAS)
        self.eimg3 = ImageTk.PhotoImage(img)  
        button = tk.Button(zoom,image=self.eimg3, relief=tk.FLAT,command=self.zoom_in)
        button.pack(side=tk.LEFT)
        img = Image.open("icons/zoom-out.png")
        img = img.resize((TB_Y,TB_Y), Image.ANTIALIAS)
        self.eimg4 = ImageTk.PhotoImage(img)  
        button = tk.Button(zoom,image=self.eimg4, relief=tk.FLAT,command=self.zoom_out)
        button.pack(side=tk.LEFT)
        zoom.pack(side=tk.LEFT,fill=tk.X,padx = 10)
        
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
    
    def make_menus(self):
       filemenu = tk.Menu(self.menubar, tearoff=0)
       filemenu.add_command(label="Open...", command=self._read, accelerator="Ctrl+O")
       filemenu.add_separator()
       filemenu.add_command(label="Save", command=self._write, accelerator="Ctrl+S")
       filemenu.add_command(label="Save as...", command=self._write_as, accelerator="Ctrl+Shift+S")
       filemenu.add_separator()
       filemenu.add_command(label="Close", command=self._close, accelerator="Ctrl+W")
       filemenu.add_separator()
       filemenu.add_command(label="Exit", command=self.root.destroy, accelerator="Ctrl+Q")
       self.menubar.add_cascade(label="File", menu=filemenu)
       
       editmenu = tk.Menu(self.menubar, tearoff=0)
       editmenu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
       editmenu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Shift+Z")
       editmenu.add_separator()
       #editmenu.add_command(label="Copy", command=self._clipboard_copy, accelerator="Ctrl+C")
       #editmenu.add_command(label="Paste", command=self._clipboard_paste, accelerator="Ctrl+V")
       #editmenu.add_separator()
       self.menubar.add_cascade(label="Edit", menu=editmenu)
       
       self.filtermenu = tk.Menu(self.menubar,tearoff=0)
       self.add_functions(color)
       self.add_functions(geometry)
       self.add_functions(convolutional)
       
       self.menubar.add_cascade(label='Filters',menu=self.filtermenu)
       
       helpmenu = tk.Menu(self.menubar,tearoff=0)
       helpmenu.add_command(label="About...", command = self.hello)
       self.menubar.add_cascade(label='Help',menu=helpmenu)
    
    #def _clipboard_copy(self):  
    #    print('TODO: implement copy')
        
    #def _clipboard_paste(self):
    #    print('TODO: implement paste')
     
    def add_functions(self, _class):
        menu = tk.Menu(tearoff=0)
        self.filtermenu.add_cascade(label = _class.name, menu = menu)
        for func in _class.functions:
            menu.add_command(label = func.name, command = lambda func = func: self.run_function(func))
    
    def run_function(self, function):
        if self.image is None:
            return
        func = function(self.image, self.root)
        if func.accepted:
            self.image = func.do()    
            self.history = self.history[:self.hist_pointer+1]
            self.history.append(func)
            self.hist_pointer +=1
            self._update()
    
    def _read(self):
        fn = filedialog.askopenfilename(filetypes = (("Images","*.jpg | *.png | *.bmp"),
                                                     ("All files","*.*")))
        if fn:
            self.fn = fn
            im = imageio.imread(fn)
            if im.ndim==3:
                im = im[:, :, :3]
            if im.ndim==2:
                im = im[:, :, np.newaxis].repeat(3,2)
            self.image = im/255.
            self.reset_hist()
            self._update()
            
    def _write_as(self):
        fn = filedialog.asksaveasfilename(defaultextension='*.png',
            filetypes=(("PNG","*.png"),("BMP","*.bmp"),("GIF","*.gif"), ("JPEG","*.jpg")))
        if fn:
            self.fn = fn
            self._write()
    
    def _write(self):
        if self.fn:
            imageio.imwrite(self.fn,(np.clip(self.image, 0, 1)*255).astype(np.uint8))
            self.root.title(TITLE + ": " + self.fn)
            self.reset_hist()
        else:
            self._write_as()
        
    def _close(self):
        self.fn = ''
        self.image = None
        self.reset_hist()
        self._update()
    
    def reset_hist(self):
        self.history = []
        self.hist_pointer = -1
                
    def _update(self):
        if self.image is None:
            im = np.zeros((SIZE[1],SIZE[0],4),dtype=np.float)
        else:
            im = self.image
        image = Image.fromarray((im*255).astype(np.uint8)).resize((int(np.round(im.shape[1]*self.zoom)),
                      int(np.round(im.shape[0]*self.zoom))), Image.ANTIALIAS)
        self.img =  ImageTk.PhotoImage(image=image)
        self.canvas.config(scrollregion=(0,0,image.width,image.height))
        self.canvas.create_image(0,0, image=self.img,anchor=tk.NW)
        # update title:
        if self.hist_pointer>=0:
            title = TITLE + ": * " + self.fn + " *"
        elif self.image is None:
            title = TITLE
        else:
            title = TITLE + ": " + self.fn
        self.root.title(title)
    
    def hello(self):
       print("hello")
              
    def zoom_in(self):
        self.zoom = np.round((self.zoom*100*1.1))/100
        self._update()
    
    def zoom_out(self):
        self.zoom = np.round(self.zoom*100/1.1)/100 
        self._update()
        
    def _undo(self):
        if self.hist_pointer>=0:
            self.image = self.history[self.hist_pointer].undo(self.image)
            self.hist_pointer-=1
            self._update()
    
    def _redo(self):
        if (self.hist_pointer+1)<len(self.history):
            self.hist_pointer+=1
            self.image = self.history[self.hist_pointer].do()
            self._update()

 
if __name__ =="__main__":
   app = Main()