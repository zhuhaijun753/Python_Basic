# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 11:03:28 2016

@author: Hanbing Guo
"""

import struct as st
import pylab as pl
import numpy as np
import scipy as sp
import os
import scipy.misc as sm

#is_centered not 0 means centered data, 1 means orignal data stored in numpy array
def load_mnist(is_centered = False, is_show = False):    
#==============================================================================
#     This block of code load MNIST dataset into memory
#==============================================================================
    '''Specifiy file path'''
    train_image_filename = './image_process/MNIST/train-images.idx3-ubyte'
    train_label_filename = './image_process/MNIST/train-labels.idx1-ubyte'
    test_image_filename = './image_process/MNIST/t10k-images.idx3-ubyte'
    test_label_filename = './image_process/MNIST/t10k-labels.idx1-ubyte'
    '''Load train image data, store it into a n-dimensional numpy array'''
    with open(train_image_filename, 'rb') as binfile:
        buf = binfile.read()
        '''Index to indicate location of file'''
        index = 0 
        '''Use big-endian to read data information'''
        magic, numImages, rows, cols = st.unpack_from('>IIII', buf, index)
        train_image = np.zeros((numImages, rows, cols))
        index += st.calcsize('>IIII')
        buffer_len = st.calcsize('>784B') 
        for i in range(numImages):
            train_image[i,:,:] = np.array(st.unpack_from('>784B', buf, index)).reshape(rows, cols)
            index += buffer_len                
        
    with open(train_label_filename, 'rb') as binlabel:
        buflabel = binlabel.read()
        label_index = 0
        lmagic, numLabels = st.unpack_from('>II',buflabel, label_index)
        label_index += st.calcsize('>II')
        train_label = np.zeros((numLabels,), dtype = np.uint8)
        buffer_len = st.calcsize('>1B')
        for i in range(numLabels):
            train_label[i] = np.uint8(st.unpack_from('1B',buflabel, label_index))
            label_index += buffer_len
    
    with open(test_image_filename, 'rb') as test_binfile:
        buf_test = test_binfile.read()
        index_test = 0
        t_magic, t_numImages, t_rows, t_cols = st.unpack_from('>IIII',buf_test, index_test)
        index_test += st.calcsize('>IIII')
        test_image = np.zeros((t_numImages, t_rows, t_cols))
        buffer_len = st.calcsize('>784B')
        for i in range(t_numImages):
            test_image[i,:,:] = np.array(st.unpack_from('>784B', buf_test, index_test)).reshape(t_rows, t_cols)
            index_test += buffer_len
    
    with open(test_label_filename, 'rb') as test_binlabel:
        buf_test_label = test_binlabel.read()
        index_label = 0
        lt_magic,lt_numLabels = st.unpack_from('>II', buf_test_label, index_label)
        index_label += st.calcsize('>II')
        test_label = np.zeros((lt_numLabels,), dtype = np.uint8)
        buffer_len = st.calcsize('>1B') 
        for i in range(lt_numLabels):
            test_label[i] = np.uint8(st.unpack_from('1B', buf_test_label, index_label))
            index_label += buffer_len     
    
    #Calculate mean image for entire data set
    mean_image = np.zeros((rows, cols))
    for i in range(numImages):
        mean_image += train_image[i,:,:]
    
    mean_image /= numImages
    
    '''Zero mean process'''
    if is_centered:
        train_image -= mean_image
        test_image -= mean_image
    '''
    It's ok, The order in MNIST has been shuffled.
    If it did not, you could use this index
    
    >>>index = np.arange(numImages)
    >>>np.ramdom.shuffle(index)
    '''
    if is_show:
        pl.figure('Mean image')
        pl.gray()
        pl.imshow(mean_image)        
        sp.misc.imsave('mean_image.bmp', mean_image)

    
    return train_image, train_label, test_image, test_label, mean_image

   
def unfold_mnist():
#==============================================================================
#     This block of code will unfold mnist dataset, and store it to disk
#      as image format. At same time each image will locate on floder named
#     with its label, but name is random number
#==============================================================================
    #Import mnist dataset, this data will store in each numpy array
    train_images, train_labels, test_images, test_labels, mean = load_mnist()
    #Specify path of store image
    root_path = './mnist_images//'
    if not os.path.isdir(root_path):
        os.mkdir(root_path)
    
    train_path = root_path + 'train_images//'
    if not os.path.isdir(train_path):
        os.mkdir(train_path)
        
    test_path = root_path + 'test_images//'
    if not os.path.isdir(test_path):
        os.mkdir(test_path)
        
    '''Achive number of train and test image'''
    train_num = train_labels.shape[0]
    test_num = test_labels.shape[0]
    
    #Images will store at different folder as their labels, so create floder firstly.
    labels = np.unique(train_labels)
    train_label_num = len(labels)
    for i in range(train_label_num):
        dst_path = train_path + str(labels[i])
        if not os.path.isdir(dst_path):
            os.mkdir(dst_path)
    
    labels = np.unique(test_labels)
    test_label_num = len(labels)
    for i in range(test_label_num):
        dst_path = test_path + str(labels[i])
        if not os.path.isdir(dst_path):
            os.mkdir(dst_path)
    
    #Store image to floder as their label
    for i in range(train_num):
        label = train_labels[i]
        dst_path = train_path + str(label)
        sm.imsave(dst_path + '//' + str(i) + '.bmp', train_images[i,...])
            
    for i in range(test_num):
        label = test_labels[i]
        dst_path = test_path + str(label)
        sm.imsave(dst_path + '//' + str(i) + '.bmp', test_images[i,...])
        
        
def gen_file_list(file_path, path_head = True):
#==============================================================================
#     This block of code will generate a file list that contain names of image
#     and its label, at same time there will be an additional file created which
#     list folder name and its label
#     path_head means every line in the list will assign image path first then
#     label, vice versa.
#==============================================================================
    if len(file_path) == 0:
        print('Please input folder path')
    '''Setting image format that will be accepted'''
    legal_format = ['.bmp','.jpg','.JEPG','.png','.tif']
    label_mapping = file_path + '/label_word.txt'    
    images_list = file_path + '/images_list.txt'    
    '''Delete old file'''
    if os.path.exists(label_mapping):
        os.remove(label_mapping)   
    if os.path.exists(images_list):
        os.remove(images_list)
    

    '''List all directories'''
    dir_list = [f for f in os.listdir(file_path) \
                if os.path.isdir(os.path.join(file_path, f))]

    '''Use a dict to store a relationship between floder name and label'''
    label_map = {}
    for i in range(len(dir_list)):
        label_map[i] = dir_list[i]

    '''Save mapping table to file'''
    with open(label_mapping, 'w') as fh:
        for i in range(len(dir_list)):
            fh.write(str(i) + ' ' + label_map[i] + '\n')
    
    #==============================================================================
    #     Save file list
    #     1.Delete all folder in each image set;
    #     2.List all file in each image set;
    #     3.Wirte image and its relative path to file list.
    #==============================================================================
    for i in range(len(dir_list)):
       sub_dir_list = [f for f in os.listdir(os.path.join(file_path, dir_list[i])) \
                   if os.path.isdir(os.path.join(file_path, dir_list[i], f))]
       for j in range(len(sub_dir_list)):
           os.rmdir(os.path.join(file_path, dir_list[i], sub_dir_list[j])) 
           
    if path_head:
        fw = lambda x, y : label_map[x] + '/' + sub_file_list[y] + ' ' + str(x) + '\n'
    else:
        fw = lambda x, y : str(x) + ' ' + label_map[x] + '/' + sub_file_list[y] + '\n'
    
    with open(images_list, 'w') as fh:
       for i in range(len(dir_list)):
           sub_file_path = os.path.join(file_path, label_map[i])
           sub_file_list = [f for f in os.listdir(sub_file_path)]           
           for j in range(len(sub_file_list)):
               '''File filter'''
               if os.path.splitext(sub_file_list[j])[1] in legal_format:
                  fh.write(fw(i, j))