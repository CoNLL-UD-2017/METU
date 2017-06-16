# args:
# /bin/bash ./run_dev.sh $inputDataset $inputRun $outputDir $dataServer $token

py="anaconda3/bin/python"


#INDIR=/media/training-datasets/universal-dependency-learning/conll17-ud-development-2017-03-19
INDIR=$1
#GOLD_DIR=../Supertagger2/ud-treebanks-conll2017
#GOLD_DIR=/media/training-datasets/universal-dependency-learning/conll17-ud-development-2017-03-19
GOLD_DIR=$1
CCG=data_ccg
PARSE=data_dep
#OUTDIR=outputs
OUTDIR=$3

#DEP_MODELS=models_dep
DEP_MODELS=models_dep
CCG_MODELS=models_ccg


echo "INPUT DIR  :" $1
echo "OUTPUT DIR :" $3
echo


#extract process metadata
$py parse_meta_test.py -v $INDIR

#LANGUAGES=(`cat name.txt`)
CODES=(`cat ltcode.txt`)
MODEL_CODES=(`cat modelcode.txt`)
#VCODES=(`cat lcode.txt`)
INPUT_FILES=(`cat psegmorfile.txt`)
OUTPUT_FILES=(`cat outfile.txt`)
#GOLD_FILES=(`cat goldfile.txt`)


for i in ${!CODES[@]}; do

	echo
	echo
	echo $((i+1))
	echo "Time: $(date)"
	echo


	#LANG=${LANGUAGES[${i}]}
	CODE=${CODES[${i}]}
	MODEL_CODE=${MODEL_CODES[${i}]}
	#VCODE=${VCODES[${i}]}
	INPUT_FILE=${INPUT_FILES[${i}]}
	OUTPUT_FILE=${OUTPUT_FILES[${i}]}
	#GOLD_FILE=${GOLD_FILES[${i}]}

	# gunzip embeddings/"$VCODE".vectors.xz

	INPUT="$INDIR"/"$INPUT_FILE"

	CCG_MODEL="$CCG_MODELS"/"$MODEL_CODE".pickle
	DEP_MODEL="$DEP_MODELS"/"$MODEL_CODE"-nndep-ccg.model.txt.gz

	TAGGED="$CCG"/"$CODE"-udpipe-ccg-2.conllu
	PARSED="$PARSE"/"$CODE"-udpipe-ccg-2-parsed.conllu
	OUTPUT="$OUTDIR"/"$OUTPUT_FILE"
	#GOLD="$GOLD_DIR"/"$GOLD_FILE"

	#echo "LANGUAGE       " $LANG
	echo "LANGUAGE CODE  " $CODE
	#echo "LANGUAGE SHORT " $VCODE

	echo "INPUT          " $INPUT
	echo "CCG MODEL      " $CCG_MODEL
	echo "DEP MODEL      " $DEP_MODEL
	echo "TAGGED         " $TAGGED
	echo "PARSED         " $PARSED
	echo "OUTPUT         " $OUTPUT
	#echo "GOLD           " $GOLD
	echo
	ls -l $INPUT
	ls -l $CCG_MODEL
	ls -l $DEP_MODEL
	echo

	# tag
	$py src_ccg/ccg_tagger.py "$MODEL_CODE" "$INPUT" "$TAGGED" "$CCG_MODELS"
	>&2 echo 
	ls -l $TAGGED

	
	# parse
	java -classpath ".:lib/trove.jar:src_dep/stanford-corenlp-3.7.0-multi.jar" \
		edu.stanford.nlp.parser.nndep.DependencyParser \
		-testFile "$TAGGED" \
		-model "$DEP_MODEL" \
		-outFile "$PARSED"
	>&2 echo 
	ls -l $PARSED

	# merge
	$py src_util/concat_multi_lines.py "$PARSED" "$TAGGED" "$OUTPUT"
	ls -l $OUTPUT
	#ls -l $GOLD

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
