# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

from time import time
import logging
import pickle
from data import Data
from conllu import CoNLL_UD
import networkx as nx
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
# from sklearn.metrics import  precision_score, recall_score, f1_score

LOG_LEVEL = logging.INFO


class Supertagger(object):
    '''
    classdocs
    '''


    def __init__(self, train=None, test=None, log_level=LOG_LEVEL, conllu_cls=CoNLL_UD):
        '''
        Constructor
        '''
        
        self.logger = None
        self.init_logging(log_level)
        
        self.conll_cls = conllu_cls
        
        self.train = None
        self.test = None
        # if given read data
        if train or test:
            t0 = t = time()
            self.logger.info('started feature extraction')
        if train:
            self.train = Data(train, cls=self.conll_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted training features')
            self.logger.info('processed ' + str(self.train.num_sents) + ' sentences')
        if test:
            self.test = Data(test, cls=self.conll_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted test features')
            self.logger.info('processed ' + str(self.test.num_sents) + ' sentences')
        
        # logistic regression / maximum entropy classifier
        self.tagger = LogisticRegression(verbose=0)
        self.vectorizer = DictVectorizer()
    
    
    def fit(self, train=None):
        '''
        '''
        t0 = t = time()
        self.logger.info('started training')
        #
        if train:
            self.train = Data(train, cls=self.conll_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted training features')
            self.logger.info('processed ' + str(self.train.num_sents) + ' sentences')
        #
        if not self.train:
            self.logger.error('cannot train without the training data')
            return
        
        #   
        train_matrix = self.vectorizer.fit_transform(self.train.features)
        self.logger.info(str(len(self.vectorizer.get_feature_names())) + ' features')
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's vectorized features')
        
        #
        self.tagger.fit(train_matrix, self.train.labels)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's trained model')
        
        
    def evaluate(self, test=None):
        '''
        '''
        t0 = t = time()
        self.logger.info('started evaluation')
        #
        if test:
            self.test = Data(test, cls=self.conll_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted test features')
            self.logger.info('processed ' + str(self.test.num_sents) + ' sentences')
        #
        if not self.test:
            self.logger.error('cannot evaluate without the test data')
            return
        
        #
        test_matrix = self.vectorizer.transform(self.test.features)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's vectorized features')
        
        #
        y_true = self.test.labels
        y_pred = self.tagger.predict(test_matrix)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's generated predictions')
        
        #
        #precision = 100 * precision_score(y_true, y_pred, average='micro')
        #recall = 100 * recall_score(y_true, y_pred, average='micro')
        #f1 = 100 * f1_score(y_true, y_pred, average='micro')
        accuracy = 100 * accuracy_score(y_true, y_pred)
        #self.logger.info('Precision : ' + '{:.2f}'.format(precision))
        #self.logger.info('Recall    : ' + '{:.2f}'.format(recall))
        #self.logger.info('F1        : ' + '{:.2f}'.format(f1))
        self.logger.info('Accuracy  : ' + '{:.2f}'.format(accuracy))
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's evaluated test data')
        
        return accuracy
    
    
    def tag(self, test=None, save=None):
        '''
        if save is not given write to stdout 
        '''
        t0 = t = time()
        self.logger.info('started tagging')
        #
        if test:
            self.test = Data(test, cls=self.conll_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted features')
            self.logger.info('processed ' + str(self.test.num_sents) + ' sentences')
        #
        if not self.test:
            self.logger.error('need data to tag')
            return
        
        #
        test_matrix = self.vectorizer.transform(self.test.features)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's vectorized features')
        
        #
        y_pred = self.tagger.predict(test_matrix)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's generated predictions')
        
        for i, sent in enumerate(self.test.sentences):
            s,e = self.test.sent_indices[i]
            pred = y_pred[s:e]
            nodes = sorted(sent.graph.nodes(), key=lambda n: sent.graph.node[n]['POSITION'])
            for i,w in enumerate(nodes):
                sent.graph.node[w]['MISC'] = 'cat='+pred[i]
        
        if not save:
            for sent in self.test.sentences:
                print(sent, end='')
        else:
            with open(save, 'w', encoding='utf-8') as f:
                for sent in self.test.sentences:
                    f.write(str(sent))
    
    
    def tag_sent(self, sent):
        '''
        '''
    
    
    def save(self, file_name):
        '''
        '''
        f = open(file_name, 'wb')
        pickle.dump([self.tagger, self.vectorizer], f)
        f.close()
        self.logger.info('saved model to ' + file_name)
    
    
    def load(self, file_name):
        '''
        '''
        f = open(file_name, 'rb')
        [self.tagger, self.vectorizer] = pickle.load(f)
        f.close()
        self.logger.info('loaded model from ' + file_name)
    
    
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



if __name__ == '__main__':
    
    '''
    tagger = Supertagger(train='data_en/train.conllu', test='data_en/test.conllu')
    tagger.fit()
    tagger.save('models/supertagger.pickle')
    print(tagger.evaluate())
    '''
    
    from conllu_10 import CoNLL_UD_10
    print('CoNLL_UD_10 load from model\n')
    tagger = Supertagger(conllu_cls=CoNLL_UD_10)
    tagger.load('models_dev/supertagger_10.pickle')
    tagger.tag(test='data_en/test_tiny.conllu')
    tagger.tag(test='data_en/test_tiny.conllu', save='data_en/test_tiny_tagger.conllu')
    print('\n')
    
'''
import numpy as np
# NaN check : use this in fit() after dict_vec.fit_transform()
print(train_matrix.data.shape)
print(np.isnan(train_matrix.data).any())
print(np.where(np.isnan(train_matrix.data)))
print(np.isnan(train_matrix.data))
print(np.isnan(train_matrix.data).sum())
print(train_matrix.data[np.isnan(train_matrix.data)])
'''
