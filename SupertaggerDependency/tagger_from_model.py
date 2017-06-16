# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

import sys
from tagger import Supertagger
from conllu_10 import CoNLL_UD_10
from conllu_8 import CoNLL_UD_8

'''
sys.stderr.write('CoNLL_UD_10 load from model\n')
tagger = Supertagger(conllu_cls=CoNLL_UD_10)
tagger.load('models_dev/supertagger_10.pickle')
print(tagger.evaluate(test='data_en/test.conllu'))
sys.stderr.write('\n')
'''


sys.stderr.write('CoNLL_UD_8 load from model\n')
tagger = Supertagger(conllu_cls=CoNLL_UD_8)
tagger.load('models/supertagger_8.pickle')
print(tagger.evaluate(test='data_en/test_23.conllu'))
sys.stderr.write('\n')


sys.stderr.write('CoNLL_UD_10 load from model\n')
tagger = Supertagger(conllu_cls=CoNLL_UD_10)
tagger.load('models/supertagger_10.pickle')
print(tagger.evaluate(test='data_en/test_23.conllu'))
sys.stderr.write('\n')
