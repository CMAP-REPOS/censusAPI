//census
var arrayCensus = [];
function getCensusData() {
  //var arrayCensus = [];
  $.getJSON("https://api.census.gov/data/2017/acs/acs5?get=NAME,B01001_001E&for=county:031&in=state:17&key=7d28d36d1b0595e1faf3c7c56ed6df8f4def1452", function(data) {
    var keys = data[0]; //extract the first row of the returned 2d array that are the column headers
    var values = data; //copy the array
    values.splice(0, 1); //delete the first row of headers in the copied array
    //arrayCensus = []; //create a new array to store the formatted object outputs
    //nested loops combining the column header with appropriate values as {key:value} pair objects
    for (var i = 0; i < values.length; i++) {
      var obj = {};
      for (var j = 0; j < values[i].length; j++) {

        obj[values[i][3]] = values[i][1];

      }
      //console.log(arrayCensus);
      arrayCensus.push(obj);
    }
    //console.log(arrayCensus)
		//return arrayCensus;
  });
}

getCensusData()
//console.log(arrayCensus)


var app;
require([
  "esri/Map",
  "esri/views/MapView",
  "esri/views/SceneView",
  "esri/widgets/Search",
  "esri/widgets/BasemapGallery",
  "esri/core/watchUtils",
  'esri/layers/FeatureLayer',
  'esri/widgets/Popup',
  'esri/PopupTemplate',
  'esri/widgets/Editor',
  'esri/popup/content/AttachmentsContent',
  'esri/popup/content/TextContent',
  "esri/symbols/SimpleMarkerSymbol",
  "esri/symbols/TextSymbol",
  // Calcite Maps
  "calcite-maps/calcitemaps-v0.8",

  // Calcite Maps ArcGIS Support
  "calcite-maps/calcitemaps-arcgis-support-v0.8",

  // Bootstrap
  "bootstrap/Collapse",
  "bootstrap/Dropdown",
  "bootstrap/Tab",
  // Can use @dojo shim for Array.from for IE11
  "@dojo/framework/shim/array"
], function(
  Map,
  MapView,
  SceneView,
  Search,
  Basemaps,
  watchUtils,
  FeatureLayer,
  Popup,
  PopupTemplate,
  Editor,
  AttachmentsContent,
  TextContent,
  SimpleMarkerSymbol,
  TextSymbol,
  CalciteMaps,
  CalciteMapsArcGIS
) {
  /******************************************************************
   *
   * App settings
   *
   ******************************************************************/

  app = {
    scale: 600000,
    basemap: "osm",
    zoom: 9,
    center: [-88.1285691261062, 41.793264502709576],
    viewPadding: {
      top: 50,
      bottom: 0
    },
    uiComponents: ["zoom", "compass", "attribution"],
    mapView: null,
    sceneView: null,
    containerMap: "mapViewDiv",
    containerScene: "sceneViewDiv",
    activeView: null,
    searchWidget: null
  };

  /******************************************************************
   *
   * Create the map and scene view and ui components
   *
   ******************************************************************/

  // Map
  const map = new Map({
    basemap: app.basemap
  });

  app.mapView = new MapView({
    container: app.containerMap,
    map: map,
    center: app.center,
    scale: app.scale,
    padding: app.viewPadding,
    ui: {
      components: app.uiComponents
    }
  });

  //load census layer
  var county = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/100", {
    mode: FeatureLayer.MODE_ONDEMAND,
    outFields:["*"]
  })
  map.add(county)

  var muni = new FeatureLayer("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_Census2010/MapServer/34")

  //load census Data
  arrayCensus.forEach(function(C){
    //console.log(C)
  });

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
  const geoLayer = document.getElementById("selectGeography");
  geoLayer.addEventListener("change",function(e){
    if(e.target.options[e.target.selectedIndex].value == 'county'){
      map.removeLayer(muni)
      //app.map.removeLayer(tract)
      map.add(county)
    }
    else if(e.target.options[e.target.selectedIndex].value == 'muni'){
      map.removeLayer(county)
      map.add(muni)
    }
  })
  // // Basemaps
  // query("#selectBasemapPanel").on("change", function(e){
  //   map.setBasemap(e.target.options[e.target.selectedIndex].value);
  // });
  // // Home
  // query(".calcite-navbar .navbar-brand").on("click", function(e) {
  //   map.setExtent(app.initialExtent);
  // })
});
