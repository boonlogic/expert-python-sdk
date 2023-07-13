import sys

sys.path.append('..')

import boonnano as bn
import csv
import os
import numpy as np
import pytest
from boonnano import BoonException, LicenseProfile
from expert_secrets import get_secrets


def create_nano_client():
    boon_license_file = os.environ.get('BOON_TEST_LICENSE_FILE', None)
    boon_license_id = os.environ.get('BOON_TEST_LICENSE_ID', None)
    assert boon_license_id is not None, 'BOON_TEST_LICENSE_ID is missing in test environment'

    # purge environment variables
    for key in Test1ProfileManagement.saved_env.keys():
        if key in os.environ:
            del os.environ[key]

    if boon_license_file is not None:
        # load license profile using a local license file
        nano_client = bn.ExpertClient.from_license_file(license_id=boon_license_id, license_file=boon_license_file)
    else:
        # load license profile from secrets manager
        secret_dict = get_secrets()
        profile = secret_dict.get(boon_license_id, None)
        nano_client = bn.ExpertClient.from_dict(profile_dict=profile)

    return nano_client


def clean_nano_instances(nano=None):
    # clean out nano instances
    if nano is None:
        nano = create_nano_client()
    nano_list = nano.nano_list()
    for nano_inst in nano_list:
        nano.open_nano(nano_inst['instanceID'])
        nano.close_nano(nano_inst['instanceID'])


