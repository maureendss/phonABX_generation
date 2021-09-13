export KALDI_ROOT=/shared/apps/kaldi
[ -f $KALDI_ROOT/tools/env.sh ] && . $KALDI_ROOT/tools/env.sh


export PATH=$PWD/utils/:$KALDI_ROOT/tools/openfst/bin:$PWD:$PATH
[ ! -f $KALDI_ROOT/tools/config/common_path.sh ] && echo >&2 "The standard file $KALDI_ROOT/tools/config/common_path.sh is not present -> Exit!" && exit 1
. $KALDI_ROOT/tools/config/common_path.sh
export LC_ALL=C


export SRILM=/scratch2/mde/repos/kaldi/tools/srilm
export PATH=${PATH}:${SRILM}/bin:${SRILM}/bin/i686-m64

export SEQUITUR="/scratch2/mde/repos/kaldi/tools/sequitur-g2p"
export PATH="$PATH:${SEQUITUR}/bin"
export PYTHONPATH="${PYTHONPATH:-}:$SEQUITUR/./lib/python3.8/site-packages"
