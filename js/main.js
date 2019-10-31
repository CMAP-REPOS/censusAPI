//countyCensusCall()
//console.log(censusGeoJson)

function json2table(json, classes) {
  var cols = Object.keys(json[0]);

  var headerRow = '';
  var bodyRows = '';

  classes = classes || '';

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  cols.map(function(col) {
    headerRow += '<th>' + capitalizeFirstLetter(col) + '</th>';
  });

  json.map(function(row) {
    bodyRows += '<tr>';

    cols.map(function(colName) {
      bodyRows += '<td>' + row[colName] + '</td>';
    })

    bodyRows += '</tr>';
  });

  return '<table class="' +
         classes +
         '"><thead><tr>' +
         headerRow +
         '</tr></thead><tbody>' +
         bodyRows +
         '</tbody></table>';
}



var app;
require([
  // ArcGIS
  "esri/map",
  "esri/layers/FeatureLayer",
  "esri/dijit/Search",
  "esri/graphic",
  "dojo/query",
  // Calcite Maps
  "calcite-maps/calcitemaps-v0.10",

  // Bootstrap
  "bootstrap/Collapse",
  "bootstrap/Dropdown",
  "bootstrap/Tab",

  //dojo
  "dojo/_base/array",
  "dojo/domReady!",
], function(Map, FeatureLayer, Search, Graphic, query, CalciteMaps, arr) {



  // App
  app = {
    map: null,
    basemap: "dark-gray",
    center: L.latLng(41.8781, -87.9298), // lon, lat
    zoom: 9,
    initialExtent: null,
    searchWidgetNav: null,
    searchWidgetPanel: null
  }
  // // Map
  // app.map = new Map("mapViewDiv", {
  //   basemap: app.basemap,
  //   center: app.center,
  //   zoom: app.zoom
  // });

  app.map = L.map("mapViewDiv").setView(app.center, 9);

  L.esri.basemapLayer('Streets').addTo(app.map);

  app.map.on("load", function() {
    app.initialExtent = app.map.extent;
  })
  //
  // //load census layer
  // var county = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/100", {
  //   mode: FeatureLayer.MODE_ONDEMAND,
  //   outFields: ["*"]
  // })

  var county = L.esri.featureLayer({
    url: "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/100"
  })
  //county.addTo(app.map);
  //app.map.addLayer(county)
  //
  // var muni = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/34")
  //
  // //load census Data
  // arrayCensus.forEach(function(C) {
  //   //console.log(C)
  // });

  var muni = L.esri.featureLayer({
    url: "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/34"
  })
  //muni.addTo(app.map);

  //console.log(county)
  //county.graphic.attributes.forEach(function(G){
  //  console.log(G)
  //})
  //county.graphics.forEach(function(G){
  //  console.log(G.attributes)
  //});

  // Search
  //app.searchDivNav = createSearchWidget("searchNavDiv");
  //app.searchWidgetPanel = createSearchWidget("searchPanelDiv");
  // function createSearchWidget(parentId) {
  //   var search = new Search({
  //     map: app.map,
  //     enableHighlight: false
  //     }, parentId);
  //   search.startup();
  //   return search;
  // }
  // Add Census Geography
  //census

  census({
      vintage: 2017, // required
      geoHierarchy: {
        // required
        state: "17",
        county: "031,197"
      },
      //cant make call for data and geojson at the same time
      //geoResolution: "5m",
      sourcePath: ["acs", "acs5", "subject"], // required
      values: ["S0102_C01_001E", "S0102_C02_001E"], // required
      statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
    },
    function(error, response) {

      console.log(response)

      const censusDataReturn = response.map(function(county) {
        return {
          "county": county['county'],
          "population": county['S0102_C01_001E']
        }
      });

      const table = document.getElementById('container')


      //set the innerHTML to the generated list
      document.getElementById('container').innerHTML = json2table(response)

      function getColor(percent) {
        return percent > 50 ?
          "#800026" :
          percent > 30 ?
          "#BD0026" :
          percent > 20 ?
          "#E31A1C" :
          percent > 10 ?
          "#FC4E2A" :
          percent > 5 ?
          "#FD8D3C" :
          percent > 0 ?
          "#FEB24C" :
          "#FFF";
      }

      function style(feature) {
        var total_pop = feature.properties.S0102_C01_001E;
        var total_pop_over60 = feature.properties.S0102_C02_001E;
        //calculate percent
        if (total_pop && total_pop_over60) {
          // check if valid (no 0s or undefined)
          var percent = (total_pop_over60 / total_pop) * 100;
          return {
            fillColor: getColor(percent),
            fillOpacity: 0.7,
            weight: 0.5,
            color: "rgba(255, 255, 255, 0.8)"
          };
        } else {
          return {
            weight: 2,
            fillOpacity: 0,
            weight: 0.5,
            color: "rgba(255, 255, 255, 0.8)"
          };
        }
      }

      L.geoJson(response, {
        style: style
      }).addTo(app.map);
    });


  query("#selectGeography").on("change", function(e) {
    if (e.target.options[e.target.selectedIndex].value == 'county') {
      app.map.removeLayer(muni);
      //app.map.removeLayer(tract)
      //app.map.addLayer(county)

    } else if (e.target.options[e.target.selectedIndex].value == 'muni') {
      app.map.removeLayer(county)
      app.map.addLayer(muni)
    }
  })
  // Basemaps
  query("#selectBasemapPanel").on("change", function(e) {
    //app.map.setBasemap(e.target.options[e.target.selectedIndex].value);
    //CensusStats.addTo(app.map)
  });
  // Home
  query(".calcite-navbar .navbar-brand").on("click", function(e) {
    app.map.setExtent(app.initialExtent);
  })
});
