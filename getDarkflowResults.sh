#!/bin/bash
DATASET=$1
RESDIR=$2
THRESH=$3
MODEL=cfg/timevary_new.cfg
WEIGHT=../yolo/darknet/yolo.weights
LABELS=../yolo/darknet/data/Bellevue_TimeVary.names
ls $DATASET | while read f;do
	flow --imgdir $DATASET/$f --model $MODEL --load $WEIGHT --restore 29375 --labels $LABELS --gpu 0.3 --threshold 0.01 --json
	flow --imgdir $DATASET/$f --model $MODEL --load $WEIGHT --restore 29375 --labels $LABELS --gpu 0.3 --threshold $THRESH
	mkdir $RESDIR/$f
	ls $DATASET/$f/out/*.json | while read g;do
		python3 convertRes2Kitti.py --json-res $DATASET/$f/out/$g --txt-res $RESDIR/$f/$g.txt
	done
done

