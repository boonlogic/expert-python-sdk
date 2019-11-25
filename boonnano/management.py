from urllib3 import PoolManager
import json
import numpy as np
import os
from os.path import expanduser

############################
# BoonNano Python API v3 #
############################

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
    success, nano_handle = define_nano_handle(user, authentication_path, timeout)
    if not success:
        return False, None

    success = create_instance(nano_handle, label)
    if not success:
        return False, nano_handle

    if nano_file:
        return load_nano(nano_handle, nano_file), nano_handle

    return True, nano_handle

# free the nano label instance and close the http connection
def close_nano(nano_handle):
    # Destructor Method.
    # build command
    close_cmd = nano_handle['url'] + 'nanoInstance/' + nano_handle['instance']

    # delete instance
    try:
        close_response = nano_handle['http'].request(
            'DELETE',
            close_cmd,
            headers={
                'x-token': nano_handle['x-token']
            }
        )

    except Exception as e:
        print('Request Timeout')
        return False

    # check for error
    if close_response.status != 200:
        print(json.loads(close_response.data.decode('utf-8')))
        return False

    nano_handle['http'].clear()
    return True

# get the labels of running nanos
def nano_list(nano_handle):
    """returns list of nano instances running
    """

    # build command
    instance_cmd = nano_handle['url'] + 'nanoInstances'

    # list of running instances
    try:
        instance_response = nano_handle['http'].request(
            'GET',
            instance_cmd,
            headers={
                'x-token': nano_handle['x-token'],
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

    return True, json.loads(instance_response.data.decode('utf-8'))['instanceIDs']

# store the nano for later use
def save_nano(nano_handle, filename):
    """serializes the nano and saves it as a tar filename
    """

    # build command
    snapshot_cmd = nano_handle['url'] + 'snapshot/' + nano_handle['instance']

    # serialize nano
    try:
        snapshot_response = nano_handle['http'].request(
            'GET',
            snapshot_cmd,
            headers={
                'x-token': nano_handle['x-token']
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
    snapshot_cmd = nano_handle['url'] + 'snapshot/' + nano_handle['instance']

    # post serialized nano
    try:
        snapshot_response = nano_handle['http'].request(
            'POST',
            snapshot_cmd,
            headers={
                'x-token': nano_handle['x-token']
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

    nano_handle['numericFormat'] = json.loads(snapshot_response.data.decode('utf-8'))['numericFormat']
    return True

def create_instance(nano_handle, label):

    # build command
    instance_cmd = nano_handle['url'] + 'nanoInstance/' + label

    # initialize instance
    try:
        instance_response = nano_handle['http'].request(
            'POST',
            instance_cmd,
            headers={
                'x-token': nano_handle['x-token'],
                'Content-Type': 'application/json'
            }
        )
    except Exception as e:
        print('Request Timeout')
        return False

    # check for error
    if instance_response.status != 200:
        if "already exists" in json.loads(instance_response.data.decode('utf-8'))['message']:
            print('Warning: '+json.loads(instance_response.data.decode('utf-8'))['message'])
            nano_handle['instance'] = label
            return True
        print(json.loads(instance_response.data.decode('utf-8')))
        nano_handle['instance'] = ''
        return False

    nano_handle['instance'] = json.loads(instance_response.data.decode('utf-8'))['instanceID']
    return True

def define_nano_handle(user, authentication_path="~/.BoonLogic", timeout=60.0):
    auth = {}
    with open (expanduser(authentication_path), "r") as json_file:
        file_data = json.load(json_file)

    try:
        file_data = file_data[user]
    except Exception as e:
        print("User does not exist")
        return False, None

    #look for token in file
    try:
        auth['x-token'] = file_data['x-token']
    # set token to be empty string
    except Exception as e:
        print("Authorization token needed to connect")
        return False, None

    try:
        server = file_data['server']
    except Exception as e:
        #server is empty
        print("No server is given")
        return False, None

    auth['url'] = server + '/expert/v3/'
    if not "http" in server:
        auth["url"] = "http://" + auth["url"]

    #create pool manager
    if(timeout == 0):
        auth['http'] = PoolManager()
    else:
        auth['http'] = PoolManager(timeout)

    return True, auth
