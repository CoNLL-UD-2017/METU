py="/Users/Shared/anaconda/bin/python"








LANGUAGES=(
UD_English
UD_French
UD_German
UD_Turkish
)


CODES=(
en
fr
de
tr
)


VCODES=(
en
fr
de
tr
)


INDIR=media/training-datasets/universal-dependency-learning/conll17-ud-development-2017-03-19
GOLD_DIR=../Supertagger2/ud-treebanks-conll2017
CCG=data_ccg
PARSE=data_dep
OUTDIR=outputs

#DEP_MODELS=models_dep
DEP_MODELS=../DependencyTraining/models-base
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
	MODEL="$DEP_MODELS"/"$CODE"-nndep-base.model.txt.gz
	PARSED="$PARSE"/"$CODE"-udpipe-base-parsed.conllu
	OUTPUT="$OUTDIR"/"$CODE"-udpipe-base-parsed.conllu
	GOLD="$GOLD_DIR"/"$CODE"-ud-dev-base.connlu

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
	#java -classpath ".:lib/trove.jar:src_dep/stanford-corenlp-base.jar" \
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
