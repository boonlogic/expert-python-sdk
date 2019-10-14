
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
        success, nano_results = bn.runNano(instance, Results='All')
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

    def setHostPort(self, host, port, token='2B69F78F61A572DBF8D1E44548B48'):
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


#############
# INSTANCES #
#############

    def getInstance(self, NanoInstanceID=''):
        """If an instance number is not given,
        the nano will return the next open number
        as a running instance
        """

        # build command
        instance_cmd = self.url + 'nanoInstance/' + str(NanoInstanceID)

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

    def getInstanceStatus(self, NanoInstanceID):
        """returns true if NanoInstanceID is a running instance
        and false otherwise
        """

        # build command
        instance_cmd = self.url + 'nanoInstance/' + str(NanoInstanceID)

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

    def deleteInstance(self, NanoInstanceID=''):
        """If an instance number is not given,
        the nano will delete ALL running instances
        """

        # build command
        if NanoInstanceID == '':
            # call to delete all instances
            instance_cmd = self.url + 'nanoInstances'
        else:
            # call to delete specified instance number
            instance_cmd = self.url + 'nanoInstance/' + str(NanoInstanceID)

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

    def getRunningInstances(self):
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

    def saveSnapshot(self, NanoInstanceID, filename):
        """serializes the nano and saves it as a tar filename
        """

        # build command
        snapshot_cmd = self.url + 'snapshot/' + str(NanoInstanceID)

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

    def postSnapshot(self, NanoInstanceID, filename):
        """deserialize existing nano
        upload file to given instance

        NOTE: must be of type tar
        """

        self.filename = filename

        #check filetype
        if not ".tar" in self.filename:
            print('Dataset Must Be In .tar Format')
            return False

        with open(self.filename, "rb") as fp:
            tar_data = fp.read()

        # build command
        snapshot_cmd = self.url + 'snapshot/' + str(NanoInstanceID)

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

    def getClusterConfiguration(self, NanoInstanceID):
        """returns the posted clustering configuration
        """

        # build command
        config_cmd = self.url + 'clusterConfig/' + str(NanoInstanceID)

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

    def getConfigTemplate(self, numFeatures, numType, min=1, max=10, percentVariation=0.05, streamingWindow=1, weight=1, accuracy=0.99):
        """returns a json config version for the given Parameters
        """

        # build command
        config_cmd = self.url + 'configTemplate?featureCount=' + str(numFeatures) + '&numericFormat=' + str(numType) + '&minVal=' + str(min) + '&maxVal=' + str(max) + '&weight=' + str(weight) + '&percentVariation=' + str(percentVariation) + '&accuracy=' + str(accuracy) + '&streamingWindowSize=' + str(streamingWindow)

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

    def postClusterConfiguration(self, NanoInstanceID, JSONConfig):
        """returns the posted clustering configuration
        """

        # build command
        config_cmd = self.url + 'clusterConfig/' + str(NanoInstanceID)

        # post config
        try:
            config_response = self.http.request(
                'POST',
                config_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                },
                body=json.dumps(JSONConfig).encode('utf-8')
            )

        except Exception as e:
            print('Request Timeout')
            return False

        # check for error
        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return False

        return True

    def autotune(self, NanoInstanceID, byFeature=False, autotunePV=True, autotuneRange=True, exclusions={}):
        """autotunes the percent variation
        and the min and max for each feature
        """

        # build command
        config_cmd = self.url + 'autoTuneConfig/' + str(NanoInstanceID) + '?byFeature=' + str(byFeature).lower() + '&autoTunePV=' + str(autotunePV).lower() + '&autoTuneRange=' + str(autotuneRange).lower() + '&exclusions=' + str(exclusions)[1:-1].replace(' ','')

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

    def uploadData(self, NanoInstanceID, filename, runNano=False, appendData=False, Results='', silent=False):
        """posts the data and clusters it if runNano is True

        results per pattern options:
            ID = cluster ID
            SI = smoothed anomaly index
            RI = raw anomaly index
            FI = frequency index
            DI = distance index
            GR = ???
            MD = metadata
        """

        self.filename = filename
        # check filetype
        if not ".bin" in str(self.filename) and not '.csv' in str(self.filename):
            dtype = filename.dtype
            if dtype == np.int64:
                if not silent:
                    print("BoonNano: uploadData: Recasting numpy array from np.int64 -> np.int32")
                filename = filename.astype(np.int32)
            elif dtype == np.float64:
                if not silent:
                    print("BoonNano: uploadData: Recasting numpy array from np.float64 -> np.float32")
                filename = filename.astype(np.float32)
            else:
                if not silent:
                    print("BoonNano: uploadData: Uploading numpy array of type {}".format(filename.dtype))
            file_data = filename.tostring()
            self.filename = 'dummy_filename.bin'
        else:
            with open(self.filename) as fp:
                file_data = fp.read()

        # build results command
        if str(Results) == 'All':
            results_str = ',ID,SI,RI,FI,DI,GR,MD'
        else:
            results_str = ''
            if 'ID' in str(Results):
                results_str = results_str + ',ID'
            if 'SI' in str(Results):
                results_str = results_str + ',SI'
            if 'RI' in str(Results):
                results_str = results_str + ',RI'
            if 'FI' in str(Results):
                results_str = results_str + ',FI'
            if 'DI' in str(Results):
                results_str = results_str + ',DI'
            if 'GR' in str(Results):
                results_str = results_str + ',GR'
            if 'MD' in str(Results):
                results_str = results_str + ',MD'

        # build command
        dataset_cmd = self.url + 'data/' + str(NanoInstanceID) + '?runNano=' + str(runNano).lower() + '&fileType=' + ('raw' if 'bin' in self.filename else 'csv') + '&gzip=false' + '&results=' + results_str[1:] + '&appendData=' + str(appendData).lower()

        # post dataset
        try:
            dataset_response = self.http.request(
                'POST',
                dataset_cmd,
                headers={
                    'x-token': self.token
                },
                fields={
                    'data': (self.filename, file_data)
                }
            )

        except Exception as e:
            print('Request Timeout')
            return False, None

        # check for error
        if dataset_response.status != 200 and dataset_response.status != 201:
            print(json.loads(dataset_response.data.decode('utf-8')))
            return False, None

        if not Results:
            return True, None

        return True, json.loads(dataset_response.data.decode('utf-8'))

    def runNano(self, NanoInstanceID, Results=''):
        """ clusters the data in the buffer
        returns any specified results

        results per pattern options:
            ID = cluster ID
            SI = smoothed anomaly index
            RI = raw anomaly index
            FI = frequency index
            DI = distance index
            GR = ???
            MD = metadata
        """

        # build results command
        if str(Results) == 'All':
            results_str = ',ID,SI,RI,FI,DI,GR,MD'
        else:
            results_str = ''
            if 'ID' in str(Results):
                results_str = results_str + ',ID'
            if 'SI' in str(Results):
                results_str = results_str + ',SI'
            if 'RI' in str(Results):
                results_str = results_str + ',RI'
            if 'FI' in str(Results):
                results_str = results_str + ',FI'
            if 'DI' in str(Results):
                results_str = results_str + ',DI'
            if 'GR' in str(Results):
                results_str = results_str + ',GR'
            if 'MD' in str(Results):
                results_str = results_str + ',MD'

        # build command
        nano_cmd = self.url + 'nanoRun/' + str(NanoInstanceID) + '?results=' + results_str[1:]

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

    def getBufferStatus(self, NanoInstanceID):
        """ results related to the bytes processed/in the buffer
        """

        # build command
        results_cmd = self.url + 'bufferStatus/' + str(NanoInstanceID)

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

    def getNanoResults(self, NanoInstanceID, Results='All'):
        """ results per pattern
        options:
            ID = cluster ID
            SI = smoothed anomaly index
            RI = raw anomaly index
            FI = frequency index
            DI = distance index
            GR = ???
            MD = metadata
        """

        # build results command
        if str(Results) == 'All':
            results_str = ',ID,SI,RI,FI,DI,GR,MD'
        else:
            results_str = ''
            if 'ID' in str(Results):
                results_str = results_str + ',ID'
            if 'SI' in str(Results):
                results_str = results_str + ',SI'
            if 'RI' in str(Results):
                results_str = results_str + ',RI'
            if 'FI' in str(Results):
                results_str = results_str + ',FI'
            if 'DI' in str(Results):
                results_str = results_str + ',DI'
            if 'GR' in str(Results):
                results_str = results_str + ',GR'
            if 'MD' in str(Results):
                results_str = results_str + ',MD'

        # build command
        results_cmd = self.url + 'nanoResults/' + str(NanoInstanceID) + '?results=' + results_str[1:]

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

    def getNanoStatus(self, NanoInstanceID, Results='All'):
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
        if str(Results) == 'All':
            results_str = ',PCA,patternMemory,clusterGrowth,clusterSizes,anomalyIndexes,frequencyIndexes,distanceIndexes,totalInferences,averageInferenceTime,numClusters'
        else:
            results_str = ''
            if 'PCA' in str(Results):
                results_str = results_str + ',PCA'
            if 'patternMemory' in str(Results):
                results_str = results_str + ',patternMemory'
            if 'clusterGrowth' in str(Results):
                results_str = results_str + ',clusterGrowth'
            if 'clusterSizes' in str(Results):
                results_str = results_str + ',clusterSizes'
            if 'anomalyIndexes' in str(Results):
                results_str = results_str + ',anomalyIndexes'
            if 'frequencyIndexes' in str(Results):
                results_str = results_str + ',frequencyIndexes'
            if 'distanceIndexes' in str(Results):
                results_str = results_str + ',distanceIndexes'
            if 'totalInferences' in str(Results):
                results_str = results_str + ',totalInferences'
            if 'averageInferenceTime' in str(Results):
                results_str = results_str + ',averageInferenceTime'
            if 'numClusters' in str(Results):
                results_str = results_str + ',numClusters'

        # build command
        results_cmd = self.url + 'nanoStatus/' + str(NanoInstanceID) + '?results=' + results_str[1:]

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
