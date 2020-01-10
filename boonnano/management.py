from urllib3 import PoolManager
import json
from os.path import expanduser
from os import path
from os import environ
import tarfile
from .rest import simple_get
from .rest import simple_delete
from .rest import simple_post


############################
# BoonNano Python API v3 #
############################


def json_msg(response):
    blob = json.loads(response.data.decode('utf-8'))
    if 'code' in blob and 'message' in blob:
        return '{}:{}'.format(blob['code'], blob['message'])
    return blob


class NanoHandle:

    def __init__(self, user, authentication_path="~/.BoonLogic", timeout=60.0):

        self.instance = ''
        self.numericFormat = ''

        authentication_path = expanduser(authentication_path)

        if path.exists(authentication_path):
            try:
                with open(authentication_path, "r") as json_file:
                    file_data = json.load(json_file)
            except json.JSONDecodeError as e:
                raise Exception(
                    "json formatting error in .BoonLogic file, {}, line: {}, col: {}".format(e.msg, e.lineno, e.colno))

        # load the user, environment gets precedence
        if 'BOON_USER' in environ:
            self.user = environ['BOON_USER']
            license_block = dict()
        else:
            if user not in file_data:
                raise Exception("'{}' is missing from configuration, set via BOON_USER or in ~/.BoonLogic".format(user))
            license_block = file_data[user]

        # load the api-key, environment gets precedence
        if 'BOON_API_KEY' in environ:
            self.api_key = environ('BOON_API_KEY')
        else:
            if 'api-key' not in license_block.keys():
                raise Exception("'api-key' is missing from configuration, set via BOON_API_KEY or in ~/.BoonLogic file")
            self.api_key = license_block['api-key']

        # load the server, environment gets precedence
        if 'BOON_SERVER' in environ:
            self.server = environ("BOON_SERVER")
        else:
            if 'server' not in license_block.keys():
                raise Exception("'server' is missing from configuration, set via BOON_SERVER or in ~/.BoonLogic file")
            self.server = license_block['server']

        # load the tenant, environment gets precedence
        if 'BOON_TENANT' in environ:
            self.api_tenant = environ("BOON_TENANT")
        else:
            if 'api-tenant' not in license_block.keys():
                raise Exception(
                    "'api-tenant' is missing from configuration, set via BOON_TENANT or in ~/.BoonLogic file")
            self.api_tenant = license_block['api-tenant']

        # set up base url
        self.url = self.server + '/expert/v3/'
        if "http" not in self.server:
            self.url = "http://" + self.url

        # create pool manager
        if timeout == 0:
            self.http = PoolManager()
        else:
            self.http = PoolManager(timeout)


# start the nano and create the unique nano handle
def open_nano(label, user, authentication_path="~/.BoonLogic", timeout=60.0):
    """
    Args:
        label (str): name of the nano.
        user (str): user authentication.
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

    success, response = create_instance(nano_handle, label)
    if not success:
        return False, None

    return True, nano_handle


# free the nano label instance and close the http connection
def close_nano(nano_handle, instance=None):
    # build command
    if not instance:
        instance = nano_handle.instance
    close_cmd = nano_handle.url + 'nanoInstance/' + instance + '?api-tenant=' + nano_handle.api_tenant

    # delete instance
    result, response = simple_delete(nano_handle, close_cmd)
    if result:
        nano_handle.http.clear()

    return result, response


# get the labels of running nanos
def nano_list(nano_handle):
    """returns list of nano instances running
    """

    # build command
    instance_cmd = nano_handle.url + 'nanoInstances' + '?api-tenant=' + nano_handle.api_tenant

    return simple_get(nano_handle, instance_cmd)


# store the nano for later use
def save_nano(nano_handle, filename):
    """serializes the nano and saves it as a tar filename
    """

    # build command
    snapshot_cmd = nano_handle.url + 'snapshot/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant

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
        return False, "request failed"

    # check for error
    if snapshot_response.status != 200:
        return False, json_msg(snapshot_response)

    # at this point, the call succeeded, saves the result to a local file
    try:
        with open(filename, 'wb') as fp:
            fp.write(snapshot_response.data)
    except Exception as e:
        return False, 'unable to write file'

    return True, None


def restore_nano(nano_handle, filename):
    """deserialize existing nano
    upload file to given instance

    NOTE: must be of type tar
    """

    # verify that input file is a valid nano file (gzip'd tar with Magic Number)
    try:
        with tarfile.open(filename, 'r:gz') as tp:
            with tp.extractfile('BoonNano/MagicNumber') as magic_fp:
                magic_num = magic_fp.read()
                if magic_num != b'\xef\xbe':
                    return False, 'file {} is not a Boon Logic nano-formatted file, bad magic number'.format(filename)

    except KeyError as ke:
        return False, 'file {} is not a Boon Logic nano-formatted file'.format(filename)

    with open(filename, 'rb') as fp:
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
        return False, 'request failed'

    # check for error
    if snapshot_response.status != 200:
        return False, json_msg(snapshot_response)

    nano_handle.numericFormat = json.loads(snapshot_response.data.decode('utf-8'))['numericFormat']

    return True, None


###########
# PRIVATE #
###########

def create_instance(nano_handle, label):
    # build command
    instance_cmd = nano_handle.url + 'nanoInstance/' + label + '?api-tenant=' + nano_handle.api_tenant

    success, response = simple_post(nano_handle, instance_cmd)
    if success:
        nano_handle.instance = label

    return success, response
