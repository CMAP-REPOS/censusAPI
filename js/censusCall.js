//Alloction Ratio Universe Selection based on table subject ids: https://www.census.gov/programs-surveys/acs/guidance/which-data-tool/table-ids-explained.html
var request = new XMLHttpRequest();
request.open("GET", "data/CMAP2010_ratios_TR.json", false);
request.send(null)
var cmap2010ratioTR = JSON.parse(request.responseText);
//var cmap2010ratioTR = require("data/CMAP2010_ratios_TR.json")
var universeRatio = {
  '01': 'POP_RAT', //Age; Sex
  '02': 'POP_RAT', //Race
  '03': 'POP_RAT', //Hispanic or Latino Origin
  '04': 'POP_RAT', //Ancestry
  '05': 'POP_RAT', //Citizenship Status; Year of Entry; Foreign Born Place of Birth
  '06': 'POP_RAT', //Place of Birth
  '07': 'POP_RAT', //Migration/Residence 1 Year Ago
  '08': 'POP_RAT', //Commuting (Journey to Work); Place of Work
  '09': 'HH_RAT', //Relationship to Householder
  '10': 'POP_RAT', //Grandparents and Grandchildren Characteristics
  '11': 'HH_RAT', //Household Type; Family Type; Subfamilies
  '12': 'POP_RAT', //Marital Status; Marital History
  '13': 'POP_RAT', //Fertility
  '14': 'POP_RAT', //School Enrollment
  '15': 'POP_RAT', //Educational Attainment; Undergraduate Field of Degree
  '16': 'POP_RAT', //Language Spoken at Home
  '17': 'POP_RAT', //Poverty Status
  '18': 'POP_RAT', //Disability Status
  '19': 'HH_RAT', //Income
  '20': 'POP_RAT', //Earnings
  '21': 'POP_RAT', //Veteran Status; Period of Military Service
  '22': 'HH_RAT', //Food Stamps/Supplemental Nutrition Assistance Program (SNAP)
  '23': 'POP_RAT', //Employment Status; Work Status Last Year
  '24': 'POP_RAT', //Industry, Occupation, and Class of Worker
  '25': 'HU_RAT', //Housing Characteristics
  '26': 'POP_RAT', //Group Quarters
  '27': 'POP_RAT', //Health Insurance Coverage
  '28': '', //Computer and Internet Use
  '29': 'POP_RAT', //Citizen Voting-Age Population
}

