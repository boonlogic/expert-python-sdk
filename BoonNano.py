
import urllib3
import json
import numpy as np
import os

############################
# BoonNano Python API v2.1 #
############################

class BoonNano:
    """Python class to perform clustering with BoonNano Server

    Args:

    Returns:
        empty returns (only bool for success of call):
            post calls
            saveSnapshot
            autotune
            deleteInstance
        functions with valued returns:
            get calls
            uploadData
            runNano

    Example Usage:
        bn = BoonNano('localhost',5010)
        success, config = bn.getConfigTemplate(numFeatures=30, numType='native', min=0, max=10, percentVariation=0.05, streamingWindow=1, accuracy=0.99, weight=1)
        success, instance = bn.getInstance()
        success = bn.postClusterConfiguration(instance, config)
        success, data_results = bn.uploadData(instance, Data)
        success = bn.autotune(instance)
        success, nano_results = bn.runNano(instance, results='All')
    """

    def __init__(self, host, port, token='2B69F78F61A572DBF8D1E44548B48', timeout=60.0):
        """BoonNano __init__ method.

        Args:
            host (str): Host Address.
            port (int): Remote Port.
            timeout (float): HTTP Request Timeout
        Returns:


        """
        #arguments
        self.timeout = timeout
        self.token = token

        self.host = host
        self.port = port
        self.primary = '/expert/v2/'
        self.url = 'http://' + str(self.host) + ':' + str(self.port) + self.primary

        #create pool manager
        if(self.timeout == 0):
            self.http = urllib3.PoolManager()
        else:
            self.http = urllib3.PoolManager(timeout=self.timeout)

        #parameters
        print('#################################')
        print('Opening BoonNano Client')
        print('URL: ', self.url)
        print('#################################')

    def __del__(self):
        """Destructor Method.


        """
        print('Closing Pool')
        self.http.clear()

    def set_host_port(self, host, port, token='2B69F78F61A572DBF8D1E44548B48'):
        """Change the host and port

        Args:
            host (str): Host Address.
            port (int): Remote Port.
        Returns:

        """
        self.host = host
        self.port = port
        self.token = token
        self.primary = '/expert/v2/'
        self.url = 'http://' + str(self.host) + ':' + str(self.port) + self.primary

    ##########################
    #  Server Requests       #
    ##########################

