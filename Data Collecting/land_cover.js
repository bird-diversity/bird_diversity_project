var points = ee.FeatureCollection("projects/your-project/assets/your_location_csv");

var years = ee.List.sequence(2014, 2025);

var extractedFeatures = years.map(function(y) {
  y = ee.Number(y);
  
  var pointsForYear = points.filter(ee.Filter.eq('year', y));

  var targetDate = ee.Date.fromYMD(y, 12, 31);
  // Load Yearly Land Cover and rename the band
  var lcImage = ee.ImageCollection("MODIS/061/MCD12Q1")
    .filterDate('2001-01-01', targetDate.advance(1, 'day'))
    .sort('system:time_start', false) 
    .first()
    .select(['LC_Type1'], ['LandCover_Class']); 

  return lcImage.reduceRegions({
    collection: pointsForYear,
    reducer: ee.Reducer.first(),
    scale: 500,
    tileScale: 16
  });
});

var finalCollection = ee.FeatureCollection(extractedFeatures).flatten();

Export.table.toDrive({
  collection: finalCollection,
  description: 'SriLanka_LandCover_Extraction',
  folder: 'EarthEngine_Exports',
  fileFormat: 'CSV',
  selectors: ['index', 'LandCover_Class'] 
});