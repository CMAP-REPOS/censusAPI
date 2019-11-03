function censusCounty(censusType,vintage,stateCodes,countyCodes,tables){

  var tableType;
  if(tables[0].startsWith('S')){
    tableType = 'subject'
  }
  else if (tables[0].startsWith('B')) {
    tableType = ''
  }

  else if (tables[0].startsWith('D')) {
    tableType = 'profile'
  }

  if(censusType.startsWith("acs")){
    src = "acs"
  }
  else if (censusType.startsWith("dec")) {
    src = "dec"
  }

  census({
      vintage: vintage, // required
      geoHierarchy: {
        // required
        state: stateCodes,
        county: countyCodes
      },
      //cant make call for data and geojson at the same time
      //geoResolution: "5m",
      sourcePath: [src, censusType, tableType], // required
      values: tables, // required
      statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
    },
    function(error, response) {

      document.getElementById('container').innerHTML = json2table(response)
    });
}
