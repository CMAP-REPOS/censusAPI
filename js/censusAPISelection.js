function censusCounty(acsType,vintage,stateCode,tables){

  var tableType;
  if(tables[0].startsWith('S')){
    tableType = 'subject'
  }
  else if (tables[0].startsWith('B')) {
    tableType = ''
  }

  else if (tables[0].startsWith('D')) {
    tableType = 'profile'
  }

  census({
      vintage: vintage, // required
      geoHierarchy: {
        // required
        state: stateCode,
        county: "*"
      },
      //cant make call for data and geojson at the same time
      //geoResolution: "5m",
      sourcePath: ["acs", acsType, tableType], // required
      values: tables, // required
      statsKey: "7d28d36d1b0595e1faf3c7c56ed6df8f4def1452" // required for > 500 calls per day
    },
    function(error, response) {

      document.getElementById('container').innerHTML = json2table(response)
    });
}




var availableAPIs = {
  acs1: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  acs5: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  dec: [1990, 2000, 2010]
}

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

var cdsList = ["B01001_001E", "B01002_001E"]

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

function submitSelection(){
  var selectedList = []
  var elements = document.getElementById("censusTables").options;
  if (elements.length > 0) {
    for (var i = 0; i < elements.length; i++) {
      if(elements[i].selected == true){
        selectedList.push(elements[i].value)
      };
    }
  }
  console.log(selectedList)
  //var tables = ["S0102_C01_001E", "S0102_C02_001E"]
  censusCounty("acs5", 2017, "17", selectedList)
}
