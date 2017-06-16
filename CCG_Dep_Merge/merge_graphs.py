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
from dep_conllu import CoNLL_UD
from ccg_bank import CCG_PArg
from setuptools.sandbox import save_path

LOG_LEVEL = logging.INFO

class Merge_UD_CCG(DepGraph):
    '''
    '''
    
    def __init__(self, ud_file, ccg_file, log_level=LOG_LEVEL):
        '''
        Constructor
        '''
        super().__init__(ud_file, log_level)
        
        self.keys = ['ID', 'FORM', 'LEMMA', 'UPOSTAG', 'XPOSTAG', 'FEATS', 'HEAD', 'DEPREL', 'DEPS', 'MISC']
        
        self.ud_file = ud_file
        self.ccg_file = ccg_file
        
        self.ud = CoNLL_UD(self.ud_file, log_level)
        self.ccg = CCG_PArg(self.ccg_file, log_level)
        
        #print(self.ud)
        #print(self.ccg)
        
        self.diff = []
        self.match_info()
        
        self.merge_graphs()
    
    
    def match_info(self):
        '''
        '''
        num_ud = len(self.ud.graphs)
        num_ccg = len(self.ccg.graphs)
        if num_ud > num_ccg:
            self.logger.debug('missing ccg derivations for '+\
                              str(num_ud-num_ccg) +' sentences')
            ud_ids = set(range(1,num_ud+1))
            ccg_ids = set([ccg.graph['SENT_INDEX'] for ccg in self.ccg.graphs])
            self.diff = sorted(ud_ids-ccg_ids)
            self.logger.info('sentences in ' +str(self.diff)+' do not have ccg derivations')
        else:
            self.logger.debug('all sentences have ccg derivations')
    
    
    def merge_graphs(self):
        '''
        '''
        
        # not all sents have ccg derivations, merge only the ones that have
        for ccg in self.ccg.graphs:
            s_index = ccg.graph['SENT_INDEX']
            ud = self.ud.graphs[ccg.graph['SENT_INDEX']-1]
            #
            g = nx.MultiDiGraph()
            
            # may have the same key, keep all
            self.logger.debug('UD GRAPH KEYS: '+str(ud.graph))
            for key in ud.graph:
                g.graph[key+'-ud'] = ud.graph[key]
            self.logger.debug('CCG GRAPH KEYS: '+str(ccg.graph))
            for key in ccg.graph:
                g.graph[key+'-ccg'] = ccg.graph[key]
            # ROOT from ud
            g.graph['ROOT'] = ud.graph['ROOT']
            # SENT ID from ccg bank
            g.graph['SENT_ID'] = ccg.graph['SENT_ID']
            g.graph['SENT_INDEX'] = ccg.graph['SENT_INDEX']
            # COMMENTS from ccg bank contains id
            g.graph['COMMENTS'] = '# sent_id = ' + str(ccg.graph['SENT_ID'])
            # weirdly need to add nodes and edges, cannot copy without key 0 in attr dicts
            #g.add_nodes_from(ud)
            for n in sorted(ud.nodes(), key=float):
                g.add_node(n, attr_dict={k:v for k,v in ud.node[n].items()})
                self.logger.debug('added node from UD: '+ n +' : '+ str(g.node[n]))
            
            self.logger.debug('nodes of the new graph: ')
            self.logger.debug(str(sorted(g.nodes(), key=float)))
            
            #
            self.logger.debug('pair ' +str(s_index)+ ' adding node data from ccg bank')
            for n in sorted(ud.nodes(), key=float):
                if n in ccg.nodes():
                    node_data = ud.node[n]
                    ccg_data = 'cat=' + ccg.node[n]['CAT']
                    if 'ARGS' in ccg.node[n]:
                        ccg_data += '|args='
                        # arg slot in category and arg id
                        ccg_data += ','.join([p+':'+a for p,a in ccg.node[n]['ARGS'].items()])
                    if 'HEADS' in ccg.node[n]:
                        ccg_data += '|preds='
                        # head id and head arg slot in category
                        ccg_data += ','.join([h+':'+p for h,p in ccg.node[n]['HEADS'].items()])
                    #if 'HEAD_CATS' in ccg.node[n]:
                    #    ccg_data += '|pcats:'
                    #    # head id and head category
                    #    ccg_data += ','.join([p+':'+c for p,c in ccg.node[n]['HEAD_CATS'].items()])
                    node_data['MISC'] = ccg_data
                    g.node[n] = node_data
                else:
                    g.node[n]['MISC'] = 'cat=_'
                
            self.logger.debug('pair ' +str(s_index)+ ' adding edge data from ccg bank, possible multiple edges between same nodes')
            for (n1,n2) in ud.edges():
                g.add_edge(n1, n2, key='ud', attr_dict=ud.edge[n1][n2])
                self.logger.debug('added edge from UD: '+ str((n1,n2)) +' : '+ str(ud.edge[n1][n2]))
            for (n1,n2) in ccg.edges():
                if n1 not in g.nodes() or n1 not in g.nodes():
                    self.logger.error('added new node from ccg edges' +str((n1,n2)))
                g.add_edge(n1, n2, key='ccg', attr_dict=ccg.edge[n1][n2])
                self.logger.debug('added edge from CCG: '+ str((n1,n2)) +' : '+ str(ccg.edge[n1][n2]))
                
            # debug
            self.logger.debug('pair ' +str(s_index)+ ' graph data:')
            for n in sorted(g.nodes(), key=float):
                if 'POSITION' not in g.node[n]:
                    self.logger.error('postion error: '+ str(s_index) +' : '+ n +' : '+ str(g.node[n]))
                self.logger.debug('node: '+ n +' : '+ str(g.node[n]))
            for n1,n2 in sorted(g.edges(), key=lambda x:(float(x[1]),float(x[0]))):
                self.logger.debug('edge: '+ str((n1,n2)) +' : '+ str(g.edge[n1][n2]))
            
            self._graphs.append(g)

    
    def misc_data(self, raw):
        d = {}
        try:
            tmp = raw.strip().split('|')
            #print(tmp)
            for field in tmp:
                key, value = field.split(':')
                #print(key, value)
                if ',' in value:
                    d[key] = {}
                    v_tmp = value.split(',')
                    for v_field in v_tmp:
                        v_key, v_value = v_field.split('-')
                        #print(v_key, v_value)
                        d[key][v_key] = v_value
                else:
                    d[key] = value
        except Exception as e:
            self.logger.error(str(e))
            self.logger.error(raw)
            d['cat'] = '_'
        return d
    
    
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
        tex += dep_style_5
        
        # words
        tex += '\n% words\n'
        # word
        tex += '\\begin{deptext}[column sep=1em, row sep=0.1em, nodes=word]\n'
        #
        nodes = sorted(graph.nodes(), key=lambda n: graph.node[n]['POSITION'])
        #
        tex += ' \\& '.join(['|[word-empty]| '+escape(graph.node[n]['FORM']) if '.' in n else 
                             escape(graph.node[n]['FORM']) for n in nodes])
        tex += ' \\\\\n'
        # pos
        tex += ' \\& '.join(['|[attr-empty]| '+graph.node[n]['UPOSTAG'] if '.' in n else 
                             '|[attr]| '+graph.node[n]['UPOSTAG'] for n in nodes])
        tex += ' \\\\\n'
        # supertag
        cat = lambda n: escape(self.misc_data(graph.node[n]['MISC'])['cat'])
        tex += ' \\& '.join(['|[word-empty]| \\_' if '.' in n else 
                             cat(n) for n in nodes])
        tex += ' \\\\\n'
        #
        tex += '\\end{deptext}\n\n'
        
        # roots
        tex += '% roots\n'
        max_dist = str(self.longest_dep(graph))
        tex += '\\deproot[root, edge unit distance='+max_dist+'ex]{'+ str(graph.node[graph.graph['ROOT']]['POSITION']) +'}{ROOT}\n'
        for n in graph.graph['ROOTS-ud']:
            if n != graph.graph['ROOT']:
                tex += '\\deproot[root2, edge unit distance='+max_dist+'ex]{'+ str(graph.node[n]['POSITION']) +'}{ROOT}\n'
        
        # ud relations
        tex += '\n% edges ud\n'
        for (n1,n2) in graph.edges():
            if 'ud' in graph.edge[n1][n2]:
                if graph.edge[n1][n2]['ud']['TYPE'] == 'primary':
                    tex += '\\depedge[rel]{'+ str(graph.node[n1]['POSITION']) +'}{' \
                        + str(graph.node[n2]['POSITION']) +'}{' \
                        + str(graph.edge[n1][n2]['ud']['REL']) +'}\n'
                elif graph.edge[n1][n2]['ud']['TYPE'] == 'secondary':
                    tex += '\\depedge[rel2]{'+ str(graph.node[n1]['POSITION']) +'}{' \
                        + str(graph.node[n2]['POSITION']) +'}{' \
                        + str(graph.edge[n1][n2]['ud']['REL']) +'}\n'
        
        # ccg relations
        tex += '\n% edges ccg\n'
        for (n1,n2) in graph.edges():
            if 'ccg' in graph.edge[n1][n2]:
                tex += '\\depedge[relccg, edge below]{'+ str(graph.node[n1]['POSITION']) +'}{' + str(graph.node[n2]['POSITION']) +'}{' \
                    + str(graph.edge[n1][n2]['ccg']['POS_arg']) +'}\n'
        
        # word groups
        tex += '\n% groups\n'
        # start, end, form
        for (s,e,_) in graph.graph['GROUPS-ud']:
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
        for g in self.graphs:
            s += g.graph['COMMENTS'] + '\n'
            nodes = sorted(g.nodes(), key=lambda n: g.node[n]['POSITION'])
            for n in nodes:
                if 'MULTI-FORM' in g.node[n]:
                    m_start = g.node[n]['MULTI-IDS'].split('-')[0]
                    if m_start == n:
                        s += g.node[n]['MULTI-IDS'] +'\t'+ g.node[n]['MULTI-FORM'] + 8*'\t_' + '\n'
                    #self.logger.debug(n +' : '+ g.node[n]['MULTI-IDS'] +' '+ g.node[n]['MULTI-FORM'])
                s += '\t'.join(g.node[n][k] for k in self.keys) + '\n'
            s += '\n'
        return s

        
if __name__ == '__main__':
    
    '''
    deps = Merge_UD_CCG(ud_file='wsj_0001.mrg', ccg_file='wsj_0001.parg')
    deps.save('wsj_0001.ud')
    deps.to_tex()
    '''
    '''
    deps = Merge_UD_CCG(ud_file='dep/00/wsj_0013.mrg', ccg_file='ccg/00/wsj_0013.parg', log_level=logging.INFO)
    deps.save('wsj_0013.ud')
    deps.to_tex('test/wsj_0013.tex', separate=True)
    '''
    '''
    deps = Merge_UD_CCG(ud_file='dep/00/wsj_0003.mrg', ccg_file='ccg/00/wsj_0003.parg')
    deps.save('wsj_0003.ud')
    deps.to_tex('test/wsj_0003.tex', separate=True)
    '''
    
    deps = Merge_UD_CCG(ud_file='dep/00/wsj_0020.mrg', ccg_file='ccg/00/wsj_0020.parg', log_level=logging.INFO)
    deps.to_tex('test/wsj_0020.tex', separate=True, build=True)
    