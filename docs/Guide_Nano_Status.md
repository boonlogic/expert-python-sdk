# Guide: Nano Status

See [How-to: Generate Cluster Status](http://github.com) for instructions on generating nano status statistics.

### Options
The nano status stats can only be called from `getNanoStatus()`. There are 12 return types:
- PCA
- clusterSizes
- anomalyIndexes
- frequencyIndexes
- distanceIndexes
- patternMemory
- clusterGrowth
- numClusters
- totalInferences
- averageInferenceTime
- All
- ""

and any subset of these (where `All` takes precedent and "" is weighted the least).

Each of these options are an overview of the clusters created. The first six options specified above are lists of length equal to the number of clusters created including the zero cluster (with the exception of patternMemory). Each index of the list corresponds to the cluster ID (zero-based except for patternMemory which is one-based indexing).

##### PCA
