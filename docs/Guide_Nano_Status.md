# Guide: Nano Status

See [How-to: Generate Cluster Status](http://github.com) for instructions on generating nano status statistics.

### Options
The nano status stats can only be called from `getNanoStatus()`. There are 12 return types:
- pca
- cluster_sizes
- anomaly_indexes
- frequency_indexes
- distance_indexes
- cluster_growth
- pattern_memory
- number_of_clusters
- total_inferences
- average_inference_time
- All
- ""

and any subset of these (where `All` takes precedent and "" is weighted the least).

Each of these options are an overview of the clusters created. The first seven options specified above are lists of length equal to the number of clusters created including the zero cluster (with the exception of patternMemory). Excluding cluster_growth, each index of those same lists corresponds to the cluster ID (zero-based except for patternMemory which is one-based indexing).

##### pca
The nano's `pca` is similar to Principal Component Analysis except it transforms the pattern memory space to three dimensions with ranges from 0 to 1 in each dimension. This is most commonly used as RGB values to give a gradient representation for each cluster. The three spanning cluster vectors will transform to colors closest to red, green, and blue while the other clusters fill in the space based on their Hamming distance to other clusters. Since the cluster IDs don't represent clusters that are close to each other, the RGB application of the PCA can be used to gain an understanding of where each cluster is in relation to the other clusters.

The zero cluster is always the first value in the list of PCA values and is always represented by {0, 0, 0}.

##### cluster_sizes
Each value in this list gives the number of patterns placed in the cluster corresponding to the zero-based index of the list. (i.e. the first element is the number of patterns in the cluster 0, etc)

##### anomaly_indexes
The zero-based indexes of the list correspond to the cluster IDs and at each index is the resulting anomaly index associated with that cluster. These values are integers that range from 0 to 1000 where values of 0 are the most common cluster and values close to 1000 are anomalous. The first element in the list is always 1000 since cluster zero is automatically categorized as an anomaly.

##### frequency_indexes
Similar to the anomaly indexes, each indexed value in this list gives the frequency index associated with the cluster whose ID matches the zero-based index. These values are integers that range from 0 to infinity. While there is no definitive upper bound, each cluster space will have a local upper bound. Values below 1000 are more frequent than average, where 0 is the most common cluster. Values above 1000 are infrequent and the further they are from 1000, the more infrequent they are. This statistic is a dual threshold value where anomalies could be considered when they have values on either side of 1000.

##### distance_indexes
The last of the zero-base indexed lists, the distance indexes are values that tell of the cluster's spatial relation to the other clusters. Values close to 1000 are very far away from the center of the cluster space and values close to 0 are located in the center of all the clusters. On average, these values don't vary much and develop a natural mean (not necessarily around 500). This is also a dual threshold statistic since the natural mean represents the typical spacing of the clusters and there can be abnormally close clusters and abnormally spread out clusters.

##### cluster_growth
The cluster growth curve is a two dimensional plot that gives the user a feel for the clustering behavior over time. During a training run with purely normal data, the curve looks logarithmic approaching an asymptote. Then when an anomaly occurs, the cluster count increases in another smaller logarithmic curve above the original training curve. The list returned by cluster_growth are the indexed pattern numbers where a new cluster was created which are also the x-values of this curve. The y-values can be derived from the zero-based index values of the list. For instance, if cluster_growth returns {0,1,5,7,20}, the coordinates become {{0,0},{1,1},{5,2},{7,20}}.

##### pattern_memory
The pattern memory represents the vector transform from the original pattern space to the cluster's location in the cluster space. These are vectors in binary space that have been encode to base64.
>NOTE: cluster zero does not a representation in cluster space since it is not created from a new cluster but rather is a catch all cluster.

##### number_of_clusters
This is exactly what the variable says it is: the number of clusters created up to that point which includes cluster zero. This value should equal the length of the lists: pca, cluster_sizes, anomaly_indexes, frequency_indexes, distance_indexes, cluster_growth, and is one more than the length of the first dimension of pattern_memory.

##### total_inferences
This is the total number of patterns successfully clustered. The total of all the values in cluster_sizes should also equal this value.

##### average_inference_time
The value returned here is the average time to cluster each inference in microseconds.

##### ''
Setting results equal to an empty string will omit any results being returned. This is not an option when calling `get_nano_status` since that function is called only when at least one value is desired.

##### All
Finally, setting results to All will return all of the options listed above as a JSON block.

For more statistical values, see [Guide: Nano Results](https://gitlab.boonlogic.com/development/tools/boonnanopyapi/blob/master/docs/Guide_Nano_Results.md)
