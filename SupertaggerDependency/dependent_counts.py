# -*- coding:utf-8 -*-
'''
Created on Feb 25, 2017

@author: BurakKerim
'''


from data import Data
from collections import Counter

from conllu import CoNLL_UD

class CoNLL_UD_dc(CoNLL_UD):
    '''
    just dep counts
    '''
    def to_features(self):
        for w in sorted(self.graph.nodes(), key=lambda n: self.graph.node[n]['POSITION']):
            if '-' in w:
                continue
            feats = {}
            # dep count
            d = self.graph.node[w]
            feats['dep_count'] = len(d.get('DEPENDENTS', []))
            # head dep count
            h = d['HEAD']
            if h != '0':
                dh = self.graph.node[h]
                feats['h_dep_count'] = len(dh.get('DEPENDENTS', []))
            else:
                feats['h_dep_count'] = 0
            self._features.append(feats)
    
    def print_feat_dict(self, d):
        for k in ['dep_count', 'h_dep_count']:
            print(k.ljust(12) +'\t'+ str(d[k]))
    
    def print_feats(self):
        for feat in self.features:
            print()
            self.print_feat_dict(feat)

'''
with open('data_en/00/wsj_0045.conllu', 'r', encoding='utf-8') as sample:
    sents = sample.read().strip().split('\n\n')
deps = CoNLL_UD_dc(sents[26].strip().split('\n'))
#print(deps)
deps.print_feats()
'''
            
data = Data('data_en/train.conllu', cls=CoNLL_UD_dc)
print('Stats from sections 02-05:')


dep_counts = [fd['dep_count'] for fd in data.features]
dc_hist = Counter(dep_counts)
total = len(dep_counts)
print('total words: '+str(total))
cum = 0
print('dependent counts:')
print('num percentage cumulative count')
for count in sorted(dc_hist):
    perc = 100*dc_hist[count]/total
    cum += perc
    print(str(count).rjust(2), 
          '{:6.2f}'.format(perc), '{:6.2f}'.format(cum),
          str(dc_hist[count]).rjust(6))

dep_counts = [fd['h_dep_count'] for fd in data.features]
dc_hist = Counter(dep_counts)
total = len(dep_counts)
print('total words: '+str(total))
cum = 0
print('head dependent counts:')
print('num percentage cumulative count')
for count in sorted(dc_hist):
    perc = 100*dc_hist[count]/total
    cum += perc
    print(str(count).rjust(2), 
          '{:6.2f}'.format(perc), '{:6.2f}'.format(cum),
          str(dc_hist[count]).rjust(6))
