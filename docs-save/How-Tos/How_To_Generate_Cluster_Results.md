# How-to: Generate Cluster results

Import the python client library from PyPI from the command line:
```sh
pip install boonnano
```

One the first line import the boonnano library:
```python
import boonnano as bn
```
On the next line, start the http connection to the BoonNano server. Input the user whose authentication criteria you want to use and the file path to your .BoonLogic authentication file.
```python
success,nano = bn.open_nano('example','userName')
```
Enter down a few lines and close the connection.
```python
bn.close_nano(nano)
```
Save the file.

All the following code will be entered between the setup and close connection calls.

### Cluster the Data
Initialize an instance and post a configuration.
```python
success = bn.configure_nano(nano, 'float', 20, -10, 15, percent_variation=0.037)
```

Next, post the data either by giving it the file name of your data or the variable name of the numpy array. Post the data either by calling run_nano() after the data is uploaded or set run_nano=True in the post_data() input parameters.
```python
bn.load_data(nano, 'Data.csv', run_nano=True)
```

### Cluster Results
There are two ways to return the results.

##### get_nano_results()
First way is as a separate call.
Once the data is uploaded and clustered, call `get_nano_results(instance)`.
This returns the list of IDs, Anomaly Indexes, Smoothed Anomaly Indexes, Frequency Indexes, and Distance Indexes. The length of each list is the number of patterns clustered when running the nano.
```python
success, results = bn.get_nano_results(nano)
```
To specify only certain results, add the input parameter `results` set as a list of the desired results.
```python
success, results = bn.get_nano_results(nano, results={ID,RI})
```

##### results (as a variable)
The second way to request results is to call it while uploading the data or after running the nano. Calling it after uploading the data only works they way one would expect as long as run_nano is also set to `True` in the `load_data` function call.
```python
success, results = bn.load_data(nano, 'Data.csv', run_nano=True, results=All)
```
>NOTE: if run_nano is not specified to `True`, the returned results will be whatever the previous results were and not the results from clustering the most recently posted data (which hasn't been clustered yet). That means that if it is the first time clustering since the instance was instantiated, the results will be empty.

or calling it after posting a nano run works the same way.
```python
success, results = bn.load_data(nano, 'Data.csv')
success, results = bn.run_nano(nano, results=All)
```

The resulting file will have a slight variation from the following example:
```python
import boonnano as bn

success,nano = bn.open_nano('example','username')
success = bn.configure_nano(nano, float, 20, -10, 15, percent_variation=0.037)

# The following may vary depending on how you call the results
bn.load_data(nano, 'Data.csv',run_nano=True, results=All)
bn.run_nano(nano, results={ID,RI})
bn.get_nano_results(nano, results={DI,SI})
bn.close_nano(nano)
```
<br/>
<br/>

[Return to documentation homepage](../python-docs.md)
