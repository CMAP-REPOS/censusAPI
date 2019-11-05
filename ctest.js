

var vintage = 2017;
var stateCodes = "17";
var countyCodes = "031"
var src = "acs";
var censusType="acs5";
var tableType = "detail";
var table = "b01002"

function getData(table){
  fetch(census({
    vintage: vintage, // required
    geoHierarchy: {
      // required
      state: stateCodes,
      county: countyCodes
    },
    //cant make call for data and geojson at the same time
    //geoResolution: "5m",
    sourcePath: [src, censusType, tableType], // required
    values: ["NAME", "group(" + table + ")"], // required
    statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
  }))
  .then(function (response){
    return response.json();
  });
  .then(function(json){
    console.log(json);
  })
}

getData(table)
