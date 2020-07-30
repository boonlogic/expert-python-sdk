from urllib3 import ProxyManager
from urllib3 import PoolManager
from urllib3 import Timeout
from functools import wraps
import json
import os
import tarfile
from .rest import simple_get
from .rest import simple_delete
from .rest import simple_post
from .rest import multipart_post
import numpy as np
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = ['BoonException', 'NanoHandle']


############################
# BoonNano Python API v3 #
############################


class BoonException(Exception):
    def __init__(self, message):
        self.message = message


class NanoHandle:

    def __init__(self, license_id='default', license_file="~/.BoonLogic.license", timeout=120.0):
        """Primary handle for BoonNano Pod instances

        The is the primary handle to manage a nano pod instance

        Args:
            license_id (str): license identifier label found within the .BoonLogic.license configuration file
            license_file (str): path to .BoonLogic license file
            timeout (float): read timeout for http requests

        Environment:
            BOON_LICENSE_FILE: sets license_file path
            BOON_LICENSE_ID: sets license_id
            BOON_API_KEY: overrides the api-key as found in .BoonLogic.license file
            BOON_API_TENANT: overrides the api-tenant as found in .BoonLogic.license file
            BOON_SERVER: overrides the server as found in .BoonLogic.license file
            PROXY_SERVER: overrides the proxy server as found in .BoonLogic.license file

        Example:
            ```python
            try:
                nano = bn.NanoHandle()
            except bn.BoonException as be:
                print(be)
                sys.exit(1)
            ```

        """
        self.license_file = license_file
        self.license_id = None
        self.api_key = None
        self.api_tenant = None
        self.instance = ''
        self.numeric_format = ''

        # when license_id comes in as None, use 'default'
        if license_id is None:
            license_id = 'default'

        license_file_env = os.getenv('BOON_LICENSE_FILE')
        if license_file_env:
            # license file path was specified in environment
            license_file = license_file_env

        license_path = os.path.expanduser(license_file)
        if os.path.exists(license_path):
            try:
                with open(license_path, "r") as json_file:
                    file_data = json.load(json_file)
            except json.JSONDecodeError as e:
                raise BoonException(
                    "json formatting error in .BoonLogic.license file, {}, line: {}, col: {}".format(e.msg, e.lineno,
                                                                                                     e.colno))
        else:
            raise BoonException("file {} does not exist".format(license_path))

        # load the license block, environment gets precedence
        license_env = os.getenv('BOON_LICENSE_ID')
        if license_env:
            # license id was specified through environment
            if license_env in file_data:
                self.license_id = license_env
            else:
                raise BoonException(
                    "BOON_LICENSE_ID value of '{}' not found in .BoonLogic.license file".format(license_env))
        else:
            if license_id in file_data:
                self.license_id = license_id
            else:
                raise BoonException("license_id '{}' not found in .BoonLogic.license file".format(license_id))

        license_block = file_data[self.license_id]

        # load the api-key, environment gets precedence
        self.api_key = os.getenv('BOON_API_KEY')
        if not self.api_key:
            if 'api-key' not in license_block.keys():
                raise BoonException(
                    "'api-key' is missing from configuration, set via BOON_API_KEY or in ~/.BoonLogic.license file")
            self.api_key = license_block['api-key']

        # load the server, environment gets precedence
        self.server = os.getenv('BOON_SERVER')
        if not self.server:
            if 'server' not in license_block.keys():
                raise BoonException(
                    "'server' is missing from configuration, set via BOON_SERVER or in ~/.BoonLogic.license file")
            self.server = license_block['server']

        # load the tenant, environment gets precedence
        self.api_tenant = os.getenv('BOON_TENANT')
        if not self.api_tenant:
            if 'api-tenant' not in license_block.keys():
                raise BoonException(
                    "'api-tenant' is missing from configuration, set via BOON_TENANT or in ~/.BoonLogic.license file")
            self.api_tenant = license_block['api-tenant']

        # load the https proxy (if any)
        self.proxy_server = os.getenv('PROXY_SERVER')
        if not self.proxy_server:
            if 'proxy-server' in license_block.keys():
                self.proxy_server = license_block['proxy-server']

        # set up base url
        self.url = self.server + '/expert/v3/'
        if "http" not in self.server:
            self.url = "http://" + self.url

        # create pool manager
        timeout_inst = Timeout(connect=30.0, read=timeout)
        if self.proxy_server:
            # proxy pool
            self.http = ProxyManager(self.proxy_server, maxsize=10, timeout=timeout_inst)
        else:
            # non-proxy pool
            self.http = PoolManager(timeout=timeout_inst)

    def _is_configured(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if args[0].numeric_format not in ['int16', 'uint16', 'float32']:
                return False, "nano instance is not configured"
            return f(*args, **kwargs)
        return inner

    def open_nano(self, instance_id):
        """Creates or attaches to a nano pod instance

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            boolean: true if successful (instance is created or attached)

            str: None when result is true, error string when result=false

        """
        instance_cmd = self.url + 'nanoInstance/' + instance_id + '?api-tenant=' + self.api_tenant

        success, response = simple_post(self, instance_cmd)
        if not success:
            return False, response

        self.instance = instance_id
        return success, response

    def close_nano(self):
        """Closes the pod instance

        Returns:
            result (boolean):  true if successful (nano pod instance was closed)
            response (str): None when result is true, error string when result=false

        """
        close_cmd = self.url + 'nanoInstance/' + self.instance + '?api-tenant=' + self.api_tenant

        # delete instance
        result, response = simple_delete(self, close_cmd)
        if not result:
            return result, response

        self.http.clear()
        return result, None

    def create_config(self, feature_count, numeric_format, cluster_mode='batch', min_val=0, max_val=1,
                      weight=1, label=None,
                      percent_variation=.05, streaming_window=1, accuracy=.99,
                      autotunePV=True, autotuneRange=True, autotune_by_feature=True, autotune_max_clusters=1000, exclusions=None,
                      streaming_autotune=True, streaming_buffer=10000, learning_numerator=10, learning_denominator=10000, learning_max_clusters=1000, learning_samples=1000000):
        """Generate a configuration template for the given parameters

        A discrete configuration is specified as a list of min, max, weights, and labels

        Args:
            feature_count (int): number of features per vector
            numeric_format (str): numeric type of data (one of "float32", "uint16", or "int16")
            min_val (list): the value that should be considered the minimum value for this feature. This
                can be set to a value larger than the actual min if you want to treat all value less
                than that as the same (for instance, to keep a noise spike from having undue influence
                in the clustering.  a single element list assigns all features with same min_val
            max_val (list): corresponding maximum value, a single element list assigns all features with same max_val
            weight (list): weight for this feature, a single element list assigns all features with same weight
            label (list): list of labels to assign to features
            percent_variation (float): amount of variation allowed within clusters
            streaming_window (integer): number of consecutive vectors treated as one inference (parametric parameter)
            accuracy (float): statistical accuracy of the clusters
            autotunePV (bool): whether to autotune the percent variation
            autotuneRange (bool): whether to autotune the min and max values
            autotune_by_feature (bool): whether to have individually set min and max values for each feature
            autotune_max_clusters (int): max number of clusters allowed
            exclusions (list): features to exclude while autotuning
            streaming_autotune (bool): whether to autotune while in streaming mode
            streaming_buffer (int): number of samples to autotune on
            learning_numerator (int): max number of new clusters learned
            learning_denominator (int): number of samples over which the new clusters are learned
            learning_max_clusters (int): max number of clusters before turning off learning
            learning_samples (int): max number of samples before turning off learning


        Returns:
            result (boolean): true if successful (configuration was successfully created)
            response (dict or str): configuration dictionary when result is true, error string when result is false

        """

        if isinstance(min_val, int) or isinstance(min_val, float):
            min_val = np.array([min_val] * feature_count)
        if isinstance(max_val, int) or isinstance(max_val, float):
            max_val = np.array([max_val] * feature_count)
        if isinstance(weight, int):
            weight = np.array([weight] * feature_count)

        config = {}
        config['clusterMode'] = cluster_mode
        config['numericFormat'] = numeric_format
        config['features'] = []

        if (isinstance(min_val, list) or isinstance(min_val, np.ndarray)) and (isinstance(max_val, list) or isinstance(max_val, np.ndarray)) and (isinstance(weight, list) or isinstance(weight, np.ndarray)):
            if len(min_val) != len(max_val) or len(min_val) != len(weight):
                return False, "parameters must be lists of the same length"

            for min, max, w in zip(min_val, max_val, weight):
                tempDict = {}
                if numeric_format == 'float32':
                    tempDict['minVal'] = float(min)
                    tempDict['maxVal'] = float(max)
                else:
                    tempDict['minVal'] = int(min)
                    tempDict['maxVal'] = int(max)
                tempDict['weight'] = int(w)
                config['features'].append(tempDict)
        else:
            return False, "min_val, max_val and weight must be list or numpy array"

        if isinstance(label, list):
            if len(label) != len(min_val):
                return False, "label must be the same length as other parameters"
            for i, l in enumerate(label):
                config['features'][i]['label'] = l
        elif label:
            return False, "label must be list"

        config['percentVariation'] = percent_variation
        config['streamingWindowSize'] = streaming_window
        config['accuracy'] = accuracy

        config['autoTuning'] = {}
        config['autoTuning']['autoTunePV'] = autotunePV
        config['autoTuning']['autoTuneRange'] = autotuneRange
        config['autoTuning']['autoTuneByFeature'] = autotune_by_feature
        config['autoTuning']['maxClusters'] = autotune_max_clusters
        if isinstance(exclusions, list):
            config['autoTuning']['exclusions'] = ",".join([int(s) for s in exclusions])
        elif exclusions:
            return False, 'exclusions must be a list'

        config['streaming'] = {}
        config['streaming']['enableAutoTuning'] = streaming_autotune
        config['streaming']['samplesToBuffer'] = streaming_buffer
        config['streaming']['learningRateNumerator'] = learning_numerator
        config['streaming']['learningRateDenominator'] = learning_denominator
        config['streaming']['learningMaxClusters'] = learning_max_clusters
        config['streaming']['learningMaxSamples'] = learning_samples

        return config

    def configure_nano(self, feature_count, numeric_format, cluster_mode='batch', min_val=0, max_val=1,
                      weight=1, label=None,
                      percent_variation=.05, streaming_window=1, accuracy=.99,
                      autotunePV=True, autotuneRange=True, autotune_by_feature=True, autotune_max_clusters=1000, exclusions=None,
                      streaming_autotune=True, streaming_buffer=10000, learning_numerator=10, learning_denominator=10000, learning_max_clusters=1000, learning_samples=1000000,
                      config=None):

        """Returns the posted clustering configuration

         Args:
             feature_count (int): number of features per vector
             numeric_format (str): numeric type of data (one of "float32", "uint16", or "int16")
             min: list of minimum values per feature, if specified as a single value, use that on all features
             max: list of maximum values per feature, if specified as a single value, use that on all features
             weight (float): influence each column has on creating a new cluster
             labels (list): name of each feature (if applicable)
             percent_variation (float): amount of variation within each cluster
             streaming_window (integer): number of consecutive vectors treated as one inference (parametric parameter)
             accuracy (float): statistical accuracy of the clusters
             autotunePV (bool): whether to autotune the percent variation
             autotuneRange (bool): whether to autotune the min and max values
             autotune_by_feature (bool): whether to have individually set min and max values for each feature
             autotune_max_clusters (int): max number of clusters allowed
             exclusions (list): features to exclude while autotuning
             streaming_autotune (bool): whether to autotune while in streaming mode
             streaming_buffer (int): number of samples to autotune on
             learning_numerator (int): max number of new clusters learned
             learning_denominator (int): number of samples over which the new clusters are learned
             learning_max_clusters (int): max number of clusters before turning off learning
             learning_samples (int): max number of samples before turning off learning
             config (dict): dictionary of configuration parameters

         Returns:
             result (boolean): true if successful (configuration was successfully loaded into nano pod instance)
             response (dict or str): configuration dictionary when result is true, error string when result is false

         """

        if config is None:
            config = create_config(feature_count, numeric_format, cluster_mode, min_val, max_val, weight, label,
                               percent_variation, streaming_window, accuracy,
                               autotunePV, autotuneRange, autotune_by_feature, autotune_max_clusters, exclusions,
                               streaming_autotune, streaming_buffer, learning_numerator, learning_denominator, learning_max_clusters, learning_samples)

        body = json.dumps(config)

        config_cmd = self.url + 'clusterConfig/' + self.instance + '?api-tenant=' + self.api_tenant
        result, response = simple_post(self, config_cmd, body=body)
        if result:
            self.numeric_format = config['numericFormat']

        return result, response

    def nano_list(self):
        """Returns list of nano instances allocated for a pod

        Returns:
            result (boolean):  true if successful (list was returned)
            response (str): json dictionary of pod instances when result=true, error string when result=false

        """

        # build command
        instance_cmd = self.url + 'nanoInstances' + '?api-tenant=' + self.api_tenant

        return simple_get(self, instance_cmd)

    @_is_configured
    def save_nano(self, filename):
        """serialize a nano pod instance and save to a local file

        Args:
            filename (str): path to local file where saved pod instance should be written

        Returns:
            result (boolean):  true if successful (pod instance was written)
            response (str): None when result is true, error string when result=false

        """

        # build command
        snapshot_cmd = self.url + 'snapshot/' + self.instance + '?api-tenant=' + self.api_tenant

        # serialize nano
        result, response = simple_get(self, snapshot_cmd)
        if not result:
            return result, response

        # at this point, the call succeeded, saves the result to a local file
        try:
            with open(filename, 'wb') as fp:
                fp.write(response)
        except Exception as e:
            return False, e.strerror

        return True, None

    def restore_nano(self, filename):
        """Restore a nano pod instance from local file

        Args:
            filename (str): path to local file containing saved pod instance

        Returns:
            result (boolean):  true if successful (nano pod instance was restored)
            response (str): None when result is true, error string when result=false

        """

        # verify that input file is a valid nano file (gzip'd tar with Magic Number)
        try:
            with tarfile.open(filename, 'r:gz') as tp:
                with tp.extractfile('BoonNano/MagicNumber') as magic_fp:
                    magic_num = magic_fp.read()
                    if magic_num != b'\xef\xbe':
                        return False, 'file {} is not a Boon Logic nano-formatted file, bad magic number'.format(
                            filename)
        except KeyError:
            return False, 'file {} is not a Boon Logic nano-formatted file'.format(filename)
        except Exception as e:
            return False, 'corrupt file {}'.format(filename)

        with open(filename, 'rb') as fp:
            nano = fp.read()

        # build command
        snapshot_cmd = self.url + 'snapshot/' + self.instance + '?api-tenant=' + self.api_tenant

        fields = {'snapshot': (filename, nano)}

        result, response = multipart_post(self, snapshot_cmd, fields=fields)

        if not result:
            return result, response

        self.numeric_format = response['numericFormat']

        return True, response

    @_is_configured
    def autotune_config(self):
        """Autotunes the percent variation, min and max for each feature

        Returns:
            result (boolean): true if successful (autotuning was completed)
            response (dict or str): configuration dictionary when result is true, error string when result is false

        """

        # build command
        config_cmd = self.url + 'autoTuneConfig/' + self.instance + '?api-tenant=' + self.api_tenant

        # autotune parameters
        return simple_post(self, config_cmd)

    @_is_configured
    def get_config(self):
        """Gets the configuration for this nano pod instance

        Returns:
            result (boolean): true if successful (configuration was found)
            response (dict or str): configuration dictionary when result is true, error string when result is false

        """
        config_cmd = self.url + 'clusterConfig/' + self.instance + '?api-tenant=' + self.api_tenant
        return simple_get(self, config_cmd)

    @_is_configured
    def load_file(self, file, file_type, gzip=False, append_data=False):
        """Load nano data from a file

        Args:
            file (str): local path to data file
            file_type (str): file type specifier, must be either 'cvs' or 'raw'
            gzip (boolean): true if file is gzip'd, false if not gzip'd
            append_data (boolean): true if data should be appended to previous data, false if existing
                data should be truncated

        Returns:
            result (boolean): true if successful (file was successful loaded into nano pod instance)
            response (str): None when result is true, error string when result=false

        """

        # load the data file
        try:
            with open(file, 'rb') as fp:
                file_data = fp.read()
        except FileNotFoundError as e:
            return False, e.strerror
        except Exception as e:
            return False, e

        # verify file_type is set correctly
        if file_type not in ['csv', 'csv-c', 'raw', 'raw-n']:
            return False, 'file_type must be "csv", "csv-c", "raw" or "raw-n"'

        file_name = os.path.basename(file)

        fields = {'data': (file_name, file_data)}

        # build command
        dataset_cmd = self.url + 'data/' + self.instance + '?api-tenant=' + self.api_tenant
        dataset_cmd += '&fileType=' + file_type
        dataset_cmd += '&gzip=' + str(gzip).lower()
        dataset_cmd += '&appendData=' + str(append_data).lower()

        return multipart_post(self, dataset_cmd, fields=fields)

    @_is_configured
    def load_data(self, data, append_data=False):
        """Load nano data from an existing numpy array or simple python list

        Args:
            data (np.ndarray or list): numpy array or list of data values
            append_data (boolean): true if data should be appended to previous data, false if existing
                data should be truncated

        Returns:
            result (boolean): true if successful (data was successful loaded into nano pod instance)
            response (str): None when result is true, error string when result=false

        """
        data = normalize_nano_data(data, self.numeric_format)
        file_name = 'dummy_filename.bin'
        file_type = 'raw'

        fields = {'data': (file_name, data)}

        # build command
        dataset_cmd = self.url + 'data/' + self.instance + '?api-tenant=' + self.api_tenant
        dataset_cmd += '&fileType=' + file_type
        dataset_cmd += '&appendData=' + str(append_data).lower()

        return multipart_post(self, dataset_cmd, fields=fields)

    def set_learning_status(self, status):
        """returns list of nano instances allocated for a pod

        Args:
            status (boolean): true or false of whether to learning is on or off

        Returns:
            result (boolean):  true if successful (list was returned)
            response (str): json dictionary of pod instances when result=true, error string when result=false

        """

        # build command
        learning_cmd = self.url + 'learning/' + self.instance + '?enable=' + str(status).lower() + '&api-tenant=' + self.api_tenant

        return simple_post(self, learning_cmd)

    def run_nano(self, results=None):
        """Clusters the data in the nano pod buffer and returns the specified results

        Args:
            results (str): comma separated list of result specifiers

                ID = cluster ID

                SI = smoothed anomaly index

                RI = raw anomaly index

                FI = frequency index

                DI = distance index

                All = ID,SI,RI,FI,DI

        Returns:
            result (boolean): true if successful (nano was successfully run)
            response (dict or str): dictionary of results when result is true, error message when result = false

        """

        results_str = ''
        if str(results) == 'All':
            results_str = 'ID,SI,RI,FI,DI'
        elif results:
            for result in results.split(','):
                if result not in ['ID', 'SI', 'RI', 'FI', 'DI']:
                    return False, 'unknown result "{}" found in results parameter'.format(result)
            results_str = results

        # build command
        nano_cmd = self.url + 'nanoRun/' + self.instance + '?api-tenant=' + self.api_tenant
        if results:
            nano_cmd += '&results=' + results_str

        return simple_post(self, nano_cmd)

    @_is_configured
    def run_streaming_nano(self, data, results=None):
        """Load streaming data into self-autotuning nano pod instance, run the nano and return results

        Args:
            data (np.ndarray or list): numpy array or list of data values
            results (str): comma separated list of result specifiers

                ID = cluster ID

                SI = smoothed anomaly index

                RI = raw anomaly index

                FI = frequency index

                DI = distance index

                All = ID,SI,RI,FI,DI

        Returns:
            result (boolean): true if successful (data was successful streamed to nano pod instance)
            response (dict or str): dictionary of results when result is true, error message when result = false

        """
        data = normalize_nano_data(data, self.numeric_format)
        file_name = 'dummy_filename.bin'
        file_type = 'raw'

        fields = {'data': (file_name, data)}

        results_str = ''
        if str(results) == 'All':
            results_str = 'ID,SI,RI,FI,DI'
        elif results:
            for result in results.split(','):
                if result not in ['ID', 'SI', 'RI', 'FI', 'DI']:
                    return False, 'unknown result "{}" found in results parameter'.format(result)
            results_str = results

        # build command
        streaming_cmd = self.url + 'nanoRunStreaming/' + self.instance + '?api-tenant=' + self.api_tenant
        streaming_cmd += '&fileType=' + file_type
        if results:
            streaming_cmd += '&results=' + results_str

        return multipart_post(self, streaming_cmd, fields=fields)

    def get_version(self):
        """Version information for this nano pod

        Returns:
            result (boolean): true if successful (version information was retrieved)
            response (dict or str): dictionary of results when result is true, error message when result = false

        """

        # build command (minus the v3 portion)
        version_cmd = self.url[:-3] + 'version' + '?api-tenant=' + self.api_tenant
        return simple_get(self, version_cmd)

    @_is_configured
    def get_buffer_status(self):
        """Results related to the bytes processed/in the buffer

        Returns:
            result (boolean): true if successful (nano was successfully run)
            response (dict or str): dictionary of results when result is true, error message when result = false

        """
        status_cmd = self.url + 'bufferStatus/' + self.instance + '?api-tenant=' + self.api_tenant
        return simple_get(self, status_cmd)

    @_is_configured
    def get_nano_results(self, results='All'):
        """Results per pattern

        Args:
            results (str): comma separated list of results

                ID = cluster ID

                SI = smoothed anomaly index

                RI = raw anomaly index

                FI = frequency index

                DI = distance index

                All = ID,SI,RI,FI,DI

        """
        # build results command
        if str(results) == 'All':
            results_str = 'ID,SI,RI,FI,DI'
        else:
            for result in results.split(','):
                if result not in ['ID', 'SI', 'RI', 'FI', 'DI']:
                    return False, 'unknown result "{}" found in results parameter'.format(result)
            results_str = results

        # build command
        results_cmd = self.url + 'nanoResults/' + self.instance + '?api-tenant=' + self.api_tenant
        results_cmd += '&results=' + results_str

        return simple_get(self, results_cmd)

    @_is_configured
    def get_nano_status(self, results='All'):
        """Results in relation to each cluster/overall stats

        Args:
            results (str): comma separated list of results

                PCA = principal components (includes 0 cluster)

                clusterGrowth = indexes of each increase in cluster (includes 0 cluster)

                clusterSizes = number of patterns in each cluster (includes 0 cluster)

                anomalyIndexes = anomaly index (includes 0 cluster)

                frequencyIndexes = frequency index (includes 0 cluster)

                distanceIndexes = distance index (includes 0 cluster)

                totalInferences = total number of patterns clustered (overall)

                averageInferenceTime = time in milliseconds to cluster per
                    pattern (not available if uploading from serialized nano) (overall)

                numClusters = total number of clusters (includes 0 cluster) (overall)

                All = PCA,clusterGrowth,clusterSizes,anomalyIndexes,frequencyIndexes,distanceIndexes,totalInferences,numClusters

        Returns:
            result (boolean): true if successful (nano was successfully run)
            response (dict or str): dictionary of results when result is true, error message when result = false

        """

        # build results command
        if str(results) == 'All':
            results_str = 'PCA,clusterGrowth,clusterSizes,anomalyIndexes,frequencyIndexes,' \
                          'distanceIndexes,totalInferences,numClusters'
        else:
            for result in results.split(','):
                if result not in ['PCA', 'clusterGrowth', 'clusterSizes', 'anomalyIndexes', 'frequencyIndexes',
                                  'distanceIndexes', 'totalInferences', 'numClusters', 'averageInferenceTime']:
                    return False, 'unknown result "{}" found in results parameter'.format(result)
            results_str = results

        # build command
        results_cmd = self.url + 'nanoStatus/' + self.instance + '?api-tenant=' + self.api_tenant
        results_cmd = results_cmd + '&results=' + results_str

        return simple_get(self, results_cmd)

def normalize_nano_data(data, numeric_format):
    # Whatever type data comes in as, cast it to numpy array
    data = np.asarray(data)

    # Cast numpy array to correct numeric type for serialization
    if numeric_format == 'int16':
        data = data.astype(np.int16)
    elif numeric_format == 'float32':
        data = data.astype(np.float32)
    elif numeric_format == 'uint16':
        data = data.astype(np.uint16)

    # Serialize to binary blob
    data = data.tostring()

    return data
