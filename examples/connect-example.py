import boonnano as bn
import json
import sys

#
# connectivity example for boonnano
#

# create new nano handle
try:
    nano = bn.ExpertClient.from_license_file(license_id='default')

    # open/attach to nano
    instance_id = 'my-instance'
    nano.open_nano(instance_id)

    # retrieve server version
    response = nano.get_version()
    print(json.dumps(response, indent=4))

    # close/detach the nano instance
    nano.close_nano(instance_id)

except bn.BoonException as be:
    print(be.message)
    sys.exit(1)
