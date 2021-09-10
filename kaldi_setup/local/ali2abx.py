#!/usr/bin/env python3




def ali2abx(alignment_file, output_item, keep_posflag=False):


    data = [line.strip().split(" ") for line in  open(alignment_file, 'r', encoding="utf8")]

    curr_utt=data[0][0]
    items = []
    for i in range(1, len(data) -1 ):

        if curr_utt == data[i][0] and curr_utt == data[i+1][0]:
            spk = data[i][0].split('-')[0]
            wav=data[i][0].split('-')[1]
            phon = data[i][4]
            start=data[i][2]
            end = data[i][3]
            prev_phon=data[i-1][4]
            next_phon=data[i-1][4]

            item =  [wav, start, end, phon, prev_phon, next_phon, spk]
            items.append(item)
        elif curr_utt != data[i][0] :
            curr_utt = data[i][0]
        else:
            continue

    items = filter_items(items, keep_posflag=keep_posflag)
    
    with open(output_item, 'w', encoding="utf8") as outfile :
        outfile.write("#file onset offset #phone prev-phone next-phone speaker\n")
        for item in items :
            outfile.write(" ".join(item)+"\n")


def filter_items(items, keep_posflag=False, silences = ["SIL", "SIL_S"]):

    final_items = []
    for item in items :
        
        if item[3] in silences or item[4] in silences or item[5] in silences :
            continue #stop don't use it.

        if not keep_posflag :
            item = [item[0], item[1], item[2], item[3].split('_')[0], item[4].split('_')[0], item[5].split('_')[0], item[6]]

        final_items.append(item)
    return final_items
            
            

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("alignment_file", help="df in pickle format from processing")
    parser.add_argument('output_item')
    parser.add_argument("--keep_posflag", help="keep position flag (eg AA_B instead of just AA", default=False, action="store_true")

    
    parser.parse_args()
    args, leftovers = parser.parse_known_args()

    ali2abx(args.alignment_file, args.output_item, keep_posflag=args.keep_posflag)
