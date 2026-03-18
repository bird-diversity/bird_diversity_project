// REPLACE WITH YOUR ACTUAL ASSET ID
var points = ee.FeatureCollection("projects/your-project/assets/your_location_csv");

// Load SRTM Elevation and rename the band to match your requested column name
var elevationImage = ee.Image("USGS/SRTMGL1_003")
  .select(['elevation'], ['elevation_meters']);

// Extract data for all points
var finalCollection = elevationImage.reduceRegions({
  collection: points,
  reducer: ee.Reducer.first(),
  scale: 250,
  tileScale: 16 // Prevents memory crashes
});

// Export to Drive
Export.table.toDrive({
  collection: finalCollection,
  description: 'SriLanka_Elevation_Extraction',
  folder: 'EarthEngine_Exports',
  fileFormat: 'CSV',
  selectors: ['index', 'elevation_meters'] 
});