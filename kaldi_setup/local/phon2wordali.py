#!/usr/bin/env python3

import pandas as pd
from tqdm import tqdm
from nltk import pos_tag
import mmap

#if french need the stanford pos tagger https://nlp.stanford.edu/software/tagger.shtml#About
from nltk.tag import StanfordPOSTagger

#to cahnge depending on machine


def phone2prons(phone_df):
    phone_df["phone"] = phone_df.apply(lambda x : x.phone_long.split("_")[0], axis=1)
    phone_df["phone_pos"] = phone_df.apply(lambda x : x.phone_long.split("_")[-1], axis=1)


    pron_list = []


    for segment in tqdm(phone_df["segment"].unique()):
        prons  = []
        dur = 0
        for index, row in phone_df[phone_df["segment"] == segment].iterrows():
            if row["phone_long"] == "SIL":
                continue
            elif row["phone_pos"] == "S": # S including SIL_S (junks)
                start = row["start"]
                dur += row["dur"]
                prons.append(row["phone"])
                pron_list.append((segment, start, dur, prons))
                prons = []
                dur = 0
            elif row["phone_pos"] == "B": # beginning of word
                start = row["start"]
                dur += row["dur"]
                prons.append(row["phone"])
            elif row["phone_pos"] == "I": # middle of word
                prons.append(row["phone"])
                dur += row["dur"]
            elif row["phone_pos"] == "E": # end of word
                prons.append(row["phone"])
                dur += row["dur"]
                pron_list.append((segment, start, dur, prons))
                prons = []
                dur = 0
            else:
                raise ValueError("Problem with segment {} on phone {}".format(segment, row["phone_long"]))

    prons_df  = pd.DataFrame(pron_list, columns=['segment', 'start', 'dur', "pron"])
    return prons_df


def prons2words(prons_df, text, get_pos = False, model=None, jar=None, lang="en"):

    pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8' )
    
    seg2words = {}
    print("Retrieveing sentences from text, and potentially getting pos")
    with open(text, encoding="UTF-8") as infile :
        for l in tqdm(infile, total=len(prons_df["segment"].unique())) :
            segment = l.split(" ")[0]
            
            if segment in prons_df["segment"].unique():
                sent = list(filter(None, l.strip().split(" ")[1:]))

                if not get_pos : 
                    seg2words[segment] = sent

                else :

                    #print(sent, pos_sent)
                    if lang == "fr" : 
                        pos_sent = pos_tagger.tag(sent)
                        seg2words[segment] =pos_sent
                    elif lang == "en":
                        seg2words[segment] = pos_tag(sent) #nltk english only                

    df_dict = {}

    print("Matching word to pron")
    if not get_pos :
        for index, row in tqdm(prons_df.iterrows(), total=prons_df.shape[0]):
            if row["pron"] == ["SIL"]:
                word = "<UNK>"
            else:
                word = seg2words[row["segment"]][0]
            df_dict[index] = [row["segment"], row["start"], row["dur"], '_'.join(row["pron"]), word]
            seg2words[row["segment"]].pop(0)

        df = pd.DataFrame.from_dict(df_dict, orient="index", columns=['segment', 'start', 'dur', "pron", "word"])
    else :
        for index, row in tqdm(prons_df.iterrows(), total=prons_df.shape[0]):
            if row["pron"] == ["SIL"]:
                word = "<UNK>"
                pos = "<UNK>"
            else:
                word = seg2words[row["segment"]][0][0]
                pos = seg2words[row["segment"]][0][1]
            df_dict[index] = [row["segment"], row["start"], row["dur"], '_'.join(row["pron"]),
                              word, pos]
            seg2words[row["segment"]].pop(0)

            
        df = pd.DataFrame.from_dict(df_dict, orient="index", columns=['segment', 'start', 'dur', "pron", "word", "pos"])
    return df
                

#utils

def get_num_lines(file_path):
    fp = open(file_path, "r+")
    buf = mmap.mmap(fp.fileno(), 0)
    lines = 0
    while buf.readline():
        lines += 1
    return lines


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument("alignment_file", help="ali CTM file from kaldi")
    parser.add_argument('output_item')
    parser.add_argument('text', help="path_to_text")
    parser.add_argument('lang', help="language (for phone folding). Currently accepted : 'en', 'fr'")
    parser.add_argument("--pos", help="Use nltk pos tagger to get pos", default=False, action="store_true")
    parser.add_argument("--stanford_pos_path", default = "/scratch2/mde/repos/stanford-postagger-full-2020-11-17")
    parser.parse_args()
    args, leftovers = parser.parse_known_args()


    if args.pos :
        
        jar = os.path.join(args.stanford_pos_path, "stanford-postagger-4.2.0.jar")
        if args.lang == "fr":
            model = os.path.join(args.stanford_pos_path, "models/french-ud.tagger")
        else:
            model = os.path.join(args.stanford_pos_path, "models/english-bidirectional-distsim.tagger")
    else:
        model=None
        jar=None
    print("Reading ali.ctm")
    phone_df = pd.read_csv(args.alignment_file, delim_whitespace=True, header=None, names=['segment', 'pos', 'start', 'dur','phone_long'])
    print("Creating phon2prons")
    prons_df = phone2prons(phone_df)
    print("Getting word from pron")
    df = prons2words(prons_df, args.text, get_pos = args.pos, model=model, jar = jar, lang=args.lang)
    df.to_csv(args.output_item, sep=" ")
