
import urllib3
import json
import numpy as np
import struct

############################
# BoonNano AD Python API v1.0 #
############################

class BoonNanoAD:
    """Python class to perform clustering with BoonNanoAD Server

    Args:
        
    Returns:

    Example Usage:
        bn = BoonNanoAD('localhost',5008,'<token>')
        success, params = bn.setClusterParameters('native', false, 30, 0, 1000, 0.05, 0.99)
        success, anomalyInfo = bn.computeAnomalyIndex([1.0,2.0,3.0])

    """
    def __init__(self, host, port, token, timeout):
        """BoonNano __init__ method.

        Args:
            host (str): Host Address.
            port (int): Remote Port.
            token (str): API Access token.
            timeout (float): HTTP Request Timeout
        Returns:
            
            
        """
        #arguments
        self.host = host
        self.port = port
        self.token = str(token)
        self.timeout = timeout 

        #construct request address
        self.primary = '/expert-ad/v1/'
        self.url = 'http://' + str(self.host) + ':' + str(self.port) + self.primary
        
        #create pool manager
        if(self.timeout == 0):
            self.http = urllib3.PoolManager()
        else:
            self.http = urllib3.PoolManager(timeout=self.timeout)
            
            
        self.data_response = None
        
        #state checks
        self.is_init = False
        self.is_sample = False

        #parameters
        print '#################################'
        print 'Opening BoonNanoAD Client'
        print 'URL: ', self.url
        print '#################################'


    def __del__(self):
        """Destructor Method.

                        
        """
        print('Closing Pool')
        self.http.clear()
        if(self.data_response is not None):
            self.data_response.release_conn()

    def setToken(self, token):
        """Change the API Access Token

        Args:
            token (str): The new access token
        Returns:
                        
        """
        self.token = str(token)

    def setHostPort(self, host, port):
        """Change the host and port

        Args:
            host (str): Host Address.
            port (int): Remote Port.
        Returns:
                        
        """
        self.host = host 
        self.port = port 
        self.url = 'http://' + str(self.host) + ':' + str(self.port) + self.primary


    ##########################
    #  Server Requests       #
    ##########################
    

    def computeAnomalyIndex(self, data):
        """Upload data sample to server, get anomaly index

        Args:
            data (list): Single data sample
        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`dict` of :obj:`float`): The 'sample','ID','raw','smooth','count' of the sent data
        """
         
        #check dataset
        if not self.is_init:
            print('You Must First Set Parameters')
            return False, None
        
        self.data = data
        datafield = {'Sample': self.data}
        encoded_data = json.dumps(datafield).encode('utf-8')

        #build command
        data_cmd = self.url + 'dataSample'
    
        
        #post data
        try:
            self.data_response = self.http.request('POST', data_cmd, headers={'x-token': self.token, 'connection': 'keep-alive', 'Content-Type': 'application/json'}, body=encoded_data )
        except Exception as e:
            print('Request Timeout')
            return False, None
    
        
        #check status
        isError, status = self.responseStatus(self.data_response)
        if isError:
            return False, None


        #parse response for sample and response
        data_dict = json.loads(self.data_response.data.decode('utf-8'))
        data_list = self.parseDictionary(data_dict, ['Response'])[0]
        
        self.is_sample = True
        
        self.data_response.release_conn()
        
        return True, data_list

    def computeAnomalyIndexRaw(self, data):
        """Upload binary data sample to server, get anomaly index

        Args:
            data (list): Single data sample
        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`dict` of :obj:`float`): The 'sample','ID','raw','smooth','count' of the sent data
        """
         
        #check dataset
        if not self.is_init:
            print('You Must First Set Parameters')
            return False, None
        
        self.data = data
        encoded_data = struct.pack('%if' % len(self.data), *self.data) #convert to binary blob

        #build command
        data_cmd = self.url + 'rawDataSample'
    
        #post data
        try:
            self.data_response = self.http.request('POST', data_cmd, headers={'x-token': self.token, 'connection': 'keep-alive', 'Content-Type': 'application/octet-stream'}, body=encoded_data )
        except Exception as e:
            print('Request Timeout')
            return False, None
    
        
        #check status
        isError, status = self.responseStatus(self.data_response)
        if isError:
            return False, None


        #parse response for sample and response
        data_dict = json.loads(self.data_response.data.decode('utf-8'))
        data_list = self.parseDictionary(data_dict, ['Response'])[0]
        
        self.is_sample = True
        
        self.data_response.release_conn()
        
        return True, data_list

    def setClusterParameters(self, numericType, streaming, patternLength, minVal, maxVal, percentVariation, accuracy):
        """Set clustering parameters

        Args:
            numericType (string): The data type
            streaming (bool): if single sensor
            patternLength (int): window size
            minVal (float): The minimum data value
            maxVal (float): The maximum data value
            percentVariation (float): The variation among clusters
            accuracy (float): The accuracy between clusters
            
        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`list` of :obj:`float`): The received parameters ['numericType','streaming','patternLength','minVal','maxVal','percentVariation','accuracy']
        """
        
        self.numericType = numericType #'float', 'int', 'native'
        self.streaming = streaming #true
        self.patternLength = patternLength #50

        self.minVal = minVal #0
        self.maxVal = maxVal #500
        self.accuracy = accuracy #0.99
        self.percentVariation = percentVariation #0.03
        

        #build body of parameters
        data = {'numericType': self.numericType, 'streaming': self.streaming, 'patternLength': self.patternLength, 'minVal': self.minVal, 'maxVal': self.maxVal, 'percentVariation': self.percentVariation, 'accuracy': self.accuracy}
        encoded_data = json.dumps(data).encode('utf-8')

        #build command
        parameter_cmd = self.url + 'clusteringParameters'

        #post clustering params
        try:
            param_set  = self.http.request( 'POST', parameter_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'}, body=encoded_data )
        except Exception as e:
            print('Request Timeout')
            return False, None
        
        #check status
        isError, status = self.responseStatus(param_set)
        if isError:
            return False, None

        #parse response
        param_dict = json.loads(param_set.data.decode('utf-8'))
        param_list = self.parseDictionary(param_dict, ['numericType','streaming','patternLength','minVal','maxVal','percentVariation','accuracy'])

        #flag check
        self.is_init = True

        #release
        param_set.release_conn()

        return True, param_list


    def getClusterParameters(self):
        """Get Current clustering parameters

        Args:

        Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`list` of :obj:`float`): The current server parameters ['numericType','streaming','patternLength','minVal','maxVal','percentVariation','accuracy']
        """
        
        #check dataset
        if not self.is_init:
            print('You Must First Set Parameters')
            return False, None
        
        #build command
        parameter_cmd = self.url + 'clusteringParameters'

        #post clustering params
        try:
            param_get  = self.http.request( 'GET', parameter_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'} )
        except Exception as e:
            print('Request Timeout')
            return False, None
        
        #check status
        isError, status = self.responseStatus(param_get)
        if isError:
            return False, None

        #parse response
        param_dict = json.loads(param_get.data.decode('utf-8'))
        param_list = self.parseDictionary(param_dict, ['numericType','streaming','patternLength','minVal','maxVal','percentVariation','accuracy'])

        #release
        param_get.release_conn()

        #return 
        return True, param_list
    
    def getLastAnomalyInfo(self):
        """Get last Anomaly Info from BN Server

        Args:
            
         Returns:
            bool: The return value. True for success, False otherwise.
            (:obj:`dict` of :obj:`int`): The 'sample','ID','raw','smooth','count' of the last uploaded data
        """
        
        #check dataset
        if not self.is_init or not self.is_sample:
            print('You Must First Set Parameters and Upload Data')
            return False, None
        
        #build command
        getid_cmd = self.url + 'dataSample'

        #get cluster ids
        try:
            ai_response  = self.http.request( 'GET', getid_cmd, headers={'x-token': self.token, 'Content-Type': 'application/json'})
        except Exception as e:
            print('Request Timeout')
            return False, None
        
        #check status
        isError, status = self.responseStatus(ai_response)
        if isError:
            return False, None


        #parse response for sample and response
        data_dict = json.loads(ai_response.data.decode('utf-8'))
        data_list = self.parseDictionary(data_dict, ['Response'])[0]

        ai_response.release_conn()
        
        return True, data_list

   


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
            print 'Redirection Error ', response.status
            print(response.data)
            return True, response.status #Redirection Messages
        elif response.status >= 400 and response.status < 500:
            print 'Client Error ', response.status
            print(response.data)
            return True, response.status #Client Error 
        elif response.status >= 500 and response.status < 600:
            print 'Server Error ', response.status
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