class Test1ProfileManagement:
    # class variable to saved license file name from environment
    saved_env = {
        'BOON_LICENSE_FILE': None,
        'BOON_LICENSE_ID': None,
        'BOON_SSL_CERT': None,
        'BOON_SSL_VERIFY': None,
        'BOON_TIMEOUT': None
    }

    @staticmethod
    def clear_environment():
        for key in Test1ProfileManagement.saved_env:
            if key in os.environ:
                Test1ProfileManagement.saved_env[key] = os.environ.get(key, None)
                del os.environ[key]

    @staticmethod
    def restore_environment():
        for key, value in Test1ProfileManagement.saved_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

    @staticmethod
    def setup_method(self):
        Test1ProfileManagement.clear_environment()

    @staticmethod
    def teardown_method(self):
        Test1ProfileManagement.restore_environment()

    def test_01_base_init(self):
        # specify server, api_key and api_tenant
        nano = bn.ExpertClient(
            profile=LicenseProfile(server='http://imtheexpertconsole.boonlogic.com', api_key="my-key",
                                   api_tenant="my-tenant"))
        assert nano.api_key == "my-key"
        assert nano.api_tenant == "my-tenant"
        assert nano.server == "http://imtheexpertconsole.boonlogic.com"
        assert nano.proxy_server is None
        assert nano.ssl_cert is None
        assert nano.ssl_verify is True
        assert nano.timeout == 300
        assert nano.url == 'http://imtheexpertconsole.boonlogic.com/expert/v3'

        # specify server, proxy_server, api_key and api_tenant
        nano = bn.ExpertClient(
            profile=LicenseProfile(server='http://imtheexpertconsole.boonlogic.com', api_key="my-key",
                                   api_tenant="my-tenant", proxy_server="http://lilproxy"))
        assert nano.api_key == "my-key"
        assert nano.api_tenant == "my-tenant"
        assert nano.server == "http://imtheexpertconsole.boonlogic.com"
        assert nano.proxy_server == "http://lilproxy"
        assert nano.ssl_cert is None
        assert nano.ssl_verify is True
        assert nano.timeout == 300
        assert nano.url == 'http://imtheexpertconsole.boonlogic.com/expert/v3'

        # specify cert, verify and timeout (set through environment)
        os.environ['BOON_SSL_CERT'] = "/home/certs/major-cert"
        os.environ['BOON_SSL_VERIFY'] = "false"
        os.environ['BOON_TIMEOUT'] = "150"
        nano = bn.ExpertClient(
            profile=LicenseProfile(server='http://imtheexpertconsole.boonlogic.com', api_key="my-key",
                                   api_tenant="my-tenant", proxy_server="http://lilproxy"))
        assert nano.api_key == "my-key"
        assert nano.api_tenant == "my-tenant"
        assert nano.server == "http://imtheexpertconsole.boonlogic.com"
        assert nano.proxy_server == "http://lilproxy"
        assert nano.ssl_cert == "/home/certs/major-cert"
        assert nano.ssl_verify is False
        assert nano.timeout == 150
        assert nano.url == 'http://imtheexpertconsole.boonlogic.com/expert/v3'

    def test_02_base_init_negative(self):
        # missing api_key
        with pytest.raises(BoonException) as e:
            bn.ExpertClient(
                profile=LicenseProfile(server='http://imtheexpertconsole.boonlogic.com', api_tenant="my-tenant"))
        assert e.typename == 'BoonException'
        assert e.value.status_code == 400
        assert e.value.message == 'api-key not specified'

        # missing api_tenant
        with pytest.raises(BoonException) as e:
            bn.ExpertClient(profile=LicenseProfile(server='http://imtheexpertconsole.boonlogic.com', api_key="my-key"))
        assert e.typename == 'BoonException'
        assert e.value.status_code == 400
        assert e.value.message == 'api-tenant not specified'

        # missing server
        with pytest.raises(BoonException) as e:
            bn.ExpertClient(profile=LicenseProfile(api_key="my-key", api_tenant="my-tenant"))
        assert e.typename == 'BoonException'
        assert e.value.status_code == 400
        assert e.value.message == 'server not specified'

    def test_03_from_license_file(self):
        # Note: a running server is not required for nano_handle tests

        # successful nano-handle created using license_file and license_id
        try:
            nano = bn.ExpertClient.from_license_file(license_file="./.BoonLogic.license", license_id='default')
            assert nano.api_key == "no-key"
            assert nano.api_tenant == "no-tenant"
            assert nano.server == "http://localhost:5007"
        except BoonException as be:
            assert False

        # successful nano-handle created using license_file and default license_id
        try:
            nano = bn.ExpertClient.from_license_file(license_file="./.BoonLogic.license")
            assert nano.api_key == "no-key"
            assert nano.api_tenant == "no-tenant"
            assert nano.server == "http://localhost:5007"
        except BoonException as be:
            assert False

        # successful nano-handle created using non default license_id
        try:
            nano = bn.ExpertClient.from_license_file(license_file=".BoonLogic.license", license_id='sample-license')
            assert nano.api_key == 'sample-key'
            assert nano.api_tenant == 'sample-tenant'
            assert nano.server == 'http://sample.host:9898'
        except BoonException as be:
            assert False

        # successful nano-handle created using environment
        try:
            os.environ['BOON_LICENSE_FILE'] = './.BoonLogic.license'
            os.environ['BOON_LICENSE_ID'] = 'sample-license'
            nano = bn.ExpertClient.from_license_file()
            assert nano.api_key == "sample-key"
            assert nano.api_tenant == "sample-tenant"
            assert nano.server == "http://sample.host:9898"
        except BoonException as be:
            assert False

    def test_04_from_license_file_negative(self):
        # Note: a running server is not required for nano_handle tests

        # license_file not found
        with pytest.raises(BoonException) as e:
            bn.ExpertClient.from_license_file(license_file=".BalloonLogic.license", license_id='sample-license')
        assert e.typename == 'BoonException'
        assert e.value.status_code == 404
        assert e.value.message == 'license_file ".BalloonLogic.license" not found'

        # license_id not found
        with pytest.raises(BoonException) as e:
            bn.ExpertClient.from_license_file(license_file=".BoonLogic.license", license_id='bad-license-id')
        assert e.typename == 'BoonException'
        assert e.value.status_code == 404
        assert e.value.message == 'license_id "bad-license-id" not found in license file .BoonLogic.license'

        # badly formatted json
        with pytest.raises(BoonException) as e:
            bn.ExpertClient.from_license_file(license_file="badformat.BoonLogic.license", license_id='sample-license')
        assert e.typename == 'BoonException'
        assert e.value.status_code == 400
        assert e.value.message == "JSON formatting error in license file: badformat.BoonLogic.license, line: 7, col: 5, message:Expecting ',' delimiter"

        # create ExpertClient with missing api-key
        with pytest.raises(BoonException) as e:
            bn.ExpertClient.from_license_file(license_file="no-api-key.BoonLogic.license")
        assert e.typename == 'BoonException'
        assert e.value.status_code == 400
        assert e.value.message == 'api-key not specified'

        # create ExpertClient with missing api-tenant
        with pytest.raises(BoonException) as e:
            bn.ExpertClient.from_license_file(license_file="no-api-tenant.BoonLogic.license")
        assert e.typename == 'BoonException'
        assert e.value.status_code == 400
        assert e.value.message == 'api-tenant not specified'

        # create ExpertClient with missing server
        with pytest.raises(BoonException) as e:
            bn.ExpertClient.from_license_file(license_file="no-server.BoonLogic.license")
        assert e.typename == 'BoonException'
        assert e.value.status_code == 400
        assert e.value.message == 'server not specified'

    def test_05_from_dict(self):
        # specify server, api_key and api_tenant
        profile_dict = {
            "server": "http://imtheexpertconsole.boonlogic.com",
            "api-key": "my-key",
            "api-tenant": "my-tenant",
            "proxy-server": None
        }
        nano = bn.ExpertClient.from_dict(profile_dict=profile_dict)
        assert nano.api_key == "my-key"
        assert nano.api_tenant == "my-tenant"
        assert nano.server == "http://imtheexpertconsole.boonlogic.com"
        assert nano.proxy_server is None
        assert nano.ssl_cert is None
        assert nano.ssl_verify is True
        assert nano.timeout == 300
        assert nano.url == 'http://imtheexpertconsole.boonlogic.com/expert/v3'

        # specify server, proxy_server, api_key and api_tenant
        profile_dict = {
            "server": "http://imtheexpertconsole.boonlogic.com",
            "api-key": "my-key",
            "api-tenant": "my-tenant",
            "proxy-server": "http://lilproxy"
        }
        nano = bn.ExpertClient.from_dict(profile_dict=profile_dict)
        assert nano.api_key == "my-key"
        assert nano.api_tenant == "my-tenant"
        assert nano.server == "http://imtheexpertconsole.boonlogic.com"
        assert nano.proxy_server == "http://lilproxy"
        assert nano.ssl_cert is None
        assert nano.ssl_verify is True
        assert nano.timeout == 300
        assert nano.url == 'http://imtheexpertconsole.boonlogic.com/expert/v3'

        # specify cert, verify and timeout (set through environment)
        os.environ['BOON_SSL_CERT'] = "/home/certs/major-cert"
        os.environ['BOON_SSL_VERIFY'] = "false"
        os.environ['BOON_TIMEOUT'] = "150"
        profile_dict = {
            "server": "http://imtheexpertconsole.boonlogic.com",
            "api-key": "my-key",
            "api-tenant": "my-tenant",
            "proxy-server": "http://lilproxy"
        }
        nano = bn.ExpertClient.from_dict(profile_dict=profile_dict)
        assert nano.api_key == "my-key"
        assert nano.api_tenant == "my-tenant"
        assert nano.server == "http://imtheexpertconsole.boonlogic.com"
        assert nano.proxy_server == "http://lilproxy"
        assert nano.ssl_cert == "/home/certs/major-cert"
        assert nano.ssl_verify is False
        assert nano.timeout == 150
        assert nano.url == 'http://imtheexpertconsole.boonlogic.com/expert/v3'

    def test_06_from_dict_negative(self):
        pass


