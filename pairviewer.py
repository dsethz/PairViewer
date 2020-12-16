#######################################################################################################################
# GUI to scan through pairs of images and mark a relevant subset.                                                     #
# Author:               Daniel Schirmacher                                                                            #
#                       PhD Student, Cell Systems Dynamics Group, D-BSSE, ETH Zurich                                  #
# Python Version:       3.8.6                                                                                         #
#######################################################################################################################
import os
import cv2
import csv

import numpy as np
import pandas as pd
import tkinter as tk

from PIL import Image
from PIL import ImageTk
from tkinter import filedialog


class SegViewer():
    def __init__(self, master):
        self.master = master
        self.master.title('SegViewer')

        self.panelA = None
        self.panelB = None
        self.files = None
        self.del_list = []
        self.current_pos = 0

        # add frames for scrollbar and images
        self.frame_img = tk.Frame(self.master, width=1566, height=815, bg='blue')
        self.frame_box = tk.Frame(self.master, width=215, height=815, bg='green')

        # add scrollable Listbox for marked images
        self.scrollbar = tk.Scrollbar(self.frame_box, orient='vertical')

        self.listbox = tk.Listbox(self.frame_box, width=20, height=30, yscrollcommand=self.scrollbar)
        self.listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        self.scrollbar.config(command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=2, sticky='NSEW')
        
        # placement of frames
        self.frame_img.grid_propagate(0)
        self.frame_img.grid(row=0, column=0, padx=5, sticky='NSEW')
        self.frame_box.grid_propagate(0)
        self.frame_box.grid(row=0, column=1, padx=5, sticky='NSEW')

        # button to load a file of image paths for displaying
        self.file_btn = tk.Button(self.frame_img, text='Select file', command=self.select_file)
        self.file_btn.grid(row=1, column=0, columnspan=2, padx=5)

        # button to load a slection .csv file
        self.load_btn = tk.Button(self.frame_box, text='Load list', command=self.load_list)
        self.load_btn.grid(row=1, column=1, padx=5, pady=5)

        # button to save a selection .csv
        self.save_btn = tk.Button(self.frame_box, text='Save list', command=self.save_list)
        self.save_btn.grid(row=1, column=0, padx=5, pady=5)
 
        # key bindings
        self.master.bind('<Left>', self.key_left)
        self.master.bind('<Right>', self.key_right)
        self.master.bind('<Up>', self.key_up)
        self.master.bind('<Down>', self.key_down)


    def load_list(self):
        '''
            Load del_list from .csv file.
        '''
        path = filedialog.askopenfilename(initialdir='/', title='Select File',
                                          filetypes=(('CSV files', '.csv'), ('all files', '*.*')))
        
        with open(path, newline='') as f:
            reader = csv.reader(f)
            self.del_list = list(reader)

        # add loaded files to listbox
        for del_pair in self.del_list:
            idx = int(np.where(self.files.isin(del_pair))[0][0])
            self.listbox.insert('end', idx)


    def save_list(self):
        '''
            Save current self.del_list.
        '''
        df = pd.DataFrame(self.del_list)
        df = df.sort_values(by=0)
        path = filedialog.asksaveasfilename(title='Save file', defaultextension='.csv')
        df.to_csv(path, index=False, header=False)


    def load_images_(self):
        '''
            Loads image and mask of the current position to panelA/B.
        '''
        # change background color if pair in del_list
        if self.files.iloc[self.current_pos, :].tolist() in self.del_list:
            self.frame_img.config(bg='red')
        else:
            self.frame_img.config(bg='blue')

        # load image as grayscale
        image = cv2.imread(self.files.iloc[self.current_pos, 0], -1)
        mask = cv2.imread(self.files.iloc[self.current_pos, 1], -1)
 
        # check if image 8bit or 16bit
        if image.dtype == np.uint8:
            image_type = '8bit'
        elif image.dtype == np.uint16:
            image_type = '16bit'
        else:
            raise TypeError(f'Image is expected to be either np.uint8 or np.uint8, but is {image.dtype}.')

        if mask.dtype == np.uint8:
            mask_type = '8bit'
        elif mask.dtype == np.uint16:
            mask_type = '16bit'
        else:
            raise TypeError(f'Mask is expected to be either np.uint8 or np.uint8, but is {mask.dtype}.')

        # rescale image if necessary
        image = cv2.resize(image, (768, 768))
        mask = cv2.resize(mask, (768, 768))

        # ensure that mask is binary
        if mask_type == '8bit':
            mask[mask > 0] = 255
        else:
            mask[mask > 0] = 65535

        # convert 16bit images to 8bit
        if image_type == '16bit':
            image = (image / 256).astype(np.uint8)

        if mask_type == '16bit':
            mask = (mask / 256).astype(np.uint8)

        # convert images to PIL format
        image = Image.fromarray(image)
        mask = Image.fromarray(mask)

        # convert to ImageTK format
        image = ImageTk.PhotoImage(image)
        mask = ImageTk.PhotoImage(mask)

        # if panels are None initialize them
        if self.panelA is None or self.panelB is None:
            self.panelA = tk.Label(self.frame_img, image=image)
            self.panelA.image = image
            self.panelA.grid(row=0, column=0, padx=5, pady=5)

            self.panelB = tk.Label(self.frame_img, image=mask)
            self.panelB.image = mask
            self.panelB.grid(row=0, column=1, padx=5, pady=5)

        else:
            # update the panels
            self.panelA.configure(image=image)
            self.panelB.configure(image=mask)
            self.panelA.image = image
            self.panelB.image = mask


    def select_file(self):
        '''
            Load list of image file paths and load first image pair.
        '''
        path = filedialog.askopenfilename(initialdir='/', title='Select File',
                                          filetypes=(('CSV files', '.csv'), ('all files', '*.*')))

        self.files = pd.read_csv(path, header=None)
        self.files = self.files.sort_values(by=0)
        self.current_pos = 0

        if len(path) > 0:
            self.load_images_()

                
    def key_left(self, event):
        '''
            Display previous image in file.
        '''
        if self.files is None:
            raise Warning('Select file first.')

        if self.current_pos == 0:
            raise Warning('No previous element in file list.')
        else:
            self.current_pos -= 1
            self.load_images_()


    def key_right(self, event):
        '''
            Display next image in file.
        '''
        if self.files is None:
            raise Warning('Select file first.')

        if self.current_pos == (len(self.files) - 1):
            raise Warning('No subsequent element in file list.')
        else:
            self.current_pos += 1
            self.load_images_()

        
    def key_up(self, event):
        '''
            Add current image pair to del_list.
        '''
        if self.files is None:
            raise Warning('Select file first.')

        del_pair = self.files.iloc[self.current_pos, :].tolist()
        
        if del_pair not in self.del_list:
            self.del_list.append(del_pair)
            self.listbox.insert('end', self.current_pos)
            self.frame_img.config(bg='red')

        
    def key_down(self, event):
        '''
            Remove current image pair from del_list.
        '''
        if self.files is None:
            raise Warning('Select file first.')

        del_pair = self.files.iloc[self.current_pos, :].tolist()
        
        if del_pair in self.del_list:
            self.del_list.remove(del_pair)
            idx = self.listbox.get(0, tk.END).index(self.current_pos)
            self.listbox.delete(idx)
            self.frame_img.config(bg='blue')


def main():
    root = tk.Tk()
    root.geometry('2000x800')
    segviewer = SegViewer(root)
    root.mainloop()
 

if __name__ == '__main__':
    main()


