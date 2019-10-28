# How-to: Generate Cluster Results

Start by downloading the python client library, importing the appropriate libraries, and defining the initialization call.

Define the main function and store the BoonNano class object in a variable, bn. For the second argument, use the port number assigned to your account and the third argument is the 32 digit token key generated specifically for your account.
```
def main():
    bn = BoonNano.BoonNano('localhost',5007,'2B69F78F61A572DBF8D1E44548B48')
```

Save the file.


### Cluster the Data
Initialize an instance and post a configuration.
```
success, instanceID = bn.getInstance()
success, config = bn.getConfigTemplate('float', 20, -10, 15, percentVariation=0.037)
bn.postClusterConfiguration(instanceID, config)
```

Next, post the data either by giving it the file name of your data or the variable name of the numpy array. Post the data either by calling runNano() after the data is uploaded or set runNano=True in the uploadData() input parameters.
```
bn.uploadData(instanceID, 'Data.csv', runNano=True)
```

### Cluster Results
There are two ways to return the results.

##### getNanoResults()
First way is as a separate call.
Once the data is uploaded and clustered, call `getNanoResults(instanceID)`.
This returns the list of IDs, Anomaly Indexes, Smoothed Anomaly Indexes, Frequency Indexes, and Distance Indexes. The length of each list is the number of patterns clustered when running the nano.
```
success, results = getNanoResults(instanceID)
```
To specify only certain results, add the input parameter `Results` set as a list of the desired results.
```
success, results = getNanoResults(instanceID, Results={ID,RI})
```

##### Results (as a variable)
The second way to request results is to call it while uploading the data, as long as runNano is also set to `True` in the `uploadData` function call.
```
success, results = uploadData(instanceID, 'Data.csv', runNano=True, Results=All)
```
>NOTE: if runNano is not specified to `True`, the returned results will be whatever the previous results were and not the results from clustering the most recently posted data (which hasn't been clustered yet). That means that if it is the first time clustering since the instance was instantiated, the results will be empty.