class Test2InstanceManagement:

    @staticmethod
    def setup_method(self):
        clean_nano_instances()

    @staticmethod
    def teardown_method(self):
        clean_nano_instances()

    def test_01_open_close(self):

        # Note: a running server is required for open_close tests

        # allocate four nano handles and open an instance for each
        nano_dict = dict()
        try:
            for cnt in range(1, 5):
                nano_key = 'nano-' + str(cnt)
                nano_inst = 'nano-instance-' + str(cnt)
                nano_dict[nano_key] = create_nano_client()
                response = nano_dict[nano_key].open_nano(nano_inst)
                assert response['instanceID'] == nano_inst
        except BoonException as be:
            assert False

        # create one more ExpertClient
        try:
            nano = create_nano_client()
        except BoonException as be:
            assert False

        # close an instance that doesn't exist, this involves creating two nano handles and point them at the
        # same instance.  closing the first should succeed, the second should fail
        clean_nano_instances(nano)

        try:
            nano1 = create_nano_client()
            nano2 = create_nano_client()
        except BoonException as be:
            assert False

        instance = 'instance-open-close'
        response = nano1.open_nano(instance)
        assert response['instanceID'] == instance
        response = nano2.open_nano(instance)
        assert response['instanceID'] == instance

        response1 = nano1.get_nano_instance(instance)
        assert instance == response1['instanceID']
        assert response == response1

        # should succeed
        nano1.close_nano(instance)

        # should fail
        with pytest.raises(BoonException) as e:
            nano2.close_nano(instance)
        assert e.value.message == f'Nano instance identifier {instance} is not an allocated instance.'

    def test_02_open_close_negative(self):
        # Note: a running server is required for open_close_negative tests

        instance = 'non-existant'
        nano = create_nano_client()
        with pytest.raises(BoonException) as e:
            _ = nano.get_nano_instance(instance)
        assert e.value.message == f'Nano instance identifier {instance} is not an allocated instance.'


