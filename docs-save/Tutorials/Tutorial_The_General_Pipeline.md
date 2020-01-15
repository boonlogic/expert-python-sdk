# Tutorial: The General Pipeline

Import the python client library from PyPI from the command line:
```sh
pip install boonnano
```

Then follow the steps below to create the file to run the data:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')
bn.configure_nano(nano, numeric_format='float', feature_count=20, min=-10, max=15, percent_variation=0.037)
success, config = bn.get_config(nano)
print(config)
bn.load_data(nano, 'Data.csv')
success = bn.run_nano(nano)
print(success)
bn.close_nano(nano)
```

### Setting up client library
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoExample.py`.

One the first line import the boonnao library:
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

### Post the configuration
On line 4, use the function configure_nano() to generate the json configuration block specific for a dataset and set up the nano.
```python
success = bn.configure_nano(nano, numeric_type='float', feature_count=20, min=-10, max=15, percent_variation=0.037)
```
Add a call to print out the configuration generated.
```python
success,config = bn.get_config(nano)
print(config)
```
Save the file.

Once the config is posted, the nano has everything it needs to start reading in data. Post the data by telling it the instance to post to and the file name (`Data.csv` is an example dataset in the `Python_API` repository).
```python
bn.load_data(nano, 'Data.csv')
```
Finally, call the `run_nano()` function to cluster the data and print out the status.
```python
success = bn.run_nano(nano)
print(success)
```
Go to the terminal and cd into the folder where the `NanoExample.py` file is saved. Run `NanoExample.py`.
```sh
$ python3 NanoExample.py
```
You should see the output:
```sh
True
```
At this point, the data is clustered and `NanoExample.py` should look like this:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')
success,config = bn.configure_nano(nano, numeric_type='float', feature_count=20, min=-10, max=15, percent_variation=0.037)
success, config = bn.get_config(nano)
print(config)
bn.load_data(nano, 'Data.csv')
success = bn.run_nano(nano)
print(success)
bn.close_nano(nano)
```
<br/>
<br/>

Reference [How-to: Generate Cluster Results](../How-Tos/How_To_Generate_Cluster_Results.md) for more detail on how to generate results and [Guide: Results](../Guides/Guide_Nano_Results) or [Guide: Status](../Guides/Guide_Nano_Status.md) for more details on the types of analysis.

<br/>

[Return to documentation homepage](../python-docs.md)
