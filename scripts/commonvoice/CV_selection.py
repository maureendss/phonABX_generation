#!/usr/bin/env python3

import pandas as pd
from tqdm import tqdm
from collections import defaultdict
import os, re, time, warnings, sys
import warnings
import pickle

def create_df(tsv, audio_dir):
    tqdm.pandas()
    df = pd.read_csv(tsv, sep='\t')
    df['dur'] = df['path'].progress_apply(get_dur, args=(audio_dir,))

    return df

def get_dur(mp3, audio_dir):
    """ return audio duration in seconds """
    audio=MP3(os.path.join(audio_dir,mp3))
    return audio.info.length

def select_subset(df, n_spk, tgt_dur, locale=None, accent=None, balanced_gender=True):


      #1. filter out speakers with accents

      if not accent:
	  df = df[df['accent'].isnull()] #only want those with no sepcific accent
      else:
	  df = df[df.accent.isin(accent)]

      if locale:
	  df = df[df.locale.isin(locale)]

      
      #2. filter out speakers with not enough data

      tgt_dur_spk = float(tgt_dur) /  n_spk
      spks = df.groupby('client_id')['dur'].sum()
      spks=list(df_spk[df_spk >= tgt_dur_spk])

      df = df[df.client_id.isin(spks)]

      if not len(df['client_id'].unique()) >= n_spk :
	    raise ValueError('There are no enough speakers to reach the desired target duration with the target number of speakers. Try reducing either one or the other of these values')


      #3. select x spks, half from each langauge.
      if balanced_gender : 
	    if (n_spk % 2) != 0:
		warnings.warn("Warning....... n_spk is an odd number, adding one speaker so that we can have equal share between males and females")
		n_spk += 1
		
	    df_m = df[df["gender"] == "male"]
	    df_f = df[df["gender"] ==  "female"]

	    if not len(df_m['client_id'].unique()) >= n_spk / 2 or not len(df_m['client_id'].unique()) >= n_spk / 2 :
		  raise ValueError('Not enough speakers of each gender for the taarget duration. It could be becuse a lot of speakers have not entered their the gender information. Try setting "balanced_gender" to false or reducing tgt_dur.')
	      
	    else :
		finalspks = list(df_m['client_id'].unique().sample(n_spk/2)) + list(df_f['client_id'].unique().sample(n_spk/2)) 
		#df = df[df.client_id.isin(finalspks)]


      #4. Sample n seconds per spk
      
      final_df = pd.DataFrame(columns=df.columns)
      for spk in tqdm(final_spks):
          tot=0
          tmp_df = df[df['client_id'] == spk]
          for i in tmp_df.sample(frac=1).iterrows():
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
    
    parser.add_argument("--tgt_spk", type=int, help='target number of speakers, must be an even number', default=24)
    parser.add_argument("--tgt_dur", type=int, help='target total duration of the selection, in seconds', default=36000)
    
    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    validated_tsv = os.path.join(CV_path, lang, "validated.tsv")
    audio_dir= os.path.join(CV_path, lang,clips)
    
    if os.path.exists(os.path.join(args.output_dir, "validated.pkl")):
	df=pickle.load(open(os.path.join(args.output_dir, "validated.pkl"), 'rb'))
    else :
        print("Retrieveing audio information from the tsv file")
        df = create_df(validated_file, audio_dir)
        df.to_pickle(os.path.join(args.CV_path, "validated.pkl"))

    if not os.path.exists(args.output_tsv):
        print("Selecting the subset")
        final_df = select_subset(df, n_spk, tgt_dur)
        final_df.to_csv(args.output_tsv, sep="\t")
