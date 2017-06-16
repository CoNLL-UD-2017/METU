# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

import pandas as pd
from conllu_crf import CCG_CoNLL_UD_crf

class Data(object):
    '''
    classdocs
    '''

    def __init__(self, file_name, sent_cls=CCG_CoNLL_UD_crf):
        '''
        Constructor
        '''
        self.file_name = file_name
        self.cls=sent_cls
        
        self._words = []
        self._sentences = []
        
        self._features = []
        self._labels = []
        
        self.num_sents = 0
        
        self.read_data()
    
    @property
    def words(self):
        return self._words
    
    @property
    def sentences(self):
        '''
        return connlu objects
        '''
        return self._sentences
    
    def get_sentence(self, i):
        '''
        return tokenized sentence
        '''
        return self._words[i]
    
    @property
    def features(self):
        return self._features
    
    @property
    def labels(self):
        return self._labels
    
    
    def read_data(self):
        '''
        '''
        f = open(self.file_name, 'r', encoding='utf-8')
        
        sent = []
        for line in f:
            if line.strip() == '':
                #print(sent)
                s = self.cls(sent)
                self._sentences.append(s)
                #l = len(self._words)
                self._words.append(s.sentence)
                # fill missing values for features
                df = pd.DataFrame(s.features)
                df.fillna('', inplace=True)
                self._features.append(df.to_dict('records'))
                # labels
                self._labels.append(s.supertags)
                self.num_sents += 1
                sent = []
                # del logger
                del s
            else:
                sent.append(line.strip())
    
    
    def update_tags(self, y_pred):
        for i, sent in enumerate(self.sentences):
            sent.update_supertags(y_pred[i])


if __name__ == '__main__':
    
    def print_feat_dict(d):
        for k in sorted(d):
            print(k.ljust(12) +'\t'+ str(d[k]))
    
    '''
    from conllu_2 import CCG_CoNLL_UD_2
    data = Data('data_en/test_tiny.conllu', sent_cls=CCG_CoNLL_UD_2)
    print(data.num_sents)
    
    print(data.sentences[1])
    print(data.get_sentence(1))
    print()
    
    for w,l,f in zip(data.words[18:18+13], data.labels[18:18+13], data.features[18:18+13]):
        print(w +'\t'+ l)
        print_feat_dict(f)
        print()
    
    
    from ccg_2 import CCG_2
    data = Data('data_tr_ms_conll/lexemic_test_1.txt', sent_cls=CCG_2)
    print(data.num_sents)
    
    i = 1
    print(data.sentences[i])
    print(data.get_sentence(i))
    print()
    for w,l,f in zip(data.words[i], data.labels[i], data.features[i]):
        print(w +'\t'+ l)
        print_feat_dict(f)
        print()
    '''
    