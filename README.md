# phonABX_generation

python scripts/commonvoice/CV_selection.py --add_precaution_spks /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/ fr /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/fr/selected.tsv

# Fo rEnglish, get both us and england so that we have both possible accents (half of each)
python scripts/commonvoice/CV_selection.py --accent us --accent england --add_precaution_spks /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/ en /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/en/selected.tsv

#or just US 
python scripts/commonvoice/CV_selection.py --accent us  --add_precaution_spks /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/ en /scratch1/data/raw_data/commonvoice/cv-corpus-7.0-2021-07-21/en/selected_us.tsv


#The -add precaution is so that we add 4 more additional speakers ( 2 per Gender" that can be removed at listening).



For alignment
-  use already existing g2p
- train g2p (refer to sequitur training)

#requires having srilm installed. If not the case, refer to Kaldi and add it to your path.
Also requires sequitur (in tools/extras)