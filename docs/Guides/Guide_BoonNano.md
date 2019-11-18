# Guide: BoonNano
<br/>

## General
### [get_version()](../Functions/get_version.md)
>returns the version number of the API that is currently running

<br/>

## Instances
### [create_instance()](../Functions/create_instance.md)
>initializes a nano instance (either using the given ID or using the next available index)

### [is_running_instance()](../Functions/is_running_instance.md)
>checks whether the given instanceID is an instantiated instance

### [delete_instance()](../Functions/delete_instance.md)
>deletes the specified instance or deletes all running instances (if no ID is given)

### [get_running_instances()](../Functions/get_running_instances.md)
>returns a list of running instance IDs

<br/>

## Configuration
### [save_snapshot()](../Functions/save_snapshot.md)
>saves the nano in its current state as a compressed serialized file

### [load_snapshot()](../Functions/load_snapshot.md)
>loads previous nano settings and status to the instantiated instance

### [get_config()](../Functions/get_config.md)
>returns the json block containing the config parameters: mins, maxes, weights, labels (if applicable), numeric type, percent variation, streaming window size, and accuracy

### [generate_config()](../Functions/generate_config.md)
>returns a formatted json block from the given parameters

### [set_config()](../Functions/set_config.md)
>loads the given configuration to the nano

### [autotune_config()](../Functions/autotune_config.md)
>determines ideal clustering parameters for the given data in the buffer

<br/>

## Cluster
### [load_data()](../Functions/load_data.md)
>uploads data to the buffer to be clustered

### [run_nano()](../Functions/run_nano.md)
>clusters the data in the buffer

### [get_buffer_status()](../Functions/get_buffer_status.md)
>returns the byte information about the status of the nano

### [get_nano_results()](../Functions/get_nano_results.md)
>returns status results for each pattern clustered

### [get_nano_status()](../Functions/get_nano_status.md)
>returns results for each cluster created

<br/>

[Return to documentation homepage](../README.md)
