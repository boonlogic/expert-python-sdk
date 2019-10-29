# **get_config_template()**
<br/>

#### Generate a correctly formatted config json block from the given parameters
##### input
>`numeric_type`
>>*float, int, or native specifies how to read in the file*
>
>`number_of_features`
>>*number of columns in the data or the dimension of the vector tells how to partition the data*
>
>`min` = 1
>>*minimum rounding cutoff for the data*
>
>`max` = 10
>>*maximum rounding cutoff for the data*
>
>`weight` = 1
>>*weights for each column (will be normalized if not inputted as such)*
>
>`percent_variation` = 0.05
>>*parameter to specify the granularity of the clusters*
>
>`streaming_window` = 1
>>*how many patterns/vectors to concatenate together into one vector (as in a parametric case)*
>
>`accuracy` = 0.99
>>*the percentage for calculating a z value on the statistical accuracy of the clustering*

##### output
>*`True` followed by the json string (successful call)*

or
>*error code and message are printed and `False`,`None` is returned if the called failed*   

[back to list](../Index.md)
