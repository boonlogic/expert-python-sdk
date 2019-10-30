# **get_buffer_status()**
<br/>

#### Gives a status check on the bytes going through the nano
##### input
>`nano_instance_id`
>>*instance to reference*

##### output
>*`True` followed by the JSON block containing the status*   
>>*JSON contains:*   
>*- totalBytesInBuffer*   
>*- totalBytesProcessed*   
>*- totalBytesWritten*   

or
>*error code and message prints and returns `False`,`None` if the call failed*

<br/>

[back to list](../Index.md)
