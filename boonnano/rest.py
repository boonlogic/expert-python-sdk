import json
import boonnano
import urllib3


def simple_get(nano_handle, get_cmd):

    try:
        response = nano_handle.http.request(
            'GET',
            get_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'Content-Type': 'application/json'
            }
        )
    except Exception as e:
        return False, 'request failed'

    # check for error
    if response.status != 200:
        return False, boonnano.http_msg(response)

    return True, json.loads(response.data.decode('utf-8'))


def multipart_post(nano_handle, post_cmd, fields=None):

    multi_fields = urllib3.filepost.encode_multipart_formdata(fields)

    try:
        response = nano_handle.http.request(
            'POST',
            post_cmd,
            headers={
                'x-token': nano_handle.api_key
            },
            fields=fields
        )
    except Exception as e:
        return False, 'request failed: {}'.format(e)

    if response.status != 200:
        return False, boonnano.http_msg(response)

    if len(response.data) == 0:
        return True, ''

    return True, json.loads(response.data.decode('utf-8'))


def simple_post(nano_handle, post_cmd, body=None):

    try:
        response = nano_handle.http.request(
            'POST',
            post_cmd,
            headers={
                'x-token': nano_handle.api_key,
                'Content-type': 'application/json'
            },
            body=body
        )
    except Exception as e:
        return False, 'request failed: {}'.format(e)

    # check for error
    if response.status != 200:
        return False, boonnano.http_msg(response)

    if len(response.data) == 0:
        return True, ''

    return True, json.loads(response.data.decode('utf-8'))


def simple_delete(nano_handle, delete_cmd):

    try:
        response = nano_handle.http.request(
            'DELETE',
            delete_cmd,
            headers={
                'x-token': nano_handle.api_key
            }
        )
    except Exception as e:
        return False, 'request failed: {}'.format(e)

    # check for error
    if response.status != 200:
        return False, boonnano.http_msg(response)

    return True, json.loads(response.data.decode('utf-8'))
