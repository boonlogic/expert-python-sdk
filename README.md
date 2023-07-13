![Logo](https://github.com/boonlogic/expert-python-sdk/blob/master/docs/BoonLogic.png?raw=true)

# Python SDK Documentation
This python package allows ease of access to calls to the BoonLogic Nano API.

- __Website__: [boonlogic.com](https://boonlogic.com)
- __Documentation__: [Boon Docs Main Page](https://docs.boonlogic.com)
- __Clustering__: [Clustering with the expert-python-sdk]({{ site.baseurl}}/docs/Tutorial_The_General_Pipeline.md)
- __Autotuning__: [Autotuning with the expert-python-sdk]({{ site.baseurl}}/docs/How_To_Autotune_Data.md)
- __Results__: [Results after clustering]({{ site.baseurl}}/docs/How_To_Generate_Cluster_Results.md)
- __SDK Functional Breakdown__: [expert-python-sdk classes and methods]({{ site.baseurl}}/docs/boonnano/index.html)(docs/boonnano/index.html)

---------
## Installation

The BoonNano SDK is a Python3 project and can be installed via pip.

```
pip install boonnano
```

---------
## License setup

Note: A license must be obtained from Boon Logic to use the BoonNano Python SDK

The license should be placed in a file named ~/.BoonLogic.license

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

The .BoonLogic.license file will be consulted by the BoonNano Python SDK to successfully find and authenticate with your designated server.


### Connectivity Test

The following Python script provides a basic proof-of-connectivity:

**connect-example.py**

```python
import boonnano as bn
import json
import sys

#
# connectivity example for boonnano
#

try:
    # create client handle
    nano = bn.ExpertClient.from_license_file(license_id='default')

    # open/attach to nano
    instance_id = 'my-instance'
    nano.open_nano(instance_id)

    # retrieve server version
    response = nano.get_version()
    print(json.dumps(response, indent=4))

    # close/detach the nano instance
    nano.close_nano(instance_id)

except bn.BoonException as be:
    print(be.message)
    sys.exit(1)
```

Running the connect-test.py script should yield something like:

```sh
% python connect-example.py
{
    "release": "dev",
    "api-version": "/expert/v3",
    "nano-secure": "3c40f1d6",
    "builder": "f5db0682",
    "expert-api": "f6643822",
    "expert-common": "c0575a50",
    "swagger-ui": "914af396"
}
```
