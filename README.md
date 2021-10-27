# Generating ABX tests from CommonVoice data

CV_DATASET=<path_to_CV_dataset>

## Select data from CommonVoice

You can choose how many speakers and how much total duration you are aiming for. Speech will be distributed in a balanced fashion between male and females.
You also have the option to choose one or more specific "accents" you want to choose from. If more than one accents are chose, speech will be balanced between all the accents and genders. If no accent is specified, only speakers who have *not* specified their accents will be selected. 
If it is not possible to fill all of these constraints from the dataset, a warning message will appear and you will have to change the parameters.

The two commands below are the ones run to get the CV21 sets: 

```
python scripts/commonvoice/CV_selection.py --accent france ${CV_DATASET} fr ${CV_DATASET}/fr/selected.tsv

python scripts/commonvoice/CV_selection.py --accent us  ${CV_DATASET} en ${CV_DATASET}en/selected.tsv
```

Below is an example of asking for multiple accents (although not used in CV21) :
`python scripts/commonvoice/CV_selection.py --accent us --accent england --add_precaution_spks ${CV_DATASET} en ${CV_DATASET}/en/UK-US_selected.tsv`

(The -add_precaution argument can also be set if you want to add  4 more additional speakers to be discarded manually afterwards).


## Align Data using Kaldi

*Note : You will need to install Kaldi, and link the steps and utils directory from Kaldi into kaldi_setup. You will also need to have SRILM installed and linked correctly into your path.sh . If you plan on training a G2P you will also need to have Sequitur installed and added to your path (in which case you will be able to use the "use_g2p" in stage 1 to true)*

Make sure that CV_DATASET points to the right location in `run.sh`.


```
cd kaldi_setup
for lang in en fr; do 
 ./run.sh --lang $lang #(careful th at use_g2p set to False )
done
```


## Create the item files and the dataset

``` 
mkdir -p ../dataset/fr
mkdir -p ../dataset/en

for lang in en fr; do
python local/ali2abx.py exp/${lang}/tri4b_ali/ali.ctm ../dataset/${lang}/${lang}.item $lang
python local/ali2abx.py --keep_pos exp/${lang}/tri4b_ali/ali.ctm ../dataset/${lang}/${lang}_pos.item $lang
python local/ali2abx.py --save_phone_dur exp/${lang}/tri4b_ali/ali.ctm ../dataset/${lang}/${lang}.stats $lang
cp exp/${lang}/tri4b_ali/ali.ctm ../dataset/${lang}/${lang}_ali.ctm
done
```

Now convert the mp3 files from CV that you will use to WAV files to the directory so that you can export all the wav files easily.

```
cd ..
for lang in en fr; do 
    cut -d' ' -f1 ./dataset/${lang}/${lang}.item | sort -u | while read p; do

        sox ${CV_DATASET}/$lang/clips/${p}.mp3 -t wav -r 16k -b 16 -e signed dataset/${lang}/${p}.wav

    done
done

```

