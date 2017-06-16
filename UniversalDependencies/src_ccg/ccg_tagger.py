# -*- coding:utf-8 -*-
'''
Created on 31 Mar 2017

@author: BurakKerim
'''

import os, sys, traceback, json
from tagger_crf import Supertagger
from conllu_ccg import CCG_CoNLL_UD


code    = sys.argv[1]
fi_name = sys.argv[2]
fo_name = sys.argv[3]

model_dir = sys.argv[4]

ccg_model = model_dir+'/'+code+'.pickle'

#print(code + '\t' + lang + '\t' + in_file + '\t' + ccg_file + '\t' + out_file)

try:
    sys.stderr.write('loading ccg tagger for '+code+'\n')
    tagger = Supertagger(sent_cls=CCG_CoNLL_UD)
    tagger.load(ccg_model)
    sys.stderr.write('tagging ccg for '+code+' dev\n')
    acc = tagger.tag(test=fi_name, save=fo_name)
    sys.stderr.write('\n\n')

except Exception as e:
    print(str(e))
    sys.stderr.write('ERROR\n')
    #sys.stderr.write(str(e) +'\n')
    sys.stderr.write('type : '+ str(sys.exc_info()[0]) +'\n')
    sys.stderr.write('value: '+ str(sys.exc_info()[1]) +'\n')
    sys.stderr.write('trace:\n')
    for t in traceback.format_tb(sys.exc_info()[2]):
        sys.stderr.write(str(t)+'\n')
    #sys.stderr.write('trace: '+ str(sys.exc_info()[2]) +'\n')
    sys.stderr.write('\n\n')



