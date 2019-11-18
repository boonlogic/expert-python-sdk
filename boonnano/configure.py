from urllib3 import PoolManager
import json
import numpy as np
import os

def configure_nano(nano_handle, numeric_format="int", feature_count=10, min=1, max=10, weight=1, labels="", percent_variation=0.05, streaming_window=1, accuracy=0.99, config=""):
    """returns the posted clustering configuration
    """

    # build command
    config_cmd = nano_handle['url'] + 'clusterConfig/' + nano_handle['instance']
    if not config == "":
        config = generate_config(numeric_format, feature_count, min, max, weight, labels, percent_variation, streaming_window, accuracy)

    # post config
    try:
        config_response = nano_handle['http'].request(
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

def generate_config(numeric_format, feature_count, min=1, max=10, weight=1, labels="", percent_variation=0.05, streaming_window=1, accuracy=0.99):
    """returns a json config version for the given Parameters
    """
    config = {}
    config['numericFormat'] = str(numeric_format)
    config['percentVariation'] = percentVariation
    config['accuracy'] = accuracy
    config['streamingWindowSize'] = streaming_window
    temp_array = []
    for x in range(feature_count):
        temp_feature = {}
        # min
        if len([min]) == 1:
            temp_feature['minVal'] = min
        else: # the min vals are given as a list
            temp_feature['minVal'] = min[x]
        # max
        if len([max]) == 1:
            temp_feature['maxVal'] = max
        else: # the max vals are given as a list
            temp_feature['maxVal'] = max[x]
        # weights
        if len([weight]) == 1:
            temp_feature['weight'] = weight
        else: # the weight vals are given as a list
            temp_feature['weight'] = weight[x]
        # labels
        if labels != "" and labels[x] != "":
            temp_feature['label'] = labels[x]
        temp_array.append(temp_feature)
    config['features'] = temp_array

    return config

def autotune_config(nano_handle, autotune_pv=True, autotune_range=True, by_feature=False, exclusions={}):
    """autotunes the percent variation
    and the min and max for each feature
    """

    # build command
    config_cmd = nano_handle['url'] + 'autoTuneConfig/' + nano_handle['instance'] + '?byFeature=' + str(by_feature).lower() + '&autoTunePV=' + str(autotune_pv).lower() + '&autoTuneRange=' + str(autotune_range).lower() + '&exclusions=' + str(exclusions)[1:-1].replace(' ','')

    # autotune parameters
    try:
        config_response = nano_handle['http'].request(
            'POST',
            config_cmd,
            headers={
                'x-token': nano_handle['xtoken'],
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

def get_config(nano_handle):
    """returns the posted clustering configuration
    """

    # build command
    config_cmd = nano_handle['url'] + 'clusterConfig/' + nano_handle['instance']

    # get config
    try:
        config_response = nano_handle['http'].request(
            'GET',
            config_cmd,
            headers={
                'x-token': nano_handle['xtoken'],
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
