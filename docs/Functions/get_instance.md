# **get_instance()**
<br/>

#### Start up an arbitrary instance
##### input
>*None*

##### output
>*`True` and the next available instance ID that is not currently running.*   

>*`False` followed by the error code and message*

-----------

<br/>

#### Start an instance at the given ID
##### input
>`nano_instance_id`  
>>*Input an integer as the desired ID for the instance*

##### output
>*If the input ID is available, the `True` along with `nano_instance_id` is returned*    

or
>*If the value is an already running instance, the error code and message is printed and the function returns `False`,`None`*

[back to list](../Index.md)
