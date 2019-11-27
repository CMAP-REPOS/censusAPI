function selectBlockRatio(data, geo, geoRatio, inGeo) {
  var obj = new Object()
  for (var i = 0; i < data.length; i++) {

    if (inGeo.includes(data[i].BLOCK.toString())) {

      obj[data[i]["BLOCK"]] = {
        GEO: data[i][geo],
        POP_RAT: data[i][geoRatio + '_POP_RAT'],
        HH_RAT: data[i][geoRatio + '_HH_RAT'],
        HU_RAT: data[i][geoRatio + '_HU_RAT']
      }
    }
  }
  return obj
}
//push census values to censusObj with GEOID as key (tract)
function createCensusObj(json, geo) {
  var obj = new Object()

  for (var i = 0; i < json.length; i++) {
    var GEOID;
    if(geo == 'blockGroup') {
      GEOID = json[i]["GEO_ID"].split("US")[1]
    } if(geo == 'tract') {
      GEOID = json[i]["state"].concat(json[i]["county"], json[i]["tract"])
    } if(geo == 'county') {
      GEOID = json[i]["state"].concat(json[i]["county"])
    }
    if(geo == 'muni') {
      GEOID = json[i]["GEO_ID"].split("US")[1]
    }
    //var GEOID = json[i]["GEO_ID"].split("US")[1]
    obj[GEOID] = json[i]
  }
  return obj
}

function censusVariables(tableName, timeOut) {
  //var availableTags =  [];

  var variableObj = new Object();
  //var timeOut = 0
  //Selected Census Data Type Value
  var v = document.getElementById("vintage");
  var selV = v.options[v.selectedIndex].value;

  //Selected Census Data Type Value
  var cDT = document.getElementById("selectCensusDataType");
  var selCDT = cDT.options[cDT.selectedIndex].value;

  var request = new XMLHttpRequest()

  //open new connection
  request.open("GET", "https://api.census.gov/data/" + selV + "/acs/" + selCDT + "/groups/" + tableName, true)

  request.onload = function() {
    // Begin accessing JSON data here
    var groupVariables = JSON.parse(this.response)
    //console.log(groups)
    if (request.status >= 200 && request.status < 400) {
      for (groupVar in groupVariables["variables"]) {
        if (groupVar.endsWith("E")) {
          variableObj[groupVar] = groupVariables["variables"][groupVar]['label']
          //timeOut += 3000
        }
      }
      //Object.keys(groupVariables).forEach(function(groupVar) {
      //  console.log(groupVariables[groupVar] + "-" + groupVar['label'])
      //  variableObj[groupVariables[groupVar]] = groupVar['label']
      //})
    } else {
      const errorMessage = document.createElement("marquee")
      errorMessage.textContent = `Gah, it"s not working!`
      app.appendChild(errorMessage)
    }
    //console.log(availableTags)
  }
  request.send()
  //return variableObj
  //console.log(timeOut)
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(variableObj);
    }, timeOut);
  });
};

function transposeUnallocated(json, tableName, tableLabel, censusGeo) {
  var excludeList = ["block-group", "tract", "county", "state", "GEO_ID", "NAME"]
  var allocatedValues = new Object();
  var tableValues = new Object();
  var tableColumns = [];
  var allocatedObj = []
  var timeOut = 900;
  var censusObj;

  console.log(json[0])
  censusObj = createCensusObj(json, censusGeo)
  console.log(censusObj)

  Object.keys(json[0]).forEach(function(censusField) {
    timeOut += 50
    if ((!excludeList.includes(censusField)) && censusField.endsWith("E")) {
      tableColumns.push(censusField)
    }
  })

  allocatedValues[tableLabel] = tableColumns

  Object.keys(censusObj).forEach(function(geoID) {

    var cValues = []
    Object.keys(json[0]).forEach(function(censusField) {
      if ((!excludeList.includes(censusField)) && censusField.endsWith("E")) {
        cValues.push(censusObj[geoID][censusField])
      }
      //cValues.push(censusObj[geoID][censusField])
    })
    allocatedValues[geoID] = cValues
  })

  allocatedObj.push(allocatedValues)
  console.log(allocatedObj)
  console.log(timeOut)

  censusVariables(tableName, timeOut).then(function(varLabels) {
    document.getElementById('dvData').innerHTML += json2table(allocatedObj, varLabels, tableLabel)
  })

  return new Promise(resolve => {
    setTimeout(() => {
      resolve(allocatedObj);
    }, 300);
  });
}

