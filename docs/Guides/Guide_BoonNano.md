# Guide: BoonNano
<br/>

## General
### [get_version()](../Functions/get_version.md)
>returns the version number of the API that is currently running

### [open_nano()](../Functions/open_nano.md)
>starts a nano with the given label, returning a handle to access it

### [close_nano()](../Functions/close_nano.md)
>deletes the specified nano and closes the server connection

### [nano_list()](../Functions/nano_list.md)
>returns a list of running instance labels

<br/>

## Configuration
### [save_nano()](../Functions/save_nano.md)
>saves the nano in its current state as a compressed serialized file

### [get_config()](../Functions/get_config.md)
>returns the json block containing the config parameters: mins, maxes, weights, labels (if applicable), numeric type, percent variation, streaming window size, and accuracy

### [configure_nano()](../Functions/configure_nano.md)
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

[Return to documentation homepage](../python-docs.md)
