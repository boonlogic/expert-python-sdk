import boonnano as bn
import csv
import nose
from nose.tools import assert_equal
from nose.tools import assert_list_equal
from nose.tools import assert_dict_equal
from nose.tools import assert_false
import os
import numpy as np
import json
from nose.tools import raises
from nose.tools import assert_not_equal
from nose.tools import assert_raises


def clean_nano_instances(nano):
    # clean out nano instances
    success, nano_list = nano.nano_list()
    for nano_inst in nano_list:
        nano.open_nano(nano_inst['instanceID'])
        nano.close_nano()


class TestManagement(object):

    # This test class verifies the NanoHandle/open/close functionality
    # Setup is skipped

    def test_nano_handle(self):

        # successful nano-handle created with default options
        try:
            nano = bn.NanoHandle(license_file="./.BoonLogic.license")
            assert_equal(nano.license_id, 'default')
        except bn.BoonException as be:
            assert_false(False, 'test for default license_id failed')

        # clean house
        clean_nano_instances(nano)

        # successful nano-handle created with None specified for license_id, should equate to default
        try:
            nano = bn.NanoHandle(license_file=".BoonLogic.license", license_id=None)
            assert_equal(nano.license_id, 'default')
        except bn.BoonException as be:
            assert_false(False, 'test for license_id = None failed')

        # successful nano-handle created with non-default specified, license_id=localhost
        try:
            nano = bn.NanoHandle(license_file=".BoonLogic.license", license_id='sample-license')
            assert_equal(nano.license_id, 'sample-license')
            assert_equal(nano.api_key, 'sample-key')
            assert_equal(nano.api_tenant, 'sample-tenant')
            assert_equal(nano.server, 'http://samplehost:5007')
        except bn.BoonException as be:
            assert_false(False, 'test for license_id = localhost failed')

        # override license_id through environment
        os.environ['BOON_LICENSE_ID'] = 'sample-license'
        try:
            nano = bn.NanoHandle(license_file=".BoonLogic.license")
            assert_equal(nano.license_id, 'sample-license')
            assert_equal(nano.api_key, 'sample-key')
            assert_equal(nano.api_tenant, 'sample-tenant')
            assert_equal(nano.server, 'http://samplehost:5007')
        except bn.BoonException as be:
            assert_false(False, 'test for BOON_LICENSE_ID = sample-license failed')
        os.environ.pop('BOON_LICENSE_ID')

        # override BOON_API_KEY, BOON_TENANT and BOON_SERVER
        os.environ['BOON_API_KEY'] = 'new-key'
        os.environ['BOON_TENANT'] = 'new-tenant'
        os.environ['BOON_SERVER'] = 'new-server:9999'
        try:
            nano = bn.NanoHandle(license_file=".BoonLogic.license")
            assert_equal(nano.license_id, 'default')
            assert_equal(nano.api_key, 'new-key')
            assert_equal(nano.api_tenant, 'new-tenant')
            assert_equal(nano.server, 'new-server:9999')
        except bn.BoonException as be:
            assert_false(False, 'test for environment override failed')
        os.environ.pop('BOON_API_KEY')
        os.environ.pop('BOON_TENANT')
        os.environ.pop('BOON_SERVER')

    def test_nano_handle_negative(self):

        # create NanoHandle using bad license path
        assert_raises(bn.BoonException, bn.NanoHandle, license_file=".BadLogic.license", license_id='sample-license')

        # create NanoHandle using badly formatted json
        assert_raises(bn.BoonException, bn.NanoHandle, license_file=".BoonLogic.badformat", license_id='sample-license')

        # create NanoHandle using non-existent license_id
        assert_raises(bn.BoonException, bn.NanoHandle, license_id='not-a-license')

        # create NanoHandle using non-existent BOON_LICENSE_ID
        os.environ['BOON_LICENSE_ID'] = 'not-a-license'
        assert_raises(bn.BoonException, bn.NanoHandle, license_id='not-a-license')
        os.environ.pop('BOON_LICENSE_ID')

        # create NanoHandle with missing api-key
        assert_raises(bn.BoonException, bn.NanoHandle, license_file=".BoonLogic.no-api-key")

        # create NanoHandle with missing api-tenant
        assert_raises(bn.BoonException, bn.NanoHandle, license_file=".BoonLogic.no-tenant-id")

        # create NanoHandle with missing api-tenant
        assert_raises(bn.BoonException, bn.NanoHandle, license_file=".BoonLogic.no-api-tenant")

        # create NanoHandle with missing server
        assert_raises(bn.BoonException, bn.NanoHandle, license_file=".BoonLogic.no-server")

    def test_open_close(self):

        # allocate four nano handles and open an instance for each
        nano_dict = dict()
        try:
            for cnt in range(1, 5):
                nano_key = 'nano-' + str(cnt)
                nano_inst = 'nano-instance-' + str(cnt)
                nano_dict[nano_key] = bn.NanoHandle(license_file=".BoonLogic.license")
                assert_equal(nano_dict[nano_key].license_id, 'default')
                success, response = nano_dict[nano_key].open_nano(nano_inst)
                assert_equal(success, True)
                assert_equal(response['instanceID'], nano_inst)
        except bn.BoonException as be:
            assert_false(False, 'creation of 4 nano handles failed')

        # create one more NanoHandle
        try:
            nano = bn.NanoHandle(license_file=".BoonLogic.license")
            assert_equal(nano.license_id, 'default')
        except bn.BoonException as be:
            assert_false(False, 'test for default license_id failed')

        # attaching to 1 more instance should cause an error
        success, response = nano.open_nano('1-too-many')
        assert_equal(success, False)
        assert_equal(response, '400: All nano instance objects are allocated (total number = 4)')

        # close an instance that doesn't exist, this involves creating two nano handles and point them at the
        # same instance.  closing the first should succeed, the second should fail
        clean_nano_instances(nano)
        try:
            nano1 = bn.NanoHandle(license_file=".BoonLogic.license")
            nano2 = bn.NanoHandle(license_file=".BoonLogic.license")
            assert_equal(nano1.license_id, 'default')
            assert_equal(nano2.license_id, 'default')
        except bn.BoonException as be:
            assert_false(False, 'test for default license_id failed')

        success, response = nano1.open_nano('instance-1')
        assert_equal(success, True)
        success, response = nano2.open_nano('instance-1')
        assert_equal(success, True)

        # should succeed
        success, response = nano1.close_nano()
        assert_equal(success, True)

        # should fail
        success, response = nano2.close_nano()
        assert_equal(success, False)


