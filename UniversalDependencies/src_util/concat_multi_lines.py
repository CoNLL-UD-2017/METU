# -*- coding:utf-8 -*-

import sys

outfilename = sys.argv[1]

testfilename = sys.argv[2]

mergefile = sys.argv[3]

update_in_last_step = False

with open(mergefile, 'w', encoding='utf-8') as mfile:
	with open(outfilename, 'r', encoding='utf-8') as outfile:
		with open(testfilename, 'r', encoding='utf-8') as readfile:
			for line in readfile:
				if line.startswith("#"):
					continue
				else:
					if not update_in_last_step:
						oline = outfile.readline()
					if oline.split("\t")[0] == line.split("\t")[0]:
						update_in_last_step = False
						mfile.write(oline)
					else:
						update_in_last_step = True
						mfile.write(line)
