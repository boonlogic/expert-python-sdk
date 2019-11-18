# Tutorial: The General Pipeline

If the client library is already downloaded from [Github](https://github.com/boonlogic/Python_API), skip to [Setting up client library](#setup)

### Download the python client library
[Python3](https://programwithus.com/learn-to-code/install-python3-mac/) is needed to run the python client library for the Nano API.

Go to the [Python API Github repository](https://github.com/boonlogic/Python_API) and clone it.

### Setting up client library (Mac OS) {#setup}
Open a text editor of your choice (one free option is [Atom](https://atom.io/)). Go up to the menu bar and under "File" -> "Save As..." save your file as `NanoExample.py`.

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

### Post the configuration
On the next line of the main function, use the function get_config_template() to generate the json configuration block specific for a dataset.
```python
success, config = bn.generate_config('float', 20, -10, 15, percent_variation=0.037)
```
Initializing the instance.
```python
success, instance = bn.create_instance()
```
Using that instance ID number, post the configuration by pointing it to that specific instance.
```python
bn.set_config(instance, config)
```

Once the config is posted, the nano has everything it needs to start reading in data. Post the data by telling it the instance to post to and the file name (`Data.csv` is an example dataset that was cloned in the `Python_API` repository).
```python
bn.load_data(instance, 'Data.csv')
```
Finally, call the `runNano()` function to cluster the data and print out the status.
```python
success = bn.run_nano(instance)
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
import BoonNano as bn

bn.setup_connection('username','~/.BoonLogic')
success, config = bn.generate_config('float', 20, -10, 15, percent_variation=0.037)
success, instance = bn.create_instance()
bn.set_config(instance, config)
bn.load_data(instance, 'Data.csv')
success = bn.run_nano(instance)
print(success)
bn.close_connection()
```
<br/>
<br/>

Reference [How-to: Generate Cluster Results](../How-Tos/How_To_Generate_Cluster_Results.md) for more detail on how to generate results and [Guide: Results](../Guides/Guide_Nano_Results) or [Guide: Status](../Guides/Guide_Nano_Status.md) for more details on the types of analysis.

<br/>

[Return to documentation homepage](../README.md)
