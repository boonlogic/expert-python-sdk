# **get_nano_status()**
<br/>

#### Get metric results for each cluster created
##### input
>`nano_instance_id`
>>*instance to reference*
>
>`results` = All
>>*specifies which result types to return if run_nano is called*    
>>*Options include: pca, pattern_memory, cluster_growth, cluster_sizes, anomaly_indexes, frequency_indexes, distance_indexes, total_inferences, average_inference_time, num_clusters*    
>>*NOTE: `None` is not an option for `results` in this call*    
>[Guide: Status](../Guides/Guide_Nano_Status.md)

##### output
>*`True` followed by the json block containing the results that were requested*

or
>*the error code and message prints and then returns `False`,`None`*

<br/>

[back to list](../Index.md)