//Median Calculation
//create breaklist from colum values
//create list of counts by break

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function numberWithCommas(x) {
  if (x == null) {
    return 0
  } else {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  //return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

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
    if (geo == 'blockGroup') {
      GEOID = json[i]["GEO_ID"].split("US")[1]
    }
    if (geo == 'tract') {
      GEOID = json[i]["state"].concat(json[i]["county"], json[i]["tract"])
    }
    if (geo == 'county') {
      GEOID = json[i]["state"].concat(json[i]["county"])
    }
    if (geo == 'muni') {
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
          variableObj[groupVar] = groupVariables["variables"][groupVar]['label'].replace("Estimate!!", "").replace("!!", "-").replace("Total-", "").replace("!!", "-")
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

function displayCensusTable(json, tableName, tableLabel, censusGeo) {

  var excludeList = ["block-group", "tract", "county", "state", "GEO_ID", "NAME"]
  var timeOut = 900;
  var headerRow = '';
  var bodyRows = '';
  var footerRow = '';
  var numRows = 0;
  var bins = new Object()

  //console.log(json[0])
  //console.log(json)
  headerRow += '<th>' + tableLabel + '</th>'
  json.forEach(function(a) {
    headerRow += '<th>' + a["NAME"] + '</th>'
  })

  Object.keys(json[0]).forEach(function(censusField) {
    timeOut += 100
    if ((!excludeList.includes(censusField)) && censusField.endsWith("E")) {
      numRows += 1
    }
  })

  censusVariables(tableName, timeOut).then(function(varLabels) {

    // Object.keys(json[0]).forEach(function(censusField) {
    //   if ((!excludeList.includes(censusField)) && censusField.endsWith("E")) {
    //     let rowLabel = varLabels[censusField]
    //     //console.log(rowLabel)
    //     //console.log(rowLabel.match(/[0-9]+(?!.*[0-9])/)[0])
    //     //bins.push(rowLabel.match(/[0-9]+(?!.*[0-9])/)[0])
    //     let binLabel = rowLabel.match(/[0-9]+(?!.*[0-9])/)[0];
    //     if(!Object.keys(bins).includes(binLabel)){
    //       bins[binLabel] = 0;
    //     }
    //     json.forEach(function(array) {
    //       bins[binLabel] += array[censusField]
    //     })
    //   }
    // })
    //
    // console.log(bins)


    Object.keys(json[0]).forEach(function(censusField) {
      var rowLabel = varLabels[censusField]
      //var tempArray = []
      //console.log(censusField + "-" + varLabels[censusField])
      if ((!excludeList.includes(censusField)) && censusField.endsWith("E")) {
        if ((varLabels[censusField].includes('Total')) && (numRows > 1)) {
          footerRow += '<tr><tfoot>'
          footerRow += '<td>' + rowLabel + '</td>'
        } else {
          bodyRows += '<tr>'
          bodyRows += '<td>' + rowLabel + '</td>'
        }

        json.forEach(function(array) {
          //var tempArray = []
          if ((varLabels[censusField].includes('Total')) && (numRows > 1)) {
            if (!tableLabel.includes("YEAR STRUCTURE")) {
              footerRow += '<td>' + numberWithCommas(array[censusField]) + '</td>'
            } else {
              footerRow += '<td>' + array[censusField] + '</td>'
            }
          } else {
            if (!tableLabel.includes("YEAR STRUCTURE")) {
              bodyRows += '<td>' + numberWithCommas(array[censusField]) + '</td>'
            } else {
              bodyRows += '<td>' + array[censusField] + '</td>'
            }
          }
        })
        bodyRows += '</tr>'
        if ((varLabels[censusField].includes('Total')) && (numRows > 1)) {
          footerRow += '</tfoot></tr>'
        }
      }
    })
    //console.log(json)
    //console.log(valuesArray)

    $(document).ready(function() {

      document.getElementById('dvData').innerHTML += '<table id=' + tableName + ' class="table display" width="100%"><thead><tr>' +
        headerRow +
        '</tr></thead><tbody>' +
        bodyRows +
        '</tbody>' + footerRow + '</table><br>'


      var table = $('#' + tableName).DataTable({
        //data: valuesArray,
        //columns: tableColumns,
        buttons: [
          'csv'
        ],
        //info: false,
        paging: false,
        searching: false,
        //order: [[ 0, "asc" ]],
        processing: true,
      });

    });
  })

  //censusObj = createCensusObj(json, censusGeo)
  //console.log(censusObj)
  //
  // Object.keys(json[0]).forEach(function(censusField) {
  //   timeOut += 50
  //   var newObj = new Object()
  //   if ((!excludeList.includes(censusField)) && censusField.endsWith("E")) {
  //     newObj['title'] = censusField
  //     //tableColumns.push(censusField)
  //     tableColumns.push(newObj)
  //   }
  // })
  //
  // var varLabels = censusVariables(tableName, timeOut)
  //
  // allocatedValues[tableLabel] = tableColumns
  //
  // Object.keys(censusObj).forEach(function(geoID) {
  //   var cValues = []
  //   Object.keys(json[0]).forEach(function(censusField) {
  //     if (!cValues.includes(censusField)) {
  //       cValues.push(varLabels[censusField])
  //     }
  //     if ((!excludeList.includes(censusField)) && censusField.endsWith("E")) {
  //       cValues.push(censusObj[geoID][censusField])
  //     }
  //     //cValues.push(censusObj[geoID][censusField])
  //   })
  //   allocatedValues[geoID] = cValues
  //   allocatedValuesArray.push(cValues)
  // })
  //
  // allocatedObj.push(allocatedValues)
  // console.log(allocatedValuesArray)
  //console.log(tableColumns)
  //console.log(valuesArray)

  //document.getElementById('dvData').innerHTML += '<table id=' + tableName + ' class="display" width="100%"></table>'
  //$(document).ready(function() {
  //  $('#' + tableName).DataTable({
  //    data: allocatedValuesArray,
  //    columns: tableColumns
  //  });
  //});

  // censusVariables(tableName, timeOut).then(function(varLabels) {
  //   //document.getElementById('dvData').innerHTML += json2table(allocatedObj, varLabels, tableLabel)
  //   document.getElementById('dvData').innerHTML += '<table id=' + tableName + ' class="display" width="100%"></table>'
  //   $(document).ready(function() {
  //     $('#' + tableName).DataTable({
  //       data: allocatedValuesArray,
  //       columns: tableColumns
  //     });
  //   });
  //
  //   // $(document).ready(function() {
  //   //   var table = $('#' + tableName).DataTable({
  //   //     "paging": false,
  //   //     "searching": false,
  //   //     "order": [[ 0, "asc" ]]
  //   //   });
  //   //   //table.column(tableLabel).order("asc")
  //   // });
  // })

  // return new Promise(resolve => {
  //   setTimeout(() => {
  //     resolve(allocatedObj);
  //   }, 300);
  // });

  return
}

function allocCensusDataPromise(json, csv, geo, geoRatio, inGeo, tableLabel, tableName, censusGeo) {
  return new Promise(function(fulfill, reject) {
    allocCensusData(json, csv, geo, geoRatio, inGeo, tableLabel, tableName, censusGeo).then(function(res) {
      try {
        //console.log(res)
        displayCensusTable(res, tableName, tableLabel, censusGeo);
      } catch (ex) {
        reject(ex);
      }
    }, reject);
  });
}

function allocCensusData(json, csv, geo, geoRatio, inGeo, tableLabel, tableName, censusGeo, medianAlloc) {
  //console.log(tableLabel)
  var excludeList = ["block-group", "tract", "county", "state", "GEO_ID", "NAME"]
  var allocatedValues = new Object();
  var tableValues = new Object();
  var tableData = []
  var ratioObj, censusObj;
  var timeOut = 900;
  var tableSubjectCode = tableName.charAt(1) + tableName.charAt(2)
  var bins = []
  var feq = []
  //var

  //  var data = d3.csv(csv, function(data) {
  //    return data
  //  })

  var data = cmap2010ratioTR
  ratioObj = selectBlockRatio(data, geo, geoRatio, inGeo)
  censusObj = createCensusObj(json, censusGeo)
  //console.log(data)


  tableColumns = [];
  Object.keys(json[1]).forEach(function(censusField) {
    var attr = censusField
    timeOut += 100
    if ((!excludeList.includes(attr)) && attr.endsWith("E")) {
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
        tableValues[censusField] += Math.round(parseFloat(censusObj[ratioObj[block]["GEO"]][censusField]) * parseFloat(ratioObj[block][universeRatio[tableSubjectCode]]))
        //allocSum += Math.round(parseFloat(censusObj[ratioObj[block]["BLKGRP"]][censusField]) * parseFloat(ratioObj[block]["BG_POP_RAT"]))
      }
    });
  });
  //console.log(tableValues)
  tableValues["NAME"] = 'Custom Study Area'
  tableData.push(tableValues)
  return new Promise(function(resolve, reject) {
    // A mock async action using setTimeout
    setTimeout(function() {
      resolve(tableData);
    }, timeOut);
  });
  //displayCensusTable(tableData, tableName, tableLabel, censusGeo)
  //setTimeout(function(){ displayCensusTable(tableData, tableName, tableLabel, censusGeo); }, timeOut)
  //})

}

function censusCounty(censusType, vintage, stateCodes, countyCodes, tables, censusGeo = 'county') {

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
      displayCensusTable(r, tName, tLable, censusGeo)
    })
    //document.getElementById('dvData').innerHTML += json2table(r)
  }
}

