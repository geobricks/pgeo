Download Example
================

This example shows the minimum code required to download a list of layers from MODIS. The one that follows is a list of the required imports.

```python
from pgeomodis.core.modis_core import list_layers_subset
from pgeo.download.download_bean import Bean
from pgeo.download.download_gateway import download
```

The first import is from the [PGeo-MODIS plug-in](https://github.com/geobricks/pgeomodis) and it will be used to fetch the list of layers to be downloaded. The following code returns a list of objects corresponding to the MODIS's MOD13Q2 layers acquired on January 1st 2014 and covering the tiles having the 'h' coordinate from 18 to 19 and the 'v' coordinate from 4 to 5.  

```python
layers = list_layers_subset('MOD13Q2', '2014', '001', '18', '19', '04', '05')
```
