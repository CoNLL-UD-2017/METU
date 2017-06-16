# -*- coding:utf-8 -*-
'''
Created on 2 Şub 2017

@author: BurakKerim
'''


tex_header = '''%!TEX TS-program = xelatex
%!TEX encoding = UTF-8 Unicode

\\documentclass[10pt,a4paper]{article} 
\\usepackage[margin=0.5in]{geometry}

\\usepackage{fontspec}

\\usepackage[dvipsnames]{xcolor}
\\usepackage{adjustbox}

\\usepackage{tikz} 
\\usepackage{tikzscale}
\\usepackage{tikz-dependency}
\\usetikzlibrary{arrows,decorations.pathmorphing,backgrounds,fit,positioning,shapes.symbols,chains}

\\setmainfont{Arial Unicode MS}

\\begin{document}


'''

tex_footer = '''

\\end{document}

'''

figure_header = '''
\\begin{figure}[h]
\\centering
'''

figure_footer = '''
\\end{figure}
'''

dep_node_style_example = '''
\\tikzstyle{word}=[draw=blue!60!black, shade, text=black,
                    rotate=45, anchor=north east, inner sep=1ex,
                    font=\\normalsize, top color=blue!60, rounded corners]
'''

dep_node_style = '''
\\tikzstyle{word}=[font=\\normalsize, text=black,
                   draw=Green, rounded corners]
'''

dep_node_style_empty = '''
\\tikzstyle{word-empty}=[font=\\normalsize, text=Thistle,
                        draw=Thistle, rounded corners]
'''

dep_node_pos_style = '''
\\tikzstyle{attr}=[text=black, font=\\normalsize, ]
'''

dep_node_pos_style_empty = '''
\\tikzstyle{attr-empty}=[text=Thistle, font=\\normalsize, ]
'''

dep_style_1 = '''
\\depstyle{rel}{edge style = {thick, OrangeRed}, 
                 label style = {thick, font=\\normalsize, draw=OrangeRed, text=blue, fill=white, anchor=mid,}}
'''

dep_style_2 = '''
\\depstyle{rel2}{edge style = {thick, BrickRed}, 
                 label style = {thick, font=\\normalsize, draw=BrickRed, text=blue, fill=white, anchor=mid,}}
'''

dep_style_3 = '''
\\depstyle{root}{edge style = {thick, OliveGreen}, 
                 label style = {thick, font=\\normalsize, draw=OliveGreen, text=blue, fill=white, anchor=mid,}}
'''

dep_style_4 = '''
\\depstyle{root2}{edge style = {thick, YellowGreen}, 
                  label style = {thick, font=\\normalsize, draw=YellowGreen, text=blue, fill=white, anchor=mid,}}
'''

dep_style_5 = '''
\\depstyle{relccg}{edge style = {thick, NavyBlue}, 
                 label style = {thick, font=\\normalsize, draw=NavyBlue, text=blue, fill=white, anchor=mid,}}
'''

group_style = '{draw=OliveGreen, inner sep=.3ex}'

tikz_node = '''
\\tikzstyle{word} = [rectangle,
           rounded corners,
           draw=black,
           fill=white,
           %minimum height=0.5cm,
           inner sep=5pt,
           text centered,
           node distance=2cm,
           align=center]
'''

tikz_node_empty = '''
\\tikzstyle{word_empty} = [rectangle,
           rounded corners,
           draw=gray,
           fill=black!10,
           %minimum height=0.5cm,
           inner sep=5pt,
           text centered,
           node distance=2cm,
           align=center]
'''

tikz_node_rel = '''
\\tikzstyle{rel} = [rectangle,
           rounded corners,
           draw=blue,
           fill=blue!10,
           %minimum height=0.5cm,
           inner sep=5pt,
           text centered,
           node distance=2cm,
           align=center]
'''

# latex escape from:
# https://github.com/vog/python-tex

_latex_special_chars = {
    u'$':  u'\\$',
    u'%':  u'\\%',
    u'&':  u'\\&',
    u'#':  u'\\#',
    u'_':  u'\\_',
    u'{':  u'\\{',
    u'}':  u'\\}',
    u'[':  u'{[}',
    u']':  u'{]}',
    u'"':  u"{''}",
    u'\\': u'\\textbackslash{}',
    u'~':  u'\\textasciitilde{}',
    u'<':  u'\\textless{}',
    u'>':  u'\\textgreater{}',
    u'^':  u'\\textasciicircum{}',
    u'`':  u'{}`',   # avoid ?` and !`
    u'\n': u'\\\\',
}

def escape(s):
    r'''Escape a unicode string for LaTeX.
    :Warning:
        The source string must not contain empty lines such as:
            - u'\n...' -- empty first line
            - u'...\n\n...' -- empty line in between
            - u'...\n' -- empty last line
    :Parameters:
        - `s`: unicode object to escape for LaTeX
    >>> s = u'\\"{}_&%a$b#\nc[]"~<>^`\\'
    >>> escape_latex(s)
    u"\\textbackslash{}{''}\\{\\}\\_\\&\\%a\\$b\\#\\\\c{[}{]}{''}\\textasciitilde{}\\textless{}\\textgreater{}\\textasciicircum{}{}`\\textbackslash{}"
    >>> print s
    \"{}_&%a$b#
    c[]"~<>^`\
    >>> print escape_latex(s)
    \textbackslash{}{''}\{\}\_\&\%a\$b\#\\c{[}{]}{''}\textasciitilde{}\textless{}\textgreater{}\textasciicircum{}{}`\textbackslash{}
    '''
    return u''.join(_latex_special_chars.get(c, c) for c in s)

if __name__ == '__main__':
    for s in ['מג"ב']: 
        print(s, escape(s))
