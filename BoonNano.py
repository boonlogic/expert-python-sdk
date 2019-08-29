
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

    Example Usage:
        bn = BoonNano('localhost',5010,'<token>')
        success, size = bn.loadDataSet('~/nativeset510.pgm')
        success, params = bn.setClusterParameters(0.99, 0.03, 0, 500)
        success, ids = bn.getClusterIds()

    """
    def __init__(self, host, port, timeout=60.0):
        """BoonNano __init__ method.

        Args:
            host (str): Host Address.
            port (int): Remote Port.
            timeout (float): HTTP Request Timeout
        Returns:


        """
        #arguments
        self.timeout = timeout
        self.token = "2B69F78F61A572DBF8D1E44548B48"

        self.host = host
        self.port = port
        self.primary = '/expert/v2/'
        self.url = 'http://' + str(self.host) + ':' + str(self.port) + self.primary

        #create pool manager
        if(self.timeout == 0):
            self.http = urllib3.PoolManager()
        else:
            self.http = urllib3.PoolManager(timeout=self.timeout)

        #state checks
        self.is_dataset = False
        self.is_parameter = False

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

    def setHostPort(self, host, port):
        """Change the host and port

        Args:
            host (str): Host Address.
            port (int): Remote Port.
        Returns:

        """
        self.host = host
        self.port = port
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

        instance_cmd = self.url + 'nanoInstance/' + str(NanoInstanceID)
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
            return None

        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return None

        return json.loads(instance_response.data.decode('utf-8'))['instanceID']

    def getInstanceStatus(self, NanoInstanceID):
        """returns true if NanoInstanceID is a running instance
        and false otherwise
        """

        instance_cmd = self.url + 'nanoInstance/' + str(NanoInstanceID)
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
            return False

        if instance_response.status != 200 and instance_response.status != 201:
            print('false')
            return False

        print('true')
        return True

    def deleteInstance(self, NanoInstanceID=''):
        """If an instance number is not given,
        the nano will delete all running instances
        """

        if NanoInstanceID == '':
            instance_cmd = self.url + 'nanoInstances'
        else:
            instance_cmd = self.url + 'nanoInstance/' + str(NanoInstanceID)

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
            return

        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return

        return

    def getRunningInstances(self):
        """returns list of nano instances running
        """

        instance_cmd = self.url + 'nanoInstances'

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
            return None

        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return None

        return json.loads(instance_response.data.decode('utf-8'))

##################
# CONFIGURATIONS #
##################

    # FIX THIS THIS NEEDS A FILE READER
    def saveSnapshot(self, NanoInstanceID, filename):
        """serializes the nano and saves it as a tar filename
        """

        snapshot_cmd = self.url + 'snapshot/' + str(NanoInstanceID)
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
            return

        if snapshot_response.status != 200 and snapshot_response.status != 201:
            print(json.loads(snapshot_response.data.decode('utf-8')))
            return

        self.filename = filename
        fp = open(self.filename, 'wb')
        fp.write(snapshot_response.data)
        fp.close
        return 'Success'

    # TEST THIS - HOW TO TELL IT A DATA FILE
    def postSnapshot(self, NanoInstanceID, filename):
        """deserialize existing nano
        upload file to given instance

        NOTE: must be of type tar
        """

        self.filename = filename

        #check filetype
        if not ".tar" in self.filename:
            print('Dataset Must Be In .tar Format')
            return None

        with open(self.filename, "rb") as fp:
            tar_data = fp.read()

        #build command
        snapshot_cmd = self.url + 'snapshot/' + str(NanoInstanceID)

        #post dataset
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
            print(e)
            return

        if snapshot_response.status != 200 and snapshot_response.status != 201:
            print(json.loads(snapshot_response.data.decode('utf-8')))
            return

        return

    def getClusterConfiguration(self, NanoInstanceID):
        """returns the posted clustering configuration
        """

        config_cmd = self.url + 'clusterConfig/' + str(NanoInstanceID)
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
            return None

        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return None

        return json.loads(config_response.data.decode('utf-8'))

    def getConfigTemplate(self, numFeatures, numType, min=1, max=10, percentVariation=0.05, streamingWindow=1, weight=1, accuracy=0.99):
        """returns a json config version for the given Parameters
        """

        config_cmd = self.url + 'configTemplate?featureCount=' + str(numFeatures) + '&numericFormat=' + str(numType) + '&minVal=' + str(min) + '&maxVal=' + str(max) + '&weight=' + str(weight) + '&percentVariation=' + str(percentVariation) + '&accuracy=' + str(accuracy) + '&streamingWindowSize=' + str(streamingWindow)

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
            return None

        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return None

        return json.loads(config_response.data.decode('utf-8'))

    def postClusterConfiguration(self, NanoInstanceID, JSONConfig):
        """returns the posted clustering configuration
        """

        config_cmd = self.url + 'clusterConfig/' + str(NanoInstanceID)
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
            return

        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return

        return


    def autotune(self, NanoInstanceID, byFeature=False, autotunePV=True, autotuneRange=True, exclusions={}):
        """autotunes the percent variation
        and the min and max for each feature
        """

        config_cmd = self.url + 'autoTuneConfig/' + str(NanoInstanceID) + '?byFeature=' + str(byFeature).lower() + '&autoTunePV=' + str(autotunePV).lower() + '&autoTuneRange=' + str(autotuneRange).lower() + '&exclusions=' + str(exclusions)[1:-1].replace(' ','')
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
            return

        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return

        return

###########
# CLUSTER #
###########

    def postData(self, NanoInstanceID, filename, runNano=False, appendData=False, Results=''):
        """posts the data and clusters it if runNano is True
        """
        self.filename = filename
        #check filetype
        if not ".bin" in str(self.filename) and not '.csv' in str(self.filename):
            # write filename to a temporary file to upload
            self.filename = 'Temp_data.csv'
            np.savetxt(self.filename, filename, delimiter=',')
        else:
            self.filename = filename

        #open filename
        with open(self.filename) as fp:
            file_data = fp.read()

        if 'Temp_data.csv' in self.filename:
            os.remove(self.filename)


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

        #build command
        dataset_cmd = self.url + 'data/' + str(NanoInstanceID) + '?runNano=' + str(runNano).lower() + '&fileType=' + ('raw' if 'bin' in self.filename else 'csv') + '&gzip=false' + '&results=' + results_str[1:] + '&appendData=' + str(appendData).lower()
        #post dataset
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
            return None

        if dataset_response.status != 200 and dataset_response.status != 201:
            print(json.loads(dataset_response.data.decode('utf-8')))
            return None

        return json.loads(dataset_response.data.decode('utf-8'))

    def postNanoRun(self, NanoInstanceID, Results=''):

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

        nano_cmd = self.url + 'nanoRun/' + str(NanoInstanceID) + '?results=' + results_str[1:]
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
            return None

        if nano_response.status != 200 and nano_response.status != 201:
            print(json.loads(nano_response.data.decode('utf-8')))
            return None

        return json.loads(nano_response.data.decode('utf-8'))

    def getBufferStatus(self, NanoInstanceID):

        results_cmd = self.url + 'bufferStatus/' + str(NanoInstanceID)
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
            return None

        if results_response.status != 200 and results_response.status != 201:
            print(json.loads(results_response.data.decode('utf-8')))
            return None

        return json.loads(results_response.data.decode('utf-8'))

    def getNanoResults(self, NanoInstanceID, Results='All'):

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

        results_cmd = self.url + 'nanoResults/' + str(NanoInstanceID) + '?results=' + results_str[1:]
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
            return None

        if results_response.status != 200 and results_response.status != 201:
            print(json.loads(results_response.data.decode('utf-8')))
            return None

        return json.loads(results_response.data.decode('utf-8'))

    def getNanoStatus(self, NanoInstanceID, Results='All'):

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

        results_cmd = self.url + 'nanoStatus/' + str(NanoInstanceID) + '?results=' + results_str[1:]
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
            return None

        if results_response.status != 200 and results_response.status != 201:
            print(json.loads(results_response.data.decode('utf-8')))
            return None

        return json.loads(results_response.data.decode('utf-8'))
