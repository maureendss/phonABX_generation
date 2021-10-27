#!/bin/bash

# Copyright 2012   Vassil Panayotov
#           2017   Ewald Enzinger
# Apache 2.0

# Adapted from egs/voxforge/s5/local/voxforge_prepare_dict.sh (commit acb5439bf97a39398d5eeb926a2a5cfa71b5f72a)

. path.sh || exit 1


use_g2p=False #when true, we use the g2p, else we put all words as junk
folding=False #when equal true, means we fold accordingly to https://docs.google.com/presentation/d/1hATl3iykOs47BK3cPfvb7Q_8NlB5qiVVA9gOtl4CYAk/edit#slide=id.gf9b4e683a9_0_57


. utils/parse_options.sh

echo $use_g2p
echo "Folding $folding"

#set -e 
if [ $# != 3 ]; then
    echo "Usage: local/prepare_lm.sh <path_to_data> <lang>"
    exit 1;
fi


data=$1
lang=$2
locdata=$3


#locdata=$data/local
locdict=$locdata/dict


echo "=== Preparing the dictionary ..."

if [ $lang != "en" ] && [ $lang != "fr" ]; then
    echo "Lang Not supported";
    exit 1
fi


if [ ! -d data/cmudict ]; then
    echo "--- Downloading CMU dictionary ..."
    svn co http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict data/cmudict || exit 1 ;
fi

if [ $lang == "en" ] && [ ! -f $locdict/cmudict/cmudict ]; then
  echo "--- Downloading CMU dictionary ..."
  mkdir -p $locdict
  cp data/cmudict/cmudict.0.7a $locdict/cmudict
  
elif [ $lang == "fr" ] && [ ! -f $locdict/cmudict/cmudict ]; then
    echo "--- Downloading CMU dictionary ..."
    mkdir -p $locdict
    wget https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/French/fr.dict/download -O $locdict/cmu_dict
fi



if [ $lang == "en" ]; then 
    echo "--- Striping stress and pronunciation variant markers from cmudict ..."
    if [ "${folding}" == "False" ]; then
        perl data/cmudict/scripts/make_baseform.pl \
         $locdict/cmudict /dev/stdout |\
            sed -e 's:^\([^\s(]\+\)([0-9]\+)\(\s\+\)\(.*\):\1\2\3:' | tr '[A-Z]' '[a-z]' > $locdict/cmudict-plain.txt

    else
        echo "Preparing with folding"
        #DON4t DO THE FOLDING BASEFORME which is done in make_baseform.pl
        perl local/cmu_make_baseform_withfolding.pl \
             $locdict/cmudict /dev/stdout |\
            sed -e 's:^\([^\s(]\+\)([0-9]\+)\(\s\+\)\(.*\):\1\2\3:' | tr '[A-Z]' \
        '[a-z]' > $locdict/cmudict-plain.txt
    fi
    #sed -e 's:^\([^\s(]\+\)([0-9]\+)\(\s\+\)\(.*\):\1\2\3:' | tr '[a-z]' '[A-Z]' > $locdict/cmudict-plain.txt

    
    echo "--- Searching for OOV words ..."
    awk 'NR==FNR{words[$1]; next;} !($1 in words)' \
        $locdict/cmudict-plain.txt $locdata/vocab-full.txt |\
        egrep -v '<.?s>' > $locdict/vocab-oov.txt



    awk 'NR==FNR{words[$1]; next;} ($1 in words)' \
        $locdata/vocab-full.txt $locdict/cmudict-plain.txt |\
        egrep -v '<.?s>' > $locdict/lexicon-iv.txt

    wc -l $locdict/vocab-oov.txt
    wc -l $locdict/lexicon-iv.txt

elif [ $lang == "fr" ]; then
    dir=$locdict
    text=$data 

    #cat $dir/cmu_dict |  tr '[a-z]' '[A-Z]' > $dir/cmu_dict-plain.txt
    cat $dir/cmu_dict | sed -e 's:^\([^\s(]\+\)([0-9]\+)\(\s\+\)\(.*\):\1\2\3:' | sed -E 's/\([0-9]*\)//g' >  $dir/cmudict-plain.txt
    
    echo "--- Preparing the corpus from data/train/text transcripts ---"
    corpusfile=$dir/corpus
    cut -f2- -d' ' < $text/text | sed -e 's:[ ]\+: :g' > $corpusfile

    echo "--- preparing full vocabulary file ---"
    sed 's/ /\n/g' $corpusfile | sort -u -f | grep '[^[:blank:]]' > $dir/vocab-full.txt
    sed -i '1i-pau-\n</s>\n<s>\n<unk>' $dir/vocab-full.txt

    echo "--- Searching for OOV words ---"
    awk 'NR==FNR{words[$1]; next;} !($1 in words)' $dir/cmudict-plain.txt $dir/vocab-full.txt | egrep -v '<.?s>' > $dir/vocab-oov.txt

    awk 'NR==FNR{words[$1]; next;} ($1 in words)' $dir/vocab-full.txt $dir/cmudict-plain.txt  | egrep -v '<.?s>' > $dir/lexicon-iv.txt

    wc -l $locdict/vocab-oov.txt
    wc -l $locdict/lexicon-iv.txt

    
fi

if [ ! -f conf/g2p/$lang/g2p_model ]; then
    echo "Please add or train a G2P model"
fi


#sequitur=$KALDI_ROOT/tools/sequitur-g2p
#export PATH=$PATH:$sequitur/bin
#export PYTHONPATH=$PYTHONPATH:`utils/make_absolute.sh $sequitur/lib/python*/site-pac!!kages`


if [ "$use_g2p" == "True" ]; then
    echo "--- Preparing pronunciations for OOV words ..."

    if ! g2p=`which g2p.py` ; then
        echo "The Sequitur was not found !"
        echo "Go to $KALDI_ROOT/tools and execute extras/install_sequitur.sh"
        exit 1
    fi

    g2p.py --model=conf/g2p/$lang/g2p_model --apply $locdict/vocab-oov.txt > $locdict/lexicon-oov.txt
else
    #awk '{ print $1 "\toov"}' $locdict/vocab-oov.txt > $locdict/lexicon-oov.txt
    touch $locdict/lexicon-oov.txt
fi

cat $locdict/lexicon-oov.txt $locdict/lexicon-iv.txt |\
  sort -u > $locdict/lexicon.txt
rm $locdict/lexiconp.txt 2>/dev/null || true

echo "--- Prepare phone lists ..."
#echo -e 'SIL'\\n'oov' > $locdict/silence_phones.txt
echo SIL > $locdict/silence_phones.txt
echo SIL > $locdict/optional_silence.txt
grep -v -w sil $locdict/lexicon.txt | \
  awk '{for(n=2;n<=NF;n++) { p[$n]=1; }} END{for(x in p) {print x}}' |\
  sort > $locdict/nonsilence_phones.txt

   #sed -i '/oov/d' $locdict/nonsilence_phones.txt 

echo "--- Adding <unk> to the lexicon ..."
echo -e "<unk>\tSIL" >> $locdict/lexicon.txt
echo -e 'SIL'\\n'oov' > $locdict/silence_phones.txt
echo -e "!SIL\tSIL" >> $locdict/lexicon.txt

# Some downstream scripts expect this file exists, even if empty
touch $locdict/extra_questions.txt

echo "*** Dictionary preparation finished!"
