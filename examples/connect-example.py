import boonnano as bn
from boonnano import BoonException
import json
import sys

#
# connectivity example for boonnano
#

# create new nano handle
try:
    nano = bn.ExpertClient(license_id='default')
except bn.BoonException as be:
    print(be)
    sys.exit(1)

# open/attach to nano
instance_id = 'my-instance'
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
print(json.dumps(response, indent=4))

# close/detach the nano instance
try:
    response = nano.close_nano(instance_id)
except BoonException as e:
    print("close_nano failed: {}".format(e.message))
    sys.exit(1)
