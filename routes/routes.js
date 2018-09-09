module.exports = function(app, db) {
  app.get('/', (req, res) => {
    var path = require('path');
    res.sendFile(path.resolve('index.html'));
  });

  app.get('/result', (req, res) => {
    var path = require('path');
    res.sendFile(path.resolve('result.html'));
  });

  app.get('/validate', (req, res) => {
    var path = require('path');
    res.sendFile(path.resolve('validate.html'));
  });

  app.post('/quote', (req, res) => {
    season = req.body.season;
    data = ajax.get("https://mapprod.environment.nsw.gov.au/arcgis/rest/services/NarCLIM/ClimateRegion/MapServer/1/query?geometry=148.641994676976%2C-32.1639287726956&geometryType=esriGeometryPoint&outFields=M2060_2079_praccfl_percent_ann&returnGeometry=true&f=json");
    console.log(change);
    change = data.features.attributes;
  });
};
