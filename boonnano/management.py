from urllib3 import PoolManager
from urllib3 import Timeout
import json
from os.path import expanduser
from os import getenv
from os import path
from os import environ
import tarfile
from .rest import simple_get
from .rest import simple_delete
from .rest import simple_post
from .rest import multipart_post


############################
# BoonNano Python API v3 #
############################

class BoonException(Exception):
    def __init__(self, message):
        self.message = message


def http_msg(response):
    return '{}:{}'.format(response.status, response.reason)


class NanoHandle:

    def __init__(self, license_id=None, license_file="~/.BoonLogic", timeout=120.0):

        self.license_file = license_file
        self.license_id = None
        self.api_key = None
        self.api_tenant = None
        self.instance = ''
        self.numeric_format = ''

        license_path = expanduser(license_file)

        if path.exists(license_path):
            try:
                with open(license_path, "r") as json_file:
                    file_data = json.load(json_file)
            except json.JSONDecodeError as e:
                raise BoonException(
                    "json formatting error in .BoonLogic file, {}, line: {}, col: {}".format(e.msg, e.lineno, e.colno))
        else:
            raise BoonException("file {} does not exist".format(license_path))

        # load the license block, environment gets precedence
        license_env = getenv('BOON_LICENSE_ID')
        if license_env:
            # license id was specified through environment
            if license_env in file_data:
                self.license_id = license_env
            else:
                raise BoonException("BOON_LICENSE_ID value of '{}' not found in .BoonLogic file".format(license_env))
        elif self.license_id:
            # license was specified as argument
            if license_id in file_data:
                self.license_id = license_id
            else:
                raise BoonException("license_id '{}' not found in .BoonLogic file".format(license_id))
        else:
            # no license specified, attempt to load only license in .BoonLogic
            if len(file_data.keys()) == 1:
                self.license_id = list(file_data.keys())[0]
            else:
                raise BoonException("must specify license_id when multiple licenses reside in license_file")

        license_block = file_data[self.license_id]

        # load the api-key, environment gets precedence
        self.api_key = getenv('BOON_API_KEY')
        if not self.api_key:
            if 'api-key' not in license_block.keys():
                raise BoonException("'api-key' is missing from configuration, set via BOON_API_KEY or in ~/.BoonLogic file")
            self.api_key = license_block['api-key']

        # load the server, environment gets precedence
        self.server = getenv('BOON_SERVER')
        if not self.server:
            if 'server' not in license_block.keys():
                raise BoonException("'server' is missing from configuration, set via BOON_SERVER or in ~/.BoonLogic file")
            self.server = license_block['server']

        # load the tenant, environment gets precedence
        self.api_tenant = getenv('BOON_TENANT')
        if not self.api_tenant:
            if 'api-tenant' not in license_block.keys():
                raise BoonException(
                    "'api-tenant' is missing from configuration, set via BOON_TENANT or in ~/.BoonLogic file")
            self.api_tenant = license_block['api-tenant']

        # set up base url
        self.url = self.server + '/expert/v3/'
        if "http" not in self.server:
            self.url = "http://" + self.url

        # create pool manager
        timeoutInst = Timeout(connect=30.0, read=timeout)
        self.http = PoolManager(timeout=timeoutInst)


# start the nano and create the unique nano handle
def open_nano(nano_handle, instance_id):
    """Creates or attaches to a nano pod instance

    Args:
        nano_handle (NanoHandle): handle for this nano instance
        instance_id (str): instance identifier to be applied to instance

    Returns:
        success status
        error message

    """
    success, response = create_instance(nano_handle, instance_id)
    if not success:
        return False, response

    return True, None


# free the nano label instance and close the http connection
def close_nano(nano_handle):
    """Closes the pod instance

    Args:
        nano_handle (NanoHandle): handle for this nano instance

    Returns:
        success status
        error message

    """
    close_cmd = nano_handle.url + 'nanoInstance/' + nano_handle.instance + '?api-tenant=' + nano_handle.api_tenant

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
    result, response = simple_get(nano_handle, snapshot_cmd)
    if not result:
        return result, response

    # at this point, the call succeeded, saves the result to a local file
    try:
        with open(filename, 'wb') as fp:
            fp.write(response)
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

    fields = {'snapshot': (filename, nano)}

    result, response = multipart_post(nano_handle, snapshot_cmd, fields=fields)

    if not result:
        return result, response

    nano_handle.numeric_format = response['numericFormat']

    return True, response


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
