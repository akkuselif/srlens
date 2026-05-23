function doPost(e) {
  var sheet = SpreadsheetApp.openById('1OVkVCCAf6uyZO2YcQNb0kwe6bfYlubRb4aizJZpbufY').getActiveSheet();

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Timestamp', 'Profile', 'Planning %', 'Monitoring %', 'Reflection %', 'Average %']);
  }

  var data = JSON.parse(e.postData.contents);
  sheet.appendRow([
    new Date(),
    data.profile,
    data.plan,
    data.monitor,
    data.reflect,
    data.avg
  ]);

  return ContentService.createTextOutput('ok');
}

function doGet() {
  return ContentService.createTextOutput('SRLens data collector is running.');
}
