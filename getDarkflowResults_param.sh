#!/bin/bash
MODEL=cfg/timevary_new.cfg
WEIGHT=yolo.weights
NAMES=./data/Bellevue_TimeVary.names
EVALSET=$1
RESDIR=$2
CKPT=$3
NRESTORE=$4
CKPTPATH=$5
GPU=$6

mkdir $RESDIR
echo flow --imgdir $EVALSET --backup $CKPTPATH --model $MODEL --load $WEIGHT --restore $CKPT --labels $NAMES --gpu $GPU --threshold 0.01 --json --nRestore $NRESTORE --nTrain -1
flow --imgdir $EVALSET --backup $CKPTPATH --model $MODEL --load $WEIGHT --restore $CKPT --labels $NAMES --gpu $GPU --threshold 0.01 --json --nRestore $NRESTORE --nTrain -1
ls $EVALSET/out/ | sed -e 's/\.json$//'| while read g;do
	echo python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
	python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
done
rm -r $EVALSET/out/

