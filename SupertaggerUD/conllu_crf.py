# -*- coding:utf-8 -*-
'''
Created on Feb 18, 2017

@author: burak
'''

import logging, re
from string import punctuation
from conllu_ccg import CCG_CoNLL_UD

LOG_LEVEL = logging.INFO

class CCG_CoNLL_UD_crf(CCG_CoNLL_UD):
    '''
    CCG with CoNLL Universal Dependencies
    '''

    def to_features(self):
        '''
        features:
        w : word
        p : universal postag
        x : extended postag
        no supertag features for crf
        '''
        
        for i in self._word_range:
            # supertags for only previous tokens
            feats = {}
            # current word
            feats['w'] = self._sent[i][0]
            feats['p'] = self._sent[i][1]
            if self.extended:
                feats['x'] = self._sent[i][2]
            # previous words
            for j in range(self.window):
                n = j+1
                s = str(n)
                p = i-n
                feats['w-'+s] = self._sent[p][0]
                feats['p-'+s] = self._sent[p][1]
                if self.extended:
                    feats['x-'+s] = self._sent[p][2]
            # following words
            for j in range(self.window):
                n = j+1
                s = str(n)
                p = i+n
                feats['w+'+s] = self._sent[p][0]
                feats['p+'+s] = self._sent[p][1]
                if self.extended:
                    feats['x+'+s] = self._sent[p][2]
                    
            # prefixes & suffixes
            w = self._sent[i][0]
            for j in range(6)[1:]:
                feats['prefix_'+str(j)] = w[:j]
            for j in range(5)[1:]:
                feats['suffix_'+str(j)] = w[-1*j:]
            
            # flags
            hyphen = re.compile('-')
            number = re.compile('\d')
            uppercase = re.compile('[A-Z]')
            punct = re.compile(r'[{}]'.format(punctuation))
            #punct = re.compile('[{' + re.escape(punctuation) + '}]')
            #punct = re.compile('[{}]'.format(re.escape(punctuation)))
            
            feats['hyp'] = True if hyphen.search(w) else False
            feats['num'] = True if number.search(w) else False
            feats['upp'] = True if uppercase.search(w) else False
            feats['pnc'] = True if punct.search(w) else False
            
            
            self._features.append(feats)


if __name__ == '__main__':
    
    with open('data_en/train_tiny.conllu', 'r', encoding='utf-8') as sample:
        sents = sample.read().strip().split('\n\n')
    ccg = CCG_CoNLL_UD_crf(sents[3].strip().split('\n'), window=3)
    print(ccg)
    ccg.print_feats()
    
    ccg = CCG_CoNLL_UD_crf(sents[3].strip().split('\n'), window=2, extended=False)
    print(ccg)
    ccg.print_feats()
    
    ccg = CCG_CoNLL_UD_crf(sents[3].strip().split('\n'), window=2, extended=False, tag_simplify=3)
    print(ccg)
    ccg.print_feats()

