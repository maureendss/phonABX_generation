#!/usr/bin/env python3

import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import os, re, time, warnings, sys
import warnings
import pickle
import numpy as np


### phone to categ
fr_phone_char = {'gn': 'nasal',
  'nn': 'nasal',
  'mm': 'nasal',
  'jj': 'fricative',
  'ss': 'fricative',
  'll': 'approximant',
  'bb': 'plosive',
  'kk': 'plosive',
  'vv': 'fricative',
  'zz': 'fricative',
  'gg': 'plosive',
  'ww': 'semi-vowel',
  'pp': 'plosive',
  'ff': 'fricative',
  'ch': 'fricative',
  'rr': 'fricative',
  'yy': 'approximant',
  'dd': 'plosive',
  'tt': 'plosive',
  'ou': 'vowel',
  'ei': 'vowel',
  'ii': 'vowel',
  'au': 'vowel',
  'aa': 'vowel',
  'ai': 'vowel',
  'on': 'vowel',
  'an': 'vowel',
  'oo': 'vowel',
  'oe': 'vowel',
  'eu': 'vowel',
  'ee': 'vowel',
  'un': 'vowel',
  'uu': 'vowel',
  'in': 'vowel',
  'uy': 'vowel'}

#removed nasal vowel

en_phone_char = {
    'dh': 'fricative', 'ah':'vowel','ah0':'vowel', 'v':'fricative', 'ae':'vowel', 'l':'approximant', 'iy':'vowel',
    'w':'approximant', 'z':'fricative', 'f':'fricative', 'ih':'vowel', 'd':'plosive', 'th':'fricative',
    'eh':'vowel', 'n':'nasal', 's':'fricative', 'ao':'vowel', 'g':'plosive', 'jh':'affricate', 'k':'plosive',
    'm':'nasal', 'ay':'vowel', 'er':'vowel', 'ow':'vowel', 'r':'approximant', 'y':'approximant', 'uw':'vowel', 
    'hh':'fricative', 't':'plosive', 'p':'plosive', 'sh':'fricative', 'uh':'vowel', 'aa':'vowel', 'ng':'nasal', 
    'ey':'vowel', 'b':'plosive', 'aw':'vowel', 'ch':'affricate', 'oy':'vowel', 'zh':'fricative'
}


#------------------




def convert_phone_item(p_item, val, phone2char):
    target_item = p_item.copy()
    target_item["triphone"] = target_item["prev-phone"] + "-" + target_item["#phone"] + "-" + target_item["next-phone"]
    target_item["prev-phone_char"] = target_item["prev-phone"].apply(lambda x : phone2char[x])
    target_item["next-phone_char"] = target_item["next-phone"].apply(lambda x : phone2char[x])
    target_item["#phone_char"] = target_item["#phone"].apply(lambda x : phone2char[x])
    target_item["triphone_char"] = target_item["prev-phone_char"] + "-" + target_item["#phone_char"] + "-" + target_item["next-phone_char"]    
    spk2gender = {}
    
    for index, row in tqdm(val.iterrows(), total=val.shape[0]):
        if not row["client_id"] in spk2gender and pd.notna(row["gender"]):
            spk2gender[row["client_id"]] = row["gender"]
        #print(spk2gender)

    target_item["gender"] = target_item["speaker"].apply(lambda x : spk2gender[x])
        
    utt2lang = pd.Series(val.locale.values,index=val.utt).to_dict()
    target_item["lang"] = target_item["#file"].apply(lambda x : utt2lang[x])

    
    # target_item["prev-phone"] = target_item["#file"].apply(lambda x : "NaN")
    # target_item["next-phone"] = target_item["#file"].apply(lambda x : "NaN")
    # target_item["#phone"] = target_item["#file"].apply(lambda x : "NaN")

    return target_item

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path_item_1", help="path to the item file in the first language, eg /scratch2/mde/projects/phonABX_generation/dataset/en/en.item")
    parser.add_argument("path_validated_1", help="path to the validated csv in CommonVoice in the 1st language, eg /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/en/validated.tsv")
    parser.add_argument("path_item_2", help="path to the item file in the 2nd language")
    parser.add_argument("path_validated_2", help="path to the validated csv in CommonVoice in the 2nd language")
    parser.add_argument('output_dir', type=str, help="path to the output dir")


    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    
    val_a = pd.read_csv(args.path_validated_1, sep='\t')
    val_a["utt"] = val_a["path"].apply(lambda x : x.split(".")[0])
    val_b = pd.read_csv(args.path_validated_2, sep='\t')
    val_b["utt"] = val_b["path"].apply(lambda x : x.split(".")[0])
    val = val_a.append(val_b)
#    val.to_csv(os.path.join(args.output_dir, "val.tsv"), sep="\t")
    #    utt2gender = pd.Series(val.gender.values,index=val.utt).to_dict()
    #    utt2lang = pd.Series(val.locale.values,index=val.utt).to_dict()
    print("here")


    #retrieve phone items
    item_p_a = pd.read_csv(args.path_item_1, sep=' ')
    item_p_b = pd.read_csv(args.path_item_2, sep=' ')
    merged_item = item_p_a.append(item_p_b)
                       
    #create gender items
    en_phone_char.update(fr_phone_char)
    final_item = convert_phone_item(merged_item, val, en_phone_char)

    final_item.to_csv(os.path.join(args.output_dir, "full.item"), sep=" ", index=False)


    # python scripts/commonvoice/merge_datasets_general.py /scratch2/mde/projects/phonABX_generation/dataset/en/en.item /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/en/validated.tsv /scratch2/mde/projects/phonABX_generation/dataset/fr/fr.item /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/fr/validated.tsv test 
    
