# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

import pandas as pd
from conllu import CoNLL_UD

class Data(object):
    '''
    classdocs
    '''

    def __init__(self, file_name, cls=CoNLL_UD):
        '''
        Constructor
        '''
        self.file_name = file_name
        self.cls=cls
        
        self._words = []
        self._sentences = []
        self.sent_indices = []
        
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
        s,e = self.sent_indices[i]
        return self.words[s:e]
    
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
                conll = self.cls(sent)
                self._sentences.append(conll)
                s = len(self._words)
                self.sent_indices.append((s,s+len(conll.sentence)))
                self._words.extend(conll.sentence)
                # fill missing values for features
                df = pd.DataFrame(conll.features)
                df.fillna('', inplace=True)
                self._features.extend(df.to_dict('records'))
                # labels
                self._labels.extend(conll.supertags)
                self.num_sents += 1
                sent = []
                # del logger
                del conll
            else:
                sent.append(line.strip())
    


if __name__ == '__main__':
    
    def print_feat_dict(d):
        keys = ['idx', 'pos', 'pos_x', 'head', 'head_pos', 'head_pos_x', 'head_position', 'head_rel', 'dep_count']
        for k in keys + sorted([k for k in d if k not in keys], key=lambda x: (int(x.split('_')[1]), x)):
            print(k.ljust(12) +'\t'+ str(d[k]))
    
    data = Data('data_en/test_tiny.conllu')
    print(data.num_sents)
    
    print(data.sentences[1])
    print(data.get_sentence(1))
    
    for w,l,f in zip(data.words[18:18+13], data.labels[18:18+13], data.features[18:18+13]):
        print(w +'\t'+ l)
        print_feat_dict(f)
        print()
    
    