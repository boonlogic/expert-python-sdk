from urllib3 import PoolManager
import json
import numpy as np
import os

def get_version(nano_handle):
    """gives the version of the api running"""
    # build command (minus the v3 portion)
    version_cmd = nano_handle['url'][:-3] + 'version'

    # call the version number
    try:
        version_response = nano_handle['http'].request(
            'GET',
            version_cmd,
            headers={
                'x-token': nano_handle['xtoken'],
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

def get_buffer_status(nano_handle):
    """ results related to the bytes processed/in the buffer
    """

    # build command
    results_cmd = nano_handle['url'] + 'bufferStatus/' + nano_handle['instance']

    # buffer status
    try:
        results_response = nano_handle['http'].request(
            'GET',
            results_cmd,
            headers={
                'x-token': nano_handle['xtoken']
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

def get_nano_results(nano_handle, results='All'):
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
    results_cmd = nano_handle['url'] + 'nanoResults/' + nano_handle['instance'] + '?results=' + results_str[1:]

    # pattern results
    try:
        results_response = nano_handle['http'].request(
            'GET',
            results_cmd,
            headers={
                'x-token': nano_handle['xtoken'],
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

def get_nano_status(nano_handle, results='All'):
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
    results_cmd = nano_handle['url'] + 'nanoStatus/' + nano_handle['instance'] + '?results=' + results_str[1:]

    # cluster status
    try:
        results_response = nano_handle['http'].request(
            'GET',
            results_cmd,
            headers={
                'x-token': nano_handle['xtoken'],
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
