from urllib3 import ProxyManager
from urllib3 import PoolManager
from urllib3 import Timeout
from functools import wraps
import json
import os
import tarfile

import requests
import numpy as np

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

############################
# BoonNano Python API v3.1 #
############################


class BoonException(Exception):
    def __init__(self, code=None, message=None):
        self.status_code = code
        self.message = message


class ExpertClient:
    def __init__(
        self,
        license_id="default",
        license_file="~/.BoonLogic.license",
        timeout=120.0,
        verify=True,
        cert=None,
    ):
        """Primary handle for BoonNano Pod instances

        The is the primary handle to manage a nano pod instance

        Args:
            license_id (str): license identifier label found within the .BoonLogic.license configuration file
            license_file (str): path to .BoonLogic license file
            timeout (float): read timeout for http requests
            verify:  Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use
            cert (bool): if String, path to ssl client cert file (.pem). If Tuple, (‘cert’, ‘key’) pair.


        Environment:
            BOON_LICENSE_FILE: sets license_file path
            BOON_LICENSE_ID: sets license_id
            BOON_API_KEY: overrides the api-key as found in .BoonLogic.license file
            BOON_API_TENANT: overrides the api-tenant as found in .BoonLogic.license file
            BOON_SERVER: overrides the server as found in .BoonLogic.license file
            PROXY_SERVER: overrides the proxy server as found in .BoonLogic.license file
            BOON_SSL_CERT: path to ssl client cert file (.pem)
            BOON_SSL_VERIFY: Either a boolean, in which case it controls whether we verify the server’s TLS certificate, or a string, in which case it must be a path to a CA bundle to use


        Example:
            ```python
            try:
                nano = bn.ExpertClient()
            except bn.BoonException as be:
                print(be)
                sys.exit(1)
            ```

        """
        self.results = ["ID", "SI", "RI", "FI", "DI", "NI", "NS", "NW", "OM", "PI"]
        self.user_agent = "Boon Logic / expert-python-sdk / requests"

        self.license_id = None
        self.api_key = None
        self.api_tenant = None
        self.numeric_format = ""

        env_license_file = os.environ.get("BOON_LICENSE_FILE", None)
        env_license_id = os.environ.get("BOON_LICENSE_ID", None)
        env_api_key = os.environ.get("BOON_API_KEY", None)
        env_api_tenant = os.environ.get("BOON_API_TENANT", None)
        env_server = os.environ.get("BOON_SERVER", None)
        env_proxy_server = os.environ.get("PROXY_SERVER", None)
        env_cert = os.environ.get("BOON_SSL_CERT", None)
        env_verify = os.environ.get("BOON_SSL_VERIFY", None)

        # certificates
        self.cert = (
            "CERT_REQUIRED"
            if env_cert
            else {None: "CERT_NONE", True: "CERT_REQUIRED"}[cert]
        )
        if env_verify:
            if env_verify.lower() == "false":
                self.verify = False
            elif env_verify.lower() == "true":
                self.verify = True
            else:
                self.verify = env_verify
        else:
            self.verify = verify

        # when license_id comes in as None, use 'default'
        if license_id is None:
            license_id = "default"

        license_file = env_license_file if env_license_file else license_file
        self.license_id = env_license_id if env_license_id else license_id

        license_path = os.path.abspath(os.path.expanduser(license_file))
        if not os.path.exists(license_path):
            raise BoonException(
                message="license file {} does not exist".format(license_file)
            )
        try:
            with open(license_path, "r") as json_file:
                file_data = json.load(json_file)
        except json.JSONDecodeError as e:
            raise BoonException(
                message="json formatting error in .BoonLogic.license file, {}, line: {}, col: {}".format(
                    e.msg, e.lineno, e.colno
                )
            )
        try:
            license_data = file_data[self.license_id]
        except KeyError:
            raise BoonException(
                message='license_id "{}" not found in license file'.format(
                    self.license_id
                )
            )

        try:
            self.api_key = env_api_key if env_api_key else license_data["api-key"]
        except KeyError:
            raise BoonException(
                message='"api-key" is missing from the specified license in license file'
            )

        try:
            self.api_tenant = (
                env_api_tenant if env_api_tenant else license_data["api-tenant"]
            )
        except KeyError:
            raise BoonException(
                message='"api-tenant" is missing from the specified license in license file'
            )

        try:
            self.server = env_server if env_server else license_data["server"]
        except KeyError:
            raise BoonException(
                message='"server" is missing from the specified license in license file'
            )

        self.proxy_server = env_proxy_server
        if not self.proxy_server and "proxy-server" in license_data.keys():
            self.proxy_server = license_data["proxy-server"]

        # set up base url
        self.url = self.server + "/expert/v3"
        if "http" not in self.server:
            self.url = "http://" + self.url

        self.timeout = timeout
        timeout_inst = Timeout(connect=30.0, read=timeout)
        self.http = PoolManager(timeout=timeout_inst, cert_reqs=self.cert)

    def _is_configured(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if args[0].numeric_format not in ["int16", "uint16", "float32"]:
                raise BoonException(400, "nano instance is not configured")
            return f(*args, **kwargs)

        return inner

    def _api_call(self, method, url, headers, body=None, fields=None):
        """Make a REST call to the Expert server and handle the response"""
        headers["x-token"] = self.api_key
        headers["User-Agent"] = self.user_agent

        if "Content-Type" in headers and "json" in headers["Content-Type"]:
            body = json.dumps(body)

        if method == "POST" and body is not None and len(body) > 10000:
            headers["content-encoding"] = "gzip"
            body = gzip.compress(body.encode("utf-8"))

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                verify=self.verify,
                timeout=self.timeout,
                files=fields,
            )
        except requests.exceptions.Timeout:
            # request timed out
            raise BoonException(500, "request timed out")
        except requests.exceptions.ConnectionError:
            raise BoonException(500, "server does not exist")

        if response.status_code > 299:
            try:
                msg = response.json()
                try:
                    msg = msg.get("message", "no message")
                except AttributeError:
                    pass
            except json.JSONDecodeError:
                msg = response.text
            raise BoonException(response.status_code, msg)

        try:
            respbody = response.json()
        except Exception:
            # save nano or load data
            return response.content

        # if code is returned in the message, it should agree with the header
        if (
            isinstance(respbody, dict)
            and "code" in respbody
            and respbody["code"] != response.status_code
        ):
            raise BoonException(respbody["code"], respbody.get("message", "no message"))

        if isinstance(respbody, dict) and "errorMessage" in respbody:
            raise BoonException(500, respbody["errorMessage"])

        return response

    def _format_results(self, results):
        results_str = ""
        if str(results) == "All":
            results_str = ",".join(self.results)
        elif results is not None:
            results_str = results if isinstance(results, str) else ",".join(results)
        return results_str

    def open_nano(self, instance_id):
        """Creates or attaches to a nano pod instance

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (dict): metadata about the instance

        """

        url = (
            self.url + "/nanoInstance/" + instance_id + "?api-tenant=" + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("POST", url, headers)

        return response.json()

    def get_nano_instance(self, instance_id):
        """Get instance info

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (dict): metadata about the instance

        """

        url = (
            self.url + "/nanoInstance/" + instance_id + "?api-tenant=" + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    def close_nano(self, instance_id):
        """Closes the pod instance

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        """

        url = (
            self.url + "/nanoInstance/" + instance_id + "?api-tenant=" + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        self._api_call("DELETE", url, headers)

    def create_config(
        self,
        feature_count,
        numeric_format,
        cluster_mode="batch",
        min_val=0,
        max_val=1,
        weight=1,
        label=None,
        percent_variation=0.05,
        streaming_window=1,
        accuracy=0.99,
        autotune_pv=True,
        autotune_range=True,
        autotune_by_feature=True,
        autotune_max_clusters=1000,
        exclusions=None,
        streaming_autotune=True,
        streaming_buffer=10000,
        anomaly_history_window=10000,
        learning_numerator=10,
        learning_denominator=10000,
        learning_max_clusters=1000,
        learning_samples=1000000,
    ):
        """Generate a configuration template for the given parameters

        A discrete configuration is specified as a list of min, max, weights, and labels

        Args:
            feature_count (int): number of features per vector
            numeric_format (str): numeric type of data (one of "float32", "uint16", or "int16")
            cluster_mode (str): 'streaming' or 'batch' for expert run type
            min_val: the value that should be considered the minimum value for this feature. This
                can be set to a value larger than the actual min if you want to treat all value less
                than that as the same (for instance, to keep a noise spike from having undue influence
                in the clustering.  a single element list assigns all features with same min_val
            max_val: corresponding maximum value, a single element list assigns all features with same max_val
            weight: weight for this feature, a single element list assigns all features with same weight
            label (list): list of labels to assign to features
            percent_variation (float): amount of variation allowed within clusters
            streaming_window (integer): number of consecutive vectors treated as one inference (parametric parameter)
            accuracy (float): statistical accuracy of the clusters
            autotune_pv (bool): whether to autotune the percent variation
            autotune_range (bool): whether to autotune the min and max values
            autotune_by_feature (bool): whether to have individually set min and max values for each feature
            autotune_max_clusters (int): max number of clusters allowed
            exclusions (list): features to exclude while autotuning
            streaming_autotune (bool): whether to autotune while in streaming mode
            streaming_buffer (int): number of samples to autotune on
            anomaly_history_window (int): number of samples to use in AH calculation
            learning_numerator (int): max number of new clusters learned
            learning_denominator (int): number of samples over which the new clusters are learned
            learning_max_clusters (int): max number of clusters before turning off learning
            learning_samples (int): max number of samples before turning off learning


        Returns:
            config (dict): configuration dictionary

        """

        if isinstance(min_val, int) or isinstance(min_val, float):
            min_val = [min_val] * feature_count
        if isinstance(max_val, int) or isinstance(max_val, float):
            max_val = [max_val] * feature_count
        if isinstance(weight, int):
            weight = [weight] * feature_count

        if exclusions is None:
            exclusions = []

        config = {}
        config["clusterMode"] = cluster_mode
        config["numericFormat"] = numeric_format
        config["features"] = []

        if (
            (isinstance(min_val, list) or isinstance(min_val, np.ndarray))
            and (isinstance(max_val, list) or isinstance(max_val, np.ndarray))
            and (isinstance(weight, list) or isinstance(weight, np.ndarray))
        ):
            if len(min_val) != len(max_val) or len(min_val) != len(weight):
                raise BoonException(
                    message="parameters must be lists of the same length"
                )

            for min, max, w in zip(min_val, max_val, weight):
                tempDict = {}
                tempDict["minVal"] = min
                tempDict["maxVal"] = max
                tempDict["weight"] = w
                config["features"].append(tempDict)
        else:
            raise BoonException(
                message="min_val, max_val and weight must be list or numpy array"
            )

        if isinstance(label, list):
            if len(label) != len(min_val):
                raise BoonException(
                    message="label must be the same length as other parameters"
                )
            for i, l in enumerate(label):
                config["features"][i]["label"] = l
        elif label:
            raise BoonException(message="label must be list")

        config["percentVariation"] = percent_variation
        config["accuracy"] = accuracy
        config["streamingWindowSize"] = streaming_window

        config["autoTuning"] = {}
        config["autoTuning"]["autoTuneByFeature"] = autotune_by_feature
        config["autoTuning"]["autoTunePV"] = autotune_pv
        config["autoTuning"]["autoTuneRange"] = autotune_range
        config["autoTuning"]["maxClusters"] = autotune_max_clusters
        if isinstance(exclusions, list):
            config["autoTuning"]["exclusions"] = exclusions
        elif exclusions:
            raise BoonException(message="exclusions must be a list")

        if config["clusterMode"] == "streaming":
            config["streaming"] = {}
            config["streaming"]["enableAutoTuning"] = streaming_autotune
            config["streaming"]["samplesToBuffer"] = streaming_buffer
            config["streaming"]["anomalyHistoryWindow"] = anomaly_history_window
            config["streaming"]["learningRateNumerator"] = learning_numerator
            config["streaming"]["learningRateDenominator"] = learning_denominator
            config["streaming"]["learningMaxClusters"] = learning_max_clusters
            config["streaming"]["learningMaxSamples"] = learning_samples

        return config

    def configure_nano(
        self,
        instance_id,
        feature_count=1,
        numeric_format="float32",
        cluster_mode="batch",
        min_val=0,
        max_val=1,
        weight=1,
        label=None,
        percent_variation=0.05,
        streaming_window=1,
        accuracy=0.99,
        autotune_pv=True,
        autotune_range=True,
        autotune_by_feature=True,
        autotune_max_clusters=1000,
        exclusions=None,
        streaming_autotune=True,
        streaming_buffer=10000,
        anomaly_history_window=10000,
        learning_numerator=10,
        learning_denominator=10000,
        learning_max_clusters=1000,
        learning_samples=1000000,
        config=None,
    ):
        """Returns the posted clustering configuration

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            feature_count (int): number of features per vector
            numeric_format (str): numeric type of data (one of "float32", "uint16", or "int16")
            cluster_mode (str): 'streaming' or 'batch' mode to run expert
            min_val: list of minimum values per feature, if specified as a single value, use that on all features
            max_val: list of maximum values per feature, if specified as a single value, use that on all features
            weight: influence each column has on creating a new cluster
            label (list): name of each feature (if applicable)
            percent_variation (float): amount of variation within each cluster
            streaming_window (integer): number of consecutive vectors treated as one inference (parametric parameter)
            accuracy (float): statistical accuracy of the clusters
            autotune_pv (bool): whether to autotune the percent variation
            autotune_range (bool): whether to autotune the min and max values
            autotune_by_feature (bool): whether to have individually set min and max values for each feature
            autotune_max_clusters (int): max number of clusters allowed
            exclusions (list): features to exclude while autotuning
            streaming_autotune (bool): whether to autotune while in streaming mode
            streaming_buffer (int): number of samples to autotune on
            anomaly_history_window (int): number of samples to use for AH calculation
            learning_numerator (int): max number of new clusters learned
            learning_denominator (int): number of samples over which the new clusters are learned
            learning_max_clusters (int): max number of clusters before turning off learning
            learning_samples (int): max number of samples before turning off learning
            config (dict): dictionary of configuration parameters

        Returns:
            response (dict): configuration dictionary

        """

        if config is None:
            config = self.create_config(
                feature_count,
                numeric_format,
                cluster_mode,
                min_val,
                max_val,
                weight,
                label,
                percent_variation,
                streaming_window,
                accuracy,
                autotune_pv,
                autotune_range,
                autotune_by_feature,
                autotune_max_clusters,
                exclusions,
                streaming_autotune,
                streaming_buffer,
                anomaly_history_window,
                learning_numerator,
                learning_denominator,
                learning_max_clusters,
                learning_samples,
            )

        body = config

        url = (
            self.url
            + "/clusterConfig/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("POST", url, headers, body)

        self.numeric_format = config["numericFormat"]

        return response.json()

    def nano_list(self):
        """Returns list of nano instances allocated for a pod

        Returns:
            response (dict): json dictionary of pod instances

        """

        url = self.url + "/nanoInstances/" + "?api-tenant=" + self.api_tenant
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    @_is_configured
    def save_nano(self, instance_id, filename):
        """serialize a nano pod instance and save to a local file

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            filename (str): path to local file where saved pod instance should be written

        """

        url = self.url + "/snapshot/" + instance_id + "?api-tenant=" + self.api_tenant
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        # at this point, the call succeeded, saves the result to a local file
        try:
            with open(filename, "wb") as fp:
                fp.write(response)
        except Exception as e:
            raise BoonException(message=str(e))

    def restore_nano(self, instance_id, filename):
        """Restore a nano pod instance from local file

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            filename (str): path to local file containing saved pod instance

        Returns:
            response (dict): config dictionary of the uploaded nano

        """

        # verify that input file is a valid nano file (gzip'd tar with Magic Number)
        try:
            with tarfile.open(filename, "r:gz") as tp:
                with tp.extractfile("CommonState/MagicNumber") as magic_fp:
                    magic_num = magic_fp.read()
                    if magic_num != b"\xda\xba":
                        raise BoonException(
                            message="file {} is not a Boon Logic nano-formatted file, bad magic number".format(
                                filename
                            )
                        )
        except KeyError:
            raise BoonException(
                message="file {} is not a Boon Logic nano-formatted file".format(
                    filename
                )
            )
        except Exception as e:
            raise BoonException(message="corrupt file {}".format(filename))

        with open(filename, "rb") as fp:
            nano = fp.read()

        fields = {"snapshot": (filename, nano)}

        url = self.url + "/snapshot/" + instance_id + "?api-tenant=" + self.api_tenant
        headers = {}
        response = self._api_call("POST", url, headers, fields=fields)

        response = response.json()

        self.numeric_format = response["numericFormat"]

        return response

    @_is_configured
    def autotune_config(self, instance_id):
        """Autotunes the percent variation, min and max for each feature

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        """

        url = self.url + "/autoTune/" + instance_id + "?api-tenant=" + self.api_tenant
        headers = {"Content-Type": "application/json"}
        self._api_call("POST", url, headers)

    @_is_configured
    def get_autotune_array(self, instance_id):
        """Gets the autotune elbow

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (list): 2D array of the autotuning elbox values

        """

        url = (
            self.url
            + "/autotuneArray/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    @_is_configured
    def get_config(self, instance_id):
        """Gets the configuration for this nano pod instance

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (dict): configuration dictionary

        """

        url = (
            self.url
            + "/clusterConfig/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    @_is_configured
    def load_file(self, instance_id, file, file_type, gzip=False, append_data=False):
        """Load nano data from a file

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            file (str): local path to data file
            file_type (str): file type specifier, must be either 'cvs' or 'raw'
            gzip (boolean): true if file is gzip'd, false if not gzip'd
            append_data (boolean): true if data should be appended to previous data, false if existing
                data should be truncated

        """

        # load the data file
        try:
            with open(file, "rb") as fp:
                file_data = fp.read()
        except FileNotFoundError as e:
            raise BoonException(message=e.strerror)
        except Exception as e:
            raise BoonException(message=str(e))

        # verify file_type is set correctly
        if file_type not in ["csv", "csv-c", "raw", "raw-n"]:
            raise BoonException(
                message='file_type must be "csv", "csv-c", "raw" or "raw-n"'
            )

        file_name = os.path.basename(file)

        fields = {"data": (file_name, file_data)}

        url = (
            self.url
            + "/data/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&fileType="
            + file_type
            + "&appendData="
            + str(append_data).lower()
            + "&gzip="
            + str(gzip).lower()
        )
        headers = {}
        self._api_call("POST", url, headers, fields=fields)

    @_is_configured
    def load_data(self, instance_id, data, append_data=False):
        """Load nano data from an existing numpy array or simple python list

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            data (np.ndarray or list): numpy array or list of data values
            append_data (boolean): true if data should be appended to previous data, false if existing
                data should be truncated

        """

        data = normalize_nano_data(data, self.numeric_format)
        file_name = "dummy_filename.bin"
        file_type = "raw"

        fields = {"data": (file_name, data)}

        url = (
            self.url
            + "/data/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&fileType="
            + file_type
            + "&appendData="
            + str(append_data).lower()
        )
        headers = {}
        self._api_call("POST", url, headers, fields=fields)

    def set_learning_enabled(self, instance_id, status):
        """returns list of nano instances allocated for a pod

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            status (boolean): true or false of whether to learning is on or off

        Returns:
            response (boolean): status of learning

        """
        if status not in [True, False]:
            raise BoonException(400, "status must be a boolean")

        url = (
            self.url
            + "/learning/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&enable="
            + str(status).lower()
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("POST", url, headers)

        return response.json()

    @_is_configured
    def is_learning_enabled(self, instance_id):
        """Results in relation to each cluster/overall stats

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (boolean): learning on/off status

        """

        url = self.url + "/learning/" + instance_id + "?api-tenant=" + self.api_tenant
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    def set_root_cause_enabled(self, instance_id, status):
        """configures whether or not to save new clusters coming in for root cause analysis

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            status (boolean): true or false of whether root cause is on or off

        Returns:
            response (boolean): status of root cause

        """
        if status not in [True, False]:
            raise BoonException(400, "status must be a boolean")

        url = (
            self.url
            + "/rootCause/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&enable="
            + str(status).lower()
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("POST", url, headers)

        return response.json()

    @_is_configured
    def is_root_cause_enabled(self, instance_id):
        """Results in relation to each cluster/overall stats

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (boolean): root cause on/off status

        """

        url = self.url + "/rootCause/" + instance_id + "?api-tenant=" + self.api_tenant
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    def set_clipping_detection_enabled(self, instance_id, status):
        """configures whether or not to save new clusters coming in for root cause analysis

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            status (boolean): true or false of whether root cause is on or off

        Returns:
            response (boolean): status of nano clipping detection

        """
        if status not in [True, False]:
            raise BoonException(400, "status must be a boolean")

        url = (
            self.url
            + "/clippingDetection/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&enable="
            + str(status).lower()
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("POST", url, headers)

        return response.json()

    @_is_configured
    def is_clipping_detection_enabled(self, instance_id):
        """Results in relation to each cluster/overall stats

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (boolean): nano clipping detection on/off status

        """

        url = (
            self.url
            + "/clippingDetection/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    def run_nano(self, instance_id, results=None):
        f"""Clusters the data in the nano pod buffer and returns the specified results

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            results (str): comma separated list of result specifiers

                ID = cluster ID

                SI = smoothed anomaly index

                RI = raw anomaly index

                FI = frequency index

                DI = distance index

                All = {",".join(self.results)}

        Returns:
            response (dict): dictionary of results

        """

        results_str = self._format_results(results)

        url = self.url + "/nanoRun/" + instance_id + "?api-tenant=" + self.api_tenant
        if results is not None:
            url += "&results=" + results_str
        headers = {"Content-Type": "application/json"}
        response = self._api_call("POST", url, headers)

        return response.json()

    @_is_configured
    def prune_ids(self, instance_id, id_list=[]):
        """Get root cause

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            id_list (list): list of IDs to remove from the model

        Returns:
            response (dict): metadata about the updated model

        """

        url = (
            self.url + "/pruneCluster/" + instance_id + "?api-tenant=" + self.api_tenant
        )

        if isinstance(id_list, int):
            id_list = [id_list]

        if len(id_list) != 0:
            # IDs
            id_list = [str(element) for element in id_list]
            url += "&clusterID=[" + ",".join(id_list) + "]"
        else:
            raise BoonException(message="Must specify cluster IDs to analyze")

        headers = {"Content-Type": "application/json"}
        response = self._api_call("POST", url, headers)

        return response.json()

    @_is_configured
    def run_streaming_nano(self, instance_id, data, results=None):
        f"""Load streaming data into self-autotuning nano pod instance, run the nano and return results

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            data (np.ndarray or list): numpy array or list of data values
            results (str): comma separated list of result specifiers

                ID = cluster ID

                SI = smoothed anomaly index

                RI = raw anomaly index

                FI = frequency index

                DI = distance index

                All = {",".join(self.results)}

        Returns:
            response (dict): dictionary of results

        """

        data = normalize_nano_data(data, self.numeric_format)
        file_name = "dummy_filename.bin"
        file_type = "raw"

        fields = {"data": (file_name, data)}

        results_str = self._format_results(results)

        url = (
            self.url
            + "/nanoRunStreaming/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&fileType="
            + file_type
        )
        if results is not None:
            url += "&results=" + results_str
        headers = {}
        response = self._api_call("POST", url, headers, fields=fields)

        return response.json()

    def get_version(self):
        """Version information for this nano pod

        Returns:
            response (dict): dictionary of version information

        """

        url = self.url[:-3] + "/version" + "?api-tenant=" + self.api_tenant
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    @_is_configured
    def get_buffer_status(self, instance_id):
        """Results related to the bytes processed/in the buffer

        Args:
            instance_id (str): instance identifier to assign to new pod instance

        Returns:
            response (dict): dictionary of buffer statistics

        """

        url = (
            self.url + "/bufferStatus/" + instance_id + "?api-tenant=" + self.api_tenant
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    @_is_configured
    def get_nano_results(self, instance_id, results="All"):
        f"""Results per pattern

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            results (str): comma separated list of results

                ID = cluster ID

                SI = smoothed anomaly index

                RI = raw anomaly index

                FI = frequency index

                DI = distance index

                All = {",".join(self.results)}

        Returns:
            response (dict): dictionary of results

        """
        results_str = self._format_results(results)

        url = (
            self.url
            + "/nanoResults/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&results="
            + results_str
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    @_is_configured
    def get_nano_status(self, instance_id, results="All"):
        """Results in relation to each cluster/overall stats

        Args:
            instance_id (str): instance identifier to assign to new pod instance
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

                All = PCA,clusterGrowth,clusterSizes,anomalyIndexes,frequencyIndexes,distanceIndexes,totalInferences,numClusters,clusterDistances

        Returns:
            response (dict): dictionary of results

        """

        # build results command
        if str(results) == "All":
            results_str = (
                "PCA,clusterGrowth,clusterSizes,anomalyIndexes,frequencyIndexes,"
                "distanceIndexes,totalInferences,numClusters,clusterDistances"
            )
        else:
            results_str = results if isinstance(results, str) else ",".join(results)

        url = (
            self.url
            + "/nanoStatus/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
            + "&results="
            + results_str
        )
        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()

    def get_root_cause(self, instance_id, id_list=[], pattern_list=[]):
        """Get root cause

        Args:
            instance_id (str): instance identifier to assign to new pod instance
            id_list (list): list of IDs to return the root cause for
            pattern_list (list): list of pattern vectors to calculate the root cause against the model

        Returns:
            response (list): list containing the root cause for each pattern/id provided for a sensor
        """

        url = (
            self.url
            + "/rootCauseAnalysis/"
            + instance_id
            + "?api-tenant="
            + self.api_tenant
        )

        if len(id_list) != 0:
            # IDs
            id_list = [str(element) for element in id_list]
            url += "&clusterID=[" + ",".join(id_list) + "]"
        elif len(pattern_list) != 0:
            # patterns
            if len(np.array(pattern_list).shape) == 1:  # only 1 pattern provided
                pattern_list = [pattern_list]
            for i, pattern in enumerate(pattern_list):
                pattern_list[i] = ",".join([str(element) for element in pattern])
            url += "&pattern=[[" + "],[".join(pattern_list) + "]]"

        headers = {"Content-Type": "application/json"}
        response = self._api_call("GET", url, headers)

        return response.json()


def normalize_nano_data(data, numeric_format):
    # Whatever type data comes in as, cast it to numpy array
    data = np.asarray(data)

    # Cast numpy array to correct numeric type for serialization
    if numeric_format == "int16":
        data = data.astype(np.int16)
    elif numeric_format == "float32":
        data = data.astype(np.float32)
    elif numeric_format == "uint16":
        data = data.astype(np.uint16)

    # Serialize to binary blob
    data = data.tostring()

    return data
