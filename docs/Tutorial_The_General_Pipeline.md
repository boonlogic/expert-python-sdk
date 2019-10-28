# Tutorial: The General Pipeline

If the client library is already downloaded from [GitLab](https://gitlab.boonlogic.com/development/tools/boonnanopyapi), skip to [Setting up client library](#setup)

### Download the python client library
[Python3](https://programwithus.com/learn-to-code/install-python3-mac/) is needed to run the python client library for the Nano API.

Go to the [Python API Github repository](https://gitlab.boonlogic.com/development/tools/boonnanopyapi) and download `BoonNano.py` into the directory

### Setting up client library (Mac OS) {#setup}
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoExample.py` in the same folder as where `BoonNano.py` is saved.

One the first five lines import the following libraries:
- os
- BoonNano
- time
- numpy
- json

the code should look like this:
```
import os
import BoonNano
import time
import numpy as np
import json
```

Enter down twice and define the main function on line 7.
```
def main():
```

On the next line, store the BoonNano class object in a variable, bn. For the second argument, use the port number assigned to your account and the third argument is the 32 digit token key generated specifically for your account.
```
bn = BoonNano.BoonNano('localhost',5007,'2B69F78F61A572DBF8D1E44548B48')
```
Enter down a few times and define the initiliazation call:
```
if __name__ == "__main__":
    main()
```
Every other instruction should be done within the main() function, keeping the initialization at the end of the file.

Save the file.


### Post the configuration
On the next line of the main function, use the function get_config_template() to generate the json configuration block specific for a dataset.
```
success, config = bn.get_config_template('float', 20, -10, 15, percent_variation=0.037)
```
Initializing the instance.
```
success, instance = bn.get_instance()
```
Using that instance ID number, post the configuration by pointing it to that specific instance.
```
bn.postClusterConfiguration(instance, config)
```

Once the config is posted, the nano has everything it needs to start reading in data. Download the example data file from [Gitlab](https://gitlab.boonlogic.com/development/tools/boonnanopyapi/tree/master/docs) and save it in the same folder as `NanoExample.py`. Post the data by telling it the instance to post to and the file name.
```
bn.post_data(instance, 'Data.csv')
```
Finally, call the runNano() function to cluster the data and print out the status.
```
success = bn.post_nano_run(instance)
print(success)
```
Go to the terminal and cd into the folder where the .py files are saved. Run `NanoExample.py`.
```
$ python3 NanoExample.py
```
You should see the output:
```

#################################
Opening BoonNano Client
URL:  http://localhost:5007/expert/v2/
#################################
True
Closing Pool
```
At this point, the data is clustered. Reference ****** for more detail on how to generate results and ***** for more details on the types of analysis.
