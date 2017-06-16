# -*- coding:utf-8 -*-
'''
Created on Feb 19, 2017

@author: BurakKerim
'''

import sys
from tagger import Supertagger

'''
from conllu_8 import CoNLL_UD_8
sys.stderr.write('CoNLL_UD_8\n')
tagger = Supertagger(train='data_en/train_02_21.conllu', test='data_en/dev_00.conllu', conllu_cls=CoNLL_UD_8)
tagger.fit()
tagger.save('models/supertagger_8.pickle')
print(tagger.evaluate())
sys.stderr.write('\n')


from conllu_9 import CoNLL_UD_9
sys.stderr.write('CoNLL_UD_9\n')
tagger = Supertagger(train='data_en/train_02_21.conllu', test='data_en/dev_00.conllu', conllu_cls=CoNLL_UD_9)
tagger.fit()
tagger.save('models/supertagger_9.pickle')
print(tagger.evaluate())
sys.stderr.write('\n')


from conllu_10 import CoNLL_UD_10
sys.stderr.write('CoNLL_UD_10\n')
tagger = Supertagger(train='data_en/train_02_21.conllu', test='data_en/dev_00.conllu', conllu_cls=CoNLL_UD_10)
tagger.fit()
tagger.save('models/supertagger_10.pickle')
print(tagger.evaluate())
sys.stderr.write('\n')


from conllu_11 import CoNLL_UD_11
sys.stderr.write('CoNLL_UD_11\n')
tagger = Supertagger(train='data_en/train_02_21.conllu', test='data_en/dev_00.conllu', conllu_cls=CoNLL_UD_11)
tagger.fit()
tagger.save('models/supertagger_11.pickle')
print(tagger.evaluate())
sys.stderr.write('\n')


from conllu_12 import CoNLL_UD_12
sys.stderr.write('CoNLL_UD_12\n')
tagger = Supertagger(train='data_en/train_02_21.conllu', test='data_en/dev_00.conllu', conllu_cls=CoNLL_UD_12)
tagger.fit()
tagger.save('models/supertagger_12.pickle')
print(tagger.evaluate())
sys.stderr.write('\n')
'''

from conllu_14 import CoNLL_UD_14
sys.stderr.write('CoNLL_UD_14\n')
tagger = Supertagger(train='data_en/train_02_21.conllu', test='data_en/dev_00.conllu', conllu_cls=CoNLL_UD_14)
tagger.fit()
tagger.save('models/supertagger_14.pickle')
print(tagger.evaluate())
sys.stderr.write('\n')


from conllu_15 import CoNLL_UD_15
sys.stderr.write('CoNLL_UD_15\n')
tagger = Supertagger(train='data_en/train_02_21.conllu', test='data_en/dev_00.conllu', conllu_cls=CoNLL_UD_15)
tagger.fit()
tagger.save('models/supertagger_15.pickle')
print(tagger.evaluate())
sys.stderr.write('\n')