function censusMuni(censusType, vintage, stateCodes, muniCodes, tables, censusGeo = 'muni') {

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
      displayCensusTable(r, tName, tLable, censusGeo)
    })
    //document.getElementById('dvData').innerHTML += json2table(r)
  }
}

function censusTract(censusType, vintage, lat, long, tables, tractcodes = "*", allocate = false, inGeo = null, censusGeo = 'tract') {

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
      //console.log(json)
      return json
    })
    // .then(function(json) {
    //   return json
    // })
  }

  var medianTables = [{"B01002":"B01001"}]
  var mTableNames = Object.keys(medianTables[0])
  var medianAlloc = false

  function returnCensusTables() {
    //var arr = []
    for (let i = 0; i < tables.length; i++) {
      //console.log(tables[i])
      let tName = tables[i].split('-')[0]
      let tLable = tables[i].split('-')[1]
      if ((allocate == true) && (mTableNames.includes(tName))){
        tName = medianTables[0][tName]
        medianAlloc = true
      }
      else{
        medianAlloc = false
      }
      getTable(tName).then(function(a) {
        if (allocate == true) {
          allocCensusDataPromise(a, "data/CMAP2010_ratios_TR.csv", "TRACT", "TR", inGeo, tLable, tName, censusGeo, medianAlloc);
        } else {
          displayCensusTable(a, tName, tLable, censusGeo)
        }
      })
    }
  }

  returnCensusTables()
}

function censusBlockGroup(censusType, vintage, lat, long, tables, bgcodes = "*", allocate = false, inGeo = null, censusGeo = 'blockGroup') {

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
          displayCensusTable(a, tName, tLable, censusGeo)
        }
      })
    }
  }

  returnCensusTables()
}
