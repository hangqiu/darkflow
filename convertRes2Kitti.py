import json
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Divide into Train Test.')
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('--json-res',
                          dest='file',
                          required=True,
                          type=str)
    required.add_argument('--txt-res',
                          dest='txt',
                          required=True,
                          type=str)
    
    args = parser.parse_args()
    # logging.info(args)
    return args

args = parse_args()
data_file = open(args.file)
data = json.load(data_file)
# print(args.txt)
names = args.txt.split('.')
filename = ''
for name in names:
	if name == names[len(names)-2]:
		break;
	filename += name + '.'
# print(filename)	
f = open(filename+'txt',"w")
for obj in data:
	# f.write(obj['label'] + ' 0 0 0 ' + str(obj['topleft']['x']))
	f.write(obj['label'] + ' 0 0 0 ' + str(obj['topleft']['x']) + ' ' + str(obj['topleft']['y']) +  ' ' + str(obj['bottomright']['x']) + ' ' + str(obj['bottomright']['y']) + ' 0 0 0 0 0 0 0 ' + str(obj['confidence']) + '\n')
