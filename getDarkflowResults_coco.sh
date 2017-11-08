#!/bin/bash
MODEL=cfg/yolo.cfg
WEIGHT=../yolo/darknet/yolo.weights
NAMES=cfg/coco.names
EVALSET=$1
RESDIR=$2
CKPT=$3
mkdir $RESDIR
echo flow --imgdir $EVALSET --model $MODEL --load $WEIGHT --labels $NAMES --gpu 0.1 --threshold 0.01 --json
flow --imgdir $EVALSET --model $MODEL --load $WEIGHT --labels $NAMES --threshold 0.01 --json
ls $EVALSET/out/ | sed -e 's/\.json$//'| while read g;do
	echo python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
	python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
done
rm -r $EVALSET/out/
