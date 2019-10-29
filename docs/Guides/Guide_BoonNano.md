# Guide: BoonNano
<br/>

## General
### [get_version()](../Functions/get_version.md)
>returns the version number of the API that is currently running

<br/>

## Instances
### [get_instance()](../Functions/get_instance.md)
>initializes a nano instance (either using the given ID or using the next available index)

### [get_instance_status()](../Functions/get_instance_status.md)
>checks whether the given instanceID is an instantiated instance

### [delete_instance()](../Functions/delete_instance.md)
>deletes the specified instance or deletes all running instances (if no ID is given)

### [get_running_instances()](../Functions/get_running_instances.md)
>returns a list of running instance IDs

<br/>

## Configuration
### [save_snapshot()](../Functions/save_snapshot.md)
>saves the nano in its current state as a compressed serialized file

### [post_snapshot()](../Functions/post_snapshot.md)
>loads previous nano settings and status to the instantiated instance

### [get_cluster_configuration()](../Functions/get_cluster_configuration.md)
>returns the json block containing the config parameters: mins, maxes, weights, labels (if applicable), numeric type, percent variation, streaming window size, and accuracy

### [get_config_template()](../Functions/get_config_template.md)
>returns a formatted json block from the given parameters

### [post_cluster_configuration()](../Functions/post_cluster_configuration.md)
>loads the given configuration to the nano

### [autotune()](../Functions/autotune.md)
>determines ideal clustering parameters for the given data in the buffer

<br/>

## Cluster
### [post_data()](../Functions/post_data.md)
>uploads data to the buffer to be clustered

### [post_nano_run()](../Functions/post_nano_run.md)
>clusters the data in the buffer

### [get_buffer_status()](../Functions/get_buffer_status.md)
>returns the byte information about the status of the nano

[Return to documentation homepage](../Docs_Landing_Page.md)
