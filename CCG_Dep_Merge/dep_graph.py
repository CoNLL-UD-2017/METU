# -*- coding:utf-8 -*-
'''
Created on 6 �ub 2017

@author: BurakKerim
'''

import os
import subprocess
import logging
import networkx as nx
from templates import *

LOG_LEVEL = logging.DEBUG

class DepGraph(object):
    '''
    classdocs
    '''


    def __init__(self, file_name, log_level=LOG_LEVEL):
        '''
        Constructor
        '''
        
        self._graphs = []
        self.file_name = file_name
             
        self.logger = None
        self.init_logging(log_level)
    
    
    @property
    def graphs(self):
        return self._graphs
    

    def read_graphs(self, file_name):
        '''
        '''
        raise NotImplementedError
    
    
    def to_tikz(self, file_name):
        '''
        '''
        raise NotImplementedError
    

    def build_tex(self, file_name):
        '''
        '''
        cwd = os.getcwd()
        dir_name = os.path.dirname(file_name)
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        extension = os.path.splitext(file_name)[-1]
        
        self.logger.debug('directories and base name: ' + cwd +' - '+ dir_name +' - '+ base_name)
        
        if dir_name:
            os.chdir(dir_name)
        
        # '-interaction=batchmode' needed to prevent freezing on errors
        p = subprocess.Popen(['xelatex', '-interaction=batchmode', base_name+extension], 
                                        stdin=None,
                                        stdout=open(os.devnull, 'w'),
                                        stderr=open(base_name+'.err', 'w'),
                                        )
        try:
            p.wait()
            if p.returncode == 0:
                os.remove(base_name+'.aux')
                os.remove(base_name+'.log')
                os.remove(base_name+'.err')
                #os.remove(base_name+'.synctex.gz')
                self.logger.info('built pdf and cleaned for ' + base_name+'.pdf')
            else:
                self.logger.error('latex error, xelatex subprocess returned ' + str(p.returncode))
                self.logger.error('\t check files ' + base_name+'.err and '  + base_name+'.log')
        except Exception as e:
            self.logger.error(str(e))
        
        os.chdir(cwd)
    

    def to_tex(self, save_path='', separate=False, build=True):
        '''
        '''
        #
        dir_name = os.path.dirname(save_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        #    
        if not save_path:
            base_name = os.path.splitext(self.file_name)[0]
            extension = '.tex'
        else:
            base_name = os.path.splitext(save_path)[0]
            extension = os.path.splitext(save_path)[-1]
                    
        if separate:
            for g in self._graphs:
                tex = tex_header
                tex += self.to_tikz(g, caption=escape(g.graph['SENT_ID']))
                tex += tex_footer
                file_name = base_name+'_'+str(g.graph['SENT_INDEX'])+extension
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(tex)
                    self.logger.info('saved as ' + file_name)
                if build:
                    self.build_tex(file_name)
        else:
            tex = tex_header
            for g in self._graphs:
                tex += self.to_tikz(g, caption=escape(g.graph['SENT_ID']))
            tex += tex_footer
            file_name = base_name+extension
            with open(base_name+extension, 'w', encoding='utf-8') as f:
                f.write(tex)
                self.logger.info('saved as ' + file_name)
            if build:
                self.build_tex(file_name)

    
    def save(self, save_path):
        dir_name = os.path.dirname(save_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        text = str(self)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(text)
        self.logger.info('saved dep file as ' + save_path)
       

    def init_logging(self, log_level):
        '''
        logging config and init
        '''
        if not self.logger:
            formatter = logging.Formatter('%(asctime)s-|%(name)s:%(funcName)12s|-%(levelname)s-> %(message)s')
            self.handler = logging.StreamHandler()
            self.handler.setLevel(log_level)
            self.handler.setFormatter(formatter)
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.addHandler(self.handler)
            self.logger.setLevel(log_level)
    
    
    def __del__(self):
        # remove handler or else duplicate logs
        self.logger.removeHandler(self.handler)
        # ? 
        del self.logger
        

