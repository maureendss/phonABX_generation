#!/usr/bin/env python3

import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import os, re, time, warnings, sys
import warnings
import pickle
import numpy as np 

def convert_phone_item(p_item, val, target="gender"):
    target_item = p_item.copy()
    if target == "gender":
        utt2target = pd.Series(val.gender.values,index=val.utt).to_dict()
    elif target == "lang":
        utt2target = pd.Series(val.locale.values,index=val.utt).to_dict()


    target_item["#phone"] = target_item["#file"].apply(lambda x : utt2target[x])
    target_item["prev-phone"] = target_item["#file"].apply(lambda x : utt2target[x])
    target_item["next-phone"] = target_item["#file"].apply(lambda x : utt2target[x])

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
    phone_item = item_p_a.append(item_p_b)
                       
    #create gender items
    gender_item = convert_phone_item(phone_item, val, target="gender")
    lang_item = convert_phone_item(phone_item, val, target="lang")

    

    phone_item.to_csv(os.path.join(args.output_dir, "phone.item"), sep=" ", index=False)
    gender_item.to_csv(os.path.join(args.output_dir, "gender.item"), sep=" ", index=False)
    lang_item.to_csv(os.path.join(args.output_dir, "lang.item"), sep=" ", index=False)
    
