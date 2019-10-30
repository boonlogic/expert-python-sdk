# How-to: Generate Cluster results

Start by downloading the python client library, importing the appropriate libraries, and defining the initialization call.

Define the main function and store the BoonNano class object in a variable, bn. For the second argument, use the port number assigned to your account and the third argument is the 32 digit token key generated specifically for your account.
```python
def main():
    bn = BoonNano.BoonNano('localhost',5007,'2B69F78F61A572DBF8D1E44548B48')
```

Save the file.

### Cluster the Data
Initialize an instance and post a configuration.
```python
success, instance = bn.get_instance()
success, config = bn.get_config_template('float', 20, -10, 15, percent_variation=0.037)
bn.post_cluster_configuration(instance, config)
```

Next, post the data either by giving it the file name of your data or the variable name of the numpy array. Post the data either by calling run_nano() after the data is uploaded or set run_nano=True in the post_data() input parameters.
```python
bn.post_data(instance, 'Data.csv', run_nano=True)
```

### Cluster Results
There are two ways to return the results.

##### get_nano_results()
First way is as a separate call.
Once the data is uploaded and clustered, call `get_nano_results(instance)`.
This returns the list of IDs, Anomaly Indexes, Smoothed Anomaly Indexes, Frequency Indexes, and Distance Indexes. The length of each list is the number of patterns clustered when running the nano.
```python
success, results = bn.get_nano_results(instance)
```
To specify only certain results, add the input parameter `results` set as a list of the desired results.
```python
success, results = bn.get_nano_results(instance, results={ID,RI})
```

##### results (as a variable)
The second way to request results is to call it while uploading the data or after running the nano. Calling it after uploading the data only works they way one would expect as long as run_nano is also set to `True` in the `post_data` function call.
```python
success, results = bn.post_data(instance, 'Data.csv', run_nano=True, results=All)
```
>NOTE: if run_nano is not specified to `True`, the returned results will be whatever the previous results were and not the results from clustering the most recently posted data (which hasn't been clustered yet). That means that if it is the first time clustering since the instance was instantiated, the results will be empty.

or calling it after posting a nano run works the same way.
```python
success, results = bn.post_data(instance, 'Data.csv')
success, results = bn.post_nano_run(instance, results=All)
```

<br/>

[Return to documentation homepage](../Python_Landing_Page.md)
