from .rest import simple_get


def get_version(nano_handle):
    """ results related to the bytes processed/in the buffer

    Args:
        nano_handle (NanoHandle): handle for this nano pod instance

    Returns:
        result (boolean): true if successful (version information was retrieved)
        response (dict or str): dictionary of results when result is true, error message when result = false

    """

    # build command (minus the v3 portion)
    version_cmd = nano_handle.url[:-3] + 'version' + '?api-tenant=' + nano_handle.api_tenant
    return simple_get(nano_handle, version_cmd)


def get_buffer_status(nano_handle):
    """ results related to the bytes processed/in the buffer

    Args:
        nano_handle (NanoHandle): handle for this nano pod instance

    Returns:
        result (boolean): true if successful (nano was successfully run)
        response (dict or str): dictionary of results when result is true, error message when result = false

    """
    status_cmd = nano_handle.url + 'bufferStatus/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    return simple_get(nano_handle, status_cmd)


def get_nano_results(nano_handle, results='All'):
    """ results per pattern

    Args:
        nano_handle (NanoHandle): handle for this nano pod instance
        results (str): comma separated list of results

            ID: cluster ID

            SI: smoothed anomaly index

            RI: raw anomaly index

            FI: frequency index

            DI: distance index

            MD: metadata

            All: ID,SI,RI,FI,DI,MD

    """

    # build results command
    if str(results) == 'All':
        results_str = 'ID,SI,RI,FI,DI'
    else:
        for result in results.split(','):
            if result not in ['ID', 'SI', 'RI', 'FI', 'DI', 'MD']:
                return False, 'unknown result "{}" found in results parameter'.format(result)
        results_str = results

    # build command
    results_cmd = nano_handle.url + 'nanoResults/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    results_cmd += '&results=' + results_str

    return simple_get(nano_handle, results_cmd)


def get_nano_status(nano_handle, results='All'):
    """results in relation to each cluster/overall stats

    Args:
        nano_handle (NanoHandle): handle for this nano pod instance
        results (str): comma separated list of results

            PCA = principal components (includes 0 cluster)

            clusterGrowth = indexes of each increase in cluster (includes 0 cluster)

            clusterSizes = number of patterns in each cluster (includes 0 cluster)

            anomalyIndexes = anomaly index (includes 0 cluster)

            frequencyIndexes = frequency index (includes 0 cluster)

            distanceIndexes = distance index (includes 0 cluster)

            patternMemory = base64 pattern memory (overall)

            totalInferences = total number of patterns clustered (overall)

            averageInferenceTime = time in milliseconds to cluster per
                pattern (not available if uploading from serialized nano) (overall)

            numClusters = total number of clusters (includes 0 cluster) (overall)

    Returns:
        result (boolean): true if successful (nano was successfully run)
        response (dict or str): dictionary of results when result is true, error message when result = false

    """

    # build results command
    if str(results) == 'All':
        results_str = 'PCA,clusterGrowth,clusterSizes,anomalyIndexes,frequencyIndexes,distanceIndexes,totalInferences,numClusters'
    else:
        for result in results.split(','):
            if result not in ['PCA', 'clusterGrowth', 'clusterSizes', 'anomalyIndexes', 'frequencyIndexes',
                              'distanceIndexes', 'totalInferences', 'numClusters', 'averageInferenceTime']:
                return False, 'unknown result "{}" found in results parameter'.format(result)
        results_str = results

    # build command
    results_cmd = nano_handle.url + 'nanoStatus/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    results_cmd = results_cmd + '&results=' + results_str

    return simple_get(nano_handle, results_cmd)
