function json2table(json, classes) {

  console.log(Object.keys(json[0]))
  var allCols = Object.keys(json[0])
  var cols=[];
  for(var i=0;i<allCols.length;i++){
    console.log(allCols[i])
    if(allCols[i].endsWith("E")){
      cols.push(allCols[i])
    }
  }
  console.log(cols)

  var headerRow = '';
  var bodyRows = '';

  classes = classes || '';

  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  cols.map(function(col) {
    headerRow += '<th>' + capitalizeFirstLetter(col) + '</th>';
  });

  json.map(function(row) {
    bodyRows += '<tr>';

    cols.map(function(colName) {
      bodyRows += '<td>' + row[colName] + '</td>';
    })

    bodyRows += '</tr>';
  });

  return '<table class="' +
    classes +
    '"><thead><tr>' +
    headerRow +
    '</tr></thead><tbody>' +
    bodyRows +
    '</tbody></table>';
}
