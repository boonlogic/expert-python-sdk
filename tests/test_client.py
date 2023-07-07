import sys

sys.path.append('..')

import boonnano as bn
import csv
import os
import json
import numpy as np
import socket
import unittest
from boonnano import BoonException

def clean_nano_instances(nano):
	# clean out nano instances
	nano_list = nano.nano_list()
	print(nano_list)
	for nano_inst in nano_list:
		nano.open_nano(nano_inst['instanceID'])
		nano.close_nano(nano_inst['instanceID'])


def find_host_addr():
	host_name = socket.gethostname()
	host_addr = socket.gethostbyname(host_name)
	return host_addr


init_done = False


def build_environment():
	global init_done
	if init_done:
		return
	server_addr = os.getenv('EXPERT_SERVER')
	if server_addr == 'auto':
		host_addr = find_host_addr()
		server_addr = "http://{}:5007".format(host_addr)

	# iterate over .BoonLogic license files and update server addresses
	if server_addr:
		for filename in os.listdir('.'):
			if filename.startswith(".BoonLogic."):
				with open(filename, "r") as jsonFile:
					blob = json.load(jsonFile)
					blob['default']['server'] = server_addr
				with open(filename, "w") as jsonFile:
					json.dump(blob, jsonFile, indent=4)
	init_done = True


