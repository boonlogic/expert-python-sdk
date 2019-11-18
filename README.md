# Python SDK Documentation
This python package allows ease of access to calls to the BoonLogic Nano API.

- __Website__: http://boonlogic.com
- __Documentation__: https://github.com/boonlogic/boonlogic-python-api/tree/master/docs

### Download the python client library
```
pip install boonnano
```

### Setting up client library (Mac OS)
The base for the file should be:
```python
import BoonNano as bn

nano=bn.open_nano('example','username')

bn.close_nano(nano)
```
