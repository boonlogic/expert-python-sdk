# Tutorial: Posting a Configuration

Import the python client library from PyPI from the command line:
```sh
pip install boonnano
```

Then follow the steps below to create the file to run the data:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')
bn.configure_nano(nano, numeric_format='float', feature_count=20, min=-10, max=15, weight=1, percent_variation=0.037, streaming_window=1, accuracy=0.99)
success,config = bn.get_config(nano)
print(config)
bn.close_nano(nano)
```

### Setting up client library
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoConfig.py`.

One the first line import the BoonNano library:
```python
import boonnano as bn
```
On the next line, start up a nano. Input a label and the user whose authentication criteria you want to use.
```python
success,nano = bn.open_nano('example','username')
```
Enter down a few lines and close the nano.
```python
bn.close_nano(nano)
```
Save the file.

All the following code will be entered between the setup and close connection calls.

### Configure the nano
On line 4, use the function configure_nano() to generate the json configuration block specific for a dataset and set up the nano.
```python
success = bn.configure_nano(nano, numeric_format='float', feature_count=20, min=-10, max=15, percent_variation=0.037)
```
Add a call to print out the configuration generated.
```python
success,config = get_config(nano)
print(config)
```
Save the file.

### Print out the configuration
Go to the terminal and cd into the folder where the .py file is saved. Run `NanoConfig.py`.
```sh
$ python3 NanoConfig.py
```
You should see the output:
```sh
{'accuracy': 0.99, 'features': [{'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}, {'maxVal': 15, 'minVal': -10, 'weight': 1}], 'numericFormat': 'float', 'percentVariation': 0.037, 'streamingWindowSize': 1}
```

And you are done! The end `NanoConfig.py` file is:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')
bn.configure_nano(nano, numeric_format='float', feature_count=20, min=-10, max=15, weight=1, percent_variation=0.037, streaming_window=1, accuracy=0.99)
success,config = bn.get_config(nano)
print(config)
bn.close_nano(nano)
```
<br/>
<br/>

See [Tutorial: The General Pipeline](./Tutorial_The_General_Pipeline.md) for next steps.

<br/>

[Return to documentation homepage](../python-docs.md)
