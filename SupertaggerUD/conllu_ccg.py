# -*- coding:utf-8 -*-
'''
Created on Feb 18, 2017

@author: burak
'''

import logging, re


LOG_LEVEL = logging.INFO

class CCG_CoNLL_UD():
    '''
    CCG with CoNLL Universal Dependencies
    '''

    def __init__(self, sentence, window=2, extended=True, tag_simplify=3, log_level=LOG_LEVEL):
        '''
        sentence: list of lines from conll similar data
        
        window: number of words to use before and after
        extended: whether to use xpostags
        tag_simplify: ccg tag simplification
                    0: none
                    1: subcategories
                    2: directions
                    3: both subcategories and directions
        '''
        self.sentence_conllu = sentence
        self.window = window
        self.extended = extended
        self.simple = tag_simplify
        
        # list of tuples of tokens, pos and ccg tags
        self._sent = []
        # list of words(tokens)
        self._tokenized_sent = []
        # list of feat dicts
        self._features = []
        # list of ccg tags
        self._supertags = []
        
        self.keys = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
             
        self.logger = None
        self.init_logging(log_level)
        
        self.process(self.sentence_conllu)
        
        self._word_range = range(len(self._sent))[self.window:-1*self.window]
        
        self.to_features()

    
    @property
    def features(self):
        return self._features
    
    @property
    def supertags(self):
        for i in self._word_range:
            self._supertags.append(self._sent[i][-1])
        return self._supertags
    
    @property
    def sentence(self):
        for i in self._word_range:
            self._tokenized_sent.append(self._sent[i][0])
        return self._tokenized_sent
    
    
    def to_attr(self, line):
        '''
        returns conllu attribute dictionary
        '''
        values = [token.strip() for token in line.strip().split('\t')]
        assert len(self.keys) == len(values), 'number of fields do not match'
        return {k:v for k,v in zip(self.keys, values)}
    
    
    def clear_tag(self, supertag):
        '''
        remove subcategories from supertags
        (S[dcl]\\NP)/(S[b]\\NP)   ->  (S\\NP)/(S\\NP)       ->  (S-NP)-(S-NP)
        ((S\\NP)\(S\\NP))/N[num]  ->  ((S\\NP)\\(S\\NP))/N  ->  ((S-NP)-(S-NP))-N
        
        maybe also remove directions from slashes
        
        self.simple:
        0: none
        1: subcategories
        2: directions
        3: both subcategories and directions
        '''
        if self.simple % 2 == 1:
            supertag = re.sub('\[[^\]]*\]', '', supertag)
        if self.simple // 2 == 1:
            supertag = re.sub(r'[\\/]', '-', supertag)
        return supertag
    
    
    def misc_attr(self, s):
        '''
        example MISC field:
            cat=((S[b]\\NP)/PP)/NP|args=2:1,11:3,12:2|preds=8:2,16:2
            {'CAT': '((S\\NP)/PP)/NP', # or '((S-NP)-PP)-NP'
            'PREDS': [('8', '2'), ('16', '2')], 
            'ARGS': [('2', '1'), ('11', '3'), ('12', '2')]}
        
        consider misc data in the treebank
        consider misc data without =
            arabic
        consider multiple =
            catalan
            MWE=Embassaments=_Transvasaments
        '''
        d = {}
        self.logger.debug(s)
        if s != '_':
            #tmp = {k:v for t in s.split('|') for k,v in [t.split('=')]}
            misc = s.split('|')
            for tmp in misc:
                if 'cat=' in tmp:
                    # d['CAT'] = tmp['cat']
                    _, v = tmp.split('=')
                    d['CAT'] = self.clear_tag(v)
                elif 'preds=' in tmp:
                    _, v = tmp.split('=')
                    d['PREDS'] = [(i,p) for t in v.split(',') for i,p in [t.split(':')]]
                elif 'args=' in tmp:
                    _, v = tmp.split('=')
                    d['ARGS'] = [(i,p) for t in v.split(',') for i,p in [t.split(':')]]
                elif '=' in tmp:
                    kv = tmp.split('=')
                    k, v = kv[0], '='.join(kv[1:])
                    d[k] = v
                else:
                    d['OTHER'] = tmp
        self.logger.debug(str(d))
        return d
    
    
    def process(self, sentence):
        '''
        
        '''
        words = []
        for line in sentence:
            # skip comments    
            if line.strip()[0] != '#':
                # words
                w = self.to_attr(line)
                # no multiword tokens
                if '-' not in w['ID']:
                    words.append(w)
        
        if words == []:
            self.logger.error('empty sentence_conllu')
            return
        
        # prepend with dummy tags
        for i in range(self.window):
            n = self.window - i
            self._sent.append(['word-'+str(n), 'POS-'+str(n),  'XPOS-'+str(n), 'CCG-'+str(n)])
        
        # add words
        for i in words:
            w = i['FORM']
            p = i['UPOSTAG']
            x = i['XPOSTAG']
            c = self.misc_attr(i['MISC'])['CAT']
            self._sent.append([w, p, x, c])
        
        # append with dummy tags
        for i in range(self.window):
            n = i + 1
            self._sent.append(['word+'+str(n), 'POS+'+str(n), 'XPOS+'+str(n), 'CCG+'+str(n)])


    def to_features(self):
        '''
        features:
        w : word
        p : universal postag
        x : extended postag
        c : supertag 
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
                feats['c-'+s] = self._sent[p][-1]
            # following words
            for j in range(self.window):
                n = j+1
                s = str(n)
                p = i+n
                feats['w+'+s] = self._sent[p][0]
                feats['p+'+s] = self._sent[p][1]
                if self.extended:
                    feats['x+'+s] = self._sent[p][2]
            
            self._features.append(feats)
    
    
    def update_supertags(self, pred):
        for i in self._word_range:
            self._sent[i][3] = pred[i-self.window]
    
    
    def print_feat_dict(self, d):
        for k in sorted(d):
            print(k.ljust(12) +'\t'+ str(d[k]))
    
    
    def print_feats(self):
        for feat in self.features:
            self.print_feat_dict(feat)
            print()


    def __repr__(self):
        s = ''
        for i in self._word_range:
            s += '\t'.join(self._sent[i]) +'\n'
        return s
    
    
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
    
    with open('data_en/train_tiny.conllu', 'r', encoding='utf-8') as sample:
        sents = sample.read().strip().split('\n\n')
    ccg = CCG_CoNLL_UD(sents[2].strip().split('\n'), window=3)
    print(ccg)
    ccg.print_feats()
    
    ccg = CCG_CoNLL_UD(sents[2].strip().split('\n'), window=2, extended=False)
    print(ccg)
    ccg.print_feats()
    
    ccg = CCG_CoNLL_UD(sents[2].strip().split('\n'), window=2, extended=False, tag_simplify=3)
    print(ccg)
    ccg.print_feats()

