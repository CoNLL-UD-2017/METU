# -*- coding:utf-8 -*-
'''
Created on 31 Mar 2017

@author: BurakKerim
'''

import os, sys, traceback
from tagger import SupertaggerDep
from tagger_crf import Supertagger
from conllu_15 import CoNLL_UD_15
from conllu_crf import CCG_CoNLL_UD_crf

# LOAD supertagger trained on dependencies: PTB + CCG_bank
sys.stderr.write('load supertagger from model\n')
supertagger = SupertaggerDep(sent_cls=CoNLL_UD_15)
supertagger.load('models/supertagger_15.pickle')
sys.stderr.write('\n')


treebanks = 'ud-treebanks-conll2017/'

dev_ = '-ud-dev.conllu'
train_ = '-ud-train.conllu'

all_langs = 0
no_dev = 0
no_train = 0

results = []

#for lang in ['UD_Catalan']:
for lang in os.listdir(treebanks):
    code = dev = train = ''
    for f in os.listdir(treebanks+lang):
        if train_ in f:
            train = treebanks+lang+'/'+f
            code = f.split('-')[0]
        elif dev_ in f:
            dev = treebanks+lang+'/'+f
        else:
            pass

    if dev and train:
        print('language: '+lang + ' code: '+ code)
        print('training: '+train)
        print('developm: '+dev)
        # 
        try:
            ccg_train = train.split('.')[0] + '-ccg.conllu'
            ccg_dev = dev.split('.')[0] + '-ccg.conllu'
            ccg_dev_2 = dev.split('.')[0] + '-ccg-2.col'
            ccg_model = 'models/'+code+'.pickle'
            #
            sys.stderr.write('LANGUAGE: '+lang + ' CODE: '+ code+'\n\n')
            # supertag train and dev data 
            sys.stderr.write('tagging ccg from dep for '+code+' train\n')
            supertagger.tag(test=train, save=ccg_train)
            sys.stderr.write('tagging ccg from dep for '+code+' dev\n')
            supertagger.tag(test=dev, save=ccg_dev)
            sys.stderr.write('\n')
            # train supertagger on newly tagged train segment
            sys.stderr.write('creating ccg tagger for '+code+'\n')
            tagger = Supertagger(train=ccg_train, 
                                 test=ccg_dev,
                                 sent_cls=CCG_CoNLL_UD_crf)
            tagger.fit()
            acc = tagger.evaluate()
            print(acc)
            tagger.save(ccg_model)
            # supertag dev segment again
            sys.stderr.write('tagging ccg for '+code+' dev\n')
            tagger.tag(save=ccg_dev_2)
            del tagger
            results.append((code,acc))
            sys.stderr.write('\n')
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

    elif train:
        print('MISSING DEV')
        print('language: '+lang + ' code: '+ code)
        print('training: '+train)
        no_dev += 1
    elif dev:
        print('MISSING TRAIN')
        print('language: '+lang + ' code: '+ code)
        print('training: '+dev)
        no_train += 1

    all_langs += 1

    print()


print(str(all_langs) + ' languages')
print(str(no_dev) + ' with no dev')
print(str(no_train) + ' with no train')

for c,a in results:
    print(c +'\t'+str(a))


