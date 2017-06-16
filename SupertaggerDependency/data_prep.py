# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

import os

data_dir = 'merged/'

def merge_sections(list_of_sections, out_file):
    
    fo = open(out_file, 'w', encoding='utf-8')
    
    for sec in list_of_sections:
        for fn in os.listdir(data_dir+sec):
            with open(data_dir+sec+'/'+fn) as fi:
                fo.write(fi.read())
    
    fo.close()


# sections 02-21 for training
merge_sections(['{:02d}'.format(i) for i in range(2,22)], data_dir+'train_02_21.conllu')

merge_sections(['00'], data_dir+'dev_00.conllu')

merge_sections(['23'], data_dir+'test_23.conllu')
