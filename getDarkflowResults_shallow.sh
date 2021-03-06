#!/bin/bash
MODEL=cfg/shallow.cfg
NAMES=../yolo/darknet/data/Bellevue_TimeVary.names
EVALSET=$1
RESDIR=$2
CKPT=$3
NRESTORE=$4
mkdir $RESDIR
echo flow --imgdir $EVALSET --model $MODEL --restore $CKPT --labels $NAMES --gpu 0.8 --threshold 0.01 --json --nRestore $NRESTORE --nTrain -1
flow --imgdir $EVALSET --model $MODEL --restore $CKPT --labels $NAMES --gpu 0.8 --threshold 0.01 --json --nRestore $NRESTORE --nTrain -1 --trainer adam
ls $EVALSET/out/ | sed -e 's/\.json$//'| while read g;do
	echo python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
	python3 convertRes2Kitti.py --json-res $EVALSET/out/$g.json --txt-res $RESDIR/$g.json.txt
done
rm -r $EVALSET/out/

