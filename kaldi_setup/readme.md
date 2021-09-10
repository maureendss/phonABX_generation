alignment
ali-to-phones --ctm-output exp/en/tri2b_ali/final.mdl ark:"gunzip -c exp/en/tri2b_ali/ali.*.gz|" -  | utils/int2sym.pl -f 5 data/en/lang/ph\
ones.txt - > exp/en/tri2b_ali/ali.ctm 