//Available census api years
//Update this list as new census data becomes available
//Alternative option-drop down can be replaced with raw input
var availableAPIs = {
  acs1: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  acs5: [2011, 2012, 2013, 2014, 2015, 2016, 2017],
  dec: [1990, 2000, 2010]
}


var availableTagsObj = new Object();
var availableTags = [];
var selectedTables = [];
//list of CDS Tables
var cdsList = [
  "B01001", //Age
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
  "B25070", //Rent/Owner Costs
  "B25091", //Housing Value
  "B25118", //HU Inc Tenure
  "B25106", //HU Inc Tenure
  "B27001", //Pop No Health Insurance
  "B99253", //Imputation of Vacancy Status
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

var cmapTracts = {
  "17197880419": "Census Tract 8804.19",
}

//includes counties within cmap modeling area
var cmapMunis = {
  "00243": "Addison",
  "00685": "Algonquin",
  "01010": "Alsip",
  "01595": "Antioch",
  "02154": "Arlington Heights",
  "02258": "Aroma Park",
  "03012": "Aurora",
  "03610": "Bannockburn",
  "03844": "Barrington",
  "03883": "Barrington Hills",
  "04013": "Bartlett",
  "04078": "Batavia",
  "04303": "Beach Park",
  "04572": "Bedford Park",
  "04585": "Beecher",
  "04975": "Bellwood",
  "05092": "Belvidere",
  "05248": "Bensenville",
  "05404": "Berkeley",
  "05573": "Berwyn",
  "05976": "Big Rock",
  "06587": "Bloomingdale",
  "06704": "Blue Island",
  "07133": "Bolingbrook",
  "07237": "Bonfield",
  "07471": "Bourbonnais",
  "07640": "Braceville",
  "07744": "Bradley",
  "07770": "Braidwood",
  "08225": "Bridgeview",
  "08446": "Broadview",
  "08576": "Brookfield",
  "09304": "Buckingham",
  "09447": "Buffalo Grove",
  "09531": "Bull Valley",
  "09642": "Burbank",
  "09759": "Burlington",
  "09798": "Burnham",
  "09980": "Burr Ridge",
  "10292": "Cabery",
  "10422": "Caledonia",
  "10487": "Calumet City",
  "10513": "Calumet Park",
  "10906": "Campton Hills",
  "11124": "Capron",
  "11176": "Carbon Hill",
  "11332": "Carol Stream",
  "11358": "Carpentersville",
  "11592": "Cary",
  "11982": "Cedar Point",
  "12476": "Channahon",
  "12801": "Chebanse",
  "13074": "Cherry Valley",
  "14000": "Chicago",
  "14026": "Chicago Heights",
  "14065": "Chicago Ridge",
  "14351": "Cicero",
  "14572": "Clarendon Hills",
  "15170": "Coal City",
  "16470": "Cortland",
  "16691": "Country Club Hills",
  "16873": "Countryside",
  "17458": "Crest Hill",
  "17497": "Crestwood",
  "17523": "Crete",
  "17887": "Crystal Lake",
  "18459": "Dalzell",
  "18485": "Dana",
  "18628": "Darien",
  "18992": "Deerfield",
  "19083": "Deer Park",
  "19161": "DeKalb",
  "19642": "Des Plaines",
  "19837": "Diamond",
  "20149": "Dixmoor",
  "20292": "Dolton",
  "20591": "Downers Grove",
  "21358": "Dwight",
  "21540": "Earlville",
  "21579": "East Brooklyn",
  "21696": "East Dundee",
  "21904": "East Hazel Crest",
  "22931": "Elburn",
  "23074": "Elgin",
  "23256": "Elk Grove Village",
  "23620": "Elmhurst",
  "23724": "Elmwood Park",
  "23945": "Elwood",
  "24452": "Essex",
  "24582": "Evanston",
  "24634": "Evergreen Park",
  "26571": "Flossmoor",
  "26710": "Ford Heights",
  "26935": "Forest Park",
  "26987": "Forest View",
  "27442": "Fox Lake",
  "27533": "Fox River Grove",
  "27624": "Frankfort",
  "27702": "Franklin Park",
  "28638": "Gardner",
  "28872": "Geneva",
  "28898": "Genoa",
  "29171": "Gilberts",
  "29652": "Glencoe",
  "29730": "Glendale Heights",
  "29756": "Glen Ellyn",
  "29938": "Glenview",
  "30029": "Glenwood",
  "30120": "Godley",
  "30328": "Golf",
  "30757": "Grand Ridge",
  "30991": "Grant Park",
  "31121": "Grayslake",
  "31446": "Green Oaks",
  "31667": "Greenwood",
  "32018": "Gurnee",
  "32200": "Hainesville",
  "32525": "Hampshire",
  "32746": "Hanover Park",
  "33331": "Harvard",
  "33383": "Harvey",
  "33435": "Harwood Heights",
  "33630": "Hawthorn Woods",
  "33695": "Hazel Crest",
  "33851": "Hebron",
  "34384": "Herscher",
  "34514": "Hickory Hills",
  "34722": "Highland Park",
  "34865": "Highwood",
  "35086": "Hillside",
  "35268": "Hinckley",
  "35307": "Hinsdale",
  "35385": "Hodgkins",
  "35411": "Hoffman Estates",
  "35515": "Holiday Hills",
  "35835": "Homer Glen",
  "35866": "Hometown",
  "35879": "Homewood",
  "36190": "Hopkins Park",
  "36750": "Huntley",
  "37218": "Indian Creek",
  "37257": "Indian Head Park",
  "37608": "Inverness",
  "37803": "Irwin",
  "37894": "Island Lake",
  "37907": "Itasca",
  "38479": "Johnsburg",
  "38570": "Joliet",
  "38830": "Justice",
  "38895": "Kaneville",
  "38921": "Kangley",
  "38934": "Kankakee",
  "39519": "Kenilworth",
  "39883": "Kildeer",
  "40065": "Kingston",
  "40143": "Kinsman",
  "40156": "Kirkland",
  "40767": "La Grange",
  "40793": "La Grange Park",
  "40884": "Lake Barrington",
  "40910": "Lake Bluff",
  "41105": "Lake Forest",
  "41183": "Lake in the Hills",
  "41326": "Lakemoor",
  "41586": "Lake Villa",
  "41651": "Lakewood",
  "41742": "Lake Zurich",
  "42028": "Lansing",
  "42184": "LaSalle",
  "42587": "Lee",
  "42756": "Leland",
  "42795": "Lemont",
  "42912": "Leonore",
  "43250": "Libertyville",
  "43406": "Lily Lake",
  "43510": "Limestone",
  "43666": "Lincolnshire",
  "43744": "Lincolnwood",
  "43770": "Lindenhurst",
  "43900": "Lisbon",
  "43939": "Lisle",
  "44225": "Lockport",
  "44407": "Lombard",
  "44524": "Long Grove",
  "44823": "Lostant",
  "45031": "Loves Park",
  "45421": "Lynwood",
  "45434": "Lyons",
  "45564": "McCook",
  "45616": "McCullom Lake",
  "45694": "McHenry",
  "46279": "Malta",
  "46357": "Manhattan",
  "46500": "Manteno",
  "46604": "Maple Park",
  "46786": "Marengo",
  "47007": "Markham",
  "47150": "Marseilles",
  "47540": "Matteson",
  "47774": "Maywood",
  "47787": "Mazon",
  "48242": "Melrose Park",
  "48333": "Mendota",
  "48554": "Merrionette Park",
  "48671": "Mettawa",
  "48892": "Midlothian",
  "49100": "Millbrook",
  "49308": "Millington",
  "49607": "Minooka",
  "49854": "Mokena",
  "49893": "Momence",
  "49945": "Monee",
  "50218": "Montgomery",
  "50491": "Morris",
  "50647": "Morton Grove",
  "51089": "Mount Prospect",
  "51349": "Mundelein",
  "51622": "Naperville",
  "51648": "Naplate",
  "52103": "Newark",
  "52584": "New Lenox",
  "53000": "Niles",
  "53377": "Norridge",
  "53442": "North Aurora",
  "53455": "North Barrington",
  "53481": "Northbrook",
  "53559": "North Chicago",
  "53663": "Northfield",
  "53871": "Northlake",
  "54144": "North Riverside",
  "54222": "North Utica",
  "54534": "Oak Brook",
  "54560": "Oakbrook Terrace",
  "54638": "Oak Forest",
  "54820": "Oak Lawn",
  "54885": "Oak Park",
  "55041": "Oakwood Hills",
  "55353": "Oglesby",
  "55639": "Old Mill Creek",
  "55938": "Olympia Fields",
  "56627": "Orland Hills",
  "56640": "Orland Park",
  "56887": "Oswego",
  "56926": "Ottawa",
  "57225": "Palatine",
  "57381": "Palos Heights",
  "57394": "Palos Hills",
  "57407": "Palos Park",
  "57654": "Park City",
  "57732": "Park Forest",
  "57875": "Park Ridge",
  "59052": "Peotone",
  "59234": "Peru",
  "59572": "Phoenix",
  "59988": "Pingree Grove",
  "60287": "Plainfield",
  "60352": "Plano",
  "60391": "Plattville",
  "61145": "Poplar Grove",
  "61216": "Port Barrington",
  "61314": "Posen",
  "61678": "Prairie Grove",
  "62016": "Prospect Heights",
  "62757": "Ransom",
  "63056": "Reddick",
  "63641": "Richmond",
  "63706": "Richton Park",
  "64135": "Ringwood",
  "64278": "Riverdale",
  "64304": "River Forest",
  "64343": "River Grove",
  "64421": "Riverside",
  "64538": "Riverwoods",
  "64616": "Robbins",
  "64902": "Rockdale",
  "65338": "Rolling Meadows",
  "65442": "Romeoville",
  "65806": "Roselle",
  "65819": "Rosemont",
  "66027": "Round Lake",
  "66040": "Round Lake Beach",
  "66053": "Round Lake Heights",
  "66066": "Round Lake Park",
  "66443": "Rutland",
  "66638": "St. Anne",
  "66703": "St. Charles",
  "67372": "Sammons Point",
  "67548": "Sandwich",
  "67769": "Sauk Village",
  "68003": "Schaumburg",
  "68081": "Schiller Park",
  "68640": "Seneca",
  "68822": "Shabbona",
  "69277": "Sheridan",
  "69758": "Shorewood",
  "70122": "Skokie",
  "70161": "Sleepy Hollow",
  "70460": "Somonauk",
  "70564": "South Barrington",
  "70629": "South Chicago Heights",
  "70720": "South Elgin",
  "70850": "South Holland",
  "71370": "South Wilmington",
  "72052": "Spring Grove",
  "72520": "Steger",
  "72676": "Stickney",
  "72923": "Stone Park",
  "73157": "Streamwood",
  "73170": "Streator",
  "73391": "Sugar Grove",
  "73638": "Summit",
  "73943": "Sun River Terrace",
  "74223": "Sycamore",
  "74275": "Symerton",
  "75081": "Third Lake",
  "75185": "Thornton",
  "75360": "Timberlane",
  "75484": "Tinley Park",
  "75718": "Tonica",
  "75874": "Tower Lakes",
  "76160": "Trout Valley",
  "76225": "Troy Grove",
  "76706": "Union",
  "76771": "Union Hill",
  "76935": "University Park",
  "77694": "Vernon Hills",
  "77707": "Verona",
  "77993": "Villa Park",
  "78175": "Virgil",
  "78227": "Volo",
  "78370": "Wadsworth",
  "78929": "Warrenville",
  "79163": "Waterman",
  "79267": "Wauconda",
  "79293": "Waukegan",
  "79397": "Wayne",
  "79813": "Wenona",
  "80047": "Westchester",
  "80060": "West Chicago",
  "80125": "West Dundee",
  "80242": "Western Springs",
  "80645": "Westmont",
  "81048": "Wheaton",
  "81087": "Wheeling",
  "81919": "Willowbrook",
  "82049": "Willow Springs",
  "82075": "Wilmette",
  "82101": "Wilmington",
  "82400": "Winfield",
  "82530": "Winnetka",
  "82686": "Winthrop Harbor",
  "82855": "Wonder Lake",
  "82985": "Wood Dale",
  "83245": "Woodridge",
  "83349": "Woodstock",
  "83518": "Worth",
  "84038": "Yorkville",
  "84220": "Zion",
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
          availableTagsObj[groups["groups"][k]['name']] = groups["groups"][k]['description']
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

  var cGeoType = document.getElementById("selectGeographyType");
  var selGeoType = cGeoType.options[cGeoType.selectedIndex].value;

  if (selGeoType == 'county') {
    $("#selectGeography").empty();
    geoDropdown(cmapCounties)
  }

  if (selGeoType == 'muni') {
    $("#selectGeography").empty();
    geoDropdown(cmapMunis)
  }

  if (selGeoType == 'tract') {
    $("#selectGeography").empty();
    geoDropdown(cmapTracts)
  }

  function geoDropdown(geos) {
    if (value.length == 0) document.getElementById("selectGeography").innerHTML = "<option></option>";
    else {
      var catOptions = "";

      for (k in geos) {
        catOptions += "<option value=" + k + ">" + geos[k] + "</option>";
      }
      document.getElementById("selectGeography").innerHTML = catOptions;
      sortDropdownList(document.getElementById("selectGeography"))
    }
  }


}

//fix sort
function sortDropdownList(ddl) {

  var options = [].slice.apply(ddl.options, [0]);
  ddl.innerHTML = "";
  var sorted = options.sort(function(a, b) {
    return +(a.innerText) - +(b.innerText);
  });

  for (var i = 0; i < sorted.length; i++) {
    ddl.options.add(sorted[i]);
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
          //selectedTables.push(splitTableName(ui.item.value)[0])
          selectedTables.push(ui.item.value)
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
      //console.log(cdsList[i] + "-" + availableTagsObj[cdsList[i]])
      selectedTables.push(cdsList[i] + "-" + availableTagsObj[cdsList[i]])
    }
  } if(cdsCheckbox.checked == false) {
    selectedTables = selectedTables.filter(function(value, index, arr) {
        if (!cdsList.includes(value.split("-")[0])) {
          console.log(value)
            return value
          }
        })
    }
  };

  function submitSelection() {

    //Remove existing table to replaced with data selection
    var element = document.getElementsByTagName("Table"),
      index;

    for (index = element.length - 1; index >= 0; index--) {
      element[index].parentNode.removeChild(element[index]);
    }

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

    if (selGeoType == 'county') {
      censusCounty(selCDT, selV, "17", selGeoList.join(","), selectedTables, selGeoType)
    }

    if (selGeoType == 'muni') {
      censusMuni(selCDT, selV, "17", selGeoList.join(","), selectedTables, selGeoType)
    }

    if (selGeoType == 'tract') {
      censusTract(selCDT, selV, "17", selGeoList.join(","), selectedTables, selGeoType)
    }

    if (selGeoType == 'bg') {
      censusMuni(selCDT, selV, "17", selGeoList.join(","), selectedTables, selGeoType)
    }

  }
