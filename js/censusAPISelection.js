//Available census api years
//Update this list as new census data becomes available
//Alternative option-drop down can be replaced with raw input
var availableAPIs = {
  acs1: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  acs5: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  dec: [1990, 2000, 2010]
}


var availableTags = [];
var selectedTables = [];
//list of CDS Tables
var cdsList = ["B01001", //Age
               "B01002", //Med Age
               "B03002", //Race
               "B08301", //Modeshare
               "B08136", //Modeshare
               "B09019", //Pop HH
               "B11003", //HH Type
               "B11016", //Family Size
               "B15003", //Educational attainment
               "C16001", //Lang at home
               "B16005", //Linguistic isolation
               "B17001", //Pop Poverty
               "B17010", //Fam Poverty
               "B18135", //Disabled Pop
               "B19001", //Income
               "B19058", //Public Assistance or "Food Stamps"
               "B19083", //Public Assistance or "Food Stamps"
               "B19101", //Public Assistance or "Food Stamps"
               "B19119", //Family Median Income
               "B23001", //Labor Force
               "B25002", //Occupied/Vacant HU
               "B25024", //HU Type
               "B25018", //HU Type
               "B25032", //HU Type
               "B25034", //HU Age / Number of Bedrooms
               "B25035", //HU Age / Number of Bedrooms
               "B25035",
               "B25037",
               "B25041",
               "B25046",


]

//list of CMAP Counties
//includes counties within cmap modeling area
var cmapCounties = {
  "031": "Cook County",
  "043": "DuPage County",
  "089": "Kane County",
  "093": "Kendall County",
  "097": "Lake County",
  "111": "McHenry County",
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
  //var availableTags =  [];
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

      for (k in groups["groups"]) {
        var lastChar = groups["groups"][k]['name'][groups["groups"][k]['name'].length - 1];
        var isNumeric = /^\d+$/.test(lastChar);
        if (isNumeric == true) {
          availableTags.push(groups["groups"][k]['name'] + "-" + groups["groups"][k]['description'])
        }

      };
    } else {
      const errorMessage = document.createElement("marquee")
      errorMessage.textContent = `Gah, it"s not working!`
      app.appendChild(errorMessage)
    }
    //console.log(availableTags)
  }
  request.send()
  //return availableTags
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
  // console.log(availableTags)
  // if (value.length == 0) document.getElementById("censusTables").innerHTML = "<option></option>";
  // else {
  //   // //console.log(availableTags)
  //   // var catOptions = "";
  //   // for (var i=0; availableTags.length;i++) {
  //   //   console.log(availableTags[i])
  //   //   catOptions += "<option value=" + availableTags[i]["name"] + ">" + availableTags[i]["name"] + "-" + availableTags[i]["description"] + "</option>";
  //   // }
  //   // document.getElementById("censusTables").innerHTML = catOptions;
  // }
  $(function() {
    function split(val) {
      return val.split(/,\s*/);
    }

    function splitTableName(val) {
      return val.split(/-\s*/);
    }

    function extractLast(term) {
      return split(term).pop();
    }

    $("#tags")
      // don't navigate away from the field on tab when selecting an item
      .on("keydown", function(event) {
        if (event.keyCode === $.ui.keyCode.TAB &&
          $(this).autocomplete("instance").menu.active) {
          event.preventDefault();
        }
      })
      .autocomplete({
        minLength: 4,
        source: function(request, response) {
          // delegate back to autocomplete, but extract the last term
          response($.ui.autocomplete.filter(
            availableTags, extractLast(request.term)));
        },
        focus: function() {
          // prevent value inserted on focus
          return false;
        },
        select: function(event, ui) {
          var terms = split(this.value);
          // remove the current input
          terms.pop();
          // add the selected item
          terms.push(ui.item.value);
          selectedTables.push(splitTableName(ui.item.value)[0])
          // add placeholder to get the comma-and-space at the end
          terms.push("");
          this.value = terms.join(", ");
          return false;
        }
      });
  });
}

//Select individual census tables or CDS Summary
//Other summary selections can be added here to support CMAP data needs
function selectCDSTables() {
  var cdsCheckbox = document.getElementById("myCheck");
  //var elements = document.getElementById("censusTables").options;

  if (cdsCheckbox.checked == true) {
    for (var i = 0; i < cdsList.length; i++) {
      selectedTables.push(cdsList[i])
    }
  }
};

function submitSelection() {
  //var selectedList = [];
  //var tablesSelected = document.getElementById("censusTables").options;
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

  // if (tablesSelected.length > 0) {
  //   for (var i = 0; i < tablesSelected.length; i++) {
  //     if (tablesSelected[i].selected == true) {
  //       selectedList.push(tablesSelected[i].value)
  //     };
  //   }
  // }
  //console.log(selectedList)
  //Submit to collect data
  //console.log(selectedTables)
  //censusCounty(selCDT, selV, "17", selGeoList.join(","), ["NAME", "group(" + selectedTables.join(",") + ")"])
  censusCounty(selCDT, selV, "17", selGeoList.join(","), selectedTables)
}
