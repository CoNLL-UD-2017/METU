# -*- coding:utf-8 -*-
'''
Created on Feb 18, 2017

@author: burak
'''

import logging
from conllu import CoNLL_UD


LOG_LEVEL = logging.INFO

class CoNLL_UD_2(CoNLL_UD):
    '''
    different set of features
    '''


    def to_features(self):
        '''
        do not use id's and extended postag's
        '''
        for w in sorted(self.graph.nodes(), key=lambda n: self.graph.node[n]['POSITION']):
            if '-' in w:
                continue
            feats = {}
            # node dict
            d = self.graph.node[w]
            feats['pos'] = d['UPOSTAG']
            # head dict, only consider the given head, not secondary edges
            h = d['HEAD']
            if h != '0':
                dh = self.graph.node[h]
                feats['head_pos'] = dh['UPOSTAG']
                feats['head_position'] = '<' if dh['POSITION'] < d['POSITION'] else '>'
                feats['head_rel'] = self.graph.edge[h][w]['ud']['REL']
            else:
                feats['head_pos'] = 'ROOT'
                feats['head_position'] = None   # False
                feats['head_rel'] = 'ROOT'
            feats['dep_count'] = 0
            # dependents, optional, multiple
            if 'DEPENDENTS' in d:
                feats['dep_count'] = len(d['DEPENDENTS'])
                if feats['dep_count']>10:
                    self.logger.debug('pruning dependents from ' + self.graph.graph['COMMENTS'] +' word_id = '+ w)
                    self.logger.debug('used first 10 of ' + str(feats['dep_count']) + ' dependencies')
                for i,dep in enumerate(d['DEPENDENTS']):
                    if i>9:
                        break
                    dd = self.graph.node[dep]
                    feats['dep_'+str(i+1)+'_pos'] = dd['UPOSTAG']
                    feats['dep_'+str(i+1)+'_position'] = '<' if dd['POSITION'] < d['POSITION'] else '>'
                    feats['dep_'+str(i+1)+'_rel'] = self.graph.edge[w][dep]['ud']['REL']
            
            self._features.append(feats)


    def print_feat_dict(self, d):
        keys = ['pos', 'head_pos', 'head_position', 'head_rel', 'dep_count']
        for k in keys + sorted([k for k in d if k not in keys], key=lambda x: (int(x.split('_')[1]), x)):
            print(k.ljust(15) +'\t'+ str(d[k]))


if __name__ == '__main__':
    
    with open('data_en/dev_00.conllu', 'r', encoding='utf-8') as sample:
        sents = sample.read().strip().split('\n\n')
    deps = CoNLL_UD_2(sents[26].strip().split('\n'))
    print(deps)
    #for i in ['3', '8', '9', '10']:
    #    print(deps.graph.node[i])
    #print()
    #for f in deps.features:
    #    print(f)

    deps.print_feats()
