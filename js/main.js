
//load modules
require(["application/bootstrapmap","esri/map", "dojo/domReady!"], function(BootstrapMap,Map){

  //load map
  var map= BootstrapMap.create("map",{
    center:[-87,41],
    zoom: 8,
    basemap: "topo"
  })

  //add census layers
})
