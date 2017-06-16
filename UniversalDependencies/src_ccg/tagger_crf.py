# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

from time import time
import logging
import pickle
from data_crf import Data
from conllu_ccg import CCG_CoNLL_UD
import sklearn_crfsuite

from sklearn_crfsuite.metrics import flat_accuracy_score

#from sklearn.metrics import accuracy_score
# from sklearn.metrics import  precision_score, recall_score, f1_score

LOG_LEVEL = logging.INFO


class Supertagger(object):
    '''
    CRF instead Logistic
    '''


    def __init__(self, train=None, test=None, log_level=LOG_LEVEL, sent_cls=CCG_CoNLL_UD):
        '''
        Constructor
        '''
        
        self.logger = None
        self.init_logging(log_level)
        
        self.sent_cls = sent_cls
        
        self.train = None
        self.test = None
        # if given read data
        if train or test:
            t0 = t = time()
            self.logger.info('started feature extraction')
        if train:
            self.train = Data(train, sent_cls=self.sent_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted training features')
            self.logger.info('processed ' + str(self.train.num_sents) + ' sentences')
        if test:
            self.test = Data(test, sent_cls=self.sent_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted test features')
            self.logger.info('processed ' + str(self.test.num_sents) + ' sentences')
        
        # conditional random fields
        self.tagger = sklearn_crfsuite.CRF( algorithm='lbfgs',
                                            c1=0.1,
                                            c2=0.1,
                                            max_iterations=100,
                                            all_possible_transitions=True
                                            )
    
    
    def fit(self, train=None):
        '''
        '''
        t0 = t = time()
        self.logger.info('started training')
        #
        if train:
            self.train = Data(train, sent_cls=self.sent_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted training features')
            self.logger.info('processed ' + str(self.train.num_sents) + ' sentences')
        #
        if not self.train:
            self.logger.error('cannot train without the training data')
            return
        
        #
        self.tagger.fit(self.train.features, self.train.labels)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's trained model')
        
        
    def evaluate(self, test=None):
        '''
        '''
        t0 = t = time()
        self.logger.info('started evaluation')
        #
        if test:
            self.test = Data(test, sent_cls=self.sent_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted test features')
            self.logger.info('processed ' + str(self.test.num_sents) + ' sentences')
        #
        if not self.test:
            self.logger.error('cannot evaluate without the test data')
            return
        #
        y_true = self.test.labels
        y_pred = self.tagger.predict(self.test.features)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's generated predictions')
        
        #
        accuracy = 100 * flat_accuracy_score(y_true, y_pred)
        self.logger.info('Accuracy  : ' + '{:.2f}'.format(accuracy))
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's evaluated test data')
        
        return accuracy
    
    
    def tag(self, test=None, save=None):
        '''
        if save is not given write to stdout 
        '''
        '''
        '''
        t0 = t = time()
        self.logger.info('started tagging')
        #
        if test:
            self.test = Data(test, sent_cls=self.sent_cls)
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's extracted test features')
            self.logger.info('processed ' + str(self.test.num_sents) + ' sentences')
        #
        if not self.test:
            self.logger.error('cannot tag without the test data')
            return
        #
        y_pred = self.tagger.predict(self.test.features)
        t0, t = t, time()
        self.logger.info('{:.2f}'.format(t-t0) + 's generated predictions')

        # print accuracy, if given data contains labels 
        accuracy = 0.0
        y_true = self.test.labels
        if [tag for s_true in y_true for tag in s_true if tag != '_']:
            accuracy = 100 * flat_accuracy_score(y_true, y_pred)
            self.logger.info('Accuracy  : ' + '{:.2f}'.format(accuracy))
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's tagged test data')

        # set ccg categories of the sentences
        self.test.update_tags(y_pred)
        #
        if not save:
            for sent in self.test.sentences:
                print(sent)
        else:
            with open(save, 'w', encoding='utf-8') as f:
                for sent in self.test.sentences:
                    f.write(str(sent)+'\n')
            t0, t = t, time()
            self.logger.info('{:.2f}'.format(t-t0) + 's saved as ' + save)

        return accuracy
        
    
    def tag_sent(self, sent):
        '''
        '''
    
    
    def save(self, file_name):
        '''
        '''
        f = open(file_name, 'wb')
        pickle.dump(self.tagger, f)
        f.close()
        self.logger.info('saved model to ' + file_name)
    
    
    def load(self, file_name):
        '''
        '''
        f = open(file_name, 'rb')
        self.tagger = pickle.load(f)
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
    
    from conllu_crf import CCG_CoNLL_UD_crf
    tagger = Supertagger(train='data_en/test_tiny.conllu', 
                         test='data_en/test_tiny.conllu',
                         sent_cls=CCG_CoNLL_UD_crf)
    tagger.fit()
    print(tagger.evaluate())
    
    
'''
print('CoNLL_UD_10 load from model\n')
tagger = Supertagger(conllu_cls=CCG_CoNLL_UD)
tagger.load('models_dev/supertagger.pickle')
tagger.tag(test='data_en/test_tiny.conllu')
tagger.tag(test='data_en/test_tiny.conllu', save='data_en/test_tiny_tagger.conllu')
print('\n')
'''

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
    
