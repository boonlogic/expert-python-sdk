import sys

sys.path.append('..')

import boonnano as bn
import csv
import os
import json
import numpy as np
import socket
import unittest


def clean_nano_instances(nano):
	# clean out nano instances
	success, nano_list = nano.nano_list()
	print(nano_list)
	assert success
	for nano_inst in nano_list:
		nano.open_nano(nano_inst['instanceID'])
		nano.close_nano()


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

	# This test class verifies the NanoHandle/open/close functionality
	def setUp(self):
		build_environment()

	def test_01_nano_handle(self):

		# successful nano-handle created with default options
		try:
			nano = bn.NanoHandle(license_file="./.BoonLogic.license")
			assert nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		# clean house
		clean_nano_instances(nano)

		# successful nano-handle created with None specified for license_id, should equate to default
		try:
			nano = bn.NanoHandle(license_file=".BoonLogic.license", license_id=None)
			assert nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		# successful nano-handle created with non-default specified, license_id=localhost
		try:
			nano = bn.NanoHandle(license_file=".BoonLogic.license", license_id='sample-license')
			assert nano.license_id == 'sample-license'
			assert nano.api_key == 'sample-key'
			assert nano.api_tenant == 'sample-tenant'
			assert nano.server == 'http://sample.host:5007'
		except bn.BoonException as be:
			assert False

		# override license_id through environment
		os.environ['BOON_LICENSE_ID'] = 'sample-license'
		try:
			nano = bn.NanoHandle(license_file=".BoonLogic.license")
			assert nano.license_id == 'sample-license'
			assert nano.api_key == 'sample-key'
			assert nano.api_tenant == 'sample-tenant'
			assert nano.server == 'http://sample.host:5007'
		except bn.BoonException as be:
			assert False
		os.environ.pop('BOON_LICENSE_ID')

		# override BOON_API_KEY, BOON_API_TENANT and BOON_SERVER
		os.environ['BOON_API_KEY'] = 'new-key'
		os.environ['BOON_API_TENANT'] = 'new-tenant'
		os.environ['BOON_SERVER'] = 'new-server:9999'
		try:
			nano = bn.NanoHandle(license_file=".BoonLogic.license")
			assert nano.license_id == 'default'
			assert nano.api_key == 'new-key'
			assert nano.api_tenant == 'new-tenant'
			assert nano.server == 'new-server:9999'
		except bn.BoonException as be:
			assert False
		os.environ.pop('BOON_API_KEY')
		os.environ.pop('BOON_API_TENANT')
		os.environ.pop('BOON_SERVER')

	def test_02_nano_handle_negative(self):

		# create NanoHandle using bad license path
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_file=".BadLogic.license", license_id='sample-license')

		# create NanoHandle using badly formatted json
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_file="badformat.Boonlogic.license", license_id='sample-license')

		# create NanoHandle using non-existent license_id
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_id='not-a-license')

		# create NanoHandle using non-existent BOON_LICENSE_ID
		os.environ['BOON_LICENSE_ID'] = 'not-a-license'
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_id='not-a-license')
		os.environ.pop('BOON_LICENSE_ID')

		# create NanoHandle with missing api-key
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_file="no-api-key.Boonlogic.license")

		# create NanoHandle with missing api-tenant
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_file="no-tenant-id.Boonlogic.license")

		# create NanoHandle with missing api-tenant
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_file="no-api-tenant.Boonlogic.license")

		# create NanoHandle with missing server
		with self.assertRaises(bn.BoonException):
			bn.NanoHandle(license_file="no-server.Boonlogic.license")

	def test_03_open_close(self):

		# allocate four nano handles and open an instance for each
		license_file = ".BoonLogic.license"
		nano_dict = dict()
		try:
			for cnt in range(1, 5):
				nano_key = 'nano-' + str(cnt)
				nano_inst = 'nano-instance-' + str(cnt)
				nano_dict[nano_key] = bn.NanoHandle(license_file=license_file)
				assert nano_dict[nano_key].license_id == 'default'
				success, response = nano_dict[nano_key].open_nano(nano_inst)
				print(response)
				assert success
				assert response['instanceID'] == nano_inst
		except bn.BoonException as be:
			assert False

		# create one more NanoHandle
		try:
			nano = bn.NanoHandle(license_file=license_file)
			assert nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		# close an instance that doesn't exist, this involves creating two nano handles and point them at the
		# same instance.  closing the first should succeed, the second should fail
		clean_nano_instances(nano)

		try:
			nano1 = bn.NanoHandle(license_file=license_file)
			nano2 = bn.NanoHandle(license_file=license_file)
			assert nano1.license_id == 'default'
			assert nano2.license_id == 'default'
		except bn.BoonException as be:
			assert False

		success, response = nano1.open_nano('instance-1')
		print(response)
		assert success
		success, response = nano2.open_nano('instance-1')
		print(response)
		assert success

		success, response1 = nano1.get_nano_instance('instance-1')
		print(response1)
		assert success
		assert response == response1

		# should succeed
		success, response = nano1.close_nano()
		print(response)
		assert success

		# should fail
		success, response = nano2.close_nano()
		assert not success

	def test_04_open_close_negative(self):
		nano = bn.NanoHandle(license_file=".BoonLogic.license")
		success, response = nano.get_nano_instance("non-existant")
		assert not success