class Test1Management(unittest.TestCase):

	# This test class verifies the ExpertClient/open/close functionality
	def setUp(self):
		build_environment()

	def test_01_nano_handle(self):

		# successful nano-handle created with default options
		try:
			nano = bn.ExpertClient(license_file="./.BoonLogic.license")
			assert nano.license_id == 'default'
		except BoonException as be:
			assert False

		# clean house
		clean_nano_instances(nano)

		# successful nano-handle created with None specified for license_id, should equate to default
		try:
			nano = bn.ExpertClient(license_file=".BoonLogic.license", license_id=None)
			assert nano.license_id == 'default'
		except BoonException as be:
			assert False

		# successful nano-handle created with non-default specified, license_id=localhost
		try:
			nano = bn.ExpertClient(license_file=".BoonLogic.license", license_id='sample-license')
			assert nano.license_id == 'sample-license'
			assert nano.api_key == 'sample-key'
			assert nano.api_tenant == 'sample-tenant'
			assert nano.server == 'http://sample.host:5007'
		except BoonException as be:
			assert False

		# override license_id through environment
		os.environ['BOON_LICENSE_ID'] = 'sample-license'
		try:
			nano = bn.ExpertClient(license_file=".BoonLogic.license")
			assert nano.license_id == 'sample-license'
			assert nano.api_key == 'sample-key'
			assert nano.api_tenant == 'sample-tenant'
			assert nano.server == 'http://sample.host:5007'
		except BoonException as be:
			assert False
		os.environ.pop('BOON_LICENSE_ID')

		# override BOON_API_KEY, BOON_API_TENANT and BOON_SERVER
		os.environ['BOON_API_KEY'] = 'new-key'
		os.environ['BOON_API_TENANT'] = 'new-tenant'
		os.environ['BOON_SERVER'] = 'new-server:9999'
		try:
			nano = bn.ExpertClient(license_file=".BoonLogic.license")
			assert nano.license_id == 'default'
			assert nano.api_key == 'new-key'
			assert nano.api_tenant == 'new-tenant'
			assert nano.server == 'new-server:9999'
		except BoonException as be:
			assert False
		os.environ.pop('BOON_API_KEY')
		os.environ.pop('BOON_API_TENANT')
		os.environ.pop('BOON_SERVER')

	def test_02_nano_handle_negative(self):

		# create ExpertClient using bad license path
		with self.assertRaises(BoonException) as e:
			bn.ExpertClient(license_file=".BadLogic.license", license_id='sample-license')
		assert 'does not exist' in e.exception.message

		# create ExpertClient using badly formatted json
		with self.assertRaises(BoonException) as e:
			bn.ExpertClient(license_file="badformat.Boonlogic.license", license_id='sample-license')
		assert 'json formatting error' in e.exception.message

		# create ExpertClient using non-existent license_id
		with self.assertRaises(BoonException) as e:
			bn.ExpertClient(license_id='not-a-license')
		assert 'not found in license file' in e.exception.message

		# create ExpertClient using non-existent BOON_LICENSE_ID
		os.environ['BOON_LICENSE_ID'] = 'not-a-license'
		with self.assertRaises(BoonException) as e:
			bn.ExpertClient(license_id='not-a-license')
		assert 'not found in license file' in e.exception.message
		os.environ.pop('BOON_LICENSE_ID')

		# create ExpertClient with missing api-key
		with self.assertRaises(BoonException) as e:
			bn.ExpertClient(license_file="no-api-key.Boonlogic.license")
		assert '"api-key" is missing from the specified license in license file' == e.exception.message

		# create ExpertClient with missing api-tenant
		with self.assertRaises(BoonException) as e:
			bn.ExpertClient(license_file="no-api-tenant.Boonlogic.license")
		assert '"api-tenant" is missing from the specified license in license file' == e.exception.message

		# create ExpertClient with missing server
		with self.assertRaises(BoonException) as e:
			bn.ExpertClient(license_file="no-server.Boonlogic.license")
		assert '"server" is missing from the specified license in license file' == e.exception.message

	def test_03_open_close(self):

		# allocate four nano handles and open an instance for each
		license_file = ".BoonLogic.license"
		nano_dict = dict()
		try:
			for cnt in range(1, 5):
				nano_key = 'nano-' + str(cnt)
				nano_inst = 'nano-instance-' + str(cnt)
				nano_dict[nano_key] = bn.ExpertClient(license_file=license_file)
				assert nano_dict[nano_key].license_id == 'default'
				response = nano_dict[nano_key].open_nano(nano_inst)
				print(response)
				assert response['instanceID'] == nano_inst
		except BoonException as be:
			assert False

		# create one more ExpertClient
		try:
			nano = bn.ExpertClient(license_file=license_file)
			assert nano.license_id == 'default'
		except BoonException as be:
			assert False

		# close an instance that doesn't exist, this involves creating two nano handles and point them at the
		# same instance.  closing the first should succeed, the second should fail
		clean_nano_instances(nano)

		try:
			nano1 = bn.ExpertClient(license_file=license_file)
			nano2 = bn.ExpertClient(license_file=license_file)
			assert nano1.license_id == 'default'
			assert nano2.license_id == 'default'
		except BoonException as be:
			assert False

		instance = 'instance-open-close'
		response = nano1.open_nano(instance)
		assert instance in response.values()
		response = nano2.open_nano(instance)
		assert instance in response.values()

		response1 = nano1.get_nano_instance(instance)
		assert instance in response1.values()
		assert response == response1

		# should succeed
		nano1.close_nano(instance)

		# should fail
		with self.assertRaises(BoonException) as e:
			nano2.close_nano(instance)
		assert e.exception.message == f'Nano instance identifier {instance} is not an allocated instance.'

	def test_04_open_close_negative(self):
		instance = 'non-existant'
		nano = bn.ExpertClient(license_file=".BoonLogic.license")
		with self.assertRaises(BoonException) as e:
			response = nano.get_nano_instance(instance)
		assert e.exception.message == f'Nano instance identifier {instance} is not an allocated instance.'


