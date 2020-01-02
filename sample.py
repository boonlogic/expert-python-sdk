import boonnano as bn
import json
import sys

# open/attach to nano
success,nano=bn.open_nano('example','Rod')
if success != True:
    print("open_nano failed")
    sys.exit(1)

# fetch the version information for this nano instance
success,response=nano.get_version()
if success != True:
    print("get_version failed")
    sys.exit(1)
print(json.dumps(response, indent=4))

# configure the nano by specifying individual parameters
success,response=nano.configure_nano(numeric_format='float',feature_count=20,min=-10,max=15,percent_variation=0.05)
if success != True:
    print("configure_nano failed")
    sys.exit(1)
print(json.dumps(response, indent=4))

# retrieve the nano configuration
success,config=nano.get_config()
if success != True:
    print("configure_nano failed")
    sys.exit(1)

# configure the nano using a pre-nade configuration block
success,response = nano.configure_nano(config=config)
if success != True:
    print("configure_nano failed")
    sys.exit(1)
print(json.dumps(response, indent=4))

# load a csv file and run the nano
dataFile='data.csv'
success,response = nano.load_data(data=dataFile, run_nano=True, results='All')
if success != True:
    print("configure_nano failed")
    sys.exit(1)
print(json.dumps(response, indent=4))

print("=====\n")

# get the nano status
success,response=nano.get_nano_status()
if success != True:
    print("configure_nano failed")
    sys.exit(1)
print(json.dumps(response, indent=4))

nano.close_nano()
