# -*- coding:utf-8 -*-
'''
Created on Feb 18, 2017

@author: burak
'''

import re
import logging
import networkx as nx


LOG_LEVEL = logging.INFO

class CoNLL_UD():
    '''
    CoNLL Universal Dependencies
    '''

    def __init__(self, sentence, tag_simplify=1, log_level=LOG_LEVEL):
        '''
        Constructor
        '''
        self.sentence_conllu = sentence
        self.simple = tag_simplify

        self._tokenized_sent = []
        self._graph = None
        self._features = []
        self._supertags = []
        self.keys = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
             
        self.logger = None
        self.init_logging(log_level)
        
        self.to_graph(self.sentence_conllu)
        self.to_features()
        self.to_supertags()
        
    
    @property
    def graph(self):
        return self._graph
    
    @property
    def features(self):
        return self._features
    
    @property
    def supertags(self):
        return self._supertags
    
    @property
    def sentence(self):
        return self._tokenized_sent
    
    @property
    def nodes(self):
        return sorted(self.graph.nodes(), key=lambda n: self.graph.node[n]['POSITION'])
        
        
    def height(self, tree, root):
        if tree.successors(root) != []:
            return max([self.height(tree, r) for r in tree.successors(root)]) + 1
        else:
            return 0
    
    
    def to_attr(self, line):
        '''
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

    
    def to_graph(self, sentence):
        '''
        
        '''

        words = []
        comments = ''
        i = 0
        for line in sentence:
            # only before the sentence_conllu    
            if line.strip()[0] == '#':
                comments += line
            # words, also adds empty nodes and multiword tokens
            else:
                w = self.to_attr(line)
                if '-' not in w['ID']:
                    i += 1
                    w['POSITION'] = i
                words.append(w)
        
        if words == []:
            self.logger.error('empty sentence_conllu')
            return
        
        # build graph if there are words 
        graph = nx.MultiDiGraph(COMMENTS=comments, GROUPS=[], NUM_TOKENS=len(words))               
        
        # add nodes while checking multi-word tokens
        m_ids = []
        m_form = ''
        for w in words:
            if '-' in w['ID']:
                start, end = [int(i) for i in w['ID'].split('-')]
                m_ids = range(start, end+1)
                m_form = w['FORM']
                graph.graph['GROUPS'].append((str(start), str(end), m_form))
                self.logger.debug('multi ' + w['ID'] +' '+ str(start) +' '+ str(end) +' '+ m_form)
            else:
                self._tokenized_sent.append(w['FORM'])
                w2 = w
                w2.update(self.misc_attr(w['MISC']))
                if int(w['ID'].split('.')[0]) in m_ids:
                    w2['MULTI-FORM'] = m_form
                    w2['MULTI-IDS'] = '-'.join([str(m_ids[0]), str(m_ids[-1])])
                graph.add_node(w['ID'], attr_dict=w2)
                self.logger.debug('added ' + w2['ID'])
                self.logger.debug('node data: ' + str(w2))
            
        # add edges
        # multiple instances of ROOT in a single sentence_conllu is possible
        root_candidates=set([])
        for w in words:
            if w['HEAD'] == '_':
                continue
            if '-' not in w['ID']:
                if w['DEPREL'].lower() != 'root' :
                    graph.add_edge(w['HEAD'], w['ID'], key='ud', attr_dict={'REL':w['DEPREL'], 'TYPE':'primary'})
                    if 'DEPENDENTS' not in graph.node[w['HEAD']]:
                        graph.node[w['HEAD']]['DEPENDENTS'] = []
                    graph.node[w['HEAD']]['DEPENDENTS'].append(w['ID'])
                    self.logger.debug('edge ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
                else:
                    root_candidates.add(w['ID'])
                    self.logger.debug('root ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
        
        # check for cycles, should be acyclic a this point
        if len(list(nx.simple_cycles(graph))) > 0:
            self.logger.error('cycle detected in sent')
            self.logger.error(list(nx.simple_cycles(graph)))
            return
        
        # choose a root based on height (only ud edges)        
        root = max(root_candidates, key=lambda r:self.height(graph, r))
        
        # add other dependencies DEPS, PHEAD, PDEPREL
        for w in words:
            # ex: 2:nsubj|4:nsubj
            # multiple :
            # ex2: 8.1:nsubj:pass
            # 0 root may not be the primary
            # ex: 2.1 _   _   _   _   _   _   _   0:exroot    _
            if w['DEPS'] != '_':
                for d in w['DEPS'].split('|'):
                    hr = d.split(':')
                    h, r = hr[0], ':'.join(hr[1:])
                    if h == '_':
                        continue
                    # root may not be the primary relation 
                    # in this case it won't be at the top of the tree
                    # exroot -> dont care
                    if r.lower() == 'root' :
                        root_candidates.add(w['ID'])
                        self.logger.debug('root2 ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
                    # DEPREL has a duplicate here
                    elif h != w['HEAD'] and h!= '0':
                        graph.add_edge(h, w['ID'], key='ud', attr_dict={'REL':r, 'TYPE':'secondary'})
                        if 'DEPENDENTS' not in graph.node[h]:
                            graph.node[h]['DEPENDENTS'] = []
                        graph.node[h]['DEPENDENTS'].append(w['ID'])
                        self.logger.debug('edge2 ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
        
        # add ccg edges
        for w in words:
            if 'ARGS' in w:
                for idx, slot in w['ARGS']:
                    graph.add_edge(w['ID'], idx, key='ccg', attr_dict={'ARG-NO':slot})
                    self.logger.debug('edge ccg ' + w['ID'] +' '+ idx +' '+ slot)
        
        graph.graph['ROOT'] = root
        graph.graph['ROOTS'] = root_candidates
        self._graph = graph
        
        self.logger.debug('GRAPH:' + str(graph.graph))
        self.logger.debug('NODES:' + str(graph.nodes()))
        self.logger.debug('EDGES:' + str(graph.edges()))


    def to_features(self):
        '''
        skip multiword tokens
        '''
        for w in self.nodes:
            if '-' in w:
                continue
            feats = {}
            # node dict
            d = self.graph.node[w]
            feats['idx'] = w
            feats['pos'] = d['UPOSTAG']
            feats['pos_x'] = d['XPOSTAG']
            # head dict, only consider the given head, not secondary edges
            h = d['HEAD']
            feats['head'] = h
            if h == '_':
                feats['head_pos'] = '_'
                feats['head_pos_x'] = '_'
                feats['head_position'] = None   # False
                feats['head_rel'] = '_'
            elif h != '0':
                dh = self.graph.node[h]
                feats['head_pos'] = dh['UPOSTAG']
                feats['head_pos_x'] = dh['XPOSTAG']
                feats['head_position'] = '<' if dh['POSITION'] < d['POSITION'] else '>'
                feats['head_rel'] = self.graph.edge[h][w]['ud']['REL']
            else:
                feats['head_pos'] = 'ROOT'
                feats['head_pos_x'] = 'ROOT'
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
                    feats['dep_'+str(i+1)] = dep
                    feats['dep_'+str(i+1)+'_pos'] = dd['UPOSTAG']
                    feats['dep_'+str(i+1)+'_pos_x'] = dd['XPOSTAG']
                    feats['dep_'+str(i+1)+'_position'] = '<' if dd['POSITION'] < d['POSITION'] else '>'
                    feats['dep_'+str(i+1)+'_rel'] = self.graph.edge[w][dep]['ud']['REL']
            
            self._features.append(feats)
    
    
    def print_feat_dict(self, d):
        print('word'.ljust(15) +'\t'+ self.graph.node[d['idx']]['FORM'])
        keys = ['idx', 'pos', 'pos_x', 'head', 'head_pos', 'head_pos_x', 'head_position', 'head_rel', 'dep_count']
        for k in keys + sorted([k for k in d if k not in keys], key=lambda x: (int(x.split('_')[1]), x)):
            print(k.ljust(12) +'\t'+ str(d[k]))
    
    def print_feats(self):
        for feat in self.features:
            print()
            self.print_feat_dict(feat)
    
    def to_supertags(self):
        '''
        skip multiword tokens
        '''
        for w in self.nodes:
            if '-' in w:
                continue
            self._supertags.append(self.graph.node[w].get('CAT', '_'))

    
    def update_supertags(self, pred):
        for i,w in enumerate(self.nodes):
            if self.graph.node[w]['MISC'] == '_':
                self.graph.node[w]['MISC'] = 'cat='+pred[i]
            else:
                self.graph.node[w]['MISC'] += '|cat='+pred[i]
        

    def __repr__(self):
        s = ''
        if self.graph.graph['COMMENTS']:
            s += self.graph.graph['COMMENTS'] + '\n'
        for n in self.nodes:
            if 'MULTI-FORM' in self.graph.node[n]:
                m_start = self.graph.node[n]['MULTI-IDS'].split('-')[0]
                if m_start == n:
                    s += self.graph.node[n]['MULTI-IDS'] +'\t'+ self.graph.node[n]['MULTI-FORM'] + 8*'\t_' + '\n'
                self.logger.debug(n +' : '+ self.graph.node[n]['MULTI-IDS'] +' '+ self.graph.node[n]['MULTI-FORM'])
            s += '\t'.join(self.graph.node[n][k] for k in self.keys) + '\n'
        s += '\n'
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
    
    with open('ud-treebanks-conll2017/UD_English/en-ud-train.conllu', 'r', encoding='utf-8') as sample:
        sents = sample.read().strip().split('\n\n')

    for sent in sents:
        #deps = CoNLL_UD(sent.strip().split('\n'), log_level=logging.DEBUG)
        deps = CoNLL_UD(sent.strip().split('\n'))
        print(deps)
        #deps.print_feats()
        print(deps.supertags)
        del deps
    #for i in ['3', '8', '9', '10']:
    #    print(deps.graph.node[i])
    #print()
    #for f in deps.features:
    #    print(f)

    #deps.print_feats()

