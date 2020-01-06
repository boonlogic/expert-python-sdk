from urllib3 import PoolManager
import json
import numpy as np
import os


def load_data(nano_handle, data, file_type='', gzip=False, metadata='', append_data=False, run_nano=False, results=''):
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
        if nano_handle.numericFormat == 'int16':
            filename = data.astype(np.int16)
        elif nano_handle.numericFormat == 'float32':
            filename = data.astype(np.float32)
        elif nano_handle.numericFormat == 'uint16':
            filename = data.astype(np.uint16)
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
        body = {'data': (filename, file_data),
                'metadata': metadata.replace(',', '|').replace('{', '').replace('}', '').replace(' ', '')}
    # build command
    dataset_cmd = nano_handle.url + 'data/' + nano_handle.instance + '?runNano=' + str(
        run_nano).lower() + '&fileType=' + (
                      str(file_type) if file_type != '' else ('raw' if 'bin' in filename else 'csv')) + '&gzip=' + str(
        gzip).lower() + '&results=' + results_str[1:] + '&appendData=' + str(
        append_data).lower() + '&api-tenant=' + nano_handle.api_tenant

    # post dataset
    try:
        dataset_response = nano_handle.http.request(
            'POST',
            dataset_cmd,
            headers={
                'x-token': nano_handle.api_key
            },
            fields=body
        )

    except Exception as e:
        print('Request Timeout')
        return False, None

    # check for error
    if dataset_response.status != 200:
        print(json.loads(dataset_response.data.decode('utf-8')))
        return False, None

    if not results:
        return True, None

    return True, json.loads(dataset_response.data.decode('utf-8'))


def run_nano(nano_handle, results=''):
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
    nano_cmd = nano_handle.url + 'nanoRun/' + nano_handle.instance + '?results=' + results_str[
                                                                                   1:] + '&api-tenant=' + nano_handle.api_tenant

    # run nano
    try:
        nano_response = nano_handle.http.request(
            'POST',
            nano_cmd,
            headers={
                'x-token': nano_handle.api_key
            }
        )

    except Exception as e:
        print('Request Timeout')
        return False, None

    # check for error
    if nano_response.status != 200:
        print(json.loads(nano_response.data.decode('utf-8')))
        return False, None

    return True, json.loads(nano_response.data.decode('utf-8'))
