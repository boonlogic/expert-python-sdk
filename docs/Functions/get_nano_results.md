# **get_nano_results()**
<br/>

#### Returns a list of each metric that is requested with values correlating to each pattern clustered
##### input
>`nano_instance_id`
>>*instance to reference*
>
>`results` = All
>>*specifies which result types to return if run_nano is called*    
>>*Options include: ID, RI, SI, FI, DI*     
>>*NOTE: `None` is not an option for `results` in this call*     
>[Guide: Results](../Guides/Guide_Nano_Results.md)

##### output
>*`True` followed by the json block containing the results that were requested*

or
>*the error code and message prints and then returns `False`,`None`*

[back to list](../Index.md)
