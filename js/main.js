//Pass all require statements to access esri, dojo,and calcite-maps,and bootstrap classes
//Casing matters
//For more info on classes and constructor options see ArcGIS API 3.30 Reference: https://developers.arcgis.com/javascript/3/jsapi/
var app;
require([
  // ArcGIS
  "esri/config",
  "esri/InfoTemplate",
  "esri/map",
  "esri/tasks/query",
  "esri/tasks/QueryTask",
  "esri/geometry/Extent",
  "esri/geometry/Polygon",
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
  QueryTask,
  Extent,
  Polygon,
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

  // App Config: Map view configuration
  // map is assigned in the next instance
  // set map properties using the app configuration
  // reference map properties here: https://developers.arcgis.com/javascript/3/jsapi/map-amd.html
  app = {
    map: null,
    basemap: "gray-vector", //https://developers.arcgis.com/javascript/3/jsapi/esri.basemaps-amd.html
    center: [-87.9298, 41.8781],
    zoom: 9,
    initialExtent: null,
    searchWidgetNav: null,
    searchWidgetPanel: null
  }

  // instantiate new map object
  // set properties using configuration
  app.map = new Map("mapViewDiv", {
    basemap: app.basemap,
    center: app.center,
    zoom: app.zoom,
    slider: false
  })
  // set map extent after map loads
  app.map.on("load", function() {
    app.initialExtent = app.map.extent;
  })

  //load census block feature layer for custom study area allocation
  var cBlocks = new FeatureLayer('https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/18', {
    mode: FeatureLayer.MODE_ONDEMAND,
    outFields: ["*"]
  })
  app.map.addLayer(cBlocks)

  var featureLayer;

  //ADD CUSTOM GEO and PERFORM ALLOCATION
  //location of proxy url used to generate custom geo on the fly
  var portalUrl = "https://www.arcgis.com";
  esriConfig.defaults.io.proxyUrl = "/proxy/";

  //Trigger to upload custom geography
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
        infoTemplate: infoTemplate,
        objectIdField: 'OBJECTID'
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

    var county = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/12", {
      mode: FeatureLayer.MODE_ONDEMAND,
      outFields: ["*"]
    })
    //;

    dom.byId('upload-status').innerHTML = "";

    // When the map is clicked create a buffer around the click point of the specified distance
    //submitButton = dom.byId("submitButton"),
    query("#submitButton").on("click", function(evt) {

      var query = new Query();
      query.geometry = app.map.extent;
      //query.spatialRelationship = Query.SPATIAL_REL_ENVELOPEINTERSECTS;
      featureLayer.queryFeatures(query, getSelectGeo)
    })

    function getSelectGeo(response) {

      var polygon = response.features[0].geometry;
      // populate the Geometry cache by calling getExtent()
      var polygonExtent = polygon.getExtent();
      //console.log(response);
      var query = new Query();
      query.spatialRelationship = 'esriSpatialRelContains'
      query.geometry = polygonExtent;
      //console.log(query)
      cBlocks.queryFeatures(query, collectIDs)
      //performAllocation()
      //console.log(inGeo)


      function collectIDs(featureSet) {
        var inGeo = []
        var poptotal=0
        var features = featureSet.features;
        //console.log(features[0])
        for (var i = 0; i < features.length; i++) {
          feature = features[i];
          //read centroid of block group features and selects
          //block group if the centroid falls within the custom geography
          if (polygon.contains(feature.geometry.getCentroid())) {
            inGeo.push(feature.attributes.GEOID);
            poptotal += feature.attributes.POP100
          }
        }
        r = "<b>The total pop is <i>" + poptotal + "</i>";
        dom.byId("messages").innerHTML = r;

        var lat = parseFloat(polygon.getCentroid().getLatitude().toFixed(2))
        var long = parseFloat(polygon.getCentroid().getLongitude().toFixed(2))
        console.log(lat,long)
        performAllocation(inGeo,lat,long)
      }

      function performAllocation(inGeo,lat,long){
        //census parameters from Document Object Model dom
        //console.log(inGeo)
        //get census values json
        var cDT = document.getElementById("selectCensusDataType");
        var selCDT = cDT.options[cDT.selectedIndex].value;

        //Selected Census Data Type Value
        var v = document.getElementById("vintage");
        var selV = v.options[v.selectedIndex].value;

        //allocation happens in censusCall.js
        //censusBlockGroup(selCDT, selV, lat,long, selectedTables, true, inGeo)
  
        censusTract(selCDT, selV, lat, long, selectedTables, tractcodes = "*", true, inGeo)
        //censusTract(censusType, vintage, lat, long, tables, tractcodes = "*", allocate = false, inGeo = null)
        //loop through block list
      }
    }
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


  // PANEL SELECTION OPTIONS
  // currently inactive
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
