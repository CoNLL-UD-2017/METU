# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

from tagger import Supertagger
from conllu_10 import CoNLL_UD_10
#from conllu_8 import CoNLL_UD_8


print('Tagging Turkish with CoNLL_UD_10 load from model\n')
tagger = Supertagger(conllu_cls=CoNLL_UD_10)
tagger.load('models_dev/supertagger_10.pickle')
tagger.tag(test='data_tr/tr-ud-dev_tiny.conllu')
tagger.tag(test='data_tr/tr-ud-dev_tiny.conllu', save='data_tr/tr-ud-dev_tiny_tagged.conllu')

