import os
import numpy as np
from .rest import simple_post
from .rest import multipart_post


def load_file(nano_handle, file, file_type, gzip=False, metadata=None, append_data=False):
    """posts data to the nano
    """

    # load the data file
    try:
        with open(file) as fp:
            file_data = fp.read()
    except FileNotFoundError as e:
        return False, e.strerror

    # verify file_type is set correctly
    if file_type not in ['csv', 'raw']:
        return False, 'file_type must be "csv" or "raw"'

    file_name = os.path.basename(file)

    if metadata:
        fields = {'data': (file_name, file_data),
                  'metadata': metadata.replace(',', '|').replace('{', '').replace('}', '').replace(' ', '')}
    else:
        fields = {'data': (file_name, file_data)}

    # build command
    dataset_cmd = nano_handle.url + 'data/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    dataset_cmd += '&fileType=' + file_type
    dataset_cmd += '&gzip=' + str(gzip).lower()
    dataset_cmd += '&appendData=' + str(append_data).lower()

    return multipart_post(nano_handle, dataset_cmd, fields=fields)


def load_data(nano_handle, data, metadata=None, append_data=False):

    if not isinstance(data, np.ndarray):
        if nano_handle.numeric_format == 'int16':
            data = np.asarray(data, dtype=np.int16)
        elif nano_handle.numeric_format == 'float32':
            data = np.asarray(data, dtype=np.float32)
        elif nano_handle.numeric_format == 'uint16':
            data = np.asarray(data, dtype=np.uint16)

    if nano_handle.numeric_format == 'int16':
        data = data.astype(np.int16)
    elif nano_handle.numeric_format == 'float32':
        data = data.astype(np.float32)
    elif nano_handle.numeric_format == 'uint16':
        data = data.astype(np.uint16)
    data = data.tostring()
    file_name = 'dummy_filename.bin'
    file_type = 'raw'

    if metadata:
        fields = {'data': (file_name, data),
                  'metadata': metadata.replace(',', '|').replace('{', '').replace('}', '').replace(' ', '')}
    else:
        fields = {'data': (file_name, data)}

    # build command
    dataset_cmd = nano_handle.url + 'data/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    dataset_cmd += '&fileType=' + file_type
    dataset_cmd += '&appendData=' + str(append_data).lower()

    return multipart_post(nano_handle, dataset_cmd, fields=fields)


def run_nano(nano_handle, results=None):
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

    results_str = ''
    if str(results) == 'All':
        results_str = 'ID,SI,RI,FI,DI'
    elif results:
        for result in results.split(','):
            if result not in ['ID', 'SI', 'RI', 'FI', 'DI', 'MD']:
                return False, 'unknown result "{}" found in results parameter'.format(result)
        results_str = results

    # build command
    nano_cmd = nano_handle.url + 'nanoRun/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant
    if results:
        nano_cmd += '&results=' + results_str

    return simple_post(nano_handle, nano_cmd)
