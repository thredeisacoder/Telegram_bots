function sendTelegramNotification(botSecret, chatId, body) { 
  var response = UrlFetchApp.fetch("https://api.telegram.org/bot" + botSecret + "/sendMessage?text=" + encodeURIComponent(body) + "&chat_id=" + chatId + "&parse_mode=HTML"); 
}

function mySendMessage() {
  const BOT_SECRET = 'API'; // API TOKEN - BOT SECRET KEY
  const CHAT_ID = 'ID_CHAT'; // ID GROUP CHAT
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName("Info"); // Assuming the sheet name is "Info"
  const lastRow = sheet.getLastRow();
  const range = sheet.getRange(`A1:D${lastRow}`).getValues(); // Adjusted range to fetch from row 1 to the last row

  Logger.log(range);
  
  // Loop through each row and send notification
  range.forEach(row => {
    const [fullName, address, dob, ssn] = row;
    const formattedDOB = Utilities.formatDate(new Date(dob), Session.getScriptTimeZone(), "MM/dd/yyyy"); // Format DOB to MM/dd/yyyy
    const message = `Full Name: ${fullName}\nAddress: ${address}\nDOB: ${formattedDOB}\nSSN: ${ssn}\n\n`; // Added newline for separation
    
    // Send notification with backoff mechanism
    sendWithBackoff(BOT_SECRET, CHAT_ID, message);
  });
}

function sendWithBackoff(botSecret, chatId, message) {
  var MAX_RETRIES = 5;
  var retryCount = 0;
  var success = false;
  
  while (!success && retryCount < MAX_RETRIES) {
    try {
      sendTelegramNotification(botSecret, chatId, message);
      success = true;
    } catch (error) {
      if (error.toString().includes("Too Many Requests")) {
        var retryAfter = 40; // Retry after 40 seconds
        Utilities.sleep(retryAfter * 1000); // Convert seconds to milliseconds
        retryCount++;
      } else {
        throw error; // Rethrow other errors
      }
    }
  }
}
