# -*- coding:utf-8 -*-
'''
Created on Feb 6, 2017

@author: burak
'''

import os
import subprocess
import logging
import networkx as nx
from templates import *
from dep_graph import DepGraph

LOG_LEVEL = logging.DEBUG

class CoNLL_UD(DepGraph):
    '''
    CoNLL Universal Dependencies
    '''


    def __init__(self, file_name, log_level=LOG_LEVEL):
        '''
        Constructor
        '''
        super().__init__(file_name, log_level)
        
        self.keys = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
        self.read_graphs(self.file_name)
        
        
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
    
    
    def read_graphs(self, file_name):
        '''
        
        '''
        if not file_name:
            self.logger.error('no file given: ' + file_name)
            return
            
        f = open(file_name, 'r', encoding='utf-8')

        sent_index = 0
        words = []
        comments = ''
        i = 0
        m_ids = []
        m_form = ''
        
        for line in f:
            # end of sentence -> build graph if there are words
            if line.strip() == '' and len(words)>0:
                # build graph -> two pass -> add nodes and edges
                sent_index += 1
                graph = nx.DiGraph(COMMENTS=comments, GROUPS=[], SENT_ID=str(sent_index), 
                                   SENT_INDEX=sent_index, NUM_TOKENS=len(words))
                
                # add nodes while checking multi-word tokens
                for w in words:
                    if '-' in w['ID']:
                        start, end = [int(i) for i in w['ID'].split('-')]
                        m_ids = range(start, end+1)
                        m_form = w['FORM']
                        graph.graph['GROUPS'].append((str(start), str(end), m_form))
                        self.logger.debug('multi ' + w['ID'] +' '+ str(start) +' '+ str(end) +' '+ m_form)
                    else:
                        w2 = w
                        if int(w['ID'].split('.')[0]) in m_ids:
                            w2['MULTI-FORM'] = m_form
                            w2['MULTI-IDS'] = '-'.join([str(m_ids[0]), str(m_ids[-1])])
                        graph.add_node(w['ID'], attr_dict=w2)
                        self.logger.debug('added ' + w2['ID'])
                        self.logger.debug('node data: ' + str(w2))
                    
                # add edges
                # multiple instances of ROOT in a single sentence is possible
                root_candidates=set([])
                for w in words:
                    if '-' not in w['ID']:
                        if w['DEPREL'].lower() != 'root' :
                            graph.add_edge(w['HEAD'], w['ID'], attr_dict={'REL':w['DEPREL'], 'TYPE':'primary'})
                            self.logger.debug('edge ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
                        else:
                            root_candidates.add(w['ID'])
                            self.logger.debug('root ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
                
                # check for cycles, should be acyclic a this point
                if len(list(nx.simple_cycles(graph))) > 0:
                    self.logger.error('cycle detected in ' + file_name + ' sent: '+ str(sent_index))
                    self.logger.error(list(nx.simple_cycles(graph)))
                    continue
                
                # choose a root based on height
                #root = sorted(root_candidates, key=lambda r:self.height(graph, r))[0]
                root = max(root_candidates, key=lambda r:self.height(graph, r))
                
                
                # add other dependencies DEPS, PHEAD, PDEPREL
                for w in words:
                    # ex: 2:nsubj|4:nsubj
                    if w['DEPS'] != '_':
                        for d in w['DEPS'].split('|'):
                            h, r = d.split(':')
                            # root may not be the primary relation 
                            # in this case it won't be at the top of the tree
                            if r.lower() == 'root' :
                                root_candidates.add(w['ID'])
                                self.logger.debug('root2 ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
                            # DEPREL has a duplicate here
                            elif h != w['HEAD']:
                                graph.add_edge(h, w['ID'], attr_dict={'REL':r, 'TYPE':'secondary'})
                                self.logger.debug('edge2 ' + w['HEAD'] +' '+ w['ID'] +' '+ w['DEPREL'])
                
                # debug, just debug
                #self.logger.debug('root candidates: ' + str(root_candidates))
                #self.logger.debug('root heights: ' +str([self.height(graph, r) for r in root_candidates]))
                
                graph.graph['ROOT'] = root
                graph.graph['ROOTS'] = root_candidates
                self._graphs.append(graph)
                
                self.logger.debug('GRAPH:' + str(graph.graph))
                self.logger.debug('NODES:' + str(graph.nodes()))
                self.logger.debug('EDGES:' + str(graph.edges()))
            
            if line.strip() == '':
                #reset
                words = []
                comments = ''
                i = 0
                m_ids = []
                m_form = ''
            
            # only before the sentence    
            elif line.strip()[0] == '#':
                comments += line
            # words, also adds empty nodes and multiword tokens
            else:
                w = self.to_attr(line)
                if '-' not in w['ID']:
                    i += 1
                    w['POSITION'] = i
                words.append(w)
        
        f.close()
    
    
    def longest_dep(self, graph):
        l = 0
        for n1, n2 in graph.edges():
            d = abs(graph.node[n1]['POSITION'] - graph.node[n2]['POSITION'])
            if d > l:
                l = d
        return l
    
    
    def to_tikz(self, graph, caption='', label=''):
        '''
        '''
        # open
        tex = figure_header
        #tex += '\\resizebox {\\columnwidth} {!} {\n\n'
        tex += '\\adjustbox{max width=\columnwidth}{\n\n'
        tex += '\\begin{dependency}[theme = simple]\n'
        tex += dep_node_style
        tex += dep_node_style_empty
        tex += dep_node_pos_style
        tex += dep_node_pos_style_empty
        tex += dep_style_1
        tex += dep_style_2
        tex += dep_style_3
        tex += dep_style_4
        
        # words
        tex += '\n% words\n'
        tex += '\\begin{deptext}[column sep=1em, row sep=0.1em, nodes=word]\n'
        #
        nodes = sorted(graph.nodes(), key=lambda n: graph.node[n]['POSITION'])
        #
        tex += ' \\& '.join(['|[word-empty]| '+escape(graph.node[n]['FORM']) if '.' in n else 
                             escape(graph.node[n]['FORM']) for n in nodes])
        tex += ' \\\\\n'
        #
        tex += ' \\& '.join(['|[attr-empty]| '+graph.node[n]['UPOSTAG'] if '.' in n else 
                             '|[attr]| '+graph.node[n]['UPOSTAG'] for n in nodes])
        tex += ' \\\\\n'
        #
        tex += '\\end{deptext}\n\n'
        
        # roots
        tex += '% roots\n'
        max_dist = str(self.longest_dep(graph))
        tex += '\\deproot[root, edge unit distance='+max_dist+'ex]{'+ str(graph.node[graph.graph['ROOT']]['POSITION']) +'}{ROOT}\n'
        for n in graph.graph['ROOTS']:
            if n != graph.graph['ROOT']:
                tex += '\\deproot[root2, edge unit distance='+max_dist+'ex]{'+ str(graph.node[n]['POSITION']) +'}{ROOT}\n'
        
        # relations
        tex += '\n% edges\n'
        for (n1,n2) in graph.edges():
            if graph.edge[n1][n2]['TYPE'] == 'primary':
                tex += '\\depedge[rel]{'+ str(graph.node[n1]['POSITION']) +'}{' \
                    + str(graph.node[n2]['POSITION']) +'}{' \
                    + str(graph.edge[n1][n2]['REL']) +'}\n'
            elif graph.edge[n1][n2]['TYPE'] == 'secondary':
                tex += '\\depedge[rel2]{'+ str(graph.node[n1]['POSITION']) +'}{' \
                    + str(graph.node[n2]['POSITION']) +'}{' \
                    + str(graph.edge[n1][n2]['REL']) +'}\n'
        
        # word groups
        tex += '\n% groups\n'
        # start, end, form
        for (s,e,_) in graph.graph['GROUPS']:
            tex += '\\wordgroup[group style='+group_style+']{1}{' +str(graph.node[s]['POSITION'])+ '}{' \
                                     +str(graph.node[e]['POSITION'])+ '}{' \
                                     +str(graph.node[s]['POSITION'])+ '}\n'
            
        tex += '\n\\end{dependency}\n\n}\n'
        # caption and label
        if caption:
            tex += '\caption{' +caption+ '}\n'
        if label:
            tex += '\label{' +label+ '}\n'
        # close
        tex += figure_footer
        
        return tex
            

    def __repr__(self):
        s = ''
        for g in self._graphs:
            s += g.graph['COMMENTS']
            nodes = sorted(g.nodes(), key=lambda n: g.node[n]['POSITION'])
            for n in nodes:
                if 'MULTI-FORM' in g.node[n]:
                    m_start = g.node[n]['MULTI-IDS'].split('-')[0]
                    if m_start == n:
                        s += g.node[n]['MULTI-IDS'] +'\t'+ g.node[n]['MULTI-FORM'] + 8*'\t_' + '\n'
                    self.logger.debug(n +' : '+ g.node[n]['MULTI-IDS'] +' '+ g.node[n]['MULTI-FORM'])
                s += '\t'.join(g.node[n][k] for k in self.keys) + '\n'
            s += '\n'
        return s
        
        
if __name__ == '__main__':
    '''
    deps = CoNLL_UD('wsj_0001.mrg')
    print(deps)
    deps.to_tex(save_path='wsj_0001.mrg.tex')
    '''
    
    #deps = CoNLL_UD('dep/00/wsj_0013.mrg', log_level=logging.INFO)
    #for p in deps.graphs:
    #    print(len(p.nodes()))
    #deps.to_tex('test/wsj_0013_mrg.tex', separate=True, build=True)    
    
    deps = CoNLL_UD('dep/00/wsj_0020.mrg', log_level=logging.INFO)
    deps.to_tex('test/wsj_0020_mrg.tex', separate=True, build=True)