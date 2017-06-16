data
	input data

data_pre
	preprocessed data

data_ccg
	ccg tagged data

outputs
	dependency parsed data

models_ccg
	ccg models for ccg tagging

models_dep
	dependency models for parsing

src_ccg
	any source files necessary for ccg tagging

src_dep
	source files for dependency parsing

src_eval
	evaluation script

src_eval
	others, data processing etc

logs
	logs, results, reports etc.

run.sh
	script: from input to dep-parsed output


Examples:

# parse
java -classpath ".:lib/trove.jar:models_dep/stanford-corenlp-3.7.0-embed.jar" \
	edu.stanford.nlp.parser.nndep.DependencyParser \
	-testFile data_ccg/tr-udpipe-ccg.conllu \
	-model models_dep/tr-nndep-ccg.model.txt.gz \
	-outFile outputs/tr-udpipe-ccg-parsed.conllu

java -classpath ".:lib/trove.jar:models_dep/stanford-corenlp-3.7.0-embed.jar" \
	edu.stanford.nlp.parser.nndep.DependencyParser \
	-testFile data_ccg_backup/de-ud-dev-ccg-2.conllu \
	-model models_dep/de-nndep-ccg.model.txt.gz \
	-outFile outputs/de-ud-dev-ccg-2-parsed.conllu

# eval
conll17_ud_eval.py [-v] [-w weights_file] gold_conllu_file system_conllu_file

python src_eval/conll17_ud_eval.py -v -w src_eval/weights.clas data_gold/tr-ud-dev.conllu outputs/tr-udpipe-ccg-parsed.conllu

python src_eval/conll17_ud_eval.py -v -w src_eval/weights.clas data_gold/tr-ud-dev.conllu data_pre/tr-ud-dev.conllu

python src_eval/conll17_ud_eval.py -v -w src_eval/weights.clas data_gold/de-ud-dev.conllu data_pre/de-ud-dev.conllu

# tag
python src_ccg/ccg_tagger.py tr data_pre/tr-udpipe.conllu data_ccg/tr-udpipe-ccg.conllu

# preprocess
python src_util/clear_multi_word.py data/tr-udpipe.conllu data_pre/tr-udpipe.conllu

