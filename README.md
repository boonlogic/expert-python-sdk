# Python SDK Documentation
This python package allows ease of access to calls to the BoonLogic Nano API.

**NOTE:** In order to use this package, it is necessary to acquire a BoonNano license
from Boon Logic, Inc.  A startup email will be sent providing the details
for using this package.

- __Website__: http://boonlogic.com

------------
### Installation of BoonNano
```
pip install boonnano
```

------------
### License setup
1. Create a file in the user home directory (ie Mac: /Users/'username' or Windows: C:\\Users\\'username')
2. Title the file `.BoonLogic`
3. Copy and paste the following json format into the file
```json
{
  "<LICENSE_NAME>": {
    "api-key": "<API-KEY>",
    "server": "<ADDRESS>",
    "api-tenant": "<API-TENANT>"
  }
}
```
4. Fill in the text with all caps with the values provided by Boon Logic specific for your account. These can be found in the email from @boonlogic.com.
5. Save the file

This file is what the SDK's look for to access the API. If it is placed somewhere other than the home directory, when opening a new nano, the file path will have to be specified.

---------------
### Setting up client library
The base for the file should be:
```python
import boonnano as bn
import json
import sys

# create new nano instance
try:
    nano = bn.NanoHandle('my-license')
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
