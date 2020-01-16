# Python SDK Documentation
This python package allows ease of access to calls to the BoonLogic Nano API.

**NOTE:** In order to use this package, it is necessary to acquire a BoonNano license
from Boon Logic, Inc.  A startup email will be sent providing the details
for using this package.

- __Website__: [https://boonlogic.com](https://github.com/boonlogic/expert-python-sdk)
- __Documentation__: [https://github.com/boonlogic/expert-python-sdk](https://github.com/boonlogic/expert-python-sdk)


------------
### Installation of BoonNano
```
pip install boonnano
```

------------
### License Configuration

Note: A license must be obtained from Boon Logic to use the BoonNano Python SDK

The license should be placed in a file named ~/.BoonLogic

```json
{
  "default": {
    "api-key": "API-KEY",
    "server": "WEB ADDRESS",
    "api-tenant": "API-TENANT"
  }
}
```

The *API-KEY*, *WEB ADDRESS*, and *API-TENANT* will be unique to your obtained license.

The .BoonLogic file will be consulted by the BoonNano Python SDK to successfully find and authenticate with your designated server.

---------------
### Connectivity Test

The following Python script provides a basic proof-of-connectivity:

**connect-example.py**

```python
import boonnano as bn
import json
import sys

# create new nano instance
try:
    nano = bn.NanoHandle('default')
except bn.BoonException as be:
    print(be)
    sys.exit(1)

# open/attach to nano
success, response = nano.open_nano('my-instance')
if not success:
    print("open_nano failed: {}".format(response))
    sys.exit(1)

# fetch the version information for this nano instance
success, response = nano.get_version()
if not success:
    print("get_version failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# close/detach the nano instance
success, response = nano.close_nano()
if not success:
    print("close_nano failed: {}".format(response))
    sys.exit(1)

```

Running the **connect-example.py** script should yield something like:

```sh
% python connect-example.py
{
    "api-version": "/expert/v3",
    "boon-nano": "e5d221de",
    "expert-api": "18a5ddfa",
    "expert-common": "f3215f72"
}
```