class Test2Results(unittest.TestCase):

	def setUp(self):
		build_environment()
		try:
			self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		success, response = self.nano.open_nano('instance-1')
		print(response)
		assert success
		assert response['instanceID'] == 'instance-1'

	def teardown(self):
		self.nano.close_nano()

	def test_01_get_version(self):
		success, response = self.nano.get_version()
		print(response)
		assert success
		assert 'nano-secure' in response
		assert 'builder' in response
		assert 'expert-api' in response
		assert 'expert-common' in response


class Test3Configure(unittest.TestCase):

	def setUp(self):
		build_environment()
		try:
			self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		success, response = self.nano.open_nano('instance-1')
		print(response)
		assert success
		assert response['instanceID'] == 'instance-1'

	def teardown(self):
		self.nano.close_nano()

	def test_01_configure(self):

		# create a configuration with single-value min_val, max_val, and weight
		success, config = self.nano.create_config(numeric_format='float32', cluster_mode='streaming',
												  feature_count=5, min_val=-10, max_val=15, weight=1, label=[f"feature-{i}" for i in range(5)],
												  streaming_window=1, percent_variation=0.05, accuracy=0.99,
												  autotune_pv=False, autotune_range=False, autotune_by_feature=False,
												  autotune_max_clusters=2000, exclusions=[1],
												  streaming_autotune=False, streaming_buffer=5000, anomaly_history_window=1000,
												  learning_numerator=1, learning_denominator=1000, learning_max_clusters=2000, learning_samples=50000)
		print(config)
		assert success
		assert config['numericFormat'] == 'float32'
		assert config['accuracy'] == 0.99
		assert config['streamingWindowSize'] == 1
		assert config['percentVariation'] == 0.05
		assert len(config['features']) == 5

		# apply the configuration
		success, gen_config = self.nano.configure_nano(config=config)
		print(gen_config)
		assert success
		assert config == gen_config

		# query the configuration, should match the above response
		success, get_response = self.nano.get_config()
		print(get_response)
		assert success
		assert config == get_response

		# use the configuration template generator to create a per feature template
		success, config = self.nano.create_config(feature_count=4, numeric_format='int16',
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
		assert success
		assert config['accuracy'] == 0.99
		assert config['features'] == expected_features
		assert config['numericFormat'] == 'int16'
		assert config['percentVariation'] == 0.04
		assert config['accuracy'] == 0.99
		assert config['streamingWindowSize'] == 1

		# create the same configuration using numpy arrays
		success, npconfig = self.nano.create_config(feature_count=4, numeric_format='int16',
													min_val=np.array([-15, -14, -13, -12]),
													max_val=np.array([15.0, 14, 13, 12]),
													weight=np.array([1, 1, 2, 1]), label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		print(npconfig)
		assert success
		assert config == npconfig

	def test_02_configure_negative(self):

		# test get_config_template with bad numeric_format
		success, response = self.nano.configure_nano(numeric_format='int64', feature_count=5, min_val=-10,
													 max_val=15,
													 weight=1, streaming_window=1, percent_variation=0.05,
													 accuracy=0.99)
		assert not success
		assert response == '606: numericFormat in body should be one of [int16 float32 uint16]'

		# test create_config with bad min_val
		success, response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=[-15, -15], max_val=[15.0, 14, 13, 12],
													weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert not success
		assert response == 'parameters must be lists of the same length'

		# test create_config with bad max_val
		success, response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=-15, max_val=[10, 10],
													weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert not success
		assert response == 'parameters must be lists of the same length'

		# test create_config with bad max_val
		success, response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=-15, max_val=10,
													weight=[1, 1], label=["l1", "l2", "l3", "l4"],
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert not success
		assert response == 'parameters must be lists of the same length'

		# test create_config with bad label
		success, response = self.nano.create_config(numeric_format='int16', feature_count=4,
													min_val=-15, max_val=10,
													weight=1, label="mylabel",
													percent_variation=0.04,
													streaming_window=1, accuracy=0.99)
		assert not success
		assert response == 'label must be list'


class Test4Cluster(unittest.TestCase):

	def setUp(self):
		build_environment()
		try:
			self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		success, response = self.nano.open_nano('instance-1')
		print(response)
		assert success
		assert response['instanceID'] == 'instance-1'

	def teardown(self):
		self.nano.close_nano()

	def test_01_load_data(self):
		# apply the configuration
		success, config = self.nano.configure_nano(feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99)
		print(config)
		assert success

		# load data set
		dataFile = 'Data.csv'
		success, response = self.nano.load_file(file=dataFile, file_type='csv', append_data=False)
		print(response)
		assert success

		# load data set with gzip compression
		dataFile = 'Data.csv.gz'
		success, response = self.nano.load_file(file=dataFile, file_type='csv', gzip=True, append_data=False)
		print(response)
		assert success

		# load Data.csv and convert to list of floats
		dataBlob = []
		with open('Data.csv', 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				dataBlob = dataBlob + row

		# load data as list
		success, response = self.nano.load_data(data=dataBlob, append_data=False)
		print(response)
		assert success

		# load data from numpy array
		success, response = self.nano.load_data(data=np.array(dataBlob), append_data=False)
		print(response)
		assert success

		# load part of the data
		length = (int)((int)(len(dataBlob) / 20) / 2)
		success, response = self.nano.load_data(data=dataBlob[:length * 20], append_data=False)
		print(response)
		assert success

		# run the nano, ask for all results
		success, response = self.nano.run_nano(results='All')
		print(response)
		assert success
		assert sorted(list(response.keys())) == sorted(['ID', 'SI', 'RI', 'FI', 'DI'])

		# ask again for the the nano results
		success, response2 = self.nano.get_nano_results(results='All')
		print(response2)
		assert success
		assert response == response2

		# run the nano, ask for just ID but the buffer has been cleared so it fails
		success, _ = self.nano.run_nano(results='ID')
		assert not success

		# ask again for the the nano results
		success, response2 = self.nano.get_nano_results(results='ID')
		print(response2)
		assert success
		assert response['ID'] == response2['ID']

		# get root cause for a pattern before root cause is turned on (still works)
		success, response = self.nano.get_root_cause(pattern_list=[[1]*len(config['features'])*config['streamingWindowSize']])
		print(response)
		assert success

		# fetch the buffer status
		success, response = self.nano.get_buffer_status()
		print(response)
		assert success

		# fetch additional nano status 'All'
		success, response = self.nano.get_nano_status(results='All')
		print(response)
		assert success
		assert sorted(list(response.keys())) == sorted(['PCA', 'clusterGrowth', 'clusterSizes', 'anomalyIndexes',
												  'frequencyIndexes', 'distanceIndexes', 'totalInferences',
												  'numClusters'])

		# fetch additional nano status 'numClusters'
		success, response = self.nano.get_nano_status(results='numClusters')
		print(response)
		assert success
		assert list(response.keys()) == ['numClusters']

		# get learning status
		success, response2 = self.nano.is_learning_enabled()
		print(response2)
		assert success
		assert response2

		# turn off learning
		success, response2 = self.nano.set_learning_enabled(False)
		print(response2)
		assert success
		assert not response2

		# get root cause analysis
		success, response2 = self.nano.is_root_cause_enabled()
		print(response2)
		assert success
		assert not response2

		# turn on root cause analysis
		success, response2 = self.nano.set_root_cause_enabled(True)
		print(response2)
		assert success
		assert response2

		# get clipping detection status
		success, response2 = self.nano.is_clipping_detection_enabled()
		print(response2)
		assert success
		assert response2

		# turn on root cause analysis
		success, response2 = self.nano.set_clipping_detection_enabled(True)
		print(response2)
		assert success
		assert response2

		# load second half of data
		length = (int)((int)(len(dataBlob) / 20) / 2)
		success, response2 = self.nano.load_data(data=dataBlob[length * 20:], append_data=False)
		print(response2)
		assert success

		# run the nano
		success, response2 = self.nano.run_nano(results=None)
		print(response2)
		assert success

		# get root cause from IDs
		success, root_cause = self.nano.get_root_cause(id_list=[1])
		print(root_cause)
		assert success

		# ask for the nano status result, 'numClusters'
		success, response2 = self.nano.get_nano_status(results='numClusters')
		print(response2)
		assert success
		assert response['numClusters'] == response2['numClusters']

		# test autotune
		success, config = self.nano.configure_nano(feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99,
												   autotune_pv=True, autotune_range=True, autotune_by_feature=False)
		print(config)
		assert success
		success, response = self.nano.load_data(data=dataBlob[:length * 20], append_data=False)
		print(response)
		assert success
		success, response = self.nano.autotune_config()
		print(response)
		assert success

		# test autotune but exclude features 1 and 3
		success, config = self.nano.configure_nano(feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99,
												   autotune_pv=True, autotune_range=True, autotune_by_feature=False,
												   exclusions=[1, 3])
		print(config)
		assert success
		success, response = self.nano.load_data(data=dataBlob[:length * 20], append_data=False)
		print(response)
		assert success
		success, response = self.nano.autotune_config()
		print(response)
		assert success

		# do a quick negative test where exclusions is not a list
		success, config = self.nano.configure_nano(feature_count=20, numeric_format='float32', min_val=-10,
												   max_val=15, weight=1, streaming_window=1,
												   percent_variation=0.05, accuracy=0.99,
												   autotune_pv=True, autotune_range=True, autotune_by_feature=False,
												   exclusions=10)
		assert not success
		assert config == 'exclusions must be a list'

		# save the configuration
		success, response = self.nano.save_nano('./saved-nano-1')
		print(response)
		assert success

		# restore the configuration
		success, response = self.nano.restore_nano('saved-nano-1')
		print(response)
		assert success

		# attempt to restore a corrupt saved nano
		success, response = self.nano.restore_nano('bad-magic.tgz')
		assert not success
		assert response == 'corrupt file bad-magic.tgz'

	def test_02_load_data_negative(self):

		# create a configuration with single-value min_val, max_val, and weight
		success, config = self.nano.create_config(numeric_format='float32', feature_count=20, min_val=-10,
												  max_val=15, weight=1, streaming_window=1,
												  percent_variation=0.05, accuracy=0.99)

		# attempt to load from a file for a nano that is not configured
		dataFile = 'Data.csv'
		success, response = self.nano.load_file(file=dataFile, file_type='csv', append_data=False)
		assert not success
		assert response == 'nano instance is not configured'

		# get root cause before configured
		success, response = self.nano.get_root_cause(id_list=[1,1])
		assert not success
		assert response == '400: The clustering parameters have not been initialized'

		# apply the configuration
		success, gen_config = self.nano.configure_nano(config=config)
		print(gen_config)
		assert success

		# attempt to load data with a non-existent file
		dataFile = 'BadData.csv'
		success, response = self.nano.load_file(file=dataFile, file_type='csv', append_data=False)
		assert not success
		assert response == 'No such file or directory'

		# attempt to load from a file and specify bad file_type
		dataFile = 'Data.csv'
		success, response = self.nano.load_file(file=dataFile, file_type='cbs', append_data=False)
		assert not success
		assert response == 'file_type must be "csv", "csv-c", "raw" or "raw-n"'

		# run a nano with bad results specifier
		success, response = self.nano.run_nano(results='NA')
		assert not success

		# set learning to a non boolean
		success, response = self.nano.set_learning_enabled(status=None)
		assert not success

		# set root cause status to a non boolean
		success, response = self.nano.set_root_cause_enabled(status=None)
		assert not success

		# get nano results with bad results specifier
		success, response = self.nano.get_nano_results(results='NA')
		assert not success

		# get nano status with bad results specifier
		success, response = self.nano.get_nano_status(results='NA')
		assert not success

		# save the configuration with a bad pathname
		success, response = self.nano.save_nano('/badpath/junk/bad-saved-nano-1')
		assert not success
		assert response == 'No such file or directory'


class Test5StreamingCluster(unittest.TestCase):

	def setUp(self):
		build_environment()
		try:
			self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		success, response = self.nano.open_nano('instance-1')
		print(response)
		assert success
		assert response['instanceID'] == 'instance-1'

	def teardown(self):
		self.nano.close_nano()

	def test_01_run_nano_streaming(self):
		# create a configuration with single-value min_val, max_val, and weight
		success, config = self.nano.create_config(numeric_format='float32', cluster_mode='streaming',
												  feature_count=20, min_val=-10,
												  max_val=15, weight=1, streaming_window=1,
												  percent_variation=0.05, accuracy=0.99)
		print(config)
		assert success

		# apply the configuration
		success, gen_config = self.nano.configure_nano(config=config)
		print(gen_config)
		assert success

		# load Data.csv and convert to list of floats
		dataBlob = list()
		with open('Data.csv', 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				dataBlob = dataBlob + row

		# write the data to the streaming nano, with results == All
		success, response = self.nano.run_streaming_nano(data=dataBlob, results='All')
		print(response)
		assert success

		# write the data to the streaming nano, with results == 'SI'
		success, response = self.nano.run_streaming_nano(data=dataBlob, results='SI')
		print(response)
		assert success

	def test_02_run_nano_streaming_negative(self):
		# create a configuration with single-value min_val, max_val, and weight
		success, config = self.nano.create_config(feature_count=20, numeric_format='float32', min_val=-10,
												  max_val=15, weight=1, streaming_window=1,
												  percent_variation=0.05, accuracy=0.99)
		print(config)
		assert success

		# apply the configuration
		success, gen_config = self.nano.configure_nano(config=config)
		print(gen_config)
		assert success

		# load Data.csv and convert to list of floats
		dataBlob = list()
		with open('Data.csv', 'r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				dataBlob = dataBlob + row

		# run streaming nano with bad results specifier
		success, response = self.nano.run_streaming_nano(data=dataBlob, results='NA')
		assert not success


class Test6Rest(unittest.TestCase):

	def setUp(self):
		build_environment()
		try:
			self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
			assert self.nano.license_id == 'default'
		except bn.BoonException as be:
			assert False

		clean_nano_instances(self.nano)
		success, response = self.nano.open_nano('instance-1')
		print(response)
		assert success
		assert response['instanceID'] == 'instance-1'

	def teardown(self):
		os.environ['BOON_SERVER'] = ''
		self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
		self.nano.close_nano()

	def test_01_negative(self):

		# override server with a bad one
		os.environ['BOON_SERVER'] = 'not-a-server:9999'
		self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")

		# simple_get with bad server
		success, response = bn.simple_get(self.nano, '/expert/v3/instance')
		assert not success
		assert response == 'request failed: No host specified.'

		# multipart_post with bad server
		success, response = bn.multipart_post(self.nano, '/expert/v3/instance')
		assert not success
		assert response == 'request failed: No host specified.'

		# simple_post with bad server
		success, response = bn.simple_post(self.nano, '/expert/v3/deleteInstance')
		assert not success
		assert response == 'request failed: No host specified.'

		# simple_delete with bad server
		success, response = bn.simple_delete(self.nano, '/expert/v3/deleteInstance')
		assert not success
		assert response == 'request failed: No host specified.'


if __name__ == '__main__':
	unittest.main()
