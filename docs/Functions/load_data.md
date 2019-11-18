# **load_data()**
<br/>

#### Post data to cluster
##### input
>`instance_id`
>>*instance to reference*
>
>`data`
>>*either the name of the binary or csv file to upload or the variable name to the numpy array*
>
>`file_type` = ''
>>*specify whether the data file is csv or binary (if not specified, it is inferred from the file extension)*
>
>`gzip` = `False`
>>*whether the file being loaded is compressed or not*
>
>`metadata` = ''
>>*pre processing keys for uploading the data before storing it in the buffer*
>
>`append_data` = `False`
>>*determines whether to append the new data to the data currently in the buffer*
>
>`run_nano` = `False`
>>*tells whether or not to run the nano after uploading the data*
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

[back to list](./Index.md)
