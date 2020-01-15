# Python SDK Documentation
This python package allows ease of access to calls to the BoonLogic Nano API.

- __Website__: http://boonlogic.com
- __Documentation__: [https://github.com/boonlogic/boonlogic-python-api](https://github.com/boonlogic/boonlogic-python-api/blob/master/python-docs.md)

---------
### Download the python client library
```
pip install boonnano
```

---------
### Authentication setup
1. Create a file in the user home directory (ie Mac: /Users/'username' or Windows: C:\\Users\\'username')
2. Title the file `.BoonLogic`
3. Copy and paste the following json format into the file
```json
{
  "USERNAME": {
    "api-key": "API-KEY",
    "server": "WEB ADDRESS",
    "api-tenant": "API-TENANT"
  }
}
```
4. Fill in the text with all caps with the values provided by Boon Logic specific for your account. These can be found in the email from @boonlogic.com.
5. Save the file

This file is what the SDK's look for to access the API. If it is placed somewhere other than the home directory, when opening a new nano, the file path will have to be specified.

----------
### Setting up client library
The base for the file should be:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')

bn.close_nano(nano)
```
