py="/Users/Shared/anaconda/bin/python"








LANGUAGES=(
UD_Ancient_Greek
UD_Ancient_Greek-PROIEL
UD_Arabic
UD_Basque
UD_Bulgarian
UD_Catalan
UD_Chinese
UD_Croatian
UD_Czech
UD_Czech-CAC
UD_Czech-CLTT
UD_Danish
UD_Dutch
UD_Dutch-LassySmall
UD_English
UD_English-LinES
UD_English-ParTUT
UD_Estonian
UD_Finnish
UD_Finnish-FTB
UD_French
UD_French-Sequoia
UD_Galician
UD_German
UD_Gothic
UD_Greek
UD_Hebrew
UD_Hindi
UD_Hungarian
UD_Indonesian
UD_Italian
UD_Italian-ParTUT
UD_Japanese
UD_Korean
UD_Latin-ITTB
UD_Latin-PROIEL
UD_Latvian
UD_Norwegian-Bokmaal
UD_Norwegian-Nynorsk
UD_Old_Church_Slavonic
UD_Persian
UD_Polish
UD_Portuguese
UD_Portuguese-BR
UD_Romanian
UD_Russian
UD_Russian-SynTagRus
UD_Slovak
UD_Slovenian
UD_Spanish
UD_Spanish-AnCora
UD_Swedish
UD_Swedish-LinES
UD_Turkish
UD_Urdu
UD_Vietnamese
)


CODES=(
grc
grc_proiel
ar
eu
bg
ca
zh
hr
cs
cs_cac
cs_cltt
da
nl
nl_lassysmall
en
en_lines
en_partut
et
fi
fi_ftb
fr
fr_sequoia
gl
de
got
el
he
hi
hu
id
it
it_partut
ja
ko
la_ittb
la_proiel
lv
no_bokmaal
no_nynorsk
cu
fa
pl
pt
pt_br
ro
ru
ru_syntagrus
sk
sl
es
es_ancora
sv
sv_lines
tr
ur
vi
)


VCODES=(
grc
grc
ar
eu
bg
ca
zh
hr
cs
cs
cs
da
nl
nl
en
en
en
et
fi
fi
fr
fr
gl
de
got
el
he
hi
hu
id
it
it
ja
ko
la
la
lv
no_bokmaal
no_nynorsk
cu
fa
pl
pt
pt
ro
ru
ru
sk
sl
es
es
sv
sv
tr
ur
vi
)


INDIR=media/training-datasets/universal-dependency-learning/conll17-ud-development-2017-03-19
GOLD_DIR=../Supertagger2/ud-treebanks-conll2017
CCG=data_ccg
PARSE=data_dep
OUTDIR=outputs

#DEP_MODELS=models_dep
DEP_MODELS=../DependencyTraining/models
CCG_MODELS=../Supertagger2/models

for i in ${!LANGUAGES[@]}; do

	echo
	echo
	echo $((i+1))
	echo "Time: $(date)"
	echo


	LANG=${LANGUAGES[${i}]}
	CODE=${CODES[${i}]}
	VCODE=${VCODES[${i}]}

	# gunzip embeddings/"$VCODE".vectors.xz

	INPUT="$INDIR"/"$CODE"-udpipe.conllu
	CCG_MODEL="$CCG_MODELS"/"$CODE".pickle
	TAGGED="$CCG"/"$CODE"-udpipe-ccg-2.conllu
	MODEL="$DEP_MODELS"/"$CODE"-nndep-ccg.model.txt.gz
	PARSED="$PARSE"/"$CODE"-udpipe-ccg-2-parsed.conllu
	OUTPUT="$OUTDIR"/"$CODE"-udpipe-ccg-2-parsed.conllu
	GOLD="$GOLD_DIR"/"$CODE"-ud-dev-ccg-2.connlu

	echo "LANGUAGE       " $LANG
	echo "LANGUAGE CODE  " $CODE
	echo "LANGUAGE SHORT " $VCODE

	echo "INPUT          " $INPUT
	echo "CCG MODEL      " $CCG_MODEL
	echo "TAGGED         " $TAGGED
	echo "DEP MODEL      " $MODEL
	echo "PARSED         " $PARSED
	echo "OUTPUT         " $OUTPUT
	echo "GOLD           " $GOLD
	echo
	ls -l $INPUT

	
	# tag
	ls -l $CCG_MODEL
	#$py src_ccg/ccg_tagger.py "$CODE" "$INPUT" "$TAGGED" "$CCG_MODELS"
	ls -l $TAGGED

	
	# parse
	ls -l $MODEL
	#java -classpath ".:lib/trove.jar:src_dep/stanford-corenlp-3.7.0-multi.jar" \
	#	edu.stanford.nlp.parser.nndep.DependencyParser \
	#	-testFile "$TAGGED" \
	#	-model "$MODEL" \
	#	-outFile "$PARSED"
	ls -l $PARSED

	# merge
	#$py src_util/concat_multi_lines.py "$PARSED" "$TAGGED" "$OUTPUT"
	ls -l $OUTPUT
	ls -l $GOLD

	#eval
	#$py src_eval/conll17_ud_eval.py \
	#	-v \
	#	-w src_eval/weights.clas \
	#	"$GOLD" \
	#	"$OUTPUT"
	
	echo
	echo
	>&2 echo 
	>&2 echo 


done

echo "Time: $(date)"
