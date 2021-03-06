#!/bin/bash
MODEL=cfg/timevary_new.cfg
WEIGHT=../yolo/darknet/yolo.weights
NAMES=../yolo/darknet/data/Bellevue_TimeVary.names
EVALSET=$1
RESDIR=$2
CKPT=$3
mkdir $RESDIR
echo flow --imgdir $EVALSET --model $MODEL --load $WEIGHT --restore $CKPT --labels $NAMES --gpu 0.3 --threshold 0.01 --json
flow --imgdir $EVALSET --model $MODEL --load $WEIGHT --restore $CKPT --labels $NAMES --threshold 0.01 --json
ls $EVALSET/out/ | sed -e 's/\.json$//'| while read g;do
	echo python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
	python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
done
rm -r $EVALSET/out/

