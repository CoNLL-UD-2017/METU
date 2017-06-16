# -*- coding:utf-8 -*-
'''
Created on Feb 6, 2017

@author: BurakKerim
'''


import os, sys
import logging
from merge_graphs import Merge_UD_CCG

LOG_LEVEL = logging.INFO

dir_ud = 'dep/'
dir_ccg = 'ccg/'
dir_merged = 'merged/'
dir_tex = 'merged_pdf/'

log = open('merge_all_check.txt', 'w', encoding='utf-8')
total_missing_ccg = 0
total_sentences = 0

# assume paraller structure in both directories
for section in sorted(os.listdir(dir_ud)):
    print('section: '+section)
    sys.stderr.write('section: '+section+'\n')
    for part in sorted(os.listdir(dir_ud+section)):
        try:
            base_name = os.path.splitext(os.path.basename(part))[0]
            base_name = section+'/'+base_name
            print('\tfile: '+base_name)
            sys.stderr.write('\tfile: '+base_name+'\n')
            deps = Merge_UD_CCG(dir_ud+base_name+'.mrg', dir_ccg+base_name+'.parg', LOG_LEVEL)
            # save merged file
            deps.save(dir_merged+base_name+'.conllu')
            # save tex files
            # if build use separate=True -> otherwise dimension error 
            #deps.to_tex(dir_tex+base_name+'.tex', separate=True, build=False)
            #deps.to_tex(dir_tex+base_name+'.tex', separate=False, build=False)
            # info
            total_sentences += len(deps.graphs)
            if deps.diff:
                log.write('FILE ' +dir_ud+base_name+ ' does not have ccg derivations for these sentences: ' +str(deps.diff)+'\n')
                log.flush()
                total_missing_ccg += len(deps.diff)
            # clear
            del deps
        except Exception as e:
            log.write('\nCRITICAL ERROR in file '+base_name+'\n\n')
            log.flush()
            sys.stderr.write('\nCRITICAL ERROR in file '+base_name+'\n')
            sys.stderr.write(str(e)+'\n\n')

log.write('\n\n')
log.write(str(total_sentences)+' sentences with ccg derivations\n')
log.write(str(total_missing_ccg)+' sentences without ccg derivations\n')
log.write(str(total_sentences+total_missing_ccg)+' sentencesin total\n')
log.close()