class TestResults(object):

    def __init__(self):
        try:
            self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
            assert_equal(self.nano.license_id, 'default')
        except bn.BoonException as be:
            assert_false(False, 'test for default license_id failed')

    def setUp(self):
        clean_nano_instances(self.nano)
        success, response = self.nano.open_nano('instance-1')
        assert_equal(success, True)
        assert_equal(response['instanceID'], 'instance-1')

    def teardown(self):
        self.nano.close_nano()

    def test_get_version(self):
        success, response = self.nano.get_version()
        assert_equal(success, True)
        assert_list_equal(list(response.keys()),
                          ['release', 'api-version', 'nano-secure', 'builder', 'expert-api', 'expert-common',
                           'swagger-ui'])


class TestConfigure(object):

    def __init__(self):
        try:
            self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
            assert_equal(self.nano.license_id, 'default')
        except bn.BoonException as be:
            assert_false(False, 'test for default license_id failed')

    def setUp(self):
        clean_nano_instances(self.nano)
        success, response = self.nano.open_nano('instance-1')
        assert_equal(success, True)
        assert_equal(response['instanceID'], 'instance-1')

    def teardown(self):
        self.nano.close_nano()

    def test_configure(self):

        # create a configuration with single-value min_val, max_val, and weight
        success, config = self.nano.create_config(numeric_format='float32', feature_count=5, min_val=[-10],
                                                  max_val=[15], weight=[1], streaming_window=1,
                                                  percent_variation=0.05, accuracy=0.99)
        assert_equal(success, True)
        assert_equal(config['numericFormat'], 'float32')
        assert_equal(config['accuracy'], 0.99)
        assert_equal(config['streamingWindowSize'], 1)
        assert_equal(config['percentVariation'], 0.05)
        assert_equal(len(config['features']), 5)

        # apply the configuration
        success, gen_config = self.nano.configure_nano(config)
        assert_equal(success, True)
        assert_dict_equal(config, gen_config)

        # query the configuration, should match the above response
        success, get_response = self.nano.get_config()
        assert_equal(success, True)
        assert_dict_equal(config, get_response)

        # use the configuration template generator to create a per feature template
        success, config = self.nano.create_config(numeric_format='int16', feature_count=4,
                                                  min_val=[-15, -14, -13, -12], max_val=[15.0, 14, 13, 12],
                                                  weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
                                                  percent_variation=0.04,
                                                  streaming_window=1, accuracy=0.99)
        expected_features = [{"minVal": -15, "maxVal": 15, "weight": 1, "label": "l1"},
                             {"minVal": -14, "maxVal": 14, "weight": 1, "label": "l2"},
                             {"minVal": -13, "maxVal": 13, "weight": 2, "label": "l3"},
                             {"minVal": -12, "maxVal": 12, "weight": 1, "label": "l4"}
                             ]
        assert_equal(success, True)
        assert_equal(config['accuracy'], 0.99)
        assert_list_equal(config['features'], expected_features)
        assert_equal(config['numericFormat'], 'int16')
        assert_equal(config['percentVariation'], 0.04)
        assert_equal(config['accuracy'], 0.99)
        assert_equal(config['streamingWindowSize'], 1)

        # create the same configuration using numpy arrays
        success, npconfig = self.nano.create_config(numeric_format='int16', feature_count=4,
                                                    min_val=np.array([-15, -14, -13, -12]),
                                                    max_val=np.array([15.0, 14, 13, 12]),
                                                    weight=np.array([1, 1, 2, 1]), label=["l1", "l2", "l3", "l4"],
                                                    percent_variation=0.04,
                                                    streaming_window=1, accuracy=0.99)
        assert_equal(success, True)
        assert_dict_equal(config, npconfig)

    def test_configure_negative(self):

        # test get_config_template with bad numeric_format
        success, response = self.nano.create_config(numeric_format='int64', feature_count=5, min_val=[-10],
                                                    max_val=[15],
                                                    weight=[1], streaming_window=1, percent_variation=0.05,
                                                    accuracy=0.99)
        assert_equal(success, False)
        assert_equal(response, '606: numericFormat in query should be one of [uint16 float32 int16]')

        # test create_config with bad min_val
        success, response = self.nano.create_config(numeric_format='int64', feature_count=4,
                                                    min_val=-15, max_val=[15.0, 14, 13, 12],
                                                    weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
                                                    percent_variation=0.04,
                                                    streaming_window=1, accuracy=0.99)
        assert_equal(success, False)
        assert_equal(response, 'min_val must be list or numpy array')

        # test create_config with bad max_val
        success, response = self.nano.create_config(numeric_format='int64', feature_count=4,
                                                    min_val=[-15], max_val=10,
                                                    weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
                                                    percent_variation=0.04,
                                                    streaming_window=1, accuracy=0.99)
        assert_equal(success, False)
        assert_equal(response, 'max_val must be list or numpy array')

        # test create_config with bad max_val
        success, response = self.nano.create_config(numeric_format='int64', feature_count=4,
                                                    min_val=[-15], max_val=[10],
                                                    weight=1, label=["l1", "l2", "l3", "l4"],
                                                    percent_variation=0.04,
                                                    streaming_window=1, accuracy=0.99)
        assert_equal(success, False)
        assert_equal(response, 'weight must be list or numpy array')

        # test create_config with bad label
        success, response = self.nano.create_config(numeric_format='int64', feature_count=4,
                                                    min_val=[-15], max_val=[10],
                                                    weight=[1], label="mylabel",
                                                    percent_variation=0.04,
                                                    streaming_window=1, accuracy=0.99)
        assert_equal(success, False)
        assert_equal(response, 'label must be list')


