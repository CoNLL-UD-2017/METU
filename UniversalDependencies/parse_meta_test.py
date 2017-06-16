# -*- coding:utf-8 -*-

import json, sys
from pprint import pprint

unknown={
	# no dep model -> no word embeddings
	'got': 'de', # gothic
	# surprise
	'bxr': 'ru', # Buryat
	'kmr': 'fa', # Kurmanji
	'sme': 'fi', # North Sami
	'hsb': 'cs', # Upper Sorbian
	# new / no model
	'ar_pud': 'ar',
	'cs_pud': 'cs',
	'de_pud': 'de',
	'en_pud': 'en',
	'es_pud': 'es',
	'fi_pud': 'fi',
	'fr_partut': 'fr',
	'fr_pud': 'fr',
	'ga': 'en', # irish
	'gl_treegal': 'gl',
	'hi_pud': 'hi',
	'it_pud': 'it',
	'ja_pud': 'ja',
	'kk': 'tr', # kazakh
	'la': 'la_ittb',
	'pt_pud': 'pt',
	'ru_pud': 'ru',
	'sl_sst': 'sl',
	'sv_pud': 'sv',
	'tr_pud': 'tr',
	'ug': 'tr', # uyghur
	'uk': 'ru', # ukrainian
	}


with open(sys.argv[2]+'/metadata.json') as data_file:
    data = json.load(data_file)

psegmorfile_file = open('psegmorfile.txt', 'w', encoding='utf-8')
outfile_file = open('outfile.txt', 'w', encoding='utf-8')
ltcode_file = open('ltcode.txt', 'w', encoding='utf-8')
modelcode_file = open('modelcode.txt', 'w', encoding='utf-8')
						

for item in data:
	psegmorfile_file.write(item['psegmorfile']+ '\n')
	outfile_file.write(item['outfile']+ '\n')
	ltcode_file.write(item['ltcode']+ '\n')
	# Gothic
	if item['ltcode'] in unknown:
		modelcode_file.write(unknown[item['ltcode']]+ '\n')
	else:
		modelcode_file.write(item['ltcode']+ '\n')

psegmorfile_file.close()
outfile_file.close()
ltcode_file.close()
modelcode_file.close()