class Test3Version:

    @staticmethod
    def setup_method(self):
        clean_nano_instances()

    @staticmethod
    def teardown_method(self):
        clean_nano_instances()

    def test_01_get_version(self):
        nano = create_nano_client()
        response = nano.get_version()
        assert 'nano-secure' in response
        assert 'builder' in response
        assert 'expert-api' in response
        assert 'expert-common' in response


class Test4Configure:

    @staticmethod
    def setup_method(self):
        clean_nano_instances()

    @staticmethod
    def teardown_method(self):
        clean_nano_instances()

    def test_01_configure(self):

        instance = 'instance-configure'
        nano = create_nano_client()
        _ = nano.open_nano(instance)

        # create a configuration with single-value min_val, max_val, and weight
        config = nano.create_config(numeric_format='float32', cluster_mode='streaming',
                                    feature_count=5, min_val=-10, max_val=15, weight=1,
                                    label=[f"feature-{i}" for i in range(5)],
                                    streaming_window=1, percent_variation=0.05, accuracy=0.99,
                                    autotune_pv=False, autotune_range=False, autotune_by_feature=False,
                                    autotune_max_clusters=2000, exclusions=[1],
                                    streaming_autotune=False, streaming_buffer=5000, anomaly_history_window=1000,
                                    learning_numerator=1, learning_denominator=1000, learning_max_clusters=2000,
                                    learning_samples=50000)
        assert config['numericFormat'] == 'float32'
        assert config['accuracy'] == 0.99
        assert config['streamingWindowSize'] == 1
        assert config['percentVariation'] == 0.05
        assert len(config['features']) == 5

        # apply the configuration
        gen_config = nano.configure_nano(instance, config=config)
        assert config == gen_config

        # query the configuration, should match the above response
        get_response = nano.get_config(instance)
        assert config == get_response

        # use the configuration template generator to create a per feature template
        config = nano.create_config(feature_count=4, numeric_format='int16',
                                    min_val=[-15, -14, -13, -12], max_val=[15.0, 14, 13, 12],
                                    weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
                                    percent_variation=0.04,
                                    streaming_window=1, accuracy=0.99)
        expected_features = [{"minVal": -15, "maxVal": 15, "weight": 1, "label": "l1"},
                             {"minVal": -14, "maxVal": 14, "weight": 1, "label": "l2"},
                             {"minVal": -13, "maxVal": 13, "weight": 2, "label": "l3"},
                             {"minVal": -12, "maxVal": 12, "weight": 1, "label": "l4"}
                             ]
        assert config['accuracy'] == 0.99
        assert config['features'] == expected_features
        assert config['numericFormat'] == 'int16'
        assert config['percentVariation'] == 0.04
        assert config['accuracy'] == 0.99
        assert config['streamingWindowSize'] == 1

        # create the same configuration using numpy arrays
        npconfig = nano.create_config(feature_count=4, numeric_format='int16',
                                      min_val=np.array([-15, -14, -13, -12]),
                                      max_val=np.array([15.0, 14, 13, 12]),
                                      weight=np.array([1, 1, 2, 1]), label=["l1", "l2", "l3", "l4"],
                                      percent_variation=0.04,
                                      streaming_window=1, accuracy=0.99)
        assert config == npconfig


    def test_02_configure_negative(self):
        instance = 'instance-configure'
        nano = create_nano_client()
        _ = nano.open_nano(instance)
        # test get_config_template with bad numeric_format
        with pytest.raises(BoonException) as e:
            _ = nano.configure_nano(instance, numeric_format='int64', feature_count=5, min_val=-10,
                                                max_val=15,
                                                weight=1, streaming_window=1, percent_variation=0.05,
                                                accuracy=0.99)
        assert e.value.message == 'numericFormat in body should be one of [int16 float32 uint16]'

        # test create_config with bad min_val format
        with pytest.raises(BoonException) as e:
            _ = nano.create_config(numeric_format='int16', feature_count=4,
                                               min_val="5", max_val=[15.0, 14, 13, 12],
                                               weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
                                               percent_variation=0.04,
                                               streaming_window=1, accuracy=0.99)
        assert e.value.message == "min_val, max_val and weight must be list or numpy array"

        # test create_config with bad min_val
        with pytest.raises(BoonException) as e:
            _ = nano.create_config(numeric_format='int16', feature_count=4,
                                               min_val=[-15, -15], max_val=[15.0, 14, 13, 12],
                                               weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
                                               percent_variation=0.04,
                                               streaming_window=1, accuracy=0.99)
        assert e.value.message == 'parameters must be lists of the same length'

        # test create_config with bad max_val
        with pytest.raises(BoonException) as e:
            _ = nano.create_config(numeric_format='int16', feature_count=4,
                                               min_val=-15, max_val=[10, 10],
                                               weight=[1, 1, 2, 1], label=["l1", "l2", "l3", "l4"],
                                               percent_variation=0.04,
                                               streaming_window=1, accuracy=0.99)
            assert _ == 'parameters must be lists of the same length'

        # test create_config with bad weight
        with pytest.raises(BoonException) as e:
            _ = nano.create_config(numeric_format='int16', feature_count=4,
                                               min_val=-15, max_val=10,
                                               weight=[1, 1], label=["l1", "l2", "l3", "l4"],
                                               percent_variation=0.04,
                                               streaming_window=1, accuracy=0.99)
        assert e.value.message == 'parameters must be lists of the same length'

        # test create_config with bad label
        with pytest.raises(BoonException) as e:
            _ = nano.create_config(numeric_format='int16', feature_count=4,
                                               min_val=-15, max_val=10,
                                               weight=1, label="mylabel",
                                               percent_variation=0.04,
                                               streaming_window=1, accuracy=0.99)
        assert e.value.message == 'label must be list'

        # test create_config with bad label
        with pytest.raises(BoonException) as e:
            _ = nano.create_config(numeric_format='int16', feature_count=4,
                                               min_val=-15, max_val=10,
                                               weight=1, label=["mylabel"],
                                               percent_variation=0.04,
                                               streaming_window=1, accuracy=0.99)
        assert e.value.message == "label must be the same length as other parameters"

