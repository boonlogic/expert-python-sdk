# **post_nano_run()**
<br/>

#### Clusters any existing data in the buffer
##### input
>`nano_instance_id`
>>*instance to reference*
>
>`results`=''
>>*specifies which result types to return if run_nano is called*    
>>*Options include: ID, RI, SI, FI, DI*     
>[Guide: Results](../Guides/Guide_Nano_Results.md)

##### output
>*`True`,`None` if the upload was successful and no results were requested*

or
>*`True` followed by the json block containing the results that were requested*

or
>*the error code and message prints and then returns `False`,`None`*

[back to list](../Index.md)
