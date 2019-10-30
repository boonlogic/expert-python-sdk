# **post_data()**
<br/>

#### Post data to cluster
##### input
>`nano_instance_id`
>>*instance to reference*
>
>`filename`
>>*either the name of the binary or csv file to upload or the variable name to the numpy array*
>
>`run_nano` = `False`
>>*tells whether or not to run the nano after uploading the data*
>
>`append_data` = `False`
>>*determines whether to append the new data to the data currently in the buffer*
>
>`results` = ''
>>*specifies which result types to return if run_nano is called*    
>>*Options include: ID, RI, SI, FI, DI*     
>[Guide: Results](../Guides/Guide_Nano_Results.md)

##### output
>*`True`,`None` if the upload was successful and no results were requested*

or
>*`True` followed by the json block containing the results that were requested*

or
>*the error code and message prints and then returns `False`,`None`*

<br/>

[back to list](../Index.md)
