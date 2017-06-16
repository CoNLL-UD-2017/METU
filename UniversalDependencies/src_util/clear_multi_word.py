'''
removes multi word token lines
removes _ used for empty words
'''

import sys

fi_name = sys.argv[1]
fo_name = sys.argv[2]

fi = open(fi_name, 'r', encoding='utf-8')
fo = open(fo_name, 'w', encoding='utf-8')

for line in fi:
    if line.strip() == '':
        fo.write(line)
    elif line.strip()[0] == '#':
        fo.write(line)
    else:
        fields = line.strip().split('\t')
        if '-' not in fields[0]:
            #if fields[1] == '_':
            #    fields[1] = ''
            fo.write('\t'.join(fields) + '\n')