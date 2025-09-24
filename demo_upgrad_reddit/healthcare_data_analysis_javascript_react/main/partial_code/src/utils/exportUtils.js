// utils/exportUtils.js
/**
 * Utility for client-side export of data as CSV or JSON file.
 * serializeAndDownload(data, filename, format="csv"|"json")
 */
export function serializeAndDownload(data, filename, format = "csv") {
  // Instructions:
  // 1. Declare 'fileData' and 'mimeType' variables, which will hold the serialized data string and the MIME type, respectively.
  // 2. Check the value of 'format'.
  //    a. If format is 'json':
  //       - Convert the 'data' argument to a formatted JSON string and assign to 'fileData'.
  //       - Set 'mimeType' to 'application/json'.
  //    b. If format is 'csv':
  //       - Check if 'data' is an array and not empty.
  //         - If not, set 'fileData' to an empty string and 'mimeType' to 'text/csv'.
  //         - Else:
  //             - Obtain the list of headers (fields) from the first object in 'data'.
  //             - Create an 'escape' function to properly quote and escape CSV values.
  //             - Construct the CSV header string by joining the fields by commas.
  //             - Iterate over the data array to produce CSV rows, escaping all values and joining them by commas.
  //             - Join all rows with line breaks and prepend the header row.
  //             - Set 'mimeType' to 'text/csv'.
  // 3. Create a Blob object using the serialized 'fileData' and provide the 'mimeType'.
  // 4. Generate a blob URL from the created Blob object using 'window.URL.createObjectURL'.
  // 5. Create an anchor ('a') element, configure its 'href' to the blob URL, set its 'download' attribute to the 'filename', and hide the element.
  // 6. Append the anchor element to the document body and trigger a click on it to start the download.
  // 7. Set a timeout to revoke the blob URL and remove the anchor element from the DOM after a short delay (e.g., 500 ms) to release resources.
  
  // Use the following variable names when implementing:
  // - fileData (string): the serialized CSV or JSON string
  // - mimeType (string): the appropriate MIME type for the file
  // - blob (Blob): the Blob object created from fileData
  // - url (string): the object URL created from the blob
  // - a (HTMLAnchorElement): the anchor element that triggers download
}