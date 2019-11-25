from urllib3 import PoolManager
import json
import numpy as np
import os
from os.path import expanduser

###########
# GLOBALS #
###########

############################
# BoonNano Python API v2.1 #
############################

def setup_connection(user, authentication_path="~/.BoonLogic", host="", port="", timeout=60.0):
    """BoonNano __init__ method.
    Args:
        host (str): Host Address.
        port (int): Remote Port.
        timeout (float): HTTP Request Timeout
    Returns:


    """

    with open (expanduser(authentication_path), "r") as json_file:
        token = json.load(json_file)

    try:
        token = token[user]
    except Exception as e:
        print("User does not exist")
        return

    #look for token in file
    try:
        global xtoken
        xtoken = token['x-token']
    # set token to be empty string
    except Exception as e:
        xtoken = ""

    try:
        file_host = token['server']
        if ':' in file_host:
            file_port = file_host[file_host.index(':') + 1: ]
            file_host = file_host[ :file_host.index(':')]
        else:
            file_port = ""
    except Exception as e:
        #server is empty
        file_host = ""
        file_port = ""

    if ':' in host:
        file_port = host[host.index(':') + 1: ]
        file_host = host[ :host.index(':')]
    elif host != "":
        file_host = host

    if port != "":
        file_port = port

    primary = '/expert/v2/'

    global url
    url = 'http://' + str(file_host) + ':' + str(file_port) + primary

    #create pool manager
    if(timeout == 0):
        global http
        http = PoolManager()
    else:
        http = PoolManager(timeout)

def close_connection():
    # Destructor Method.
    http.clear()

##########################
#  Server Requests       #
##########################

###########
# GENERAL #
###########

