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
