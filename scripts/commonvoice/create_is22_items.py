#!/usr/bin/env python3

import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import os, re, time, warnings, sys
import warnings
import pickle
import numpy as np 





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

    # Here AT PHONE LEVEL (not triphone)
    
    # remove items with phones not part of the knwon phone categories :
    accepted_cat = ["fricative", "plosive", "approximant", "nasal", "vowel"]
    full_item = full_item[full_item["#phone_char"].isin(accepted_cat)]

    
    #create phone items
    # within gender and within lang (not within speaker)
    phone_i = full_item.copy()
    phone_i["next-phone"] = "NaN"
    phone_i["prev-phone"] = "NaN"
    phone_i["speaker"] = phone_i.apply(lambda x : "+".join([x["gender"], x["lang"]]) , axis=1)
    phone_i = phone_i[["#file","onset" ,"offset","#phone", "prev-phone", "next-phone", "speaker"]]

    phonecat_i = full_item.copy()
    phonecat_i["next-phone"] = "NaN"
    phonecat_i["prev-phone"] = "NaN"
    phonecat_i["speaker"] = phonecat_i.apply(lambda x : "+".join([x["gender"], x["lang"]]) , axis=1)
    phonecat_i["#phone"] = phonecat_i["#phone_char"].apply(lambda x : x)
    phonecat_i = phonecat_i[["#file","onset" ,"offset","#phone", "prev-phone", "next-phone", "speaker"]]

    
    #create phone items
    # within phone cat and within lang (not within speaker)
    gender_i = full_item.copy()
    gender_i["speaker"] = gender_i.apply(lambda x : "+".join([x["#phone_char"], x["lang"]]) , axis=1)
    gender_i["#phone"] = gender_i["gender"].apply(lambda x : x)
    gender_i["next-phone"] = "NaN"
    gender_i["prev-phone"] = "NaN"
    gender_i = gender_i[["#file","onset" ,"offset","#phone", "prev-phone", "next-phone", "speaker"]]
    
    #create lang items
    #  within gender (not within speaker) and within phone cat
    lang_i = full_item.copy()
    lang_i["speaker"] = lang_i.apply(lambda x : "+".join([x["#phone_char"], x["gender"]]) , axis=1)
    lang_i["#phone"] = lang_i["lang"].apply(lambda x : x)
    lang_i["next-phone"] = "NaN"
    lang_i["prev-phone"] = "NaN"
    lang_i = lang_i[["#file","onset" ,"offset","#phone", "prev-phone", "next-phone", "speaker"]]   

    
    

    gender_i.to_csv(os.path.join(args.output_dir, "is22_gender.item"), sep=" ", index=False)
    lang_i.to_csv(os.path.join(args.output_dir, "is22_lang.item"), sep=" ", index=False)
    phone_i.to_csv(os.path.join(args.output_dir, "is22_phone.item"), sep=" ", index=False)
    phonecat_i.to_csv(os.path.join(args.output_dir, "is22_phonecat.item"), sep=" ", index=False)
    
    # python scripts/commonvoice/create_is22_items.py /scratch2/mde/projects/phonABX_generation/dataset/en+fr/full.item test 
    
