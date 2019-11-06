//countyCensusCall()
//console.log(censusGeoJson)

var app;
require([
  // ArcGIS
  "esri/config",
  "esri/InfoTemplate",
  "esri/map",
  "esri/tasks/query",
  "esri/geometry/Extent",
  "esri/request",
  "esri/geometry/scaleUtils",
  "esri/layers/FeatureLayer",
  "esri/dijit/Search",
  "esri/graphic",
  "dojo/query",
  "esri/renderers/SimpleRenderer",
  "esri/symbols/PictureMarkerSymbol",
  "esri/symbols/SimpleFillSymbol",
  "esri/symbols/SimpleLineSymbol",
  "dojo/dom",
  "dojo/json",
  "dojo/on",
  "dojo/parser",
  "dojo/sniff",
  "dojo/_base/array",
  "esri/Color",
  "dojo/_base/lang",
  "dijit/layout/BorderContainer",
  "dijit/layout/ContentPane",
  // Calcite Maps
  "calcite-maps/calcitemaps-v0.10",

  // Bootstrap
  "bootstrap/Collapse",
  "bootstrap/Dropdown",
  "bootstrap/Tab",

  //dojo
  "dojo/_base/array",
  "dojo/domReady!",
], function(
  esriConfig,
  InfoTemplate,
  Map,
  Query,
  Extent,
  request,
  scaleUtils,
  FeatureLayer,
  Search,
  Graphic,
  query,
  SimpleRenderer,
  PictureMarkerSymbol,
  SimpleFillSymbol,
  SimpleLineSymbol,
  dom,
  JSON,
  on,
  parser,
  sniff,
  arrayUtils,
  Color,
  lang,
  CalciteMaps,
  arr
) {

  parser.parse();

  var portalUrl = "https://www.arcgis.com";

  esriConfig.defaults.io.proxyUrl = "/proxy/";

  on(dom.byId("uploadForm"), "change", function(event) {
    var fileName = event.target.value.toLowerCase();

    if (sniff("ie")) { //filename is full path in IE so extract the file name
      var arr = fileName.split("\\");
      fileName = arr[arr.length - 1];
    }
    if (fileName.indexOf(".zip") !== -1) { //is file a zip - if not notify user
      generateFeatureCollection(fileName);
    } else {
      dom.byId('upload-status').innerHTML = '<p style="color:red">Add shapefile as .zip file</p>';
    }
  });

  // App
  app = {
    map: null,
    basemap: "dark-gray",
    //center: L.latLng(41.8781, -87.9298), // lon, lat
    center: [-87.9298, 41.8781],
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

  //app.map = L.map("mapViewDiv").setView(app.center, 9);

  //L.esri.basemapLayer('Streets').addTo(app.map);

  app.map = new Map("mapViewDiv", {
    basemap: app.basemap,
    center: app.center,
    zoom: app.zoom,
    slider: false
  })

  app.map.on("load", function() {
    app.initialExtent = app.map.extent;
  })

  var cBlocks;
  var featureLayer;

  function generateFeatureCollection(fileName) {
    var name = fileName.split(".");
    //Chrome and IE add c:\fakepath to the value - we need to remove it
    //See this link for more info: http://davidwalsh.name/fakepath
    name = name[0].replace("c:\\fakepath\\", "");

    dom.byId('upload-status').innerHTML = '<b>Loading… </b>' + name;

    //Define the input params for generate see the rest doc for details
    //http://www.arcgis.com/apidocs/rest/index.html?generate.html
    var params = {
      'name': name,
      'targetSR': app.map.spatialReference,
      'maxRecordCount': 1000,
      'enforceInputFileSizeLimit': true,
      'enforceOutputJsonSizeLimit': true
    };

    //generalize features for display Here we generalize at 1:40,000 which is approx 10 meters
    //This should work well when using web mercator.
    var extent = scaleUtils.getExtentForScale(app.map, 40000);
    var resolution = extent.getWidth() / app.map.width;
    params.generalize = true;
    params.maxAllowableOffset = resolution;
    params.reducePrecision = true;
    params.numberOfDigitsAfterDecimal = 0;

    var myContent = {
      'filetype': 'shapefile',
      'publishParameters': JSON.stringify(params),
      'f': 'json',
      'callback.html': 'textarea'
    };

    //use the rest generate operation to generate a feature collection from the zipped shapefile
    request({
      url: portalUrl + '/sharing/rest/content/features/generate',
      content: myContent,
      form: dom.byId('uploadForm'),
      handleAs: 'json',
      load: lang.hitch(this, function(response) {
        if (response.error) {
          errorHandler(response.error);
          return;
        }
        var layerName = response.featureCollection.layers[0].layerDefinition.name;
        dom.byId('upload-status').innerHTML = '<b>Loaded: </b>' + layerName;
        addShapefileToMap(response.featureCollection);
      }),
      error: lang.hitch(this, errorHandler)
    });
  }

  function errorHandler(error) {
    dom.byId('upload-status').innerHTML =
      "<p style='color:red'>" + error.message + "</p>";
  }

  function addShapefileToMap(featureCollection) {
    //add the shapefile to the map and zoom to the feature collection extent
    //If you want to persist the feature collection when you reload browser you could store the collection in
    //local storage by serializing the layer using featureLayer.toJson()  see the 'Feature Collection in Local Storage' sample
    //for an example of how to work with local storage.
    var fullExtent;
    var layers = [];

    arrayUtils.forEach(featureCollection.layers, function(layer) {
      var infoTemplate = new InfoTemplate("Details", "${*}");
      featureLayer = new FeatureLayer(layer, {
        infoTemplate: infoTemplate
      });
      //associate the feature with the popup on click to enable highlight and zoom to
      featureLayer.on('click', function(event) {
        app.map.infoWindow.setFeatures([event.graphic]);
      });
      //change default symbol if desired. Comment this out and the layer will draw with the default symbology
      changeRenderer(featureLayer);
      fullExtent = fullExtent ?
        fullExtent.union(featureLayer.fullExtent) : featureLayer.fullExtent;
      layers.push(featureLayer);
    });
    app.map.addLayers(layers);
    app.map.setExtent(fullExtent.expand(1.25), true);

    cBlocks = new FeatureLayer('https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/18', {
      mode: FeatureLayer.MODE_ONDEMAND,
      outFields: ["*"]
    })

    var county = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/100", {
      mode: FeatureLayer.MODE_ONDEMAND,
      outFields: ["*"]
    })
    app.map.addLayer(cBlocks);

    dom.byId('upload-status').innerHTML = "";
  }

  function changeRenderer(layer) {
    //change the default symbol for the feature collection for polygons and points
    var symbol = null;
    switch (layer.geometryType) {
      case 'esriGeometryPoint':
        symbol = new PictureMarkerSymbol({
          'angle': 0,
          'xoffset': 0,
          'yoffset': 0,
          'type': 'esriPMS',
          'url': 'https://static.arcgis.com/images/Symbols/Shapes/BluePin1LargeB.png',
          'contentType': 'image/png',
          'width': 20,
          'height': 20
        });
        break;
      case 'esriGeometryPolygon':
        symbol = new SimpleFillSymbol(SimpleFillSymbol.STYLE_SOLID,
          new SimpleLineSymbol(SimpleLineSymbol.STYLE_SOLID,
            new Color([112, 112, 112]), 1), new Color([136, 136, 136, 0.25]));
        break;
    }
    if (symbol) {
      layer.setRenderer(new SimpleRenderer(symbol));
    }
  }


  // When the map is clicked create a buffer around the click point of the specified distance
  app.map.on("click", function(evt) {

    var query = new Query();
    query.geometry = featureLayer;
    console.log(query)
    // Use a fast bounding box query. It will only go to the server if bounding box is outside of the visible map.
    console.log("features select")
    cBlocks.queryFeatures(query, selectInBuffer);
  });

  function selectInBuffer(response) {
    var feature;
    var features = response.features;
    console.log(features)
    var inBuffer = [];
    // Filter out features that are not actually in buffer, since we got all points in the buffer's bounding box
    for (var i = 0; i < features.length; i++) {
      feature = features[i];
      if (featureLayer.contains(feature.geometry)) {
        console.log(feature.geometry)
        inBuffer.push(feature.attributes[cBlocks.objectIdField]);
      }
      console.log(inBuffer)
    }
    var query = new Query();
    query.objectIds = inBuffer;
    // Use an objectIds selection query (should not need to go to the server)
    featureLayer.selectFeatures(query, FeatureLayer.SELECTION_NEW, function(results) {
      var blockCount = sumBlocks(results);
      var r = "";
      r = "<b>The total count of Census Blocks is <i>" + blockCount + "</i>.</b>";
      dom.byId("messages").innerHTML = r;
    });
  }

  function sumBlocks(features) {
          var count = 0;
          for (var x = 0; x < features.length; x++) {
            count+=x;
          }
          return count;
        }

  //
  // //load census layer
  // var county = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/100", {
  //   mode: FeatureLayer.MODE_ONDEMAND,
  //   outFields: ["*"]
  // })

  //var county = L.esri.featureLayer({
  //url: "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/100"
  //})
  //county.addTo(app.map);
  //app.map.addLayer(county)
  //
  // var muni = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/34")
  //
  // //load census Data
  // arrayCensus.forEach(function(C) {
  //   //console.log(C)
  // });

  //var muni = L.esri.featureLayer({
  //  url: "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/34"
  //})
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


  // var tables = ["S0102_C01_001E", "S0102_C02_001E"]
  // //censusCounty("acs5", 2017, "17", tables)
  //
  // census({
  //     vintage: 2017, // required
  //     geoHierarchy: {
  //       // required
  //       state: "17",
  //       county: "*"
  //     },
  //     //cant make call for data and geojson at the same time
  //     geoResolution: "5m",
  //     sourcePath: ["acs", "acs5", "subject"], // required
  //     values: ["S0102_C01_001E", "S0102_C02_001E"], // required
  //     statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
  //   },
  //   function(error, response) {
  //     //set the innerHTML to the generated list
  //
  //     function getColor(percent) {
  //       return percent > 50 ?
  //         "#800026" :
  //         percent > 30 ?
  //         "#BD0026" :
  //         percent > 20 ?
  //         "#E31A1C" :
  //         percent > 10 ?
  //         "#FC4E2A" :
  //         percent > 5 ?
  //         "#FD8D3C" :
  //         percent > 0 ?
  //         "#FEB24C" :
  //         "#FFF";
  //     }
  //
  //     function style(feature) {
  //       var total_pop = feature.properties.S0102_C01_001E;
  //       var total_pop_over60 = feature.properties.S0102_C02_001E;
  //       //calculate percent
  //       if (total_pop && total_pop_over60) {
  //         // check if valid (no 0s or undefined)
  //         var percent = (total_pop_over60 / total_pop) * 100;
  //         return {
  //           fillColor: getColor(percent),
  //           fillOpacity: 0.7,
  //           weight: 0.5,
  //           color: "rgba(255, 255, 255, 0.8)"
  //         };
  //       } else {
  //         return {
  //           weight: 2,
  //           fillOpacity: 0,
  //           weight: 0.5,
  //           color: "rgba(255, 255, 255, 0.8)"
  //         };
  //       }
  //     }
  //
  //     L.geoJson(response, {
  //       style: style
  //     }).addTo(app.map);
  //   });


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
