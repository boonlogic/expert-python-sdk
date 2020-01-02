import boonnano as bn
import json

import nose
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises
from nose.tools import raises

class test_management(object):

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

    def setUp(self):
        """This method is run once before _each_ test method is executed"""

    def teardown(self):
        """This method is run once after _each_ test method is executed"""

    def test_open(self):
        assert_equal(True, True)

    def test_close(self):
        assert_equal(True, True)

    def test_get_version(self):
        global global_nano
        success,response=global_nano.get_version()
        assert_equal(success, True)
        assert_equal(list(response.keys()), ['api-version', 'boon-nano', 'expert-api', 'expert-common'])

    def test_nano_list(self):
        global global_nano
        success,response=global_nano.nano_list()
        assert_equal(success, True)
        assert len(response) > 0

class test_results(object):

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

class test_configure(object):

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""

    def test_configure_nano(self):
        global global_nano

        print(global_nano)
  
        # set a configuration
        success,response=global_nano.configure_nano(numeric_format='float',feature_count=20,min=-10,max=15,percent_variation=0.05)
        print(response)
        assert_equal(success, True)
        assert_equal(response['numericFormat'], 'float')
        assert_equal(response['accuracy'], 0.99)
        assert_equal(response['streamingWindowSize'], 1)
        assert_equal(response['percentVariation'], 0.05)
        assert_equal(len(response['features']), 20)

        # query the configuration, should match the above response
        success,get_response=global_nano.get_config()
        assert_equal(success, True)
        assert_equal(response, get_response)

    def test_generate_config(self):
        global global_nano
        # success,response=global_nano.generate_config(numeric_format='float',feature_count=20,min=-10,max=15,percent_variation=0.05)
        #assert_equal(success, True)

    def test_autotune_config(self):
        global global_nano
        # success,response=global_nano.autotune_config()
        #assert_equal(success, True)

    def test_get_config(self):
        global global_nano
        success,response=global_nano.get_config()
        assert_equal(success, True)


class test_cluster(object):

    @classmethod
    def setup_class(klass):
        """This method is run once for each class before any tests are run"""

    @classmethod
    def teardown_class(klass):
        """This method is run once for each class _after_ all tests are run"""


if __name__ == '__main__':

    # use a global nano handlers
    global global_nano
    success,global_nano=bn.open_nano('example','Rod')
    print(global_nano)
    if success != True:
        print("open_nano failed")
        sys.exit(1)

    nose.run(defaultTest = __name__ + ':test_management')
    nose.run(defaultTest = __name__ + ':test_configure')

    global_nano.close_nano()

