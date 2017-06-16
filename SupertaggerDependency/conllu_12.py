# -*- coding:utf-8 -*-
'''
Created on Feb 18, 2017

@author: burak
'''

import re
import logging
from conllu import CoNLL_UD


LOG_LEVEL = logging.INFO

class CoNLL_UD_12(CoNLL_UD):
    '''
    without directions in the categories
    dep cut at 10
    head dep cut at 10
    dependents of the node
    the head
    the head of the head
    the dependents of the head
    '''

    def clear_tag(self, supertag):
        '''
        remove subcategories from supertags
        (S[dcl]\\NP)/(S[b]\\NP)   ->  (S\\NP)/(S\\NP)       ->  (S-NP)-(S-NP)
        ((S\\NP)\(S\\NP))/N[num]  ->  ((S\\NP)\\(S\\NP))/N  ->  ((S-NP)-(S-NP))-N
        
        maybe also remove directions from slashes
        '''
        # supertag = supertag.replace('\\', '-').replace('/', '-')
        supertag = re.sub(r'[\\/]', '-', supertag)
        return re.sub('\[[^\]]*\]', '', supertag)
    
    
    def to_features(self):
        '''
        do not use id's
        '''
        for w in sorted(self.graph.nodes(), key=lambda n: self.graph.node[n]['POSITION']):
            if '-' in w:
                continue
            feats = {}
            # node dict
            d = self.graph.node[w]
            feats['idx'] = w
            feats['pos'] = d['UPOSTAG']
            feats['pos_x'] = d['XPOSTAG']
            # dependents, optional, multiple
            feats['dep_count'] = 0
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
                    feats['dep_'+str(i+1)+'_pos_x'] = dd['XPOSTAG']
                    feats['dep_'+str(i+1)+'_position'] = '<' if dd['POSITION'] < d['POSITION'] else '>'
                    feats['dep_'+str(i+1)+'_rel'] = self.graph.edge[w][dep]['ud']['REL']
            # head dict, only consider the given head, not secondary edges
            h = d['HEAD']
            if h != '0':
                dh = self.graph.node[h]
                feats['head_pos'] = dh['UPOSTAG']
                feats['head_pos_x'] = dh['XPOSTAG']
                feats['head_position'] = '<' if dh['POSITION'] < d['POSITION'] else '>'
                feats['head_rel'] = self.graph.edge[h][w]['ud']['REL']
                # head of head
                hh = dh['HEAD']
            else:
                feats['head_pos'] = 'ROOT'
                feats['head_pos_x'] = 'ROOT'
                feats['head_position'] = None   # False
                feats['head_rel'] = 'ROOT'
                # head of head
                hh = '0'
            # head of head
            if hh != '0':
                dhh = self.graph.node[hh]
                feats['h_head_pos'] = dhh['UPOSTAG']
                feats['h_head_pos_x'] = dhh['XPOSTAG']
                feats['h_head_position'] = '<' if dhh['POSITION'] < d['POSITION'] else '>'
                feats['h_head_rel'] = feats['head_rel'] +'-'+ self.graph.edge[hh][h]['ud']['REL'] 
            else:    
                feats['h_head_pos'] = 'h_ROOT'
                feats['h_head_pos_x'] = 'h_ROOT'
                feats['h_head_position'] = None   # False
                feats['h_head_rel'] = 'h_ROOT'
            # dependents of the head
            feats['h_dep_count'] = 0
            if h != '0' and 'DEPENDENTS' in dh:
                feats['h_dep_count'] = len(dh['DEPENDENTS'])
                if feats['h_dep_count']>10:
                    self.logger.debug('pruning head dependents from ' + self.graph.graph['COMMENTS'] +' word_id = '+ w)
                    self.logger.debug('used first 10 of ' + str(feats['dep_count']) + ' dependencies')
                for i,h_dep in enumerate(dh['DEPENDENTS']):
                    if i>9:
                        break
                    hdd = self.graph.node[h_dep]
                    feats['h_dep_'+str(i+1)+'_pos'] = hdd['UPOSTAG']
                    feats['h_dep_'+str(i+1)+'_pos_x'] = hdd['XPOSTAG']
                    feats['h_dep_'+str(i+1)+'_position'] = '<' if hdd['POSITION'] < d['POSITION'] else '>'
                    feats['h_dep_'+str(i+1)+'_rel'] = self.graph.edge[h][h_dep]['ud']['REL']
            
            # add to the list of features
            self._features.append(feats)
    
    
    def print_feat_dict(self, d):
        keys = ['idx', 'pos', 'pos_x', 'head_pos', 'head_pos_x', 'head_position', 'head_rel', 
                    'h_head_pos', 'h_head_pos_x', 'h_head_position', 'h_head_rel', 'dep_count', 'h_dep_count']
        for k in keys + sorted([k for k in d if k not in keys], 
                               key=lambda x: (x[0], int(x.split('_')[2]) if 'h_' in x else int(x.split('_')[1]), x)):
            print(k.ljust(15) +'\t'+ str(d[k]))


if __name__ == '__main__':
    
    
    with open('data_en/test_tiny.conllu', 'r', encoding='utf-8') as sample:
        sents = sample.read().strip().split('\n\n')
    deps = CoNLL_UD_12(sents[2].strip().split('\n'))
    print(deps)
    #for i in ['3', '8', '9', '10']:
    #    print(deps.graph.node[i])
    #print()
    #for f in deps.features:
    #    print(f)

    deps.print_feats()
    print(deps.supertags)
    '''
    
    with open('data_tr/tr-ud-dev_tiny.conllu', 'r', encoding='utf-8') as sample:
        sents = sample.read().strip().split('\n\n')
    print(len(sents))
    deps = CoNLL_UD_13(sents[2].strip().split('\n'))
    print('-------------------')
    print(deps, end='')
    print('-------------------')
    deps.print_feats()
    '''