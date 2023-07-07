import boonnano as bn
from boonnano import *
import json
import sys

#
# example of autotuning with boonnano
#

try:
    nano = bn.ExpertClient(license_id='default')
except bn.BoonException as be:
    print(be)
    sys.exit(1)

# create new nano instance
instance_id = 'sample-instance'
try:
    response = nano.open_nano(instance_id)
except BoonException as e:
    print("open_nano failed: {}".format(e.message))
    sys.exit(1)

# create the configuration
response = nano.create_config(numeric_format='float32', feature_count=20, min_val=-10, max_val=15,
                                       percent_variation=0.05, accuracy=0.99, weight=1, streaming_window=1)
print(json.dumps(response, indent=4))

# configure the nano with created configuration
try:
    response = nano.configure_nano(instance_id, config=response)
except BoonException as e:
    print("configure_nano failed: {}".format(e.message))
    sys.exit(1)

# load a csv file
try:
    dataFile = 'Data.csv'
    response = nano.load_file(instance_id, file=dataFile, file_type='csv')
except BoonException as e:
    print("load_file failed: {}".format(e.message))
    sys.exit(1)

# autotune the configuration
try:
    nano.autotune_config(instance_id)
except BoonException as e:
    print("autotune_config failed: {}".format(e.message))
    sys.exit(1)

# run the nano
try:
    response = nano.run_nano(instance_id, results='All')
except BoonException as e:
    print("run_nano failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))
