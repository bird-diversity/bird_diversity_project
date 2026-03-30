# Data Dictionary for Bird Diversity & Environmental Factors (final5.csv)

This document explains the dataset columns used in the bird diversity analysis. The list below follows the exact column order requested.

## Column Definitions (in dataset order)

* **`index`**: Row identifier for each record in the integrated dataset. Usually used as a technical index, not an environmental variable.
* **`verbatimScientificName`**: Scientific species name recorded in the source observation (as originally reported).
* **`stateProvince`**: Administrative region where the observation was made (state/province field from occurrence metadata).
* **`individualCount`**: Number of individual birds observed in that event.
* **`decimalLatitude`**: Observation latitude in decimal degrees (WGS84).
* **`decimalLongitude`**: Observation longitude in decimal degrees (WGS84).
* **`eventDate`**: Date of the bird observation event.
* **`avg_rad`**: Average nighttime radiance (VIIRS ALAN), used as a proxy for artificial light pollution.
* **`NDVI_raw`**: Raw Normalized Difference Vegetation Index value representing vegetation greenness.
* **`LandCover_Class`**: Land cover category at the observation location (e.g., forest, urban, cropland, water).
* **`elevation_meters`**: Elevation of the location above sea level in meters.
* **`Carbon_Mass`**: Surface black carbon mass concentration (a combustion-related aerosol component).
* **`Dust_Mass`**: Surface dust aerosol mass concentration.
* **`SO2_Mass`**: Surface sulfur dioxide-related mass indicator from the atmospheric product.
* **`Sulfate_Mass`**: Surface sulfate aerosol mass concentration.
* **`Sea_Salt_Mass`**: Surface sea-salt aerosol mass concentration.
* **`Total_Aerosol_Extinction`**: Total aerosol extinction optical thickness (AOD-like indicator of aerosol loading in the atmosphere).
* **`temp_mean`**: Mean air temperature for the matched time period/location.
* **`rainfall`**: Accumulated precipitation for the matched time period/location.
* **`wind_mean`**: Mean wind speed for the matched time period/location.
* **`humid_mean`**: Mean relative humidity for the matched time period/location.
* **`shortwave_radiation`**: Downward shortwave solar radiation at surface level.

## Notes

* Air pollution and aerosol fields are integrated from gridded atmospheric products (MERRA-2 family variables in your pipeline).
* Climate fields (`temp_mean`, `rainfall`, `wind_mean`, `humid_mean`, `shortwave_radiation`) come from weather/climate data integration.
* `individualCount` is count data and often right-skewed; transformations or count models may be useful during analysis.
