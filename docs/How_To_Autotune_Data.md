# How-to: Autotune Data

Autotune finds the best min, max, and percent variation for the data posted.  **autotune-example.py** demonstrates how this is accomplished.

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

#### Create the configuration
```python
# create the configuration
success, response = nano.create_config(numeric_format='float32', feature_count=20, min_val=[-10], max_val=[15],
	percent_variation=0.05, accuracy=0.99, weight=[1], streaming_window=1)
if not success:
    print("create_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

#### Configure the Nano Instance
```python
# configure the nano with created configuration
success, response = nano.configure_nano(config=response)
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)
```

#### Load Data to Nano Instance

In order to autotune the parameters, the pipeline needs data to train from, so post data without running the nano.

```python
dataFile = 'Data.csv'
success, response = nano.load_file(file=dataFile, file_type='csv')
if not success:
    print("load_file failed: {}".format(response))
    sys.exit(1)
```


#### Autotune the configuration

```
success, response = nano.autotune_config()
if not success:
    print("autotune_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

```

There are a few different parameters that be set when the autotune_config is called:

##### by_feature
Autotune tries to find the best min, max, and percent variation for the data posted, but the min and max might not apply to the data overall. by_feature tells autotune to set each column of data with a different min and max specific for that column. The default is false.

One example of an application is if each column has a different meaning. For instance: {weight, height, age, blood pressure}. Each column would not benefit with an overall min and max since they are all so different.

##### autotune_pv
This bool variable specifies whether to autotune the percent variation or use the given one from the original config. The default is true.

##### autotune_range
Similarly, this bool variable tells whether to autotune the min and max or use the values given from the original config. The default is true.

##### exclusions
This option only applies when autotuning by feature. Using one-based indexing, the exclusions are the list of column indexes that should be ignored when autotuning the min and max and the original config's min and max value are used on those columns. The default is an empty list.

**autotune-example.py**

```python
import boonnano as bn
import json
import sys

#
# example of autotuning with boonnano
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

```

[expert-python-sdk main page](https://boonlogic.github.io/expert-python-sdk/)
