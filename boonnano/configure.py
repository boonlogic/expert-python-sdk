import json
from .rest import simple_get
from .rest import simple_post


def configure_nano(nano_handle, feature_count=10, numeric_format="float32", min=1, max=10, weight=1, labels="",
                   percent_variation=0.05, streaming_window=1, accuracy=0.99, config=None):
    """returns the posted clustering configuration
    """

    # verify numeric_format
    if numeric_format not in ['float32', 'int16', 'uint16']:
        return False, 'numeric_format must be "float32", "int16", or "uint16"'

    # build command
    config_cmd = nano_handle.url + 'clusterConfig/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    if not config:
        new_config = generate_config(numeric_format, feature_count, min, max, weight, labels, percent_variation,
                                     streaming_window, accuracy)
    else:
        new_config = config

    body = json.dumps(new_config)

    result, response = simple_post(nano_handle, config_cmd, body=body)
    if result:
        nano_handle.numeric_format = new_config['numericFormat']

    return result, response


def generate_config(numeric_format, feature_count, min=1, max=10, weight=1, labels="", percent_variation=0.05,
                    streaming_window=1, accuracy=0.99):
    """returns a json config version for the given Parameters
    """
    config = {}
    config['accuracy'] = accuracy
    temp_array = []
    for x in range(feature_count):
        temp_feature = {}
        # max
        if len([max]) == 1:
            temp_feature['maxVal'] = max
        else:  # the max vals are given as a list
            temp_feature['maxVal'] = max[x]
        # min
        if len([min]) == 1:
            temp_feature['minVal'] = min
        else:  # the min vals are given as a list
            temp_feature['minVal'] = min[x]
        # weights
        if len([weight]) == 1:
            temp_feature['weight'] = weight
        else:  # the weight vals are given as a list
            temp_feature['weight'] = weight[x]
        # labels
        if labels != "" and labels[x] != "":
            temp_feature['label'] = labels[x]
        temp_array.append(temp_feature)
    config['features'] = temp_array
    config['numericFormat'] = str(numeric_format)
    config['percentVariation'] = percent_variation
    config['streamingWindowSize'] = streaming_window

    return config


def autotune_config(nano_handle, autotune_pv=True, autotune_range=True, by_feature=False, exclusions={}):
    """autotunes the percent variation
    and the min and max for each feature
    """

    # build command
    config_cmd = nano_handle.url + 'autoTuneConfig/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    config_cmd += '&byFeature=' + str(by_feature).lower()
    config_cmd += '&autoTunePV=' + str(autotune_pv).lower()
    config_cmd += '&autoTuneRange=' + str(autotune_range).lower()
    config_cmd += '&exclusions=' + str(exclusions)[1:-1].replace(' ', '')

    # autotune parameters
    return simple_post(nano_handle, config_cmd)


def get_config(nano_handle):
    """returns the posted clustering configuration
    """
    config_cmd = nano_handle.url + 'clusterConfig/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    return simple_get(nano_handle, config_cmd)
