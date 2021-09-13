#!/usr/bin/env python3

import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import os, re, time, warnings, sys
import warnings
import pickle
from mutagen.mp3 import MP3
import numpy as np 
def create_df(tsv, audio_dir):
    tqdm.pandas()
    df = pd.read_csv(tsv, sep='\t')
    df['dur'] = df['path'].progress_apply(get_dur, args=(audio_dir,))

    return df

def get_dur(mp3, audio_dir):
    """ return audio duration in seconds """
    audio=MP3(os.path.join(audio_dir,mp3))
    return audio.info.length

def select_subset(df, n_spk, tgt_dur, accent=None, balanced_gender=True, add_precaution_spks=False):

    print("n_spk = ", n_spk)

    if add_precaution_spks:
        tgt_dur= (tgt_dur/n_spk)*(n_spk+4)
        n_spk+=4
        print(n_spk)
        print('Adding 4 additional speakers that will be not counted towards max duration, to allow manual suppression of unwanted speakers')
        
    #1. filter out speakers with accents

    df_start=len(df)
    if not accent:
        df = df[df['accent'].isnull()] #only want those with no sepcific accent
    else:
        print(accent)
        df = df[df.accent.isin(accent)]

    print("{}% of data was removed after filtering by accent".format((df_start-len(df))/df_start*100))

    df_start=len(df)
      
    #2. filter out speakers with not enough data
    print("n_spk = ", n_spk)
    
    tgt_dur_spk = float(tgt_dur) /  n_spk
    df_spk = df.groupby('client_id')['dur'].sum()
    spks=list(df_spk[df_spk >= tgt_dur_spk].index)
    df = df[df.client_id.isin(spks)]

    if not len(df['client_id'].unique()) >= n_spk :
        raise ValueError('There are no enough speakers to reach the desired target duration with the target number of speakers. Try reducing either one or the other of these values')


    #3. select x spks, half from each langauge.
    if (n_spk % 2) != 0:
        warnings.warn("Warning....... n_spk is an odd number, adding one speaker so that we can have equal share between males and females")
        n_spk += 1
            
    df_m = df[df["gender"] == "male"]
    df_f = df[df["gender"] ==  "female"]
    print("n_spk = ", n_spk)
    if not len(df_m['client_id'].unique()) >= n_spk / 2 or not len(df_f['client_id'].unique()) >= n_spk / 2 :

        raise ValueError('Not enough speakers of each gender for the taarget duration. It could be becuse a lot of speakers have not entered their the gender information. Try setting "balanced_gender" to false or reducing tgt_dur.')

    if accent and len(accent) > 1:
        #then do balanced. 
        finalspks = set()
        for ac in accent :
            a=df_m[df_m["accent"] == ac]['client_id']
            spks= list(list(np.random.choice(df_m[df_m["accent"] == ac]['client_id'].unique(),int(n_spk/2/len(accent)), replace=False)) + list(np.random.choice(df_f[df_f["accent"] == ac]['client_id'].unique(),int(n_spk/2/len(accent)), replace=False)))
            for x in spks:
                finalspks.add(x)
    else:
        print("n_spk/2 = ", int(n_spk/2))
        print("n_spk/2 = ", n_spk/2)
        finalspks = set(list(np.random.choice(df_m['client_id'].unique(),int(n_spk/2), replace=False)) + list(np.random.choice(df_f['client_id'].unique(),int(n_spk/2), replace=False)))
        
    print(len(finalspks))
    print("male: ", len(df_m['client_id'].unique()))
    print("female: ", len(df_f['client_id'].unique()))

    #4. Sample n seconds per spk
    #filter out if above threshold length
    
    final_df = pd.DataFrame(columns=df.columns)
    for spk in tqdm(finalspks):
        print(spk)
        tot=0
        tmp_df = df[df['client_id'] == spk]
        for i in tmp_df.sample(frac=1).iterrows():
            if i[1]['dur'] >= 20:
                continue #not over 20 sec
            if tot >= tgt_dur_spk:
                break
            final_df = final_df.append(i[1])
            tot += i[1]['dur']
            

    return final_df

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("CV_path", help="path to the commonvoice main directory")
    parser.add_argument("lang", help="language code in CV format")    
    parser.add_argument('output_tsv', type=str, help="path to the output tsv")
    
    parser.add_argument("--tgt_spk", type=int, help='target number of shespeakers, must be an even number', default=24)
    parser.add_argument("--tgt_dur", type=int, help='target total duration of the selection, in seconds', default=36000)
    parser.add_argument("--add_precaution_spks", default=False, action="store_true", help="If True, add 4 more speakers (2 for each gender) that will have to be manually removed.")
    parser.add_argument("--accent", default=None, action='append')
    
    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    validated_tsv = os.path.join(args.CV_path, args.lang, "validated.tsv")
    audio_dir= os.path.join(args.CV_path, args.lang,"clips")


    print(args.accent)
    if os.path.exists(os.path.join(args.CV_path, args.lang, "validated.pkl")):
        df=pickle.load(open(os.path.join(args.CV_path, args.lang, "validated.pkl"), 'rb'))
    else :
        print("Retrieveing audio information from the tsv file")
        df = create_df(validated_tsv, audio_dir)
        df.to_pickle(os.path.join(args.CV_path, args.lang, "validated.pkl"))

    if not os.path.exists(args.output_tsv):
        print("Selecting the subset")
        if args.add_precaution_spks:
            final_df = select_subset(df, args.tgt_spk, args.tgt_dur, add_precaution_spks=args.add_precaution_spks, accent=args.accent)
        else:
            final_df = select_subset(df, args.tgt_spk, args.tgt_dur, accent=args.accent)
        final_df.to_csv(args.output_tsv, sep="\t")
