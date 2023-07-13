import boonnano as bn
from boonnano import BoonException
import json
import sys
import csv

#
# example of each boonnano SDK endpoint
#

# create new nano instance
try:
    nano = bn.ExpertClient.from_license_file(license_id='default')
except bn.BoonException as be:
    print(be)
    sys.exit(1)

# open/attach to nano
instance_id = 'sample-instance'
try:
    response = nano.open_nano(instance_id)
except BoonException as e:
    print("open_nano failed: {}".format(e.message))
    sys.exit(1)

# fetch the version information for this nano instance
try:
    response = nano.get_version()
except BoonException as e:
    print("get_version failed: {}".format(e.message))
    sys.exit(1)
print(response)
print(json.dumps(response, indent=4))

# list the nano instances
try:
    response = nano.nano_list()
except BoonException as e:
    print("configure_nano failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# create the configuration
try:
    response = nano.create_config(numeric_format='float32', feature_count=20, min_val=-10, max_val=15,
                                  percent_variation=0.05, accuracy=0.99, weight=1, streaming_window=1)
except BoonException as e:
    print("create_config failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# configure the nano with created configuration
try:
    response = nano.configure_nano(instance_id, config=response)
except BoonException as e:
    print("configure_nano failed: {}".format(e.message))
    sys.exit(1)

# retrieve the nano configuration
try:
    response = nano.get_config(instance_id)
except BoonException as e:
    print("get_config failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# configure the nano using a pre-made configuration block
try:
    response = nano.configure_nano(instance_id, config=response)
except BoonException as e:
    print("configure_nano failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# load a csv file
dataFile = 'Data.csv'
try:
    response = nano.load_file(instance_id, file=dataFile, file_type='csv')
except BoonException as e:
    print("load_file failed: {}".format(e.message))
    sys.exit(1)

# check buffer status again
try:
    response = nano.get_buffer_status(instance_id, )
except BoonException as e:
    print("get_buffer_status failed: {}".format(e.message))
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
try:
    response = nano.load_data(instance_id, data=dataBlob, append_data=True)
except BoonException as e:
    print("load_data failed: {}".format(e.message))
    sys.exit(1)

# get the buffer status
try:
    response = nano.get_buffer_status(instance_id)
except BoonException as e:
    print("get_buffer_status failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# autotune the configuration
try:
    response = nano.autotune_config(instance_id)
except BoonException as e:
    print("autotune_config failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# run the nano
try:
    response = nano.run_nano(instance_id, results='All')
except BoonException as e:
    print("run_nano failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# get the results again
try:
    response = nano.get_nano_results(instance_id, results='All')
except BoonException as e:
    print("run_nano_status failed: {}".format(e.message))
    sys.exit(1)

# get the nano status
try:
    response = nano.get_nano_status(instance_id, results='averageInferenceTime')
except BoonException as e:
    print("run_nano_status failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# get the buffer status
try:
    response = nano.get_buffer_status(instance_id)
except BoonException as e:
    print("get_buffer_status failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# save the nano
try:
    response = nano.save_nano(instance_id, 'sample-nano-image')
except BoonException as e:
    print("save_nano failed: {}".format(e.message))
    sys.exit(1)

# close/detach the nano instance
try:
    response = nano.close_nano(instance_id)
except BoonException as e:
    print("close_nano failed: {}".format(e.message))
    sys.exit(1)

# open/attach to nano
instance_id_2 = 'sample-instance-2'
try:
    response = nano.open_nano(instance_id_2)
except BoonException as e:
    print("open_nano failed: {}".format(e.message))
    sys.exit(1)

# load the nano
try:
    response = nano.restore_nano(instance_id_2, 'sample-nano-image')
except BoonException as e:
    print("save_nano failed: {}".format(e.message))
    sys.exit(1)

# list the nano instances
try:
    response = nano.nano_list()
except BoonException as e:
    print("configure_nano failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# get the nano status
try:
    response = nano.get_nano_status(instance_id_2, 'All')
except BoonException as e:
    print("run_nano_status failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# retrieve the nano configuration
try:
    response = nano.get_config(instance_id_2)
except BoonException as e:
    print("get_config failed: {}".format(e.message))
    sys.exit(1)
print(json.dumps(response, indent=4))

# close/detach the nano instance
try:
    response = nano.close_nano(instance_id_2)
except BoonException as e:
    print("close_nano failed: {}".format(e.message))
    sys.exit(1)
