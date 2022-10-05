# OpenStreetMap Address Import - Cache Valley, UT

Setup for importing address points from Utah's dataset to OpenStreetMap. 

## Scope

This should work anywhere in Utah with minimal changes. However, there are surely some issues that will arise in areas outside of Cache Valley, I haven't tested this anywhere else!

Some issues may occur when using this on more "squiggly" roads since I made some assumptions about the grid system when writing the translation functionality. TODO: More testing should reveal what fixes need to be made.

## Procedure

0. Community Prerequisites
    - Follow standard procedure for OSM imports:
      - [OSM Wiki - Imports](https://wiki.openstreetmap.org/wiki/Import)
      - [OSM Wiki - Import Guidelines](https://wiki.openstreetmap.org/wiki/Import/Guidelines)
      - [OSM Wiki - Automated Edits Code of Conduct](https://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct)
1. Download files
    - This Script
    - Address Points dataset from [UGRC](https://gis.utah.gov/data/location/address-data/) (Shapefile or GeoDatabase will do, I think)
2. Software Prerequisites
    - This Script - Provides "translation" functionality
    - [QGIS](https://www.qgis.org/en/site/) - Desktop GIS Software
    - [`ogr2osm`](https://pypi.org/project/ogr2osm/), allows conversion from many formats to OSM features
    - [JOSM](https://josm.openstreetmap.de/) - Desktop OSM Editor
3. Narrow Dataset
    - In QGIS, open data source, select AddressPoints downloaded from UGRC.
    - Add an OSM raster base layer if you want. Not necessary, it just helps me get my bearings.
    - Right-click on AddressPoints layer, hit filter, choose a city and apply the filter. Expression should look something like `"City" = 'CLARKSTON'`. Hit OK.
    - ![Clarkston Map with Address Points](imgs/clarkston_addresses.png)
    - Right-click on now filtered AddressPoints layer, then Export. I think a few different formats should work, but I left it on GeoPackage. Choose a filename, the rest of the options should be OK at default.
4. Translate tags
    - After downloading this script, open it up and pick the right path for the exported city address points file. (TODO: Add ability to just pass it in)
    - Run the script. Output file will be the same filename but with `.osm` extension.
    - Watch for warnings/errors in console. The script should add FIXME tags to anything that might have an issue.
5. Inspect Output
    - Launch JOSM, open the `.osm` file. Hit ctrl+A to select all points, and look at the tag inspector for anything that looks out of place.
    - You can do a search for `FIXME=*` to check out any issues and fix before uploading.
6. Upload to OSM
    - Be sure to follow recommended guidelines such as tagging changesets as autmated, using a bot account, etc.
