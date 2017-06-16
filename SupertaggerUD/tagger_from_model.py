# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

import sys
from tagger import Supertagger
from conllu_15 import CoNLL_UD_15


sys.stderr.write('load supertagger from model\n')
tagger = Supertagger(conllu_cls=CoNLL_UD_15)
tagger.load('models/supertagger_15.pickle')
sys.stderr.write('\n')

sys.stderr.write('tagging fr train\n')
tagger.tag(test='data_fr/fr-ud-train.conllu', save='data_fr/fr-ud-train-ccg.conllu')
sys.stderr.write('\n')

sys.stderr.write('tagging fr dev\n')
tagger.tag(test='data_fr/fr-ud-dev.conllu', save='data_fr/fr-ud-dev-ccg.conllu')
sys.stderr.write('\n')


sys.stderr.write('tagging de train\n')
tagger.tag(test='data_de/de-ud-train.conllu', save='data_de/de-ud-train-ccg.conllu')
sys.stderr.write('\n')

sys.stderr.write('tagging de dev\n')
tagger.tag(test='data_de/de-ud-dev.conllu', save='data_de/de-ud-dev-ccg.conllu')
sys.stderr.write('\n')


sys.stderr.write('tagging tr train\n')
tagger.tag(test='data_tr/tr-ud-train.conllu', save='data_tr/tr-ud-train-ccg.conllu')
sys.stderr.write('\n')

sys.stderr.write('tagging tr dev\n')
tagger.tag(test='data_tr/tr-ud-dev.conllu', save='data_tr/tr-ud-dev-ccg.conllu')
sys.stderr.write('\n')