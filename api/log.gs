function doGet(e) {
  var sheet = SpreadsheetApp.openById('1OVkVCCAf6uyZO2YcQNb0kwe6bfYlubRb4aizJZpbufY').getActiveSheet();

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Timestamp', 'Profile', 'Planning %', 'Monitoring %', 'Reflection %', 'Average %']);
  }

  sheet.appendRow([
    new Date(),
    e.parameter.profile,
    e.parameter.plan,
    e.parameter.monitor,
    e.parameter.reflect,
    e.parameter.avg
  ]);

  return ContentService.createTextOutput('ok');
}
