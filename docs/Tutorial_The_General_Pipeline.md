# Tutorial: The General Pipeline

## Package Installation

### Package Installation

Import the python client library from PyPI using:

```sh
pip install boonnano
```

### License Configuration

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

The .BoonLogic file will be consulted by the BoonNano Python SDK to successfully find and authenticate with your designated server.


**NOTE:** See the *examples* directory for the code used in this tutorial


### General WorkFlow

Most boonnano sessions will consist of the following steps.

#### Create NanoHandle

```python
try:
    nano = bn.NanoHandle('default')
except bn.BoonException as be:
    print(be)
    sys.exit(1)
```

#### Open Connection to Instance

```python
# open/attach to nano
success, response = nano.open_nano('my-instance')
if not success:
    print("open_nano failed: {}".format(response))
    sys.exit(1)
```

#### Create the nano configuration
```python
success, response = nano.create_config(numeric_format='float32', feature_count=20, min_val=[-10], max_val=[15],
	percent_variation=0.05, accuracy=0.99, weight=[1], streaming_window=1)
if not success:
    print("create_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))
```

#### Configure the Nano Instance
```python
success, response = nano.configure_nano(config=response)
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)
```

#### Load Data to Nano Instance

```python
dataFile = 'Data.csv'
success, response = nano.load_file(file=dataFile, file_type='csv')
if not success:
    print("load_file failed: {}".format(response))
    sys.exit(1)
```

#### Run Clustering

```
success, response = nano.run_nano(results='All')
if not success:
    print("run_nano failed: {}".format(response))
    sys.exit(1)
```

#### Close NanoHanlde

```python
success, response = nano.close_nano()
if not success:
    print("close_nano failed: {}".format(response))
    sys.exit(1)
```

### Connectivity Test

The following Python script provides a basic proof-of-connectivity:

**connect-example.py**

```python
import boonnano as bn
import json
import sys

# create new nano handle
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

Running the connect-example.py script should yield something like:

```sh
% python connect-example.py
{
    "api-version": "/expert/v3",
    "boon-nano": "e5d221de",
    "expert-api": "18a5ddfa",
    "expert-common": "f3215f72"
}
```

### Basic Clustering

**cluster-example.py**

```python
import boonnano as bn
import json
import sys

#
# example of clustering with boonnano SDK
#

# create new nano instance
try:
    nano = bn.NanoHandle()
except bn.BoonException as be:
    print(be)
    sys.exit(1)

# open/attach to nano
success, response = nano.open_nano('sample-instance')
if not success:
    print("open_nano failed: {}".format(response))
    sys.exit(1)

# create the configuration
success, response = nano.create_config(numeric_format='float32', feature_count=20, min_val=[-10], max_val=[15],
                                       percent_variation=0.05, accuracy=0.99, weight=[1], streaming_window=1)
if not success:
    print("create_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# configure the nano with created configuration
success, response = nano.configure_nano(config=response)
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)

# load a csv file
dataFile = 'Data.csv'
success, response = nano.load_file(file=dataFile, file_type='csv')
if not success:
    print("load_file failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# run the nano
success, response = nano.run_nano(results='All')
if not success:
    print("run_nano failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# get the nano results
success, response = nano.get_nano_results(results='All')
if not success:
    print("run_nano_status failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# close/detach the nano instance
success, response = nano.close_nano()
if not success:
    print("close_nano failed: {}".format(response))
    sys.exit(1)
```


### Full Example

Consider the following code snippet:

**full-example.py**

```python
import boonnano as bn
import json
import sys
import csv

#
# example of each boonnano SDK endpoint
#

# create new nano instance
try:
    nano = bn.NanoHandle()
except bn.BoonException as be:
    print(be)
    sys.exit(1)

# open/attach to nano
success, response = nano.open_nano('sample-instance')
if not success:
    print("open_nano failed: {}".format(response))
    sys.exit(1)

# fetch the version information for this nano instance
success, response = nano.get_version()
if not success:
    print("get_version failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# list the nano instances
success, response = nano.nano_list()
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# create the configuration
success, response = nano.create_config(numeric_format='float32', feature_count=20, min_val=[-10], max_val=[15],
                                       percent_variation=0.05, accuracy=0.99, weight=[1], streaming_window=1)
if not success:
    print("create_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# configure the nano with created configuration
success, response = nano.configure_nano(config=response)
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)

# retrieve the nano configuration
success, response = nano.get_config()
if not success:
    print("get_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# configure the nano using a pre-made configuration block
success, response = nano.configure_nano(config=response)
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# load a csv file
dataFile = 'Data.csv'
success, response = nano.load_file(file=dataFile, file_type='csv')
if not success:
    print("load_file failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# check buffer status again
success, response = nano.get_buffer_status()
if not success:
    print("get_buffer_status failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# load Data.csv and convert to list of floats
dataBlob = list()
with open('Data.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        dataBlob = dataBlob + row

# load data, data can be either list or nparray
success, response = nano.load_data(data=dataBlob, append_data=True)
if not success:
    print("load_data failed: {}".format(response))
    sys.exit(1)

# get the buffer status
success, response = nano.get_buffer_status()
if not success:
    print("get_buffer_status failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# autotune the configuration
success, response = nano.autotune_config()
if not success:
    print("autotune_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# run the nano
success, response = nano.run_nano(results='All')
if not success:
    print("run_nano failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# get the results again
success, response = nano.get_nano_results(results='All')
if not success:
    print("run_nano_status failed: {}".format(response))
    sys.exit(1)

# get the nano status
success, response = nano.get_nano_status(results='averageInferenceTime')
if not success:
    print("run_nano_status failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# get the buffer status
success, response = nano.get_buffer_status()
if not success:
    print("get_buffer_status failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# save the nano
success, response = nano.save_nano('sample-nano-image')
if not success:
    print("save_nano failed: {}".format(response))
    sys.exit(1)

# close/detach the nano instance
success, response = nano.close_nano()
if not success:
    print("close_nano failed: {}".format(response))
    sys.exit(1)

# open/attach to nano
success, response = nano.open_nano('sample-instance-2')
if not success:
    print("open_nano failed: {}".format(response))
    sys.exit(1)

# load the nano
success, response = nano.restore_nano('sample-nano-image')
if not success:
    print("save_nano failed: {}".format(response))
    sys.exit(1)

# list the nano instances
success, response = nano.nano_list()
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# get the nano status
success, response = nano.get_nano_status('All')
if not success:
    print("run_nano_status failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# retrieve the nano configuration
success, response = nano.get_config()
if not success:
    print("get_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# close/detach the nano instance
success, response = nano.close_nano()
if not success:
    print("close_nano failed: {}".format(response))
    sys.exit(1)
```

[expert-python-sdk main page](https://boonlogic.github.io/expert-python-sdk/)