class Test2Results(unittest.TestCase):

	def setUp(self):
		build_environment()
		self.instance = 'instance-results'
		try:
			self.nano = bn.ExpertClient(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		response = self.nano.open_nano(self.instance)
		print(response)
		assert response['instanceID'] == self.instance

	def teardown(self):
		self.nano.close_nano(self.instance)

	def test_01_get_version(self):
		response = self.nano.get_version()
		print(response)
		assert 'nano-secure' in response
		assert 'builder' in response
		assert 'expert-api' in response
		assert 'expert-common' in response


class Test3Configure(unittest.TestCase):

	def setUp(self):
		self.instance = 'instance-configure'
		build_environment()
		try:
			self.nano = bn.ExpertClient(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		response = self.nano.open_nano(self.instance)
		print(response)
		assert response['instanceID'] == self.instance

	def teardown(self):
		self.nano.close_nano(self.instance)

	def test_01_configure(self):

		# create a configuration with single-value min_val, max_val, and weight
		config = self.nano.create_config(numeric_format='float32', cluster_mode='streaming',
												  feature_count=5, min_val=-10, max_val=15, weight=1, label=[f"feature-{i}" for i in range(5)],
												  streaming_window=1, percent_variation=0.05, accuracy=0.99,
												  autotune_pv=False, autotune_range=False, autotune_by_feature=False,
												  autotune_max_clusters=2000, exclusions=[1],
												  streaming_autotune=False, streaming_buffer=5000, anomaly_history_window=1000,
												  learning_numerator=1, learning_denominator=1000, learning_max_clusters=2000, learning_samples=50000)
		print(config)
		assert config['numericFormat'] == 'float32'
		assert config['accuracy'] == 0.99
		assert config['streamingWindowSize'] == 1
		assert config['percentVariation'] == 0.05
		assert len(config['features']) == 5

		# apply the configuration
		gen_config = self.nano.configure_nano(self.instance, config=config)
		print(gen_config)
		assert config == gen_config

		# query the configuration, should match the above response
		get_response = self.nano.get_config(self.instance)
		print(get_response)
		assert config == get_response

		# use the configuration template generator to create a per feature template
		config = self.nano.create_config(feature_count=4, numeric_format='int16',
												  min_val=[-15, -14, -13, -12], max_val=[15.0, 14, 13, 12],
												  weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
												  percent_variation=0.04,
												  streaming_window=1, accuracy=0.99)
		expected_features = [{"minVal": -15, "maxVal": 15, "weight": 1, "label": "l1"},
							 {"minVal": -14, "maxVal": 14, "weight": 1, "label": "l2"},
							 {"minVal": -13, "maxVal": 13, "weight": 2, "label": "l3"},
							 {"minVal": -12, "maxVal": 12, "weight": 1, "label": "l4"}
							 ]
		print(config)
		assert config['accuracy'] == 0.99
		assert config['features'] == expected_features
		assert config['numericFormat'] == 'int16'
		assert config['percentVariation'] == 0.04
		assert config['accuracy'] == 0.99
		assert config['streamingWindowSize'] == 1

		# create the same configuration using numpy arrays
		npconfig = self.nano.create_config(feature_count=4, numeric_format='int16',
													min_val=np.array([-15, -14, -13, -12]),
													max_val=np.array([15.0, 14, 13, 12]),
													weight=np.array([1, 1, 2, 1]), label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		print(npconfig)
		assert config == npconfig

	def test_02_configure_negative(self):

		# test get_config_template with bad numeric_format
		with self.assertRaises(BoonException) as e:
			response = self.nano.configure_nano(self.instance, numeric_format='int64', feature_count=5, min_val=-10,
													 max_val=15,
													 weight=1, streaming_window=1, percent_variation=0.05,
													 accuracy=0.99)
		assert e.exception.message == 'numericFormat in body should be one of [int16 float32 uint16]'

		# test create_config with bad min_val format
		with self.assertRaises(BoonException) as e:
			response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val="5", max_val=[15.0, 14, 13, 12],
													weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert e.exception.message == "min_val, max_val and weight must be list or numpy array"

		# test create_config with bad min_val
		with self.assertRaises(BoonException) as e:
			response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=[-15, -15], max_val=[15.0, 14, 13, 12],
													weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert e.exception.message == 'parameters must be lists of the same length'

		# test create_config with bad max_val
		with self.assertRaises(BoonException) as e:
			response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=-15, max_val=[10, 10],
													weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
			assert response == 'parameters must be lists of the same length'

		# test create_config with bad weight
		with self.assertRaises(BoonException) as e:
			response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=-15, max_val=10,
													weight=[1, 1], label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert e.exception.message == 'parameters must be lists of the same length'

		# test create_config with bad label
		with self.assertRaises(BoonException) as e:
			response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=-15, max_val=10,
													weight=1, label="mylabel",
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert e.exception.message == 'label must be list'

		# test create_config with bad label
		with self.assertRaises(BoonException) as e:
			response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=-15, max_val=10,
													weight=1, label=["mylabel"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert e.exception.message == "label must be the same length as other parameters"


class Test4Cluster(unittest.TestCase):

	def setUp(self):
		self.instance = 'instance-cluster'
		build_environment()
		try:
			self.nano = bn.ExpertClient(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		response = self.nano.open_nano(self.instance)
		print(response)
		assert response['instanceID'] == self.instance

	def teardown(self):
		self.nano.close_nano()

	def test_01_load_data(self):
		# apply the configuration
		config = self.nano.configure_nano(self.instance, feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99)
		print(config)

		# load data set
		dataFile = 'Data.csv'
		self.nano.load_file(self.instance, file=dataFile, file_type='csv', append_data=False)

		# load data set with gzip compression
		dataFile = 'Data.csv.gz'
		self.nano.load_file(self.instance, file=dataFile, file_type='csv', gzip=True, append_data=False)

		# load Data.csv and convert to list of floats
		dataBlob = []
		with open('Data.csv', 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				dataBlob = dataBlob + row

		# load data as list
		self.nano.load_data(self.instance, data=dataBlob, append_data=False)

		# load data from numpy array
		self.nano.load_data(self.instance, data=np.array(dataBlob), append_data=False)

		# load part of the data
		length = (int)((int)(len(dataBlob) / 20) / 2)
		self.nano.load_data(self.instance, data=dataBlob[:length * 20], append_data=False)

		# run the nano, ask for all results
		response = self.nano.run_nano(self.instance, results='All')
		print(response)
		assert sorted(list(response.keys())) == sorted(['ID', 'SI', 'RI', 'FI', 'DI', 'PI', 'OM', 'NI', 'NS', 'NW'])

		# ask again for the the nano results
		response2 = self.nano.get_nano_results(self.instance, results='All')
		print(response2)
		assert response == response2

		# run the nano, ask for just ID but the buffer has been cleared so it fails
		with self.assertRaises(BoonException) as e:
			self.nano.run_nano(self.instance, results='ID')
		assert 'There is no data to cluster' in e.exception.message

		# ask again for the the nano results
		response2 = self.nano.get_nano_results(self.instance, results='ID')
		print(response2)
		assert response['ID'] == response2['ID']

		# get root cause for a pattern before root cause is turned on (still works)
		response = self.nano.get_root_cause(self.instance, pattern_list=[[1]*len(config['features'])*config['streamingWindowSize']])
		print(response)
		assert len(response[0]) == 20

		# get root cause for a pattern with only one pattern
		print(([1]*len(config['features'])*config['streamingWindowSize']))
		response = self.nano.get_root_cause(self.instance, pattern_list=([1]*len(config['features'])*config['streamingWindowSize']))
		print(response)
		assert len(response[0]) == 20

		# fetch the buffer status
		response = self.nano.get_buffer_status(self.instance)
		print(response)
		assert len(response) == 3

		# fetch additional nano status 'All'
		response = self.nano.get_nano_status(self.instance, results='All')
		print(response)
		assert sorted(list(response.keys())) == sorted(['PCA', 'clusterGrowth', 'clusterSizes', 'anomalyIndexes',
												  'frequencyIndexes', 'distanceIndexes', 'totalInferences',
												  'numClusters', 'clusterDistances'])

		# fetch additional nano status 'numClusters'
		response = self.nano.get_nano_status(self.instance, results='numClusters')
		print(response)
		assert list(response.keys()) == ['numClusters']

		# get learning status
		response2 = self.nano.is_learning_enabled(self.instance)
		print(response2)
		assert response2

		# turn off learning
		response2 = self.nano.set_learning_enabled(self.instance, False)
		assert not response2

		# get root cause analysis
		response2 = self.nano.is_root_cause_enabled(self.instance)
		print(response2)
		assert not response2

		# turn on root cause analysis
		response2 = self.nano.set_root_cause_enabled(self.instance, True)
		print(response2)
		assert response2

		# get clipping detection status
		response2 = self.nano.is_clipping_detection_enabled(self.instance)
		print(response2)
		assert response2

		# turn on root cause analysis
		response2 = self.nano.set_clipping_detection_enabled(self.instance, True)
		print(response2)
		assert response2

		# load second half of data
		length = (int)((int)(len(dataBlob) / 20) / 2)
		self.nano.load_data(self.instance, data=dataBlob[length * 20:], append_data=False)

		# run the nano
		response2 = self.nano.run_nano(self.instance, results=None)
		print(response2)

		# get root cause from IDs
		root_cause = self.nano.get_root_cause(self.instance, id_list=[1])
		print(root_cause)

		# ask for the nano status result, 'numClusters'
		response2 = self.nano.get_nano_status(self.instance, results='numClusters')
		print(response2)
		assert response['numClusters'] == response2['numClusters']

		# prune ids
		response1 = self.nano.prune_ids(self.instance, id_list=1)
		print(response1)
		assert response['numClusters'] > response1['numClustersRemaining']

		# test autotune
		config = self.nano.configure_nano(self.instance, feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99,
												   autotune_pv=True, autotune_range=True, autotune_by_feature=False)
		print(config)
		self.nano.load_data(self.instance, data=dataBlob[:length * 20], append_data=False)
		self.nano.autotune_config(self.instance)

		# test autotune but exclude features 1 and 3
		config = self.nano.configure_nano(self.instance, feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99,
												   autotune_pv=True, autotune_range=True, autotune_by_feature=False,
												   exclusions=[1, 3])
		print(config)
		self.nano.load_data(self.instance, data=dataBlob[:length * 20], append_data=False)
		self.nano.autotune_config(self.instance)

		response = self.nano.get_autotune_array(self.instance)
		assert len(response) == 2

		# do a quick negative test where exclusions is not a list
		with self.assertRaises(BoonException) as e:
			self.nano.configure_nano(self.instance, feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99,
												   autotune_pv=True, autotune_range=True, autotune_by_feature=False,
												   exclusions=10)
		assert e.exception.message == 'exclusions must be a list'

		# save the configuration
		self.nano.save_nano(self.instance, './saved-nano-1')

		# restore the configuration
		response = self.nano.restore_nano(self.instance, 'saved-nano-1')
		print(response)

		# attempt to restore a corrupt saved nano
		with self.assertRaises(BoonException) as e:
			response = self.nano.restore_nano(self.instance, 'bad-magic.tgz')
		assert e.exception.message == 'corrupt file bad-magic.tgz'

	def test_02_load_data_negative(self):

		# create a configuration with single-value min_val, max_val, and weight
		config = self.nano.create_config(numeric_format='float32', feature_count=20, min_val=-10,
												  max_val=15, weight=1, streaming_window=1,
												  percent_variation=0.05, accuracy=0.99)

		# attempt to load from a file for a nano that is not configured
		dataFile = 'Data.csv'
		with self.assertRaises(BoonException) as e:
			self.nano.load_file(self.instance, file=dataFile, file_type='csv', append_data=False)
		assert e.exception.message == 'nano instance is not configured'

		# get root cause before configured
		with self.assertRaises(BoonException) as e:
			response = self.nano.get_root_cause(self.instance, id_list=[1,1])
		assert e.exception.message == 'The clustering parameters have not been initialized'

		# apply the configuration
		gen_config = self.nano.configure_nano(self.instance, config=config)
		print(gen_config)

		# attempt to load data with a non-existent file
		dataFile = 'BadData.csv'
		with self.assertRaises(BoonException) as e:
			self.nano.load_file(self.instance, file=dataFile, file_type='csv', append_data=False)
		assert e.exception.message == 'No such file or directory'

		# attempt to load from a file and specify bad file_type
		dataFile = 'Data.csv'
		with self.assertRaises(BoonException) as e:
			self.nano.load_file(self.instance, file=dataFile, file_type='cbs', append_data=False)
		assert e.exception.message == 'file_type must be "csv", "csv-c", "raw" or "raw-n"'

		# run a nano with bad results specifier
		with self.assertRaises(BoonException) as e:
			response = self.nano.run_nano(self.instance, results='NA')

		# no ids given to prune
		with self.assertRaises(BoonException) as e:
			response = self.nano.prune_ids(self.instance)
		assert e.exception.message == "Must specify cluster IDs to analyze"

		# set learning to a non boolean
		with self.assertRaises(BoonException) as e:
			response = self.nano.set_learning_enabled(self.instance, status=None)

		# set root cause status to a non boolean
		with self.assertRaises(BoonException) as e:
			response = self.nano.set_root_cause_enabled(self.instance, status=None)

		# set clipping status to a non boolean
		with self.assertRaises(BoonException) as e:
			response = self.nano.set_clipping_detection_enabled(self.instance, status=None)

		# get nano results with bad results specifier
		with self.assertRaises(BoonException) as e:
			response = self.nano.get_nano_results(self.instance, results='NA')

		# get nano status with bad results specifier
		with self.assertRaises(BoonException) as e:
			response = self.nano.get_nano_status(self.instance, results='NA')

		# save the configuration with a bad pathname
		with self.assertRaises(BoonException) as e:
			self.nano.save_nano(self.instance, '/badpath/junk/bad-saved-nano-1')
		assert 'No such file or directory' in e.exception.message


class Test5StreamingCluster(unittest.TestCase):

	def setUp(self):
		self.instance = 'instance-streaming-cluster'
		build_environment()
		try:
			self.nano = bn.ExpertClient(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		response = self.nano.open_nano(self.instance)
		print(response)
		assert response['instanceID'] == self.instance

	def teardown(self):
		self.nano.close_nano(self.instance)

	def test_01_run_nano_streaming(self):
		# create a configuration with single-value min_val, max_val, and weight
		config = self.nano.create_config(numeric_format='float32', cluster_mode='streaming',
												  feature_count=20, min_val=-10,
												  max_val=15, weight=1, streaming_window=1,
												  percent_variation=0.05, accuracy=0.99)
		print(config)

		# apply the configuration
		gen_config = self.nano.configure_nano(self.instance, config=config)
		print(gen_config)

		# load Data.csv and convert to list of floats
		dataBlob = list()
		with open('Data.csv', 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				dataBlob = dataBlob + row

		# write the data to the streaming nano, with results == All
		response = self.nano.run_streaming_nano(self.instance, data=dataBlob, results='All')
		print(response)
		assert len(response) == 10

		# write the data to the streaming nano, with results == 'SI'
		response = self.nano.run_streaming_nano(self.instance, data=dataBlob, results='SI')
		print(response)
		assert 'SI' in response

	def test_02_run_nano_streaming_negative(self):
		# create a configuration with single-value min_val, max_val, and weight
		config = self.nano.create_config(feature_count=20, numeric_format='float32', min_val=-10,
												  max_val=15, weight=1, streaming_window=1,
												  percent_variation=0.05, accuracy=0.99)
		print(config)

		# apply the configuration
		gen_config = self.nano.configure_nano(self.instance, config=config)
		print(gen_config)

		# load Data.csv and convert to list of floats
		dataBlob = list()
		with open('Data.csv', 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				dataBlob = dataBlob + row

		# run streaming nano with bad results specifier
		with self.assertRaises(BoonException) as e:
			response = self.nano.run_streaming_nano(self.instance, data=dataBlob, results='NA')
		assert 'formData should be one of' in e.exception.message


class Test6Rest(unittest.TestCase):

	def setUp(self):
		self.instance = 'instance-rest'
		build_environment()
		try:
			self.nano = bn.ExpertClient(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		response = self.nano.open_nano(self.instance)
		print(response)
		assert response['instanceID'] == self.instance

	def teardown(self):
		os.environ['BOON_SERVER'] = ''
		self.nano = bn.ExpertClient(license_file="./.BoonLogic.license")
		self.nano.close_nano(self.instance)

	def test_01_negative(self):

		# override server with a bad one
		os.environ['BOON_SERVER'] = 'not-a-server:9999'
		self.nano = bn.ExpertClient(license_file="./.BoonLogic.license")

		# simple_get with bad server
		self.nano.server = '/expert/v3/instance'
		with self.assertRaises(BoonException) as e:
			self.nano.get_version()
		assert e.exception.message == 'server does not exist'

if __name__ == '__main__':
	unittest.main()
