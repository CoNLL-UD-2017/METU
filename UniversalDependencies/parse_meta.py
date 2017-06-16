# -*- coding:utf-8 -*-

import json, sys
from pprint import pprint



with open(sys.argv[2]+'/metadata.json') as data_file:
    data = json.load(data_file)

with open('name.txt', 'w', encoding='utf-8') as name_file:
	with open('lcode.txt', 'w', encoding='utf-8') as lcode_file:
		with open('psegmorfile.txt', 'w', encoding='utf-8') as psegmorfile_file:
			with open('outfile.txt', 'w', encoding='utf-8') as outfile_file:
				with open('goldfile.txt', 'w', encoding='utf-8') as goldfile_file:
					with open('ltcode.txt', 'w', encoding='utf-8') as ltcode_file:
						for item in data:
							name_file.write(item['name']+ '\n')
							lcode_file.write(item['lcode']+ '\n')
							psegmorfile_file.write(item['psegmorfile']+ '\n')
							outfile_file.write(item['outfile']+ '\n')
							goldfile_file.write(item['goldfile']+ '\n')
							ltcode_file.write(item['ltcode']+ '\n')