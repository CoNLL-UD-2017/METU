# -*- coding:utf-8 -*-
'''
Created on 31 Mar 2017

@author: BurakKerim
'''

import os, sys, traceback
from tagger_crf import Supertagger
from conllu_ccg import CCG_CoNLL_UD


#treebanks = 'test_data/'
treebanks = '../SupertaggerUD/ud-treebanks-conll2017/'

out_dir = 'ud-treebanks-conll2017/'

dev_ = '-ud-dev-ccg.conllu'
train_ = '-ud-train-ccg.conllu'

all_langs = 0
no_dev = 0
no_train = 0

results = []

#for lang in ['UD_Catalan']:
for lang in os.listdir(treebanks):
    if lang[0] == '.':
        continue 

    code = dev = train = ''
    ccg_train = ccg_dev = ccg_dev_2 = ''
    
    for f in os.listdir(treebanks+lang):
        if train_ in f:
            ccg_train = treebanks+lang+'/'+f
            code = f.split('-')[0]
            ccg_model = 'models/'+code+'.pickle'
        elif dev_ in f:
            ccg_dev = treebanks+lang+'/'+f
            ccg_dev_2 = out_dir + f.split('.')[0] + '-2.connlu'
        else:
            pass

    print('language: '+lang + ' code: '+ code)
    print('training: '+ccg_train)
    print('developm: '+ccg_dev)
    #
    sys.stderr.write('LANGUAGE: '+lang + ' CODE: '+ code+'\n\n')

    try:
        if ccg_train:
            # train supertagger on newly tagged train segment
            sys.stderr.write('creating ccg tagger for '+code+'\n')
            tagger = Supertagger(train=ccg_train, 
                                 sent_cls=CCG_CoNLL_UD)
            tagger.fit()
            tagger.save(ccg_model)
        else:
            print('MISSING TRAIN')
            no_train += 1

        if ccg_dev:
            # supertag dev segment again
            sys.stderr.write('tagging ccg for '+code+' dev\n')
            acc = tagger.tag(test=ccg_dev,save=ccg_dev_2)
            del tagger
            #
            results.append((code,acc))
            sys.stderr.write('\n')
        else:
            print('MISSING DEV')
            no_dev += 1

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

    all_langs += 1

    print()


print(str(all_langs) + ' languages')
print(str(no_dev) + ' with no dev')
print(str(no_train) + ' with no train')

for c,a in results:
    print(c +'\t'+str(a))


