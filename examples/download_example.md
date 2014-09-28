Download Example
================

This example shows the minimum code required to download a list of layers from MODIS. The one that follows is a list of the required imports.

```python
from pgeomodis.core.modis_core import list_layers_subset
from pgeo.download.download_bean import Bean
from pgeo.download.download_gateway import download
```
The first import is from the PGeo-MODIS plug-in [PGeo-MODIS plug-in](https://github.com/geobricks/pgeomodis)