class Test4Cluster:
    @staticmethod
    def setup_method(self):
        clean_nano_instances()

    @staticmethod
    def teardown_method(self):
        clean_nano_instances()

    def test_01_load_data(self):

        instance = 'instance-configure'
        nano = create_nano_client()
        _ = nano.open_nano(instance)

        # apply the configuration
        config = nano.configure_nano(instance, feature_count=20, numeric_format='float32', min_val=-10,
                                          max_val=15, weight=1, streaming_window=1,
                                          percent_variation=0.05, accuracy=0.99)
        # load data set
        dataFile = 'Data.csv'
        nano.load_file(instance, file=dataFile, file_type='csv', append_data=False)

        # load data set with gzip compression
        dataFile = 'Data.csv.gz'
        nano.load_file(instance, file=dataFile, file_type='csv', gzip=True, append_data=False)

        # load Data.csv and convert to list of floats
        dataBlob = []
        with open('Data.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                dataBlob = dataBlob + row

        # load data as list
        nano.load_data(instance, data=dataBlob, append_data=False)

        # load data from numpy array
        nano.load_data(instance, data=np.array(dataBlob), append_data=False)

        # load part of the data
        length = (int)((int)(len(dataBlob) / 20) / 2)
        nano.load_data(instance, data=dataBlob[:length * 20], append_data=False)

        # run the nano, ask for all results
        response = nano.run_nano(instance, results='All')
        assert sorted(list(response.keys())) == sorted(['AD', 'AH', 'AM', 'AW', 'DI', 'FI', 'ID', 'NI', 'NS', 'NW', 'OM', 'PI', 'RI', 'SI'])

        # ask again for the the nano results
        response2 = nano.get_nano_results(instance, results='All')
        assert response == response2

        # run the nano, ask for just ID but the buffer has been cleared so it fails
        with pytest.raises(BoonException) as e:
            nano.run_nano(instance, results='ID')
        assert 'There is no data to cluster' in e.value.message

        # ask again for the the nano results
        response2 = nano.get_nano_results(instance, results='ID')
        assert response['ID'] == response2['ID']

        # get root cause for a pattern before root cause is turned on (still works)
        response = nano.get_root_cause(instance, pattern_list=[
            [1] * len(config['features']) * config['streamingWindowSize']])
        assert len(response[0]) == 20

        # get root cause for a pattern with only one pattern
        response = nano.get_root_cause(instance, pattern_list=(
                    [1] * len(config['features']) * config['streamingWindowSize']))
        assert len(response[0]) == 20

        # fetch the buffer status
        response = nano.get_buffer_status(instance)
        assert len(response) == 3

        # fetch additional nano status 'All'
        response = nano.get_nano_status(instance, results='All')
        assert sorted(list(response.keys())) == sorted(['PCA', 'clusterGrowth', 'clusterSizes', 'anomalyIndexes',
                                                        'anomalyThreshold', 'frequencyIndexes', 'distanceIndexes',
                                                        'totalInferences', 'numClusters', 'clusterDistances'])

        # fetch additional nano status 'numClusters'
        response = nano.get_nano_status(instance, results='numClusters')
        assert list(response.keys()) == ['numClusters']

        # get learning status
        response2 = nano.is_learning_enabled(instance)
        assert response2

        # turn off learning
        response2 = nano.set_learning_enabled(instance, False)
        assert not response2

        # get root cause analysis
        response2 = nano.is_root_cause_enabled(instance)
        assert not response2

        # turn on root cause analysis
        response2 = nano.set_root_cause_enabled(instance, True)
        assert response2

        # get clipping detection status
        response2 = nano.is_clipping_detection_enabled(instance)
        assert response2

        # turn on root cause analysis
        response2 = nano.set_clipping_detection_enabled(instance, True)
        assert response2

        # load second half of data
        length = (int)((int)(len(dataBlob) / 20) / 2)
        nano.load_data(instance, data=dataBlob[length * 20:], append_data=False)

        # run the nano
        response2 = nano.run_nano(instance, results=None)

        # get root cause from IDs
        root_cause = nano.get_root_cause(instance, id_list=[1])

        # ask for the nano status result, 'numClusters'
        response2 = nano.get_nano_status(instance, results='numClusters')
        assert response['numClusters'] == response2['numClusters']

        # prune ids
        response1 = nano.prune_ids(instance, id_list=1)
        assert response['numClusters'] > response1['numClustersRemaining']

        # test autotune
        config = nano.configure_nano(instance, feature_count=20, numeric_format='float32', min_val=-10,
                                          max_val=15, weight=1, streaming_window=1,
                                          percent_variation=0.05, accuracy=0.99,
                                          autotune_pv=True, autotune_range=True, autotune_by_feature=False)
        nano.load_data(instance, data=dataBlob[:length * 20], append_data=False)
        nano.autotune_config(instance)

        # test autotune but exclude features 1 and 3
        config = nano.configure_nano(instance, feature_count=20, numeric_format='float32', min_val=-10,
                                          max_val=15, weight=1, streaming_window=1,
                                          percent_variation=0.05, accuracy=0.99,
                                          autotune_pv=True, autotune_range=True, autotune_by_feature=False,
                                          exclusions=[1, 3])
        nano.load_data(instance, data=dataBlob[:length * 20], append_data=False)
        nano.autotune_config(instance)

        response = nano.get_autotune_array(instance)
        assert len(response) == 2

        # do a quick negative test where exclusions is not a list
        with pytest.raises(BoonException) as e:
            nano.configure_nano(instance, feature_count=20, numeric_format='float32', min_val=-10,
                                     max_val=15, weight=1, streaming_window=1,
                                     percent_variation=0.05, accuracy=0.99,
                                     autotune_pv=True, autotune_range=True, autotune_by_feature=False,
                                     exclusions=10)
        assert e.value.message == 'exclusions must be a list'

        # save the configuration
        nano.save_nano(instance, './saved-nano-1')

        # restore the configuration
        _ = nano.restore_nano(instance, 'saved-nano-1')

        # attempt to restore a corrupt saved nano
        with pytest.raises(BoonException) as e:
            _ = nano.restore_nano(instance, 'bad-magic.tgz')
        assert e.value.message == 'corrupt file bad-magic.tgz'

    def test_02_load_data_negative(self):

        instance = 'instance-configure'
        nano = create_nano_client()
        response = nano.open_nano(instance)

        # create a configuration with single-value min_val, max_val, and weight
        config = nano.create_config(numeric_format='float32', feature_count=20, min_val=-10,
                                         max_val=15, weight=1, streaming_window=1,
                                         percent_variation=0.05, accuracy=0.99)

        # attempt to load from a file for a nano that is not configured
        dataFile = 'Data.csv'
        with pytest.raises(BoonException) as e:
            nano.load_file(instance, file=dataFile, file_type='csv', append_data=False)
        assert e.value.message == 'nano instance is not configured'

        # get root cause before configured
        with pytest.raises(BoonException) as e:
            _ = nano.get_root_cause(instance, id_list=[1, 1])
        assert e.value.message == 'The clustering parameters have not been initialized'

        # apply the configuration
        gen_config = nano.configure_nano(instance, config=config)

        # attempt to load data with a non-existent file
        dataFile = 'BadData.csv'
        with pytest.raises(BoonException) as e:
            nano.load_file(instance_id=instance, file=dataFile, file_type='csv', append_data=False)
        assert e.value.message == 'No such file or directory'

        # attempt to load from a file and specify bad file_type
        dataFile = 'Data.csv'
        with pytest.raises(BoonException) as e:
            nano.load_file(instance_id=instance, file=dataFile, file_type='cbs', append_data=False)
        assert e.value.message == 'file_type must be "csv", "csv-c", "raw" or "raw-n"'

        # run a nano with bad results specifier
        with pytest.raises(BoonException) as e:
            _ = nano.run_nano(instance, results='NA')

        # no ids given to prune
        with pytest.raises(BoonException) as e:
            _ = nano.prune_ids(instance)
        assert e.value.message == "Must specify cluster IDs to analyze"

        # set learning to a non boolean
        with pytest.raises(BoonException) as e:
            _ = nano.set_learning_enabled(instance, status=None)

        # set root cause status to a non boolean
        with pytest.raises(BoonException) as e:
            _ = nano.set_root_cause_enabled(instance, status=None)

        # set clipping status to a non boolean
        with pytest.raises(BoonException) as e:
            _ = nano.set_clipping_detection_enabled(instance, status=None)

        # get nano results with bad results specifier
        with pytest.raises(BoonException) as e:
            _ = nano.get_nano_results(instance, results='NA')

        # get nano status with bad results specifier
        with pytest.raises(BoonException) as e:
            _ = nano.get_nano_status(instance, results='NA')

        # save the configuration with a bad pathname
        with pytest.raises(BoonException) as e:
            nano.save_nano(instance, '/badpath/junk/bad-saved-nano-1')
        assert 'No such file or directory' in e.value.message


class Test5StreamingCluster:

    @staticmethod
    def setup_method(self):
        clean_nano_instances()

    @staticmethod
    def teardown_method(self):
        clean_nano_instances()

    def test_01_run_nano_streaming(self):
        instance = 'instance-configure'
        nano = create_nano_client()
        _ = nano.open_nano(instance)

        # create a configuration with single-value min_val, max_val, and weight
        config = nano.create_config(numeric_format='float32', cluster_mode='streaming',
                                         feature_count=20, min_val=-10,
                                         max_val=15, weight=1, streaming_window=1,
                                         percent_variation=0.05, accuracy=0.99)

        # apply the configuration
        gen_config = nano.configure_nano(instance, config=config)

        # load Data.csv and convert to list of floats
        dataBlob = list()
        with open('Data.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                dataBlob = dataBlob + row

        # write the data to the streaming nano, with results == All
        response = nano.run_streaming_nano(instance, data=dataBlob, results='All')
        assert len(response) == 14

        # write the data to the streaming nano, with results == 'SI'
        response = nano.run_streaming_nano(instance, data=dataBlob, results='SI')
        assert 'SI' in response

    def test_02_run_nano_streaming_negative(self):
        instance = 'instance-configure'
        nano = create_nano_client()
        _ = nano.open_nano(instance)

        # create a configuration with single-value min_val, max_val, and weight
        config = nano.create_config(feature_count=20, numeric_format='float32', min_val=-10,
                                         max_val=15, weight=1, streaming_window=1,
                                         percent_variation=0.05, accuracy=0.99)

        # apply the configuration
        gen_config = nano.configure_nano(instance, config=config)

        # load Data.csv and convert to list of floats
        dataBlob = list()
        with open('Data.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                dataBlob = dataBlob + row

        # run streaming nano with bad results specifier
        with pytest.raises(BoonException) as e:
            _ = nano.run_streaming_nano(instance, data=dataBlob, results='NA')
        assert 'formData should be one of' in e.value.message


class Test6Rest:

    @staticmethod
    def setup_method(self):
        clean_nano_instances()

    @staticmethod
    def teardown_method(self):
        clean_nano_instances()

    def test_01_negative(self):

        instance = 'instance-configure'
        nano = create_nano_client()
        _ = nano.open_nano(instance)

        # simple_get with bad server
        nano.url = 'http://localhost-bad:5007/expert/v3'
        with pytest.raises(BoonException) as e:
            nano.get_version()
        assert e.value.message == 'server does not exist'
