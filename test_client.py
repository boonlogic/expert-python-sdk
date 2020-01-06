import boonnano as bn
import json

import nose
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises


class test_management(object):

    # these tests are verfiying the open and close functionality and
    # don't use the setUp/teardown methods
    def __init__(self):
        self.nano = None

    def test_open_close(self):
        success, nano = bn.open_nano('sample-instance', 'sample-user')
        assert_equal(success, True)
        nano.close_nano()

    def test_nano_list(self):
        success, nano = bn.open_nano('sample-instance', 'sample-user')
        assert_equal(success, True)
        success, response = nano.nano_list()
        assert_equal(success, True)
        assert len(response) > 0
        nano.close_nano()


class test_results(object):

    def __init__(self):
        self.nano = None

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        success, self.nano = bn.open_nano('sample-instance', 'sample-user')
        assert_equal(success, True)

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        self.nano.close_nano()

    def test_get_version(self):
        success, response = self.nano.get_version()
        assert_equal(success, True)
        assert_equal(list(response.keys()), ['api-version', 'boon-nano', 'expert-api', 'expert-common'])


class test_configure(object):

    def __init__(self):
        self.nano = None

    def setUp(self):
        """This method is run once before _each_ test method is executed"""
        success, self.nano = bn.open_nano('sample-instance', 'sample-user')
        assert_equal(success, True)

    def teardown(self):
        """This method is run once after _each_ test method is executed"""
        self.nano.close_nano()

    def test_configure(self):
        # set a configuration
        success, response = self.nano.configure_nano(numeric_format='float32', feature_count=20, min=-10, max=15,
                                                     percent_variation=0.05)
        assert_equal(success, True)
        assert_equal(response['numericFormat'], 'float32')
        assert_equal(response['accuracy'], 0.99)
        assert_equal(response['streamingWindowSize'], 1)
        assert_equal(response['percentVariation'], 0.05)
        assert_equal(len(response['features']), 20)

        # query the configuration, should match the above response
        success, get_response = self.nano.get_config()
        assert_equal(success, True)
        assert_equal(response, get_response)

        # generate a configuration, it shoulld match the others
        gen_response = bn.generate_config(numeric_format='float32', feature_count=20, min=-10, max=15,
                                          percent_variation=0.05)
        assert_equal(success, True)
        assert_equal(response, gen_response)


class test_cluster(object):

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""


if __name__ == '__main__':
    nose.run(defaultTest=__name__ + ':test_management')
    nose.run(defaultTest=__name__ + ':test_configure')
    nose.run(defaultTest=__name__ + ':test_results')
    nose.run(defaultTest=__name__ + ':test_cluster')
