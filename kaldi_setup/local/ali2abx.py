#!/usr/bin/env python3


def fold_phone(phone, lang):
    if lang=="en":
        phon2phon= {}
    elif lang=="fr":
        #fold AU to OO, 
        phon2phon={"au":"oo","au_B":"oo_B", "au_E":"oo_E", "au_I":"oo_I", "au_S":"oo_S"} 
    else:
        raise ValueError("Language not supported for the folding")

    if phone in phon2phon:
        return phon2phon[phone]
    else:
        return phone
                


def ali2abx(alignment_file, output_item, lang,  keep_posflag=False, save_phone_dur=False):


    data = [line.strip().split(" ") for line in  open(alignment_file, 'r', encoding="utf8")]

    curr_utt=data[0][0]
    items = []
    for i in range(1, len(data) -1 ):

        if curr_utt == data[i][0] and curr_utt == data[i+1][0]:
            spk = data[i][0].split('-')[0]
            wav=data[i][0].split('-')[1]
            phon = fold_phone(data[i][4], lang)
            start=data[i-1][2]
            end = format(round(float(data[i+1][2]) + float(data[i+1][3]),3),'.3f')
            prev_phon=fold_phone(data[i-1][4], lang)
            next_phon=fold_phone(data[i+1][4], lang)
            phon_dur=data[i][3]
            item =  [wav, start, end, phon, prev_phon, next_phon, spk, phon_dur]
            items.append(item)
        elif curr_utt != data[i][0] :
            curr_utt = data[i][0]
        else:
            continue

    items = filter_items(items, keep_posflag=keep_posflag, save_phone_dur=save_phone_dur)
    
    with open(output_item, 'w', encoding="utf8") as outfile :
        if save_phone_dur:
            outfile.write("#file onset offset #phone prev-phone next-phone speaker center-phone-dur\n")
        else:
            outfile.write("#file onset offset #phone prev-phone next-phone speaker\n")            
        for item in items :
            outfile.write(" ".join(item)+"\n")


def filter_items(items, keep_posflag=False, silences = ["SIL", "SIL_S"], save_phone_dur=False):

    final_items = []
    for item in items :
        
        if item[3] in silences or item[4] in silences or item[5] in silences :
            continue #stop don't use it.

        if not keep_posflag :
            if save_phone_dur :
                item = [item[0], item[1], item[2], item[3].split('_')[0], item[4].split('_')[0], item[5].split('_')[0], item[6], item[7]]
            else:
                item = [item[0], item[1], item[2], item[3].split('_')[0], item[4].split('_')[0], item[5].split('_')[0], item[6]]

        final_items.append(item)
    return final_items
            
            

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("alignment_file", help="ali file from kaldi")
    parser.add_argument('output_item')
    parser.add_argument('lang', help="language (for phone folding). Currently accepted : 'en', 'fr'")
    parser.add_argument("--keep_posflag", help="keep position flag (eg AA_B instead of just AA", default=False, action="store_true")
    parser.add_argument("--save_phone_dur", help="Also save the central phone duration in the last column (mainly for stats purposes)", default=False, action="store_true")

    
    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    ali2abx(args.alignment_file, args.output_item, args.lang, keep_posflag=args.keep_posflag, save_phone_dur=args.save_phone_dur)
