import boonnano as bn
import json
import sys
import csv

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

# configure the nano by specifying individual parameters
success, response = nano.configure_nano(numeric_format='float32', feature_count=20, min=-10, max=15,
                                        percent_variation=0.05)
if not success:
    print("configure_nano failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))
json_config = response

# retrieve the nano configuration
success, response = nano.get_config()
if not success:
    print("get_config failed: {}".format(response))
    sys.exit(1)
print(json.dumps(response, indent=4))

# configure the nano using a pre-made configuration block
success, response = nano.configure_nano(config=json_config)
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

print("=====\n")

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
