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
BATCHSIZE=16

mkdir $RESDIR
echo flow --imgdir $EVALSET --backup $CKPTPATH --model $MODEL --load $WEIGHT --restore $CKPT --labels $NAMES --gpu $GPU --threshold 0.00001 --json --nRestore $NRESTORE --nTrain -1 --batch $BATCHSIZE
flow --imgdir $EVALSET --backup $CKPTPATH --model $MODEL --load $WEIGHT --restore $CKPT --labels $NAMES --gpu $GPU --threshold 0.00001 --json --nRestore $NRESTORE --nTrain -1 --batch $BATCHSIZE

ls $EVALSET/out/ | sed -e 's/\.json$//'| while read g;do
	echo python3.5 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
	python3.5 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
done
rm -r $EVALSET/out/

