# Tutorial: Posting a Configuration

If the client library is already downloaded from [GitLab](https://gitlab.boonlogic.com/development/tools/boonnanopyapi), skip to [Setting up client library](#setup)

### Download the python client library
[Python3](https://programwithus.com/learn-to-code/install-python3-mac/) is needed to run the python client library for the Nano API.

Go to the [Python API Github repository](https://gitlab.boonlogic.com/development/tools/boonnanopyapi) and download `BoonNano.py` into the directory

### Setting up client library (Mac OS) {#setup}
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoConfig.py` in the same folder as where `BoonNano.py` is saved.

One the first five lines import the following libraries:
- os
- BoonNano
- time
- numpy
- json

the code should look like this:
```python
import os
import BoonNano
import time
import numpy as np
import json
```

Enter down twice and define the main function on line 7.
```python
def main():
```

On the next line, store the BoonNano class object in a variable, bn. For the second argument, use the port number assigned to your account and the third argument is the 32 digit token key generated specifically for your account.
```python
bn = BoonNano.BoonNano('localhost',5007,'2B69F78F61A572DBF8D1E44548B48')
```
Enter down seven times and on line 15 and 16, define the initiliazation call:
```python
if __name__ == "__main__":
    main()
```

Save the file.


### Generate the configuration block
On line 9, use the function get_config_template() to generate the json configuration block specific for a dataset.
```python
success, config = bn.get_config_template('float', 20, -10, 15, percent_variation=0.037)
```
Add a call to print out the configuration generated.
```python
print(config)
```
Save the file.

### Print out the configuration
Go to the terminal and cd into the folder where the .py files are saved. Run `NanoConfig.py`.
```sh
$ python3 NanoConfig.py
```
You should see the output:
```sh
#################################
Opening BoonNano Client
URL:  http://localhost:5007/expert/v2/
#################################
{'accuracy': 0.99, 'features': [{'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}], 'numericFormat': 'float', 'percentVariation': 0.037, 'streamingWindowSize': 1}
Closing Pool
```

### Post the configuration

Now you have all the pieces to start actually using the nano. First start by initializing the instance on line 11.
```python
success, instance = bn.get_instance()
```
Using that instance ID number, post the configuration by pointing it to that specific instance.
```python
success = bn.post_cluster_configuration(instance, config)
```
Print out the  status of the post.
```python
print(success)
```
Save the file.

Now, go to back to the terminal and run `NanoConfig.py` again.
```sh
$ python3 NanoConfig.py
```
You should see the output:
```sh
#################################
Opening BoonNano Client
URL:  http://localhost:5007/expert/v2/
#################################
{'accuracy': 0.99, 'features': [{'maxVal': 15, 'minVal': -10, 'weight': 1}, ... {'maxVal': 15, 'minVal': -10, 'weight': 1}], 'numericFormat': 'float', 'percentVariation': 0.037, 'streamingWindowSize': 1}
True
Closing Pool
```
The output here is abbreviated but in terminal the json block in the middle will print out all features.
The second to last line is the status of your configuration post.

If the status is True, then congratulations!
