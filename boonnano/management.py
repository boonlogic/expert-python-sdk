from urllib3 import PoolManager
import json
import numpy as np
import os
from os.path import expanduser

############################
# BoonNano Python API v3 #
############################

class NanoHandle:

    def __init__(self, user, authentication_path="~/.BoonLogic", timeout=60.0):

        self.instance = ''
        self.numericFormat = ''

        with open (expanduser(authentication_path), "r") as json_file:
            file_data = json.load(json_file)

        if user not in file_data.keys():
            raise Exception("user does not exist in ~/.BoonLogic")
        self.user = user

        license_block = file_data[user]

        if 'api-key' not in license_block.keys():
            raise Exception("'api-key' does not exist in ~/.BoonLogic file")
        self.api_key = license_block['api-key']

        if 'server' not in license_block.keys():
            raise Exception("'server' does not exist in ~/.BoonLogic file")
        self.server = license_block['server']

        if 'api-tenant' not in license_block.keys():
            raise Exception("'api-tenant' does not exist in ~/.BoonLogic file")
        self.api_tenant = license_block['api-tenant']

        self.url = self.server + '/expert/v3/'
        if not "http" in self.server:
            self.url = "http://" + self.url

        #create pool manager
        if(timeout == 0):
            self.http = PoolManager()
        else:
            self.http = PoolManager(timeout)

# start the nano and create the unique nano handle
def open_nano(label, user, nano_file=None, authentication_path="~/.BoonLogic", timeout=60.0):
    """
    Args:
        label (str): name of the nano.
        user (str): user authentication.
        nano_file (str): file of saved nano to load.
        authentication_path (str): path to the authentication file.
        timeout (float): HTTP Request Timeout
    Returns:
        success status
        nano dictionary handle
    """
    try:
        nano_handle = NanoHandle(user, authentication_path, timeout)
    except Exception as e:
        print(e)
        return False, None

    success = create_instance(nano_handle, label)
    if not success:
        return False, nano_handle

    if nano_file:
        return load_nano(nano_handle, nano_file), nano_handle

    return True, nano_handle

# free the nano label instance and close the http connection
def close_nano(nano_handle,instance=''):
    # Destructor Method.
    # build command
    if instance == '':
        instance = nano_handle.instance
    close_cmd = nano_handle.url + 'nanoInstance/' + instance + '?api-tenant=' + nano_handle.api_tenant

    # delete instance
    try:
        close_response = nano_handle.http.request(
            'DELETE',
            close_cmd,
            headers={
                'x-token': nano_handle.api_key
            }
        )

    except Exception as e:
        print('Request Timeout')
        return False

    # check for error
    if close_response.status != 200:
        print(json.loads(close_response.data.decode('utf-8')))
        return False

    nano_handle.http.clear()
    return True

# get the labels of running nanos
def nano_list(nano_handle):
    """returns list of nano instances running
    """

    # build command
    instance_cmd = nano_handle.url + 'nanoInstances' + '?api-tenant=' + nano_handle.api_tenant

    # list of running instances
    try:
        instance_response = nano_handle.http.request(
            'GET',
            instance_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'Content-Type': 'application/json'
            }
        )

    except Exception as e:
        print('Request Timeout')
        return False, None

    # check for error
    if instance_response.status != 200:
        print(json.loads(instance_response.data.decode('utf-8')))
        return False, None

    return True, json.loads(instance_response.data.decode('utf-8'))

# store the nano for later use
def save_nano(nano_handle, filename):
    """serializes the nano and saves it as a tar filename
    """

    # build command
    snapshot_cmd = nano_handleurl + 'snapshot/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant

    # serialize nano
    try:
        snapshot_response = nano_handle.http.request(
            'GET',
            snapshot_cmd,
            headers={
                'x-token': nano_handle.api_key
            }
        )

    except Exception as e:
        print('Request Timeout')
        return False

    # check for error
    if snapshot_response.status != 200:
        print(json.loads(snapshot_response.data.decode('utf-8')))
        return False

    # at this point, the call succeed so saves the return to a tar file
    fp = open(filename, 'wb')
    fp.write(snapshot_response.data)
    fp.close

    return True

###########
# PRIVATE #
###########

def load_nano(nano_handle, filename):
    """deserialize existing nano
    upload file to given instance

    NOTE: must be of type tar
    """

    # check filetype
    # if not ".tar" in filename:
    #     print('Dataset Must Be In .tar Format')
    #     return False

    with open(filename, "rb") as fp:
        nano = fp.read()

    # build command
    snapshot_cmd = nano_handle.url + 'snapshot/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant

    # post serialized nano
    try:
        snapshot_response = nano_handle.http.request(
            'POST',
            snapshot_cmd,
            headers={
                'x-token': nano_handle.api_key
            },
            fields={
                'snapshot': (filename, nano)
            }
        )

    except Exception as e:
        print("Request Timeout")
        return False

    # check for error
    if snapshot_response.status != 200:
        print(json.loads(snapshot_response.data.decode('utf-8')))
        return False

    nano_handle.numericFormat = json.loads(snapshot_response.data.decode('utf-8'))['numericFormat']
    return True

def create_instance(nano_handle, label):

    # build command
    instance_cmd = nano_handle.url + 'nanoInstance/' + label + '?api-tenant=' + nano_handle.api_tenant

    # initialize instance
    try:
        instance_response = nano_handle.http.request(
            'POST',
            instance_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'Content-Type': 'application/json'
            }
        )
    except Exception as e:
        print('Request Timeout')
        return False

    # check for error
    if instance_response.status != 200:
        print(json.loads(instance_response.data.decode('utf-8')))
        nano_handle.instance = ''
        return False

    nano_handle.instance = label
    return True