class TestCluster(object):

    def __init__(self):
        try:
            self.nano = bn.NanoHandle(license_file="./.BoonLogic.license")
            assert_equal(self.nano.license_id, 'default')
        except bn.BoonException as be:
            assert_false(False, 'test for default license_id failed')

    def setUp(self):
        clean_nano_instances(self.nano)
        success, response = self.nano.open_nano('instance-1')
        assert_equal(success, True)
        assert_equal(response['instanceID'], 'instance-1')

    def teardown(self):
        self.nano.close_nano()

    def test_load_data(self):
        # create a configuration with single-value min_val, max_val, and weight
        success, config = self.nano.create_config(numeric_format='float32', feature_count=20, min_val=[-10],
                                                  max_val=[15], weight=[1], streaming_window=1,
                                                  percent_variation=0.05, accuracy=0.99)
        # apply the configuration
        success, gen_config = self.nano.configure_nano(config)
        assert_equal(success, True)

        # load data set
        dataFile = 'Data.csv'
        success, response = self.nano.load_file(file=dataFile, file_type='csv', append_data=False)
        assert_equal(success, True)

        # load data set with gzip compression
        dataFile = 'Data.csv.gz'
        success, response = self.nano.load_file(file=dataFile, file_type='csv', gzip=True, append_data=False)
        assert_equal(success, True)

        # load Data.csv and convert to list of floats
        dataBlob = list()
        with open('Data.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                dataBlob = dataBlob + row

        # load data as list
        success, response = self.nano.load_data(data=dataBlob, append_data=False)
        assert_equal(success, True)

        # load data from numpy array
        success, response = self.nano.load_data(data=np.array(dataBlob), append_data=False)
        assert_equal(success, True)

        # run the nano, ask for all results
        success, response = self.nano.run_nano(results='All')
        assert_equal(success, True)
        assert_list_equal(list(response.keys()), ['ID', 'SI', 'RI', 'FI', 'DI'])

        # run the nano, ask for just ID
        success, response = self.nano.run_nano(results='ID')
        assert_equal(success, True)
        assert_list_equal(list(response.keys()), ['ID'])

        # save the nano

    def test_load_data_negative(self):

        # create a configuration with single-value min_val, max_val, and weight
        success, config = self.nano.create_config(numeric_format='float32', feature_count=20, min_val=[-10],
                                                  max_val=[15], weight=[1], streaming_window=1,
                                                  percent_variation=0.05, accuracy=0.99)

        # attempt to load from a file that doesn't exist
        dataFile = 'BadData.csv'
        success, response = self.nano.load_file(file=dataFile, file_type='csv', append_data=False)
        assert_equal(success, False)
        assert_equal(response, 'No such file or directory')

        # attempt to load from a file and specify bad file_type
        dataFile = 'Data.csv'
        success, response = self.nano.load_file(file=dataFile, file_type='cbs', append_data=False)
        assert_equal(success, False)
        assert_equal(response, 'file_type must be "csv", "csv-c", "raw" or "raw-n"')


if __name__ == '__main__':
    myargv = ['nosetests', '--verbosity=2']
    nose.run(defaultTest=__name__ + ':TestManagement', argv=myargv)
    nose.run(defaultTest=__name__ + ':TestResults', argv=myargv)
    nose.run(defaultTest=__name__ + ':TestConfigure', argv=myargv)
    # nose.run(defaultTest=__name__ + ':TestCluster', argv=myargv)
