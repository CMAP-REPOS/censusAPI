//var variableObj = new Object();

function json2table(json, varLables, tableLabel) {

  var headerRow = '';
  var bodyRows = '';
  var classes = 'table';
  var tableID;

  //for(var i=0; i<json)
  console.log(json)
  var allCols = Object.keys(json[0])
  //console.log(allCols[0])
  //console.log(json)
  var cols = [tableLabel];
  for (var i = 0; i < allCols.length; i++) {
    //console.log(allCols[i])
    if (allCols[i] != tableLabel) {
      cols.push(allCols[i])
    }
  }
  //console.log(cols)
  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  cols.map(function(col) {
    headerRow += '<th>' + capitalizeFirstLetter(col) + '</th>';
  });

  json.map(function(row) {

    // cols.map(function(colName) {
    //   if (colName == tableLabel) {
    //     for (var i = 0; i < row[colName].length; i++) {
    //       console.log(varLables)
    //       console.log(row[colName][i])
    //       console.log(varLables[row[colName][i]])
    //       //var rowLabel = varLables[row[colName][i]]
    //       bodyRows += '<td>' + row[colName][i] + '</td>' + '<td>' + row['Count'][i] + '</td>';
    //       bodyRows += '</tr>';
    //     }
    //   }
    //
    //   //bodyRows += '<td>' + row[colName] + '</td>';
    //   //bodyRows += '</tr>';
    // })

    var valueLength = row[tableLabel].length
    var footerTrigger = false;
    for (var i=0; i<valueLength;i++){
      bodyRows += '<tr>';
      cols.map(function(colName) {
        if (colName == tableLabel){
          tableID = row[colName][i].split("_")[0]
          var rowLabel = varLables[row[colName][i]]
          if(rowLabel == 'Total'){
            bodyRows += '<tfoot>'
            footerTrigger = true
          }
          else{
            footerTrigger = false
          }
          bodyRows += '<td>' + rowLabel + '</td>';
        }
        else{
          bodyRows += '<td>' + row[colName][i] + '</td>';
        }
      })
      if(footerTrigger == true){
        bodyRows += '</tfoot>'
      }
      bodyRows += '</tr>';
    }

    //bodyRows += '</tr>';
  });

  return '<table id="' + tableID  + '"'+ 'class="' +
    classes +
    '"><thead><tr>' +
    headerRow +
    '</tr></thead><tbody>' +
    bodyRows +
    '</tbody></table>';

}
