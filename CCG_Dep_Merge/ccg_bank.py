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

class CCG_PArg(DepGraph):
    '''
    CCG Bank predicate arguments
    '''


    def __init__(self, file_name, log_level=LOG_LEVEL):
        '''
        Constructor
        '''
        super().__init__(file_name, log_level)
        
        # 'i   j   cat_j    arg_k   word_i  word_j'
        self.keys = ['ID_arg', 'ID_pred', 'CAT_pred', 'POS_arg', 'ARG', 'PRED', 'X']
        self.read_graphs(self.file_name)
        
    
    def to_attr(self, line):
        '''
        4 tabs then 1 space ?
        1      0      N/N      1      Vinken Pierre
        maybe another space and <XX> at the end
        1      5      (S[adj]\\NP)\\NP      1      Vinken old <XB>
        '''
        values = [token.strip() for token in line.strip().split('\t')]
        values = values[:4] + values[4].split()
        d = {k:v for k,v in zip(self.keys, values)}
        # add 1 to match indices with conll
        d['ID_arg'] = str(int(d['ID_arg'])+1)
        d['ID_pred'] = str(int(d['ID_pred'])+1)
        return d
    
    
    def read_graphs(self, file_name):
        '''
        
        '''
        if not file_name:
            self.logger.error('no file given: ' + file_name)
            return
            
        f = open(file_name, 'r', encoding='utf-8')
        
        pargs = []
        comments = ''
        sent_id = ''
        sent_index = -1
        num_tokens = -1
        
        for line in f:
            # end of sentence -> build graph if there are pargs
            if line.strip() == '<\s>' and len(pargs)>0:
                # build graph -> two pass -> add nodes and edges
                graph = nx.DiGraph(COMMENTS=comments, SENT_ID=sent_id, 
                                   SENT_INDEX=sent_index, NUM_TOKENS=num_tokens)
                
                for i in range(num_tokens):
                    graph.add_node(str(i+1))
                
                # add nodes while checking multi-word tokens
                for parg in pargs:
                    self.logger.debug('parg: ' + str(parg))
                    # update head node, predicate
                    d = graph.node[parg['ID_pred']]
                    if 'CAT' not in d:
                        d['WORD'] = parg['PRED']
                        d['CAT'] = parg['CAT_pred']
                        d['ARGS'] = {}
                    # can have multiple arg_positions to different ids 
                    d['ARGS'][parg['ID_arg']] = parg['POS_arg']
                    graph.node[parg['ID_pred']] = d
                    # update dependent, argument
                    d = graph.node[parg['ID_arg']]
                    if 'HEADS' not in d:
                        d['HEADS'] = {}
                        d['HEAD_CATS'] = {}
                    d['WORD'] = parg['ARG']
                    d['HEADS'][parg['ID_pred']] = parg['POS_arg']
                    d['HEAD_CATS'][parg['ID_pred']] = parg['CAT_pred']
                    graph.node[parg['ID_arg']] = d
                    # add relation to the graph
                    d={'POS_arg':parg['POS_arg'], 'CAT_pred':parg['CAT_pred']}
                    if 'X' in parg:
                        d['X'] = parg['X']
                    graph.add_edge(parg['ID_pred'], parg['ID_arg'], attr_dict= d)
                    self.logger.debug('added edge from ' + parg['ID_pred'] + ' to ' + parg['ID_arg'] )
                
                # if no category, assign 'N'
                for n in graph.nodes():
                    # arguments
                    if 'CAT' not in graph.node[n] and 'WORD' in graph.node[n] :
                        graph.node[n]['CAT'] = 'N'
                    # probably punctuation
                    elif 'CAT' not in graph.node[n]:
                        graph.node[n]['WORD'] = '_'
                        graph.node[n]['CAT'] = '_'
                
                # check for cycles
                if len(list(nx.simple_cycles(graph))) > 0:
                    self.logger.debug('cycle detected in ' + file_name + ' sent: '+ str(sent_index))
                    self.logger.debug(list(nx.simple_cycles(graph)))
                    
                self._graphs.append(graph)
                
                self.logger.debug('GRAPH:' + str(graph.graph))
                self.logger.debug('NODES:' + str(graph.nodes()))
                self.logger.debug('EDGES:' + str(graph.edges()))
                
                # debug
                if len(graph.nodes()) > num_tokens:
                    self.logger.error('EXTRA nodes ' + str(len(graph.nodes()) +' '+ str(num_tokens)))
                for n in sorted(graph.nodes(), key=int):
                    self.logger.debug(n +' : '+ str(graph.node[n]))
                for n1,n2 in sorted(graph.edges(), key=lambda x:(int(x[1]),int(x[0]))):
                    self.logger.debug(str((n1,n2)) +' : '+ str(graph.edge[n1][n2]))
            
            # sentence may be empty reset at closing tag
            if line.strip() == '<\s>':   
                pargs = []
                comments = ''
                sent_id = ''
                sent_index = -1
                num_tokens = -1
            
            # only before the sentence    
            elif line.strip()[0] == '<':
                # <s id="wsj_0013.7"> 27
                comments += line.strip()
                i = comments.find('"')
                j = comments.find('"', i+1)
                #print(i,j,comments[i+1:j])
                # wsj_0013.7
                sent_id = comments[i+1:j]
                # 7
                sent_index = int(sent_id.split('.')[1])
                # 28 <- 27+1
                num_tokens = int(comments[comments.find('>')+1:].strip()) +1
            # pargs, also adds empty nodes and multiword tokens
            else:
                w = self.to_attr(line)
                pargs.append(w)
        
        f.close()        

    
    def _to_str(self, ids='ccgbank'):
        '''
        Args:
            ids: if 'conllu' print 1 added ids
                 if 'ccgbank' 0 based indices
        '''  
        if ids != 'conllu' and ids != 'ccgbank':
            self.logger.error('unknown type: '+ids+ ', expected conllu or ccgbank')
                    
        s = ''
        for g in self._graphs:
            s += '<s id="'
            s += g.graph['SENT_ID']
            s += '"> '
            s += str(g.graph['NUM_TOKENS']) if ids=='conllu' else str(g.graph['NUM_TOKENS']-1)
            s += '\n'
            edges = sorted(g.edges(), key=lambda x:(int(x[1]),int(x[0])))
            for n1, n2 in edges:
                if ids == 'conllu':
                    s += n2 +' \t '+ n1 +' \t ' 
                else:
                    s += str(int(n2)-1) +' \t '+ str(int(n1)-1) +' \t '
                s += g.edge[n1][n2]['CAT_pred'] +' \t '+ g.edge[n1][n2]['POS_arg'] +' \t '
                s += g.node[n2]['WORD'] +' '+ g.node[n1]['WORD']
                if 'X' in g.edge[n1][n2]:
                    s += ' ' + g.edge[n1][n2]['X']
                s += '\n'
            s += '<\s>\n'
        return s
    
    def __repr__(self):
        return self._to_str()
    
    
    def to_tikz(self, graph, caption='', label=''):
        '''
        '''
        # open
        tex = figure_header
        #tex += '\\resizebox {\\columnwidth} {!} {\n\n'
        tex += '\\adjustbox{max width=\columnwidth}{\n\n'
        tex += '\\begin{dependency}[theme = simple]\n'
        tex += dep_node_style
        tex += dep_style_5
        
        # words
        tex += '\n% words\n'
        tex += '\\begin{deptext}[column sep=1em, row sep=0.1em, nodes=word]\n'
        #
        nodes = sorted(graph.nodes(), key=int)
        #
        tex += ' \\& '.join([escape(graph.node[n]['WORD']) for n in nodes])
        tex += ' \\\\\n'
        #
        tex += ' \\& '.join([escape(graph.node[n]['CAT']) for n in nodes])
        tex += ' \\\\\n'
        #
        tex += '\\end{deptext}\n\n'
        
        # relations
        tex += '\n% edges\n'
        for (n1,n2) in graph.edges():
            tex += '\\depedge[relccg]{'+ n1 +'}{' + n2 +'}{' \
                + str(graph.edge[n1][n2]['POS_arg']) +'}\n'
        
        tex += '\n\\end{dependency}\n\n}\n'
        # caption and label
        if caption:
            tex += '\caption{' +caption+ '}\n'
        if label:
            tex += '\label{' +label+ '}\n'
        # close
        tex += figure_footer
        
        return tex
    
        
        
if __name__ == '__main__':
    '''
    pargs = CCG_PArg('wsj_0001.parg')
    print(pargs)
    print(pargs._to_str(ids='conllu'))
    pargs.to_tex(save_path='wsj_0001.parg.tex')
    '''
    
    #pargs = CCG_PArg('ccg/00/wsj_0013.parg', log_level=logging.INFO)
    #for p in pargs.graphs:
    #    print(len(p.nodes()), p.graph['NUM_TOKENS'])
    #pargs.to_tex('test/wsj_0013_parg.tex', separate=True, build=True)
    #print(pargs) 
    #print(pargs._to_str(ids='conllu'))

    pargs = CCG_PArg('ccg/00/wsj_0020.parg', log_level=logging.INFO)
    pargs.to_tex('test/wsj_0020_parg.tex', separate=True, build=True)
        