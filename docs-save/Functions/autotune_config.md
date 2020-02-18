# **autotune_config()**
<br/>

[How-to: Auotune Data](../How-Tos/How_To_Autotune_Data.md)

#### Calculates and sets ideal min, max, and percent variations for the data in the buffer
##### input
>`nano_handle`
>>*dictionary handle in reference to specified nano connection*
>
>`autotune_pv` = `True`
>>*tells whether to autotune the percent variation or use the one given in the config*
>
>`autotune_range` = `True`
>>*determines whether to autotune the mins and maxes or just use the values previously given in the config*
>
>`by_feature` = `False`
>>*whether to autotune the min and max per feature or overall*
>
>`exclusions` = {}
>>*when autotuning by feature, exclusions are the one-based indexes of the columns to omit from the autotuning*

#### output
>*`True` if the call was successful*

or
>*print the error code and message and return `False`*

<br/>

[back to list](./Index.md)