//Available census api years
//Update this list as new census data becomes available
//Alternative option-drop down can be replaced with raw input
var availableAPIs = {
  acs1: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  acs5: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  dec: [1990, 2000, 2010]
}

var availableTables =  [];

//list of CDS Tables
var cdsList = ["B01001_001E", "B01002_001E"]

//list of CMAP Counties
//includes counties within cmap modeling area
var cmapCounties = {
  "031": "Cook County",
  "197": "Will County"
}

var cdsTables = {
  "B01001": {
    "name": "SEX BY AGE",
    "tableColumns": [],
    "tableLabels": []
  }
}



//Make request to census groups API
//censusGroups()
function censusGroups() {
  //Selected Census Data Type Value
  var v = document.getElementById("vintage");
  var selV = v.options[v.selectedIndex].value;

  //Selected Census Data Type Value
  var cDT = document.getElementById("selectCensusDataType");
  var selCDT = cDT.options[cDT.selectedIndex].value;

  var request = new XMLHttpRequest()

  //open new connection
  request.open("GET", "https://api.census.gov/data/" + selV + "/acs/" + selCDT + "/groups/", true)

  request.onload = function() {
    // Begin accessing JSON data here
    var groups = JSON.parse(this.response)
    //console.log(groups)
    if (request.status >= 200 && request.status < 400) {

      //
      for (k in groups["groups"]) {
         availableTables.push(groups["groups"][k])
      };
    } else {
      const errorMessage = document.createElement("marquee")
      errorMessage.textContent = `Gah, it"s not working!`
      app.appendChild(errorMessage)
    }
    //console.log(availableTables)
  }
  request.send()
};


//Add available vintage years based on census data type selection
function changecat(value) {
  if (value.length == 0) document.getElementById("vintage").innerHTML = "<option></option>";
  else {
    var catOptions = "";
    for (vintageId in availableAPIs[value]) {
      catOptions += "<option>" + availableAPIs[value][vintageId] + "</option>";
    }
    document.getElementById("vintage").innerHTML = catOptions;
  }
}

//Add available geographies based on census geo type selection
function changeGeo(value) {
  if (value.length == 0) document.getElementById("selectGeography").innerHTML = "<option></option>";
  else {
    var catOptions = "";
    for (k in cmapCounties) {
      catOptions += "<option value=" + k + ">" + cmapCounties[k] + "</option>";
    }
    document.getElementById("selectGeography").innerHTML = catOptions;
  }
}

//Add available tables based on census data type and vintage selection
function changeTable(value) {
  censusGroups();
  if (value.length == 0) document.getElementById("censusTables").innerHTML = "<option></option>";
  else {
    //console.log(availableTables)
    var catOptions = "";
    for (var i=0; i<availableTables.length;i++) {
      console.log(availableTables)
      catOptions += "<option value=" + availableTables[i]["name"] + ">" + availableTables[i]["name"] + "-" + availableTables[i]["description"] + "</option>";
    }
    document.getElementById("censusTables").innerHTML = catOptions;
  }
}

//Select individual census tables or CDS Summary
//Other summary selections can be added here to support CMAP data needs
function selectCDSTables() {
  var checkBox = document.getElementById("myCheck");
  var elements = document.getElementById("censusTables").options;

  if (checkBox.checked == true) {
    for (var i = 0; i < elements.length; i++) {
      if (cdsList.includes(elements[i].value)) {
        elements[i].selected = true;
      }
    }
  } else {
    if (elements.length > 0) {
      for (var i = 0; i < elements.length; i++) {
        elements[i].selected = false;
      }
    }
  }
};

function submitSelection() {
  var selectedList = [];
  var tablesSelected = document.getElementById("censusTables").options;
  //Selected Census Data Type Value
  var cDT = document.getElementById("selectCensusDataType");
  var selCDT = cDT.options[cDT.selectedIndex].value;

  var cGeoType = document.getElementById("selectGeographyType");
  var selGeoType = cGeoType.options[cGeoType.selectedIndex].value;

  var cGeo = document.getElementById("selectGeography").options;
  var selGeoList = [];

  if (cGeo.length > 0) {
    for (var i = 0; i < cGeo.length; i++) {
      if (cGeo[i].selected == true) {
        selGeoList.push(cGeo[i].value)
      };
    }
    //console.log(selGeoList)
  }

  //Selected Census Data Type Value
  var v = document.getElementById("vintage");
  var selV = v.options[v.selectedIndex].value;

  if (tablesSelected.length > 0) {
    for (var i = 0; i < tablesSelected.length; i++) {
      if (tablesSelected[i].selected == true) {
        selectedList.push(tablesSelected[i].value)
      };
    }
  }
  //console.log(selectedList)
  //Submit to collect data
  censusCounty(selCDT, selV, "17", selGeoList.join(","), ["NAME", "group(" + selectedList.join(",") + ")"])
}
