
import urllib3
import json
import numpy as np
import struct

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
            return

        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return

        print(json.loads(instance_response.data.decode('utf-8'))['instanceID'])
        return

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
            return

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
                    'x-token': self.token,
                    'Content-Type': 'application/json'
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
            return

        if instance_response.status != 200 and instance_response.status != 201:
            print(json.loads(instance_response.data.decode('utf-8')))
            return

        print(json.loads(instance_response.data.decode('utf-8')))
        return

    # FIX THIS THIS NEEDS A FILE READER
    def getSnapshot(self, NanoInstanceID):
        """serializes the nano and saves it as a tar filename
        """

        snapshot_cmd = self.url + 'snapshot/' + str(NanoInstanceID)
        try:
            snapshot_response = self.http.request(
                'GET',
                snapshot_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'application/json'
                }
            )

        except Exception as e:
            print('Request Timeout')
            return

        if snapshot_response.status != 200 and snapshot_response.status != 201:
            print(json.loads(snapshot_response.data.decode('utf-8')))
            return

        print(json.loads(snapshot_response.data.decode('utf-8')))
        return

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
            return

        #open filename
        with open(self.filename) as fp:
            file_data = fp.read()

        #build command
        snapshot_cmd = self.url + 'snapshot/' + str(NanoInstanceID)

        #post dataset
        try:
            snapshot_response = self.http.request(
                'POST',
                snapshot_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'multipart/form-data'
                },
                fields={
                    'snapshot': (self.filename, file_data)
                }
            )

        except Exception as e:
            print('Request Timeout')
            return

        if snapshot_response.status != 200 and snapshot_response.status != 201:
            print(json.loads(snapshot_response.data.decode('utf-8')))
            return

        print(json.loads(snapshot_response.data.decode('utf-8')))
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
            return

        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return

        return json.loads(config_response.data.decode('utf-8'))

    def getConfigTemplate(self, numFeatures, numType, min=1, max=10, weight=1, percentVariation=0.05, accuracy=0.99, streamingWindow=1):
        """returns a json config version for the given Parameters
        """

        config_cmd = self.url + 'configTemplate?featureCount=' + str(numFeatures) + '&numericFormat' + str(numType) + '&minVal' + str(min) + '&maxVal' + str(max) + '&weight' + str(weight) + '&percentVariation' + str(percentVariation) + '&accuracy' + str(accuracy) + '&streamingWindow' + str(streamingWindow)


        try:
            config_response = self.url.request(
                'GET',
                config_cmd,
                headers={
                    'x-token': self.token,
                    'Content-Type': 'applicatin/json'
                }
            )

        except Exceptino as e:
            print('Request Timeout')
            return

        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return

        return json.loads(config_response.data.decode('utf-8'))


    def postClusterConfiguration(self, NanoInstanceID, JSONConfig):
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
            return

        if config_response.status != 200 and config_response.status != 201:
            print(json.loads(config_response.data.decode('utf-8')))
            return

        return json.loads(config_response.data.decode('utf-8'))













    def loadDataSet(self, filename):
        """Upload data set to server

        Notes:
            Filename must be binary or csv
        Args:
            filename (str): Full path to file.
        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`list` of :obj:`int`): The Width,Height of the received dataset
        """

        self.filename = filename

        #check filetype
        #if not ".pgm" in self.filename:
        #    print('Dataset Must Be In .pgm Format')
        #    return

        #open filename
        with open(self.filename) as fp:
            file_data = fp.read()

        #build command
        dataset_cmd = self.url + 'dataSet?gzip=false'
        if ".tar" in self.filename:
            dataset_cmd = self.url + 'dataSet?gzip=true'

        #post dataset
        try:
            load_response = self.http.request( 'POST', dataset_cmd, headers={'x-token': self.token}, fields={ 'binFile': (self.filename, file_data)} )
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(load_response)
        if isError:
            return

        #parse response
        load_dict = json.loads(load_response.data.decode('utf-8'))
        load_list = self.parseDictionary(load_dict, ['Width','Height'])

        #flag check
        self.is_dataset = True

        #release
        load_response.release_conn()

        return True, load_list


    def deleteDataSet(self):
        """Delete current dataset from server

        Args:

        Returns:
            bool: The return value. True for success, False otherwise.
        """
        #build command
        dataset_cmd = self.url + 'dataSet'

        #delete dataset
        try:
            del_response = self.http.request( 'DELETE', dataset_cmd, headers={'x-token': self.token} )
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(del_response)
        if isError:
            return

        #release
        del_response.release_conn()

        return True


    def setClusterParameters(self, accuracy, percentVariation, minVal, maxVal):
        """Set clustering parameters

        Args:
            accuracy (float): The accuracy between clusters
            percentVariation (float): The variation among clusters
            minVal (float): The minimum data value
            maxVal (float): The maximum data value
        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`list` of :obj:`float`): The received parameters (accuracy, percentVariation, minVal, maxVal)
        """

        #check dataset
        if not self.is_dataset:
            print('You Must First Upload Dataset')
            return

        self.accuracy = accuracy #0.99
        self.percentVariation = percentVariation #0.03
        self.minVal = minVal #0
        self.maxVal = maxVal #500

        #build body of parameters
        data = {'accuracy': self.accuracy, 'percentVariation': self.percentVariation, 'minVal': self.minVal, 'maxVal': self.maxVal}
        encoded_data = json.dumps(data).encode('utf-8')

        #build command
        parameter_cmd = self.url + 'clusteringParameters'

        #post clustering params
        try:
            param_set  = self.http.request( 'POST', parameter_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'}, body=encoded_data )
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(param_set)
        if isError:
            return

        #parse response
        param_dict = json.loads(param_set.data.decode('utf-8'))
        param_list = self.parseDictionary(param_dict, ['accuracy','percentVariation','minVal','maxVal'])

        #flag check
        self.is_parameter = True

        #release
        param_set.release_conn()

        return True, param_list


    def getClusterParameters(self):
        """Get Current clustering parameters

        Args:

        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`list` of :obj:`float`): The current server parameters (accuracy, percentVariation, minVal, maxVal)
        """
        #check dataset
        if not self.is_dataset or not self.is_parameter:
            print('You Must First Upload Dataset & Set Parameters')
            return

        #build command
        parameter_cmd = self.url + 'clusteringParameters'

        #post clustering params
        try:
            param_get  = self.http.request( 'GET', parameter_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'} )
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(param_get)
        if isError:
            return

        #parse response
        param_dict = json.loads(param_get.data.decode('utf-8'))
        param_list = self.parseDictionary(param_dict, ['accuracy','percentVariation','minVal','maxVal'])

        #release
        param_get.release_conn()

        #return
        return True, param_list


    def getClusterIds(self):
        """Get Cluster IDs from BN Server

        Args:

        Returns:
            bool: The return value. True for success, False otherwise.
            numpy.array: The clusters IDs. Array of size 1xn_Samples

        """

        #check dataset
        if not self.is_dataset or not self.is_parameter:
            print('You Must First Upload Dataset & Set Parameters')
            return

        #build command
        getid_cmd = self.url + 'clusterIDs'

        #get cluster ids
        try:
            id_response  = self.http.request( 'GET', getid_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'})
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(id_response)
        if isError:
            return

        #parse response
        id_dict = json.loads(id_response.data.decode('utf-8'))
        id_list = self.parseDictionary(id_dict, ['IDs'])[0]
        ids_np = np.array(id_list)

        #release
        id_response.release_conn()

        return True, ids_np

    def getClusterSummary(self):
        """Get cluster summary

        Args:

        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`list` of :obj:`float`): The summary data (clustersCreated, patternsClustered, timePerPatternMicroSec, totalTimeInSec)
        """

        #check dataset
        if not self.is_dataset or not self.is_parameter:
            print('You Must First Upload Dataset & Set Parameters')
            return

        #build command
        getsum_cmd = self.url + 'clusterSummary'

        #get cluster ids
        try:
            sum_response  = self.http.request( 'GET', getsum_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'})
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(sum_response)
        if isError:
            return

        #parse response
        sum_dict = json.loads(sum_response.data.decode('utf-8'))
        sum_list = self.parseDictionary(sum_dict, ['clustersCreated', 'patternsClustered', 'timePerPatternMicroSec', 'totalTimeInSec'])

        #release
        sum_response.release_conn()

        return True, sum_list

    def getClusterPCA(self):
        """Get cluster principal component analysis

        Args:

        Returns:
            bool: The return value. True for success, False otherwise.
            numpy.array: The principal components for each cluster index [r,g,b,anomoly]
        """

        #check dataset
        if not self.is_dataset or not self.is_parameter:
            print('You Must First Upload Dataset & Set Parameters')
            return

        #build command
        getpca_cmd = self.url + 'clusterPCA'

        #get cluster ids
        try:
            pca_response  = self.http.request( 'GET', getpca_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'})
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(pca_response)
        if isError:
            return

        #parse response
        pca_dict = json.loads(pca_response.data.decode('utf-8'))
        pca_list = self.parseDictionary(pca_dict, ['Values'])[0]
        pca_np = np.array(pca_list)

        #release
        pca_response.release_conn()

        return True, pca_np


    def CSVToPGM(self, csvfile, pgmfile, datatype):
        """Convert CSV file to PGM

        Args:
            csvfile (str): The full path to the local csv file
            pgmfile (str): The full path where we store the new pgm file
            datatype (str): Data type for the csv file ('int','float','native')
        Returns:
            bool: The return value. True for success, False otherwise.
            int: server response status
        """
        self.csvfile = csvfile #'/Users/rodneydockter/python_ws/nativeset1.csv'

        #open filename
        with open(self.csvfile) as fp:
            csv_data = fp.read()

        #build command
        csv_cmd = self.url + 'csvToDataSet?type=' + str(datatype)

        #post csv
        try:
            csv_response = self.http.request( 'POST', csv_cmd, headers={'x-token': self.token}, fields={ 'csvFile': (self.csvfile, csv_data)} )
        except Exception as e:
            print('Request Timeout')
            return

        #check status
        isError, status = self.responseStatus(csv_response)
        if isError:
            return False, csv_response.status

        #download response data
        pgmout = open(pgmfile, 'wb')
        pgmout.write(csv_response.data)
        pgmout.close()

        #release
        csv_response.release_conn()

        return True, csv_response.status


    ##################
    #     Utils      #
    ##################

    def responseStatus(self, response):
        """Check status of http response for errors

        Args:
            response (int): The http request response
        Returns:
            bool: Is error. False if valid status. True if error occured.
            int: Server response status
        """
        #check status of http response
        if response.status >= 200 and response.status < 300:
            return False, response.status #No Error
        elif response.status >= 300 and response.status < 400:
            print('Redirection Error ', response.status)
            print(response.data)
            return True, response.status #Redirection Messages
        elif response.status >= 400 and response.status < 500:
            print('Client Error ', response.status)
            print(response.data)
            return True, response.status #Client Error
        elif response.status >= 500 and response.status < 600:
            print('Server Error ', response.status)
            print(response.data)
            return True, response.status #Server Error


    def parseDictionary(self, dict_in, keys):
        """Parse elements in dictionary using key

        Args:
            dict_in (dict): An existing dictionary
            keys (:obj:`list` of :obj:`str`): A list of keys to find
        Returns:
            (:obj:`list` of :obj:`str`): List of floats from dictionary. In order of keys.

        """
        elements = []
        for key in keys:
            elements.append(dict_in.get(key))
        return elements

    def scaleDataNative(self, np_data, scalefactor):
        """Scale numpy array data to 'native' range

        Notes:
            Native range is an unsigned int 0<x<maxval. Used by BoonNano
        Args:
            np_data (numpy.array): A numpy array of unscaled data
            scalefactor (float): scale factor to shift and round float values to integers
        Returns:
            numpy.array: The scaled native data
            max_scaled: The new maximum value in the data
        """
        #allocate
        data_native = np.zeros_like(np_data)
        #Grab unscaled minimum
        min_raw = np.amin(np_data,axis=0)
        max_raw = np.amax(np_data,axis=0)
        #compute scale factor so each feature maps to the same integer range
        scaling_range = scalefactor / np.subtract(max_raw,min_raw)
        #shift from min
        for i in range(np.shape(np_data)[0]):
            row = np_data[i,:]
            row_shift = np.subtract(row, min_raw) #0 min
            row_scaled = np.rint(np.multiply(row_shift,scaling_range)) #scale to integers
            data_native[i,:] = row_scaled

        #return data and range
        max_scaled = np.amax(data_native,axis=0)
        return data_native, max_scaled
