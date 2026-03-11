var points = ee.FeatureCollection("projects/your-project/assets/your_location_csv");

var years = ee.List.sequence(2014, 2025);
var months = ee.List.sequence(1, 12);

var yearMonths = years.map(function(y) {
  return months.map(function(m) {
    return ee.Dictionary({'year': y, 'month': m});
  });
}).flatten();

var extractedFeatures = yearMonths.map(function(ym) {
  var y = ee.Number(ee.Dictionary(ym).get('year'));
  var m = ee.Number(ee.Dictionary(ym).get('month'));

  var pointsForMonth = points
    .filter(ee.Filter.eq('year', y))
    .filter(ee.Filter.eq('month', m));

  var startDate = ee.Date.fromYMD(y, m, 1);
  var endDate = startDate.advance(1, 'month');

  // Load VIIRS Nighttime Lights
  var viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
    .filterDate(startDate, endDate)
    .select(['avg_rad', 'cf_cvg'])
    .mean(); // Get the average for that month

  return viirs.reduceRegions({
    collection: pointsForMonth,
    reducer: ee.Reducer.first(), 
    scale: 500, // VIIRS native resolution
    tileScale: 16
  });
});

var finalCollection = ee.FeatureCollection(extractedFeatures).flatten();

Export.table.toDrive({
  collection: finalCollection,
  description: 'SriLanka_NightLights_Extraction',
  folder: 'EarthEngine_Exports',
  fileFormat: 'CSV',
  selectors: ['index', 'avg_rad', 'cf_cvg'] 
});