# How-to: Autotune Data

Start by downloading the python client library, importing the appropriate libraries, and defining the initialization call.

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

### Autotune
First, start up an instance and post a config. Since the config is going to be autotuned anyway, the important parameters are the data type and number of features. The rest can be arbitrary values.
```python
success, instance = bn.create_instance()
success, config = bn.generate_config(float, 20, -10, 15) #default values for weight, percent_variation, streaming_window, and accuracy are automatically set
success = bn.set_config(instance, config)
```

In order to autotune the parameters, the pipeline needs data to train off of, so post data without running the nano.
```python
bn.load_data(instance, 'Data.csv')
```
Now it is all set to call `autotune`.

```python
success, = bn.autotune_config(instance)
```

There are a few different options that go along with this:

##### by_feature
Autotune tries to find the best min, max, and percent variation for the data posted, but the min and max might not apply to the data overall. by_feature tells autotune to set each column of data with a different min and max specific for that column. The default is false.

One example of an application is if each column has a different meaning. For instance: {weight, height, age, blood pressure}. Each column would not benefit with an overall min and max since they are all so different.

##### autotune_pv
This bool variable specifies whether to autotune the percent variation or use the given one from the original config. The default is true.

##### autotune_range
Similarly, this bool variable tells whether to autotune the min and max or use the values given from the original config. The default is true.

##### exclusions
This option only applies when autotuning by feature. Using one-based indexing, the exclusions are the list of column indexes that should be ignored when autotuning the min and max and the original config's min and max value are used on those columns. The default is an empty list.


Then at the end you have the file:
```python
import BoonNano as bn

bn.setup_connection('username','~/.BoonLogic')
success, instance = create_instance()
success, config = bn.generate_config(float, 20, -10, 15) #default values for weight, percent_variation, streaming_window, and accuracy are automatically set
success = bn.set_config(instance, config)
bn.load_data(instance, 'Data.csv')
success = bn.autotune_config(instance)
bn.close_connection()
```
<br/>

[Return to documentation homepage](../README.md)
