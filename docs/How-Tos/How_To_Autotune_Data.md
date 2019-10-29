# How-to: Autotune Data

Start by downloading the python client library, importing the appropriate libraries, and defining the initialization call.

Define the main function and store the BoonNano class object in a variable, bn. For the second argument, use the port number assigned to your account and the third argument is the 32 digit token key generated specifically for your account.
```python
def main():
    bn = BoonNano.BoonNano('localhost',5007,'2B69F78F61A572DBF8D1E44548B48')
```

Save the file.

### Autotune
First, start up an instance and post a config. Since the config is going to be autotuned anyway, the important parameters are the data type and number of features. The rest can be arbitrary values.
```python3
success, instance = bn.get_instance()
success, config = bn.get_config_template(float, 20, -10, 15) #default values for weight, percent_variation, streaming_window, and accuracy are automatically set
success = bn.post_cluster_configuration(instance, config)
```

In order to autotune the parameters, the pipeline needs data to train off of, so post data without running the nano.
```python
bn.post_data(instance, 'Data.csv')
```
Now it is all set to call `autotune`.

```python
success, config = bn.autotune(instance)
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
