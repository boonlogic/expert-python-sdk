# Guide: Nano Results

See [How-to: Generate Cluster Results](http://github.com) for instructions on generating the results.

### Options
The results call (no matter where you call it from) has seven options:
- ID
- RI
- SI
- FI
- DI
- MD
- All
- ""

and any subset of those.

Each of these lists is the same length as the number of patterns that was most recently clustered, so each value in the resulting list corresponds to the pattern/vector in the same location of the list of patterns/vectors.

##### ID
The `ID` placeholder corresponds to the cluster IDs. These are integer values ranging from 1 (or sometimes zero) to the total number of clusters generated up to that point. Numbers similar in value do not necessarily mean the clusters are close together or similar, but IDs with the same value all correspond to the same cluster. The IDs are merely references to the cluster that the pattern belongs to and the references are generated as new clusters are created.

In the case where learning is turned off, any patterns that don't fit into the existing cluster options are given an ID of 0.

##### RI
`RI` stands for "raw index" which is referring to the anomaly index. These integer values range from 0 to 1000 where zero signifies that those patterns are the most common and happen very frequently. Values close to 1000 are very infrequent and are considered more anomalous the closer the values get to 1000.

When learning is turned off, patterns with cluster IDs of 0 have an anomaly index of 1000.

##### SI
Building on the anomaly index, `SI` stands for "smoothed index". These values are also integer values ranging from 0 to 1000 with similar meanings as the anomaly index in regards to the values' meanings. The smoothed index is one step further than the anomaly indexes. An exponential smoothing function is applied to the anomaly index values to get the smoothed index values. This helps smooth out stand alone anomalies so that single occurances are not flagged.

##### FI
Similar to the anomaly indexes, the `FI`, or frequency index, relates to the number of patterns placed in each cluster. The biggest difference is these values are two-way thresholded. Whereas anomaly index values are in relation to the largest cluster, the frequency index relates everything to the average size cluster. This means that values from 1000 to 0 are abnormally frequent with values closest to 0 as most strangely frequent clusters. Values above 1000 are abnormally infrequent where the further the values get from 1000, the more anomalous they are.
>NOTE: ID, RI, and SI all have definitive upper and lower bounds, but FI only has a lower bound and not an upper bound.


##### DI
The distance index (`DI`), is the last of the results' statistical metrics. The values range from 0 to 1000 but instead of the values relating to the number of patterns in each cluster, they are in relation to the distance from the centroid of the pattern memory space. This is a different centroid than those generated from k-means or other clustering algorithms. This centroid is a single value for the center of a manhattan distance spanned space. Indexes closest to 1000 are furthest from the center and values close to 0 are abnormally close. Patterns in a space that are similar distances appart have values that are close to the average distance between all clusters to the centroid. On average, these values do not vary a lot in value, but that is not to say that they can't.

##### MD
`MD` stands for "metadata" and is the one result that is not the same length as the number of clustered patterns. This returns the preprocessing key that was posted with the data.

##### ""
Setting Results equal to an empty string will omit any results being returned. This is not an option when calling `getNanoResults` since that function is called only when results are desired.

##### All
Finally, setting results to All will return the IDs, RIs, SIs, FIs, and DIs. This lists are returned uncollated but are all the same length (that matches the number of patterns most recently clustered)


For more statistical values, see [Guide: Nano Status](http://github.com)
