import os

treebanks = 'ud-treebanks-conll2017/'

dev_ = '-ud-dev.conllu'
train_ = '-ud-train.conllu'

all_langs = 0
no_dev = 0
no_train = 0

for lang in os.listdir(treebanks):
    code = dev = train = ''
    for f in os.listdir(treebanks+lang):
        if train_ in f:
            train = treebanks+lang+'/'+f
            key = f.split('-')[0]
        elif dev_ in f:
            dev = treebanks+lang+'/'+f
        else:
            pass

    if dev and train:
        print('language: '+lang + ' code: '+ key)
        print('training: '+train)
        print('developm: '+dev)
    elif train:
        print('MISSING DEV')
        print('language: '+lang + ' code: '+ key)
        print('training: '+train)
        no_dev += 1
    elif dev:
        print('MISSING TRAIN')
        print('language: '+lang + ' code: '+ key)
        print('training: '+dev)
        no_train += 1

    all_langs += 1

    print()


print(str(all_langs) + ' languages')
print(str(no_dev) + ' with no dev')
print(str(no_train) + ' with no train')