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
  'on': 'nasal-vowel',
  'an': 'nasal-vowel',
  'oo': 'vowel',
  'oe': 'vowel',
  'eu': 'vowel',
  'ee': 'vowel',
  'un': 'nasal-vowel',
  'uu': 'vowel',
  'in': 'nasal-vowel',
  'uy': 'vowel'}

en_phone_char = {
    'dh': 'fricative', 'ah':'vowel','ah0':'vowel', 'v':'fricative', 'ae':'vowel', 'l':'approximant', 'iy':'vowel',
    'w':'approximant', 'z':'fricative', 'f':'fricative', 'ih':'vowel', 'd':'plosive', 'th':'fricative',
    'eh':'vowel', 'n':'nasal', 's':'fricative', 'ao':'vowel', 'g':'plosive', 'jh':'affricate', 'k':'plosive',
    'm':'nasal', 'ay':'vowel', 'er':'vowel', 'ow':'vowel', 'r':'approximant', 'y':'approximant', 'uw':'vowel', 
    'hh':'fricative', 't':'plosive', 'p':'plosive', 'sh':'fricative', 'uh':'vowel', 'aa':'vowel', 'ng':'nasal', 
    'ey':'vowel', 'b':'plosive', 'aw':'vowel', 'ch':'affricate', 'oy':'vowel', 'zh':'fricative'
}
#------------------



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("path_item", help="path to the full item file")
    parser.add_argument('output_dir', type=str, help="path to the output dir")


    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    if not os.path.isdir(args.output_dir):
        os.makedirs(args.output_dir)
    full_item = pd.read_csv(args.path_item, sep=' ')
                       
    #create phone items
    # within gender and within lang (not within speaker)
    
    phone_i = full_item.copy()
    phone_i["speaker"] = phone_i.apply(lambda x : "+".join([x["gender"], x["lang"]]) , axis=1)
    phone_i = phone_i[["#file","onset" ,"offset","#phone", "prev-phone", "next-phone", "speaker"]]

    #create phone items
    # within phone and within lang (not within speaker)
    gender_i = full_item.copy()
    gender_i["speaker"] = gender_i.apply(lambda x : "+".join([x["triphone"], x["lang"]]) , axis=1)
    gender_i["#phone"] = gender_i["gender"].apply(lambda x : x)
    gender_i["next-phone"] = "NaN"
    gender_i["prev-phone"] = "NaN"
    gender_i = gender_i[["#file","onset" ,"offset","#phone", "prev-phone", "next-phone", "speaker"]]
    
    #create lang items
    #  within gender (not within speaker) and Can't do within phone...
    lang_i = full_item.copy()
    #    lang_i["speaker"] = lang_i.apply(lambda x : "+".join([x["triphone"], x["gender"]]) , axis=1)
    #    lang_i["speaker"] = lang_i.apply(lambda x : x["gender"] , axis=1)
    lang_i["speaker"] = lang_i.apply(lambda x : "+".join([x["triphone_char"], x["gender"]]) , axis=1)
    lang_i["#phone"] = lang_i["lang"].apply(lambda x : x)
    lang_i["next-phone"] = "NaN"
    lang_i["prev-phone"] = "NaN"
    lang_i = lang_i[["#file","onset" ,"offset","#phone", "prev-phone", "next-phone", "speaker"]]   

    
    

    gender_i.to_csv(os.path.join(args.output_dir, "is22_gender.item"), sep=" ", index=False)
    lang_i.to_csv(os.path.join(args.output_dir, "is22_lang.item"), sep=" ", index=False)
    phone_i.to_csv(os.path.join(args.output_dir, "is22_phone.item"), sep=" ", index=False)
    # python scripts/commonvoice/create_is22_items.py /scratch2/mde/projects/phonABX_generation/dataset/en+fr/full.item test 
    
