import boonnano as bn
import sys

import nose
from nose.tools import assert_equal
from nose.tools import assert_list_equal
from nose.tools import assert_false
import os
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
        # set a configuration
        success, response = self.nano.configure_nano(numeric_format='float32', feature_count=5, min=-10, max=15,
                                                     weight=1, labels="", streaming_window=1,
                                                     percent_variation=0.05,
                                                     accuracy=0.99)
        assert_equal(success, True)
        assert_equal(response['numericFormat'], 'float32')
        assert_equal(response['accuracy'], 0.99)
        assert_equal(response['streamingWindowSize'], 1)
        assert_equal(response['percentVariation'], 0.05)
        assert_equal(len(response['features']), 5)

        # query the configuration, should match the above response
        success, get_response = self.nano.get_config()
        assert_equal(success, True)
        assert_equal(response, get_response)

        success, gen_response = self.nano.get_config_template(numeric_format='float32', feature_count=5, min=[-10],
                                                              max=[15], weight=[1], labels=None, streaming_window=1,
                                                              percent_variation=0.05,
                                                              accuracy=0.99)
        assert_equal(success, True)
        assert_equal(response, gen_response)

        # use the configuration template generator to create a per feature template
        success, gen_response = self.nano.get_config_template(numeric_format='int16', feature_count=4,
                                                              min=[-15, -14, -13, -12], max=[15.0, 14, 13, 12],
                                                              weight=[1, 1, 2, 1], labels=["l1", "l2", "l3", "l4"],
                                                              percent_variation=0.04,
                                                              streaming_window=1, accuracy=0.99)
        expected_features = [{"minVal": -15, "maxVal": 15, "weight": 1, "label": "l1"},
                             {"minVal": -14, "maxVal": 14, "weight": 1, "label": "l2"},
                             {"minVal": -13, "maxVal": 13, "weight": 2, "label": "l3"},
                             {"minVal": -12, "maxVal": 12, "weight": 1, "label": "l4"}
                             ]
        assert_equal(success, True)
        assert_equal(gen_response['accuracy'], 0.99)
        assert_equal(gen_response['features'], expected_features)
        assert_equal(gen_response['numericFormat'], 'int16')
        assert_equal(gen_response['percentVariation'], 0.04)
        assert_equal(gen_response['accuracy'], 0.99)
        assert_equal(gen_response['streamingWindowSize'], 1)


class TestCluster(object):

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""


if __name__ == '__main__':
    myargv = ['nosetests', '--verbosity=2']
    nose.run(defaultTest=__name__ + ':TestManagement', argv=myargv)
    nose.run(defaultTest=__name__ + ':TestResults', argv=myargv)
    nose.run(defaultTest=__name__ + ':TestConfigure', argv=myargv)
    # nose.run(defaultTest=__name__ + ':TestCluster', argv=myargv)
