# Tutorial: Posting a Configuration

If the client library is already downloaded from [Github](https://github.com/boonlogic/Python_API), skip to __Setting up client library__

### Download the python client library
[Python3](https://programwithus.com/learn-to-code/install-python3-mac/) is needed to run the python client library for the Nano API.

Go to the [Python API Github repository](https://github.com/boonlogic/Python_API) and clone it.

### Setting up client library (Mac OS) {#setup}
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoConfig.py`.

One the first line import the BoonNano library:
```python
import BoonNano as bn
```
On the next line, start the http connection to the BoonNano server. Input the user whose authentication criteria you want to use and the file path to your .BoonLogic authentication file.
```python
bn.setup_connection('userName','~/.BoonLogic')
```
Enter down a few lines and close the connection.
```python
bn.close_connection()
```
Save the file.

All the following code will be entered between the setup and close connection calls.

### Generate the configuration block
On line 9, use the function get_config_template() to generate the json configuration block specific for a dataset.
```python
success, config = bn.generate_config('float', 20, -10, 15, percent_variation=0.037)
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
{'accuracy': 0.99, 'features': [{'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}], 'numericFormat': 'float', 'percentVariation': 0.037, 'streamingWindowSize': 1}
```

### Post the configuration

Now you have all the pieces to start actually using the nano. First start by initializing the instance on line 11.
```python
success, instance = bn.create_instance()
```
Using that instance ID number, post the configuration by pointing it to that specific instance.
```python
success = bn.set_config(instance, config)
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
{'accuracy': 0.99, 'features': [{'maxVal': 15, 'minVal': -10, 'weight': 1}, ... {'maxVal': 15, 'minVal': -10, 'weight': 1}], 'numericFormat': 'float', 'percentVariation': 0.037, 'streamingWindowSize': 1}
True
```
The output here is abbreviated but in terminal the json block in the middle will print out all features.
The second to last line is the status of your configuration post.

If the status is True, then congratulations! The end `NanoConfig.py` file is:
```python
import BoonNano as bn

bn.setup_connection('username','~/.BoonLogic')
success, config = bn.generate_config('float', 20, -10, 15, percent_variation=0.037)
print(config)
success, instance = bn.create_instance()
success = bn.set_config(instance, config)
print(success)
bn.close_connection()
```
<br/>
<br/>

See [Tutorial: The General Pipeline](./Tutorial_The_General_Pipeline.md) for next steps.

<br/>

[Return to documentation homepage](../README.md)
