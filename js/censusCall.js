function censusCounty(censusType, vintage, stateCodes, countyCodes, tables) {

  //Remove existing table to replaced with data selection
  var element = document.getElementsByTagName("Table"),
    index;

  for (index = element.length - 1; index >= 0; index--) {
    element[index].parentNode.removeChild(element[index]);
  }

  function censusPromise(args) {
    return new Promise(function(resolve, reject) {
      census(args, function(err, json) {
        if (!err) {
          resolve(json);
        } else {
          reject(err);
        }
      });
    });
  }

  var tableType;

  function getTable(i) {

    if (i.startsWith('S')) {
      tableType = 'subject'
    } else if ((i.startsWith('B')) || (i.startsWith('C'))) {
      tableType = ''
    } else if (i.startsWith('D')) {
      tableType = 'profile'
    }

    if (censusType.startsWith("acs")) {
      src = "acs"
    } else if (censusType.startsWith("dec")) {
      src = "dec"
    }

    censusParams = {
      vintage: vintage, // required
      geoHierarchy: {
        // required
        state: stateCodes,
        county: countyCodes
      },
      //cant make call for data and geojson at the same time
      //geoResolution: "5m",
      sourcePath: [src, censusType, tableType], // required
      //sourcePath: ["acs", "acs5"],
      values: ["NAME", "group(" + i + ")"], // required
      statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
    }

    return censusPromise(censusParams).then(function(json) {
        return json
      })
      .then(function(json) {
        return json
      })
  }

  for (let i = 0; i < tables.length; i++) {
    getTable(tables[i]).then(function(r) {
      document.getElementById('dvData').innerHTML += json2table(r)
    })
  }
}

function censusMuni(censusType, vintage, stateCodes, muniCodes, tables) {

  //Remove existing table to replaced with data selection
  var element = document.getElementsByTagName("Table"),
    index;

  for (index = element.length - 1; index >= 0; index--) {
    element[index].parentNode.removeChild(element[index]);
  }

  function censusPromise(args) {
    return new Promise(function(resolve, reject) {
      census(args, function(err, json) {
        if (!err) {
          resolve(json);
        } else {
          reject(err);
        }
      });
    });
  }

  var tableType;

  function getTable(i) {

    if (i.startsWith('S')) {
      tableType = 'subject'
    } else if ((i.startsWith('B')) || (i.startsWith('C'))) {
      tableType = ''
    } else if (i.startsWith('D')) {
      tableType = 'profile'
    }

    if (censusType.startsWith("acs")) {
      src = "acs"
    } else if (censusType.startsWith("dec")) {
      src = "dec"
    }

    censusParams = {
      vintage: vintage, // required
      geoHierarchy: {
        // required
        state: stateCodes,
        place: muniCodes,
      },
      //cant make call for data and geojson at the same time
      //geoResolution: "5m",
      sourcePath: [src, censusType, tableType], // required
      //sourcePath: ["acs", "acs5"],
      values: ["NAME", "group(" + i + ")"], // required
      statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
    }

    return censusPromise(censusParams).then(function(json) {
        return json
      })
      .then(function(json) {
        return json
      })
  }

  for (let i = 0; i < tables.length; i++) {
    getTable(tables[i]).then(function(r) {
      document.getElementById('dvData').innerHTML += json2table(r)
    })
  }
}

function censusTract(censusType, vintage, stateCodes, tractCodes, tables) {

  //Remove existing table to replaced with data selection
  var element = document.getElementsByTagName("Table"),
    index;

  for (index = element.length - 1; index >= 0; index--) {
    element[index].parentNode.removeChild(element[index]);
  }

  function censusPromise(args) {
    return new Promise(function(resolve, reject) {
      census(args, function(err, json) {
        if (!err) {
          resolve(json);
        } else {
          reject(err);
        }
      });
    });
  }

  var tableType;

  function getTable(i) {

    if (i.startsWith('S')) {
      tableType = 'subject'
    } else if ((i.startsWith('B')) || (i.startsWith('C'))) {
      tableType = ''
    } else if (i.startsWith('D')) {
      tableType = 'profile'
    }

    if (censusType.startsWith("acs")) {
      src = "acs"
    } else if (censusType.startsWith("dec")) {
      src = "dec"
    }

    censusParams = {
      vintage: vintage, // required
      geoHierarchy: {
        // required
        state: stateCodes,
        county: "031,043,089,093,097,111,197",
        tract: tractCodes,
      },
      //cant make call for data and geojson at the same time
      //geoResolution: "5m",
      sourcePath: [src, censusType, tableType], // required
      //sourcePath: ["acs", "acs5"],
      values: ["NAME", "group(" + i + ")"], // required
      statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
    }

    return censusPromise(censusParams).then(function(json) {
        return json
      })
      .then(function(json) {
        return json
      })
  }

  for (let i = 0; i < tables.length; i++) {
    getTable(tables[i]).then(function(r) {
      document.getElementById('dvData').innerHTML += json2table(r)
    })
  }
}