###########
# GENERAL #
###########

    def get_version(self):
        """gives the version of the api running"""
        # build command
        version_cmd = self.url[:-3] + 'version'

        # call the version number
        try:
            version_response = self.http.request(
                'GET',
                version_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if version_response.status != 200 and version_response.status != 201:
            print(json.loads(version_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(version_response.data.decode('utf-8'))


#############
# INSTANCES #
#############

    def post_nanoInstance(self, instanceID=''):
        """If an instance number is not given,
        the nano will return the next open number
        as a running instance
        """

        # build command
        instance_cmd = self.url + 'nanoInstance/' + str(instanceID)

        # initialize instance
        try:
            instance_response = self.http.request(
                'POST',
                instance_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(instance_response.data.decode('utf-8'))['instanceID']

    def get_nanoInstance(self, instanceID):
        """returns true if instanceID is a running instance
        and false otherwise
        """

        # build command
        instance_cmd = self.url + 'nanoInstance/' + str(instanceID)

        # check status of instance
        try:
            instance_response = self.http.request(
                'GET',
                instance_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if instance_response.status != 200 and instance_response.status != 201:
            # Error code 404 is that instance is not a running instance
            if instance_response.status == 404:
                return True, False
            # all other errors are a problem with the call rather than returning the status of the instance
            return False, None

        # the instance is running
        return True, True

    def delete_nanoInstance(self, instanceID=''):
        """If an instance number is not given,
        the nano will delete ALL running instances
        """

        # build command
        if instanceID == '':
            # call to delete all instances
            instance_cmd = self.url + 'nanoInstances'
        else:
            # call to delete specified instance number
            instance_cmd = self.url + 'nanoInstance/' + str(instanceID)

        # delete instance(s)
        try:
            instance_response = self.http.request(
                'DELETE',
                instance_cmd,
                headers={
                    'x-token': self.token
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False

            # check for error
        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return False

        return True

    def get_nanoInstances(self):
        """returns list of nano instances running
        """

        # build command
        instance_cmd = self.url + 'nanoInstances'

        # list of running instances
        try:
            instance_response = self.http.request(
                'GET',
                instance_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(instance_response.data.decode('utf-8'))

##################
# CONFIGURATIONS #
##################

    def get_snapshot(self, instanceID, filename):
        """serializes the nano and saves it as a tar filename
        """

        # build command
        snapshot_cmd = self.url + 'snapshot/' + str(instanceID)

        # serialize nano
        try:
            snapshot_response = self.http.request(
                'GET',
                snapshot_cmd,
                headers={
                    'x-token': self.token
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False

        # check for error
        if snapshot_response.status != 200 and snapshot_response.status != 201:
            print(json.loads(snapshot_response.data.decode('utf-8')))
            return False

        # at this point, the call succeed so saves the return to a tar file
        self.filename = filename
        fp = open(self.filename, 'wb')
        fp.write(snapshot_response.data)
        fp.close

        return True

    def post_snapshot(self, instanceID, snapshot):
        """deserialize existing nano
        upload file to given instance

        NOTE: must be of type tar
        """

        self.filename = snapshot

        # check filetype
        if not ".tar" in self.filename:
            print('Dataset Must Be In .tar Format')
            return False

        with open(self.filename, "rb") as fp:
            tar_data = fp.read()

        # build command
        snapshot_cmd = self.url + 'snapshot/' + str(instanceID)

        # post serialized nano
        try:
            snapshot_response = self.http.request(
                'POST',
                snapshot_cmd,
                headers={
                    'x-token': self.token
                },
                fields={
                    'snapshot': (self.filename, tar_data)
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False

        # check for error
        if snapshot_response.status != 200 and snapshot_response.status != 201:
            print(json.loads(snapshot_response.data.decode('utf-8')))
            return False

        return True

    def get_clusterConfig(self, instanceID):
        """returns the posted clustering configuration
        """

        # build command
        config_cmd = self.url + 'clusterConfig/' + str(instanceID)

        # get config
        try:
            config_response = self.http.request(
                'GET',
                config_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(config_response.data.decode('utf-8'))

    def get_configTemplate(self, numericFormat, featureCount, minVal=1, maxVal=10, weight=1, percentVariation=0.05, streamingWindowSize=1, accuracy=0.99):
        """returns a json config version for the given Parameters
        """

        # build command
        config_cmd = self.url + 'configTemplate?featureCount=' + str(featureCount) + '&numericFormat=' + str(numericFormat) + '&minVal=' + str(minVal) + '&maxVal=' + str(maxVal) + '&weight=' + str(weight) + '&percentVariation=' + str(percentVariation) + '&accuracy=' + str(accuracy) + '&streamingWindowSize=' + str(streamingWindowSize)

        # convert to config format
        try:
            config_response = self.http.request(
                'GET',
                config_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(config_response.data.decode('utf-8'))

    def post_clusterConfig(self, instanceID, config):
        """returns the posted clustering configuration
        """

        # build command
        config_cmd = self.url + 'clusterConfig/' + str(instanceID)

        # post config
        try:
            config_response = self.http.request(
                'POST',
                config_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                },
                body=json.dumps(config).encode('utf-8')
            )

        except Exception as e:
            print('Request Timeout')
            return False

        # check for error
        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return False

        return True

    def post_autoTuneConfig(self, instanceID, byFeature=False, autoTunePV=True, autoTuneRange=True, exclusions={}):
        """autotunes the percent variation
        and the min and max for each feature
        """

        # build command
        config_cmd = self.url + 'autoTuneConfig/' + str(instanceID) + '?byFeature=' + str(byFeature).lower() + '&autoTunePV=' + str(autoTunePV).lower() + '&autoTuneRange=' + str(autoTuneRange).lower() + '&exclusions=' + str(exclusions)[1:-1].replace(' ','')

        # autotune parameters
        try:
            config_response = self.http.request(
                'POST',
                config_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False

        # check for error
        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return False

        return True

###########
# CLUSTER #
###########

    def post_data(self, instanceID, data, fileType='raw', gzip=False, metadata='', appendData=False, runNano=False, results=''):
        """posts the data and clusters it if runNano is True

        results per pattern options:
            ID = cluster ID
            SI = smoothed anomaly index
            RI = raw anomaly index
            FI = frequency index
            DI = distance index
            MD = metadata
        """

        self.filename = data
        # check filetype
        if not ".bin" in str(self.filename) and not '.csv' in str(self.filename):
            dtype = data.dtype
            if dtype == np.int64:
                filename = data.astype(np.int32)
            elif dtype == np.float64:
                filename = data.astype(np.float32)
            file_data = data.tostring()
            self.filename = 'dummy_filename.bin'
        else:
            with open(self.filename) as fp:
                file_data = fp.read()

        # build results command
        if str(results) == 'All':
            results_str = ',ID,SI,RI,FI,DI,MD'
        else:
            results_str = ''
            if 'ID' in str(results):
                results_str = results_str + ',ID'
            if 'SI' in str(results):
                results_str = results_str + ',SI'
            if 'RI' in str(results):
                results_str = results_str + ',RI'
            if 'FI' in str(results):
                results_str = results_str + ',FI'
            if 'DI' in str(results):
                results_str = results_str + ',DI'
            if 'MD' in str(results):
                results_str = results_str + ',MD'

        if metadata != '':
            body = {'data': (self.filename, file_data)}
        else:
            body = {'data': (self.filename, file_data),'metadata': metadata.replace(',','|').replace('{','').replace('}','').replace(' ','')}
        # build command
        dataset_cmd = self.url + 'data/' + str(instanceID) + '?runNano=' + str(run_nano).lower() + '&fileType=' + ('raw' if 'bin' in self.filename else 'csv') + '&gzip=' + str(gzip).lower() + '&results=' + results_str[1:] + '&appendData=' + str(append_data).lower()

        # post dataset
        try:
            dataset_response = self.http.request(
                'POST',
                dataset_cmd,
                headers={
                    'x-token': self.token
                },
                fields=body
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if dataset_response.status != 200 and dataset_response.status != 201:
            print(json.loads(dataset_response.data.decode('utf-8')))
            return False, None

        if not results:
            return True, None

        return True, json.loads(dataset_response.data.decode('utf-8'))

    def post_nanoRun(self, instanceID, results=''):
        """ clusters the data in the buffer
        returns any specified results

        results per pattern options:
            ID = cluster ID
            SI = smoothed anomaly index
            RI = raw anomaly index
            FI = frequency index
            DI = distance index
            MD = metadata
        """

        # build results command
        if str(results) == 'All':
            results_str = ',ID,SI,RI,FI,DI,MD'
        else:
            results_str = ''
            if 'ID' in str(results):
                results_str = results_str + ',ID'
            if 'SI' in str(results):
                results_str = results_str + ',SI'
            if 'RI' in str(results):
                results_str = results_str + ',RI'
            if 'FI' in str(results):
                results_str = results_str + ',FI'
            if 'DI' in str(results):
                results_str = results_str + ',DI'
            if 'MD' in str(results):
                results_str = results_str + ',MD'

        # build command
        nano_cmd = self.url + 'nanoRun/' + str(instanceID) + '?results=' + results_str[1:]

        # run nano
        try:
            nano_response = self.http.request(
                'POST',
                nano_cmd,
                headers={
                    'x-token': self.token
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if nano_response.status != 200 and nano_response.status != 201:
            print(json.loads(nano_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(nano_response.data.decode('utf-8'))

    def get_bufferStatus(self, instanceID):
        """ results related to the bytes processed/in the buffer
        """

        # build command
        results_cmd = self.url + 'bufferStatus/' + str(instanceID)

        # buffer status
        try:
            results_response = self.http.request(
                'GET',
                results_cmd,
                headers={
                    'x-token': self.token
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if results_response.status != 200 and results_response.status != 201:
            print(json.loads(results_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(results_response.data.decode('utf-8'))

    def get_nanoResults(self, instanceID, results='All'):
        """ results per pattern
        options:
            ID = cluster ID
            SI = smoothed anomaly index
            RI = raw anomaly index
            FI = frequency index
            DI = distance index
            MD = metadata
        """

        # build results command
        if str(results) == 'All':
            results_str = ',ID,SI,RI,FI,DI,MD'
        else:
            results_str = ''
            if 'ID' in str(results):
                results_str = results_str + ',ID'
            if 'SI' in str(results):
                results_str = results_str + ',SI'
            if 'RI' in str(results):
                results_str = results_str + ',RI'
            if 'FI' in str(results):
                results_str = results_str + ',FI'
            if 'DI' in str(results):
                results_str = results_str + ',DI'
            if 'MD' in str(results):
                results_str = results_str + ',MD'

        # build command
        results_cmd = self.url + 'nanoresults/' + str(instanceID) + '?results=' + results_str[1:]

        # pattern results
        try:
            results_response = self.http.request(
                'GET',
                results_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if results_response.status != 200 and results_response.status != 201:
            print(json.loads(results_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(results_response.data.decode('utf-8'))

    def get_nanoStatus(self, instanceID, results='All'):
        """results in relation to each cluster/overall stats

        results options:
        (includes 0 cluster)
            PCA = principal components
            clusterGrowth = indexes of each increase in cluster
            clusterSizes = number of patterns in each cluster
            anomalyIndexes = anomaly index
            frequencyIndexes = frequency index
            distanceIndexes = distance index

        (overall or no 0 cluster)
            patternMemory = base64 pattern memory
            totalInferences = total number of patterns clustered
            averageInferenceTime = time to cluster per pattern (not available if uploading from serialized nano)
            numClusters = total number of clusters (includes 0 cluster)
        """

        # build results command
        if str(results) == 'All':
            results_str = ',PCA,patternMemory,clusterGrowth,clusterSizes,anomalyIndexes,frequencyIndexes,distanceIndexes,totalInferences,averageInferenceTime,numClusters'
        else:
            results_str = ''
            if 'PCA' in str(results):
                results_str = results_str + ',PCA'
            if 'patternMemory' in str(results):
                results_str = results_str + ',patternMemory'
            if 'clusterGrowth' in str(results):
                results_str = results_str + ',clusterGrowth'
            if 'clusterSizes' in str(results):
                results_str = results_str + ',clusterSizes'
            if 'anomalyIndexes' in str(results):
                results_str = results_str + ',anomalyIndexes'
            if 'frequencyIndexes' in str(results):
                results_str = results_str + ',frequencyIndexes'
            if 'distanceIndexes' in str(results):
                results_str = results_str + ',distanceIndexes'
            if 'totalInferences' in str(results):
                results_str = results_str + ',totalInferences'
            if 'averageInferenceTime' in str(results):
                results_str = results_str + ',averageInferenceTime'
            if 'numClusters' in str(results):
                results_str = results_str + ',numClusters'

        # build command
        results_cmd = self.url + 'nanoStatus/' + str(instanceID) + '?results=' + results_str[1:]

        # cluster status
        try:
            results_response = self.http.request(
                'GET',
                results_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if results_response.status != 200 and results_response.status != 201:
            print(json.loads(results_response.data.decode('utf-8')))
            return False, None

        return True, json.loads(results_response.data.decode('utf-8'))
