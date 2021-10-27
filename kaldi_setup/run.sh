#!/bin/bash

# Recipe for Mozilla Common Voice corpus v1
#
# Copyright 2017   Ewald Enzinger
# Apache 2.0

# for EN and FR 

data=/scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/



. ./cmd.sh
. ./path.sh

stage=0
lang=en

. ./utils/parse_options.sh

set -euo pipefail

echo "stage : $stage , lang : $lang"

if [ $stage -le 1 ]; then

    #we create two lang dict : one with OOV the other without
    # we use the one with transcription to train the GMM, then the one withput to align 
  # use underscore-separated names in data directories.
  local/data_prep.pl $data $lang/selected data/$lang $lang

  
  # Prepare ARPA LM and vocabulary using SRILM
  local/prepare_lm.sh data/$lang 
  # Prepare the lexicon and various phone lists
  # Pronunciations for OOV words are obtained using a pre-trained Sequitur model
  #local/prepare_dict.sh --use_g2p True data/$lang $lang data/$lang/local_g2p

  local/prepare_dict.sh --folding True --use_g2p False data/$lang $lang data/$lang/local



  
  # Prepare data/lang and data/local/lang directories
  #utils/prepare_lang.sh data/$lang/local_g2p/dict \
  #  '<unk>' data/$lang/local_g2p/lang data/$lang/lang_g2p || exit 1

    # Prepare data/lang and data/local/lang directories
  utils/prepare_lang.sh data/$lang/local/dict \
    '<unk>' data/$lang/local/lang data/$lang/lang || exit 1

  #utils/format_lm.sh data/$lang/lang_g2p data/$lang/local/lm.gz data/$lang/local_g2p/dict/lexicon.txt data/$lang/lang_g2p_test/
  
  utils/format_lm.sh data/$lang/lang data/$lang/local/lm.gz data/$lang/local/dict/lexicon.txt data/$lang/lang_test/

fi

if [ $stage -le 2 ]; then
  mfccdir=mfcc
  # spread the mfccs over various machines, as this data-set is quite large.

    steps/make_mfcc.sh --cmd "$train_cmd" --nj 1 data/$lang exp/make_mfcc/$lang $mfccdir
    steps/compute_cmvn_stats.sh data/$lang exp/make_mfcc/$lang $mfccdir
fi



#train with G2P pron
# align silence.

# train a monophone system
# first alignment is done using the g2p
# then only we will use the ones with OOV.

if [ $stage -le 3 ]; then
      
      # if [ $lang == "fr" ]; then
      #     steps/train_mono.sh --nj 24  --totgauss 2000 --cmd "$train_cmd" data/$lang data/$lang/lang exp/$lang/mono || exit 1;
          
      #     steps/align_si.sh --nj 10 --cmd "$train_cmd" \
      #                       data/$lang data/$lang/lang exp/$lang/mono exp/$lang/mono_ali
      # else
          steps/train_mono.sh --nj 24  --cmd "$train_cmd" data/$lang data/$lang/lang exp/$lang/mono || exit 1;
          
          steps/align_si.sh --boost_silence 1.25 --nj 10 --cmd "$train_cmd" \
                            data/$lang data/$lang/lang exp/$lang/mono exp/$lang/mono_ali
          # fi                    

  # #only silence 0.5 to reduce silence proba.
  #   if [ $lang == "fr" ]; then
  #    steps/train_mono.sh --nj 24 --cmd "$train_cmd" \
  #    --boost-silence 0.1  data/$lang data/$lang/lang_g2p exp/$lang/mono || exit 1;

  #     steps/align_si.sh --boost-silence 0.1 --nj 24 --cmd "$train_cmd" \
  #       data/$lang data/$lang/lang_g2p exp/$lang/mono exp/$lang/mono_ali
  # else
  #     steps/train_mono.sh --nj 24 --cmd "$train_cmd" \
  #           data/$lang data/$lang/lang_g2p exp/$lang/mono || exit 1;
      
  #     steps/align_si.sh --boost-silence 1.25 --nj 10 --cmd "$train_cmd" \
  #      data/$lang data/$lang/lang_g2p exp/$lang/mono exp/$lang/mono_ali
  # fi
fi

# train a first delta + delta-delta triphone system
if [ $stage -le 4 ]; then
  steps/train_deltas.sh   --boost-silence 1.25 --cmd "$train_cmd" \
    2000 10000 data/$lang data/$lang/lang exp/$lang/mono_ali exp/$lang/tri1

  steps/align_si.sh --nj 10 --cmd "$train_cmd" \
    data/$lang data/$lang/lang exp/$lang/tri1 exp/$lang/tri1_ali
fi

# train an LDA+MLLT system.
if [ $stage -le 5 ]; then
  steps/train_lda_mllt.sh  --cmd "$train_cmd" \
    --splice-opts "--left-context=3 --right-context=3" 2500 15000 \
    data/$lang data/$lang/lang exp/$lang/tri1_ali exp/$lang/tri2b

  # decode using the LDA+MLLT model
  utils/mkgraph.sh data/$lang/lang_test exp/$lang/tri2b exp/$lang/tri2b/graph

  # Align utts using the tri2b model
  steps/align_si.sh --nj 10 --cmd "$train_cmd" --use-graphs true \
    data/$lang data/$lang/lang exp/$lang/tri2b exp/$lang/tri2b_ali;
fi

# Train tri3b, which is LDA+MLLT+SAT
if [ $stage -le 6 ]; then
  steps/train_sat.sh --cmd "$train_cmd" 2500 15000 \
    data/$lang data/$lang/lang exp/$lang/tri2b_ali exp/$lang/tri3b
fi

if [ $stage -le 7 ]; then
  # Align utts in the full training set using the tri3b model
  steps/align_fmllr.sh --nj 20 --cmd "$train_cmd" \
    data/$lang data/$lang/lang \
    exp/$lang/tri3b exp/$lang/tri3b_ali

  # train another LDA+MLLT+SAT system on the entire training set
  steps/train_sat.sh  --cmd "$train_cmd" 4200 40000 \
    data/$lang data/$lang/lang \
    exp/$lang/tri3b_ali exp/$lang/tri4b

  steps/align_fmllr.sh --nj 20 --cmd "$train_cmd" \
   data/$lang data/$lang/lang \
    exp/$lang/tri4b exp/$lang/tri4b_ali

  # # decode using the tri4b model
  # (
  #   utils/mkgraph.sh data/lang_test exp/tri4b exp/tri4b/graph
  #   for testset in valid_dev; do
  #     steps/decode_fmllr.sh --nj 20 --cmd "$decode_cmd" \
  #       exp/tri4b/graph data/$testset \
  #       exp/tri4b/decode_$testset
  #   done
  # )&
fi

ali-to-phones --ctm-output exp/$lang/tri4b_ali/final.mdl ark:"gunzip -c exp/$lang/tri4b_ali/ali.*.gz|" -  | utils/int2sym.pl -f 5 data/$lang/lang/phones.txt - > exp/$lang/tri4b_ali/ali.ctm 
