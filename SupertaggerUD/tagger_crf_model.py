# -*- coding:utf-8 -*-
'''
Created on 13 Mar 2017

@author: BurakKerim
'''

import sys
from tagger import Supertagger as DepSupertagger
from tagger_crf import Supertagger
from conllu_crf import CCG_CoNLL_UD_crf


# TINY ENGLISH TEST
tagger = DepSupertagger(train='data_en/train_tiny.conllu', 
                     test='data_en/test_tiny.conllu',
                     sent_cls=CCG_CoNLL_UD_crf)
tagger.fit()
print(tagger.evaluate())
tagger.save('models/en_tiny.pickle')
#tagger.tag()
tagger.tag(save='data_en/test_tiny-ccg-2.col')
del tagger
sys.stderr.write('\n')


# GERMAN
tagger = Supertagger(train='data_de/de-ud-train-ccg.conllu', 
                     test='data_de/de-ud-dev-ccg.conllu',
                     sent_cls=CCG_CoNLL_UD_crf)
tagger.fit()
print(tagger.evaluate())
tagger.save('models/de.pickle')
tagger.tag(save='data_de/de-ud-dev-ccg-2.col')
del tagger
sys.stderr.write('\n')

# FRENCH
tagger = Supertagger(train='data_fr/fr-ud-train-ccg.conllu', 
                     test='data_fr/fr-ud-dev-ccg.conllu',
                     sent_cls=CCG_CoNLL_UD_crf)
tagger.fit()
print(tagger.evaluate())
tagger.save('models/fr.pickle')
tagger.tag(save='data_fr/fr-ud-dev-ccg-2.col')
del tagger
sys.stderr.write('\n')

# TURKISH
tagger = Supertagger(train='data_tr/tr-ud-train-ccg.conllu', 
                     test='data_tr/tr-ud-dev-ccg.conllu',
                     sent_cls=CCG_CoNLL_UD_crf)
tagger.fit()
print(tagger.evaluate())
tagger.save('models/tr.pickle')
tagger.tag(save='data_tr/tr-ud-dev-ccg-2.col')
del tagger
sys.stderr.write('\n')
