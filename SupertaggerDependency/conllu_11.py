# -*- coding:utf-8 -*-
'''
Created on Feb 18, 2017

@author: burak
'''

import logging
from conllu import CoNLL_UD


LOG_LEVEL = logging.INFO

class CoNLL_UD_11(CoNLL_UD):
    '''
    also add ids and sent len
    dep cut at 10
    head dep cut at 10
    dependents of the node
    the head
    the head of the head
    the dependents of the head
    '''


    def to_features(self):
        '''
        do not use id's
        '''
        nodes = [n for n in sorted(self.graph.nodes(), key=lambda n: self.graph.node[n]['POSITION']) if '-' not in n] 
        for w in nodes:
            feats = {}
            # node dict
            d = self.graph.node[w]
            feats['len_sent'] = len(nodes)
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
                    feats['dep_'+str(i+1)] = dep
                    feats['dep_'+str(i+1)+'_pos'] = dd['UPOSTAG']
                    feats['dep_'+str(i+1)+'_pos_x'] = dd['XPOSTAG']
                    feats['dep_'+str(i+1)+'_position'] = '<' if dd['POSITION'] < d['POSITION'] else '>'
                    feats['dep_'+str(i+1)+'_rel'] = self.graph.edge[w][dep]['ud']['REL']
            # head dict, only consider the given head, not secondary edges
            h = d['HEAD']
            feats['head'] = h
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
            feats['h_head'] = hh
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
                    feats['h_dep_'+str(i+1)] = h_dep
                    feats['h_dep_'+str(i+1)+'_pos'] = hdd['UPOSTAG']
                    feats['h_dep_'+str(i+1)+'_pos_x'] = hdd['XPOSTAG']
                    feats['h_dep_'+str(i+1)+'_position'] = '<' if hdd['POSITION'] < d['POSITION'] else '>'
                    feats['h_dep_'+str(i+1)+'_rel'] = self.graph.edge[h][h_dep]['ud']['REL']
            
            # add to the list of features
            self._features.append(feats)
    
    
    def print_feat_dict(self, d):
        keys = ['len_sent', 'idx', 'pos', 'pos_x', 'head', 'head_pos', 'head_pos_x', 'head_position', 'head_rel', 
                    'h_head', 'h_head_pos', 'h_head_pos_x', 'h_head_position', 'h_head_rel', 'dep_count', 'h_dep_count']
        for k in keys + sorted([k for k in d if k not in keys], 
                               key=lambda x: (x[0], int(x.split('_')[2]) if 'h_' in x else int(x.split('_')[1]), x)):
            print(k.ljust(15) +'\t'+ str(d[k]))


if __name__ == '__main__':
    
    with open('data_en/dev_00.conllu', 'r', encoding='utf-8') as sample:
        sents = sample.read().strip().split('\n\n')
    deps = CoNLL_UD_11(sents[26].strip().split('\n'))
    print(deps)
    #for i in ['3', '8', '9', '10']:
    #    print(deps.graph.node[i])
    #print()
    #for f in deps.features:
    #    print(f)

    deps.print_feats()