function censusBlockGroup(censusType, vintage, lat, long, tables, inGeo=null) {

  //Remove existing table to replaced with data selection
  var element = document.getElementsByTagName("Table"),
    index;

  for (index = element.length - 1; index >= 0; index--) {
    element[index].parentNode.removeChild(element[index]);
  }

  function censusPromise(args) {
    return new Promise(function(resolve, reject) {
      census(args, function(err, json) {
        if (!err) {
          resolve(json);
        } else {
          reject(err);
        }
      });
    });
  }

  var tableType;

  function getTable(i) {

    if (i.startsWith('S')) {
      tableType = 'subject'
    } else if ((i.startsWith('B')) || (i.startsWith('C'))) {
      tableType = ''
    } else if (i.startsWith('D')) {
      tableType = 'profile'
    }

    if (censusType.startsWith("acs")) {
      src = "acs"
    } else if (censusType.startsWith("dec")) {
      src = "dec"
    }

    censusParams = {
      vintage: vintage, // required
      geoHierarchy: {
        // required
        //state: 17,
        county: {
          "lat":lat,
          "lng":long
        },
        tract: "*",
        blockGroup: "*",
      },
      //cant make call for data and geojson at the same time
      //geoResolution: "5m",
      sourcePath: [src, censusType, tableType], // required
      //sourcePath: ["acs", "acs5"],
      values: ["NAME", "group(" + i + ")"], // required
      statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
    }
    //console.log(censusParams)
    return censusPromise(censusParams).then(function(json) {
        //console.log(json)
        return json
      })
      .then(function(json) {
        //console.log(inGeo)
        readCsv("data/CMAP2010_ratios_TR.csv", json)
      })
  }

  //convert to promise
  function readCsv(csv, json) {
    var excludeList = ["tract", "county", "state", "GEO_ID", "NAME"]
    var ratioObj = [];
    var ratioObjKeys;
    var allocatedValues = new Object();
    var allocatedObj = []
    var censusObj = []
    var censusObjKeys = Object.keys(json[1])

    d3.csv(csv, function(data) {
      for (var i = 0; i < data.length; i++) {
        //console.log(data[i].BLOCK)
        //if block in block list
        //push to object
        //console.log(data[i].BLOCK)
        if(inGeo.includes(data[i].BLOCK.toString())){
          var obj = new Object()
          obj[data[i].BLOCK] = [data[i].TRACT,data[i].TR_POP_RAT,data[i].TR_HH_RAT,data[i].TR_HU_RAT]
          //console.log(data[i].BLOCK)
          ratioObj.push(obj)
        }
      }

      //perform allocation
      //iterate over ratio object
      //iterate over attributes in census return
      for(var i=0;i < json.length;i++){
        var obj = new Object();
        var GEOID = json[i].state + json[i].county + json[i].tract
        obj[GEOID] = json[i]
        censusObj.push(obj)
      }
    })
    //censusObjKeys = Object.keys(censusObj)
    var count = 0
    for(key in ratioObj){
      for(var i=0;i<censusObjKeys.length;i++){
        var attr = censusObjKeys[i]
        if(!exlcudeList.includes(attr)){
          var obj = new Object();
          obj[censusObjKeys] += censusObj[ratioObj[key].TRACT].attr * censusObj[ratioObj[key].TR_POP_RAT]
        }
        count++;
      }

    }

    console.log(censusObjKeys)
    return ratioObj
  }

  for (let i = 0; i < tables.length; i++) {
    getTable(tables[i]).then(function(r) {
      //document.getElementById('dvData').innerHTML += json2table(r)
      //console.log(r)
      //read in
      //console.log(inGeo)
    })
  }
}
