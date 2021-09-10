# phonABX_generation

python scripts/commonvoice/CV_selection.py --add_precaution_spks /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/ fr /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/fr/selected.tsv

# Fo rEnglish, get both us and england so that we have both possible accents (half of each)
python scripts/commonvoice/CV_selection.py --accent us --accent england --add_precaution_spks /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/ en /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/en/selected.tsv

#or just US 
python scripts/commonvoice/CV_selection.py --accent us  --add_precaution_spks /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/ en /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/en/selected_us.tsv


#The -add precaution is so that we add 4 more additional speakers ( 2 per Gender" that can be removed at listening).



For alignment
-  use already existing g2p
- train g2p (refer to sequitur training) (only if you want to phonemise the OOV)

#requires having srilm installed. If not the case, refer to Kaldi and add it to your path.
Also requires sequitur (in tools/extras)sh if you want the G2P



Go into kaldi_setup
```
for lang in en fr; do 
 ./run.sh --lang $lang #(careful th at use_g2p set to False )
done
```


#create dataset

mkdir -p ../dataset/fr
mkdir -p ../dataset/en

for lang in en fr; do
python local/ali2abx.py exp/${lang}/tri4b_ali/ali.ctm ../dataset/${lang}/${lang}.item
python local/ali2abx.py --keep_pos exp/${lang}/tri4b_ali/ali.ctm ../dataset/${lang}/${lang}_pos.item

done

for lang in en fr; do 
cut -d' ' -f1 ./dataset/${lang}/${lang}.item | sort -u | while read p; do
ln -s /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/$lang/clips/${p}.mp3 ./dataset/${lang}/.
done
done


#needs to be listened to manually
#need to understand diff 1s 10s 