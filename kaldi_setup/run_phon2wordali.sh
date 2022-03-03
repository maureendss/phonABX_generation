#!/bin/bash
#SBATCH --job-name=word_ali             # Job name
#SBATCH --partition=cpu               # Take a node from the 'cpu' partition
#SBATCH --cpus-per-task=20            # Ask for 20 CPU cores
#SBATCH --mem=100G                    # Memory request; MB assumed if unit not specified
#SBATCH --time=20:00:00               # Time limit hrs:min:sec
#SBATCH --output=%x-%j.log            # Standard output and error log


conda activate abxgen

echo "---en"
python local/phon2wordali.py --pos exp/en/tri4b_ali/ali.ctm exp/en/tri4b_ali/word_ali.ctm data/en/text en


# echo "---fr"
# python local/phon2wordali.py --pos exp/fr/tri4b_ali/ali.ctm exp/fr/tri4b_ali/word_ali.ctm data/fr/text fr
