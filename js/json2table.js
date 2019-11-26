function json2table(json, tableName) {

  //for(var i=0; i<json)
  console.log(tableName)
  var allCols = Object.keys(json[0])
  console.log(allCols[0])
  //console.log(json)
  var cols = [tableName];
  for (var i = 0; i < allCols.length; i++) {
    //console.log(allCols[i])
    if (allCols[i] != tableName) {
      cols.push(allCols[i])
    }
  }
  //console.log(cols)

  var headerRow = '';
  var bodyRows = '';

  var classes = classes || '';

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  cols.map(function(col) {
    headerRow += '<th>' + capitalizeFirstLetter(col) + '</th>';
  });

  json.map(function(row) {
    bodyRows += '<tr>';


    cols.map(function(colName) {
      if (colName == tableName) {
        for (var i = 0; i < row[colName].length; i++) {
          //console.log(row[colName][i])
          bodyRows += '<td>' + row[colName][i] + '</td>' + '<td>' + row['Count'][i] + '</td>';
          bodyRows += '</tr>';
        }
      }

      //bodyRows += '<td>' + row[colName] + '</td>';
      //bodyRows += '</tr>';
    })

    //bodyRows += '</tr>';
  });

  return '<table class="' +
    classes +
    '"><thead><tr>' +
    headerRow +
    '</tr></thead><tbody>' +
    bodyRows +
    '</tbody></table>';

}
