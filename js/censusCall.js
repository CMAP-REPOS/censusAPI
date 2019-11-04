function censusCounty(censusType, vintage, stateCodes, countyCodes, tables) {

  var tableType;

  var len;


  function collectTables(){
    var responses = [];
    for (var i = 0; i < tables.length; i++) {
      var def = Q.defer();
      var table = tables[i]
      if (tables[0].startsWith('S')) {
        tableType = 'subject'
      } else if (tables[0].startsWith('B')) {
        tableType = ''
      } else if (tables[0].startsWith('D')) {
        tableType = 'profile'
      }

      if (censusType.startsWith("acs")) {
        src = "acs"
      } else if (censusType.startsWith("dec")) {
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
          values: ["NAME", "group(" + table + ")"], // required
          statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
        },
        function(error, response) {
            //var responses = []
            if(i ==0){
              responses.push(response[0].promise);
            }
            if(i > 0){
              $.extend(responses, response[0].promise)
            }
          // function sendResponsesToTable() {
          //   var responses = pushReponses(response)
          // }
          //
          // function sendToTable(value) {
          //   return document.getElementById('container').innerHTML = json2table(value);
          // }
          //document.getElementById('container').innerHTML = json2table(response)
        });

        //console.log(responses)
    }
  }


  setTimeout(function(){
    console.log(responses)}
    ,2000)
    setTimeout(function(){
      document.getElementById('container').innerHTML = json2table(responses)}
      ,5000)
}
