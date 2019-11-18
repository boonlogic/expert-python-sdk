# Python SDK Documentation
This python package allows ease of access to calls to the BoonLogic Nano API.

- __Website__: http://boonlogic.com
- __Documentation__: [https://github.com/boonlogic/boonlogic-python-api](https://github.com/boonlogic/boonlogic-python-api/blob/master/python-docs.md)

### Download the python client library
```
pip install boonnano
```

### Setting up client library
The base for the file should be:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')

bn.close_nano(nano)
```
