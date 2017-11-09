import tensorflow as tf
import time
from . import help
from . import flow
from .ops import op_create, identity
from .ops import HEADER, LINE
from .framework import create_framework
from ..dark.darknet import Darknet
import json
import os

class TFNet(object):

	_TRAINER = dict({
		'rmsprop': tf.train.RMSPropOptimizer,
		'adadelta': tf.train.AdadeltaOptimizer,
		'adagrad': tf.train.AdagradOptimizer,
		'adagradDA': tf.train.AdagradDAOptimizer,
		'momentum': tf.train.MomentumOptimizer,
		'adam': tf.train.AdamOptimizer,
		'ftrl': tf.train.FtrlOptimizer,
		'sgd': tf.train.GradientDescentOptimizer
	})

	# imported methods
	_get_fps = help._get_fps
	say = help.say
	train = flow.train
	camera = help.camera
	predict = flow.predict
	return_predict = flow.return_predict
	to_darknet = help.to_darknet
	build_train_op = help.build_train_op
	load_from_ckpt = help.load_from_ckpt
	restore_from_ckpt = help.restore_from_ckpt

	def __init__(self, FLAGS, darknet = None):
		self.ntrain = 0
		self.nRestore = 0

		if isinstance(FLAGS, dict):
			from ..defaults import argHandler
			newFLAGS = argHandler()
			newFLAGS.setDefaults()
			newFLAGS.update(FLAGS)
			FLAGS = newFLAGS

		self.FLAGS = FLAGS
		if self.FLAGS.pbLoad and self.FLAGS.metaLoad:
			self.say('\nLoading from .pb and .meta')
			self.graph = tf.Graph()
			device_name = FLAGS.gpuName \
				if FLAGS.gpu > 0.0 else None
			with tf.device(device_name):
				with self.graph.as_default() as g:
					self.build_from_pb()
			return

		if darknet is None:	
			darknet = Darknet(FLAGS)
			if (self.FLAGS.nTrain==-1):
				self.ntrain = len(darknet.layers)
			else:
			# self.ntrain = 2
				self.ntrain = self.FLAGS.nTrain
		self.nRestore = self.FLAGS.nRestore

		self.darknet = darknet
		args = [darknet.meta, FLAGS]
		self.num_layer = len(darknet.layers)
		self.framework = create_framework(*args)
		
		self.meta = darknet.meta

		self.say('\nBuilding net ...')
		start = time.time()
		self.graph = tf.Graph()
		device_name = FLAGS.gpuName \
			if FLAGS.gpu > 0.0 else None
		with tf.device(device_name):
			with self.graph.as_default() as g:
				self.build_forward()
				self.setup_meta_ops()
		self.say('Finished in {}s\n'.format(
			time.time() - start))
	
	def build_from_pb(self):
		with tf.gfile.FastGFile(self.FLAGS.pbLoad, "rb") as f:
			graph_def = tf.GraphDef()
			graph_def.ParseFromString(f.read())
		
		tf.import_graph_def(
			graph_def,
			name=""
		)
		with open(self.FLAGS.metaLoad, 'r') as fp:
			self.meta = json.load(fp)
		self.framework = create_framework(self.meta, self.FLAGS)

		# Placeholders
		self.inp = tf.get_default_graph().get_tensor_by_name('input:0')
		self.feed = dict() # other placeholders
		self.out = tf.get_default_graph().get_tensor_by_name('output:0')
		
		self.setup_meta_ops()
	
	def build_forward(self):
		verbalise = self.FLAGS.verbalise

		# Placeholders
		inp_size = [None] + self.meta['inp_size']
		self.inp = tf.placeholder(tf.float32, inp_size, 'input')
		self.feed = dict() # other placeholders

		# Build the forward pass
		state = identity(self.inp)
		roof = self.num_layer - self.ntrain
		self.say(HEADER, LINE)
		for i, layer in enumerate(self.darknet.layers):
			scope = '{}-{}'.format(str(i),layer.type)
			args = [layer, state, i, roof, self.feed]
			state = op_create(*args)
			mess = state.verbalise()
			self.say(mess)
		self.say(LINE)

		self.top = state
		self.out = tf.identity(state.out, name='output')

	def setup_meta_ops(self):
		cfg = dict({
			'allow_soft_placement': False,
			'log_device_placement': False
		})

		utility = min(self.FLAGS.gpu, 1.)
		if utility > 0.0:
			self.say('GPU mode with {} usage'.format(utility))
			cfg['gpu_options'] = tf.GPUOptions(
				per_process_gpu_memory_fraction = utility)
			cfg['allow_soft_placement'] = True
		else: 
			self.say('Running entirely on CPU')
			cfg['device_count'] = {'GPU': 0}

		if self.FLAGS.train: self.build_train_op()
		
		if self.FLAGS.summary is not None:
			self.summary_op = tf.summary.merge_all()
			self.writer = tf.summary.FileWriter(self.FLAGS.summary + 'train')
		
		self.sess = tf.Session(config = tf.ConfigProto(**cfg))
		self.sess.run(tf.global_variables_initializer())

		self.saver = tf.train.Saver(tf.global_variables(),
									max_to_keep=self.FLAGS.keep)

		if not self.ntrain: return

		if self.nRestore!=0:
			# restore only part of the model from ckpt
			# print(self.num_layer)
			variables_to_restore = []
			for layerNum in range(self.num_layer - int(self.nRestore), self.num_layer):
				for var in tf.global_variables():
					if var.name.startswith(str(layerNum)):
						variables_to_restore.append(var)

			print(variables_to_restore)
			self.saver_Restore = tf.train.Saver(variables_to_restore)
		else:
			self.saver_Restore = self.saver
		# print(tf.global_variables())




		# exit()
		# self.saver = tf.train.Saver(max_to_keep=self.FLAGS.keep)

		if self.FLAGS.load != 0:
			print('loading from checkpoint')
			self.load_from_ckpt()

			# add restore conversion -- Hang
		# if self.FLAGS.restore == str():
		if self.FLAGS.restore:
			# print('restoring weights from {}'.format(self.FLAGS.restore))
			self.FLAGS.restore = int(self.FLAGS.restore)
			# print('restoring weights from {}'.format(self.FLAGS.restore))
			# exit(-1)
			self.restore_from_ckpt()
		
		if self.FLAGS.summary is not None:
			self.writer.add_graph(self.sess.graph)

	def savepb(self):
		"""
		Create a standalone const graph def that 
		C++	can load and run.
		"""
		darknet_pb = self.to_darknet()
		flags_pb = self.FLAGS
		flags_pb.verbalise = False
		
		flags_pb.train = False
		# rebuild another tfnet. all const.
		tfnet_pb = TFNet(flags_pb, darknet_pb)		
		tfnet_pb.sess = tf.Session(graph = tfnet_pb.graph)
		# tfnet_pb.predict() # uncomment for unit testing
		name = 'built_graph/{}.pb'.format(self.meta['name'])
		os.makedirs(os.path.dirname(name), exist_ok=True)
		#Save dump of everything in meta
		with open('built_graph/{}.meta'.format(self.meta['name']), 'w') as fp:
			json.dump(self.meta, fp)
		self.say('Saving const graph def to {}'.format(name))
		graph_def = tfnet_pb.sess.graph_def
		tf.train.write_graph(graph_def,'./', name, False)