function allocCensusData(json, csv, geo, geoRatio, inGeo, tableLabel, tableName, censusGeo) {
  //console.log(tableLabel)
  var excludeList = ["block-group", "tract", "county", "state", "GEO_ID", "NAME"]
  var allocatedValues = new Object();
  var tableValues = new Object();
  var allocatedObj = []
  var ratioObj, censusObj;
  var censusObjKeys = Object.keys(json[1]);
  var timeOut = 900;

  d3.csv(csv, function(data) {

    //varLabels = censusVariables(tableName)
    ratioObj = selectBlockRatio(data, geo, geoRatio, inGeo)
    //console.log(ratioObj)
    censusObj = createCensusObj(json, censusGeo)
    //console.log(censusObj)
    tableColumns = [];
    //tableData = [];
    Object.keys(json[1]).forEach(function(censusField) {
      var attr = censusField
      timeOut += 600
      if ((!excludeList.includes(attr)) && attr.endsWith("E")) {
        //allocatedValues["NAME"] = 'Custom Area';
        //allocatedValues[censusField] = 0;
        tableValues[censusField] = 0;
        tableColumns.push(attr)
      }
    })

    allocatedValues[tableLabel] = tableColumns

    Object.keys(ratioObj).forEach(function(block) {
      Object.keys(json[1]).forEach(function(censusField) {
        //attr = list includes list of geographic attributes to exclude from allocation
        if ((!excludeList.includes(censusField)) && censusField.endsWith("E") && !isNaN(censusObj[ratioObj[block]["GEO"]][censusField])) {
          //add correct ratio application based on table name
          tableValues[censusField] += Math.round(parseFloat(censusObj[ratioObj[block]["GEO"]][censusField]) * parseFloat(ratioObj[block]["POP_RAT"]))
          //allocSum += Math.round(parseFloat(censusObj[ratioObj[block]["BLKGRP"]][censusField]) * parseFloat(ratioObj[block]["BG_POP_RAT"]))
        }
      });
    });
    //console.log(tableValues)
    //tableData.push(Object.values(tableValues))
    allocatedValues['Count'] = Object.values(tableValues)
    //console.log(allocatedValues)
    allocatedObj.push(allocatedValues)

    //timeOut = timeOut * Object.values(tableValues).length
    //while(timeOut < 5000){
    //  timeOut+=1000
    //}
    console.log(timeOut)
    censusVariables(tableName, timeOut).then(function(varLabels) {
      document.getElementById('dvData').innerHTML += json2table(allocatedObj, varLabels, tableLabel)
    })
    //document.getElementById('dvData').innerHTML += json2table(allocatedObj, varLabels, tableLabel)
  })

  return new Promise(resolve => {
    setTimeout(() => {
      resolve(allocatedObj);
    }, 300);
  });
}

function censusCounty(censusType, vintage, stateCodes, countyCodes, tables, censusGeo='county') {

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
    let tName = tables[i].split('-')[0]
    let tLable = tables[i].split('-')[1]
    getTable(tName).then(function(r) {
      transposeUnallocated(r, tName, tLable, censusGeo)
      })
      //document.getElementById('dvData').innerHTML += json2table(r)
  }
}

function censusMuni(censusType, vintage, stateCodes, muniCodes, tables, censusGeo='muni') {

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
    let tName = tables[i].split('-')[0]
    let tLable = tables[i].split('-')[1]
    getTable(tName).then(function(r) {
      transposeUnallocated(r, tName, tLable, censusGeo)
      })
      //document.getElementById('dvData').innerHTML += json2table(r)
  }
}

function censusTract(censusType, vintage, lat, long, tables, tractcodes = "*", allocate = false, inGeo = null, censusGeo='tract') {

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
        //state: stateCodes,
        county: {
          "lat": lat,
          "lng": long
        },
        tract: tractcodes,
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

  function returnCensusTables() {
    //var arr = []
    for (let i = 0; i < tables.length; i++) {
      //console.log(tables[i])
      let tName = tables[i].split('-')[0]
      let tLable = tables[i].split('-')[1]
      getTable(tName).then(function(a) {
        if (allocate == true) {
          allocCensusData(a, "data/CMAP2010_ratios_TR.csv", "TRACT", "TR", inGeo, tLable, tName, censusGeo)
        } else {
          transposeUnallocated(a, tName, tLable, censusGeo)
        }
      })
    }
  }

  returnCensusTables()
}

function censusBlockGroup(censusType, vintage, lat, long, tables, bgcodes = "*", allocate = false, inGeo = null, censusGeo='blockGroup') {

  // //Remove existing table to replaced with data selection
  // var element = document.getElementsByTagName("Table"),
  //   index;
  //
  // for (index = element.length - 1; index >= 0; index--) {
  //   element[index].parentNode.removeChild(element[index]);
  // }

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
          "lat": lat,
          "lng": long
        },
        //"tract": "*",
        "block group": bgcodes,
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
      return json
    })
  }

  //convert to promise



  function returnCensusTables() {
    //var arr = []
    for (let i = 0; i < tables.length; i++) {
      getTable(splitTableName(tables[i])[0]).then(function(a) {
        if (allocate == true) {
          allocCensusData(a, "data/CMAP2010_ratios_BG.csv", "BLKGRP", "BG", inGeo, tLable, tName, censusGeo)
        } else {
          transposeUnallocated(a, tName, tLable, censusGeo)
        }
      })
    }
  }

  returnCensusTables()
}