def get_version():
    """gives the version of the api running"""
    # build command (minus the v2 portion)
    try:
        version_cmd = url[:-3] + 'version'
    except NameError as e:
        print('setup connection first')
        return False, None

    # call the version number
    try:
        version_response = http.request(
            'GET',
            version_cmd,
            headers={
                'x-token': xtoken,
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

def create_instance(instance_id=''):
    """If an instance number is not given,
    the nano will return the next open number
    as a running instance
    """

    # build command
    try:
        instance_cmd = url + 'nanoInstance/' + str(instance_id)
    except NameError as e:
        print('setup connection first')
        return False, None

    # initialize instance
    try:
        instance_response = http.request(
            'POST',
            instance_cmd,
            headers={
                'x-token': xtoken,
                'Content-Type': 'application/json'
            }
        )

    except Exception as e:
        print('Request Timeout')
        return False, None

    # check for error
    if instance_response.status != 200 and instance_response.status != 201:
        if instance_id != '' and instance_response.status == 400:
            return True, instance_id
        print(json.loads(instance_response.data.decode('utf-8')))
        return False, None

    return True, json.loads(instance_response.data.decode('utf-8'))['instanceID']

def is_running_instance(instance_id):
    """returns true if instance_id is a running instance
    and false otherwise
    """

    # build command
    try:
        instance_cmd = url + 'nanoInstance/' + str(instance_id)
    except NameError as e:
        print('setup connection first')
        return False, None

    # check status of instance
    try:
        instance_response = http.request(
            'GET',
            instance_cmd,
            headers={
                'x-token': xtoken,
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

def delete_instance(instance_id=''):
    """If an instance number is not given,
    the nano will delete ALL running instances
    """
    try:
        # build command
        if instance_id == '':
            # call to delete all instances
            instance_cmd = url + 'nanoInstances'
        else:
            # call to delete specified instance number
            instance_cmd = url + 'nanoInstance/' + str(instance_id)
    except NameError as e:
        print('setup connection first')
        return False

    # delete instance(s)
    try:
        instance_response = http.request(
            'DELETE',
            instance_cmd,
            headers={
                'x-token': xtoken
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

def get_running_instances():
    """returns list of nano instances running
    """

    try:
        # build command
        instance_cmd = url + 'nanoInstances'
    except NameError as e:
        print('setup connection first')
        return False, None

    # list of running instances
    try:
        instance_response = http.request(
            'GET',
            instance_cmd,
            headers={
                'x-token': xtoken,
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

def save_snapshot(instance_id, filename):
    """serializes the nano and saves it as a tar filename
    """

    try:
        # build command
        snapshot_cmd = url + 'snapshot/' + str(instance_id)
    except NameError as e:
        print('setup connection first')
        return False

    # serialize nano
    try:
        snapshot_response = http.request(
            'GET',
            snapshot_cmd,
            headers={
                'x-token': xtoken
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
    fp = open(filename, 'wb')
    fp.write(snapshot_response.data)
    fp.close

    return True

def load_snapshot(instance_id, filename):
    """deserialize existing nano
    upload file to given instance

    NOTE: must be of type tar
    """

    # check filetype
    if not ".tar" in filename:
        print('Dataset Must Be In .tar Format')
        return False

    with open(filename, "rb") as fp:
        tar_data = fp.read()

    try:
        # build command
        snapshot_cmd = url + 'snapshot/' + str(instance_id)
    except NameError as e:
        print('setup connection first')
        return False

    # post serialized nano
    try:
        snapshot_response = http.request(
            'POST',
            snapshot_cmd,
            headers={
                'x-token': xtoken
            },
            fields={
                'snapshot': (filename, tar_data)
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

def get_config(instance_id):
    """returns the posted clustering configuration
    """

    try:
        # build command
        config_cmd = url + 'clusterConfig/' + str(instance_id)
    except NameError as e:
        print('setup connection first')
        return False, None

    # get config
    try:
        config_response = http.request(
            'GET',
            config_cmd,
            headers={
                'x-token': xtoken,
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

def generate_config(numeric_format, feature_count, min=1, max=10, weight=1, percent_variation=0.05, streaming_window=1, accuracy=0.99):
    """returns a json config version for the given Parameters
    """

    # build command
    config_cmd = url + 'configTemplate?featureCount=' + str(feature_count) + '&numericFormat=' + str(numeric_format) + '&minVal=' + str(min) + '&maxVal=' + str(max) + '&weight=' + str(weight) + '&percentVariation=' + str(percent_variation) + '&accuracy=' + str(accuracy) + '&streamingWindowSize=' + str(streaming_window)

    # convert to config format
    try:
        config_response = http.request(
            'GET',
            config_cmd,
            headers={
                'x-token': xtoken,
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

def set_config(instance_id, config):
    """returns the posted clustering configuration
    """

    # build command
    config_cmd = url + 'clusterConfig/' + str(instance_id)

    # post config
    try:
        config_response = http.request(
            'POST',
            config_cmd,
            headers={
                'x-token': xtoken,
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

def autotune_config(instance_id, autotune_pv=True, autotune_range=True, by_feature=False, exclusions={}):
    """autotunes the percent variation
    and the min and max for each feature
    """

    # build command
    config_cmd = url + 'autoTuneConfig/' + str(instance_id) + '?byFeature=' + str(by_feature).lower() + '&autoTunePV=' + str(autotune_pv).lower() + '&autoTuneRange=' + str(autotune_range).lower() + '&exclusions=' + str(exclusions)[1:-1].replace(' ','')

    # autotune parameters
    try:
        config_response = http.request(
            'POST',
            config_cmd,
            headers={
                'x-token': xtoken,
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

def load_data(instance_id, data, file_type='', gzip=False, metadata='', append_data=False, run_nano=False, results=''):
    """posts the data and clusters it if runNano is True

    results per pattern options:
        ID = cluster ID
        SI = smoothed anomaly index
        RI = raw anomaly index
        FI = frequency index
        DI = distance index
        MD = metadata
    """

    filename = data
    # check filetype
    if not ".bin" in str(filename) and not '.csv' in str(filename):
        dtype = data.dtype
        if dtype == np.int64:
            filename = data.astype(np.int32)
        elif dtype == np.float64:
            filename = data.astype(np.float32)
        file_data = data.tostring()
        filename = 'dummy_filename.bin'
    else:
        with open(filename) as fp:
            file_data = fp.read()

    # build results command
    if str(results) == 'All':
        results_str = ',ID,SI,RI,FI,DI'
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
        body = {'data': (filename, file_data)}
    else:
        body = {'data': (filename, file_data),'metadata': metadata.replace(',','|').replace('{','').replace('}','').replace(' ','')}
    # build command
    dataset_cmd = url + 'data/' + str(instance_id) + '?runNano=' + str(run_nano).lower() + '&fileType=' + (str(file_type) if file_type != '' else ('raw' if 'bin' in filename else 'csv')) + '&gzip=' + str(gzip).lower() + '&results=' + results_str[1:] + '&appendData=' + str(append_data).lower()

    # post dataset
    try:
        dataset_response = http.request(
            'POST',
            dataset_cmd,
            headers={
                'x-token': xtoken
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

def run_nano(instance_id, results=''):
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
        results_str = ',ID,SI,RI,FI,DI'
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
    nano_cmd = url + 'nanoRun/' + str(instance_id) + '?results=' + results_str[1:]

    # run nano
    try:
        nano_response = http.request(
            'POST',
            nano_cmd,
            headers={
                'x-token': xtoken
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

def get_buffer_status(instance_id):
    """ results related to the bytes processed/in the buffer
    """

    # build command
    results_cmd = url + 'bufferStatus/' + str(instance_id)

    # buffer status
    try:
        results_response = http.request(
            'GET',
            results_cmd,
            headers={
                'x-token': xtoken
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

def get_nano_results(instance_id, results='All'):
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
        results_str = ',ID,SI,RI,FI,DI'
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
    results_cmd = url + 'nanoResults/' + str(instance_id) + '?results=' + results_str[1:]

    # pattern results
    try:
        results_response = http.request(
            'GET',
            results_cmd,
            headers={
                'x-token': xtoken,
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

def get_nano_status(instance_id, results='All'):
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
    results_cmd = url + 'nanoStatus/' + str(instance_id) + '?results=' + results_str[1:]

    # cluster status
    try:
        results_response = http.request(
            'GET',
            results_cmd,
            headers={
                'x-token': xtoken,
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
