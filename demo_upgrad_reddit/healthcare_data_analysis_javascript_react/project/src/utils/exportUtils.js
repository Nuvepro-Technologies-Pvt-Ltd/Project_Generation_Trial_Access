// utils/exportUtils.js
/**
 * Utility for client-side export of data as CSV or JSON file.
 * serializeAndDownload(data, filename, format="csv"|"json")
 */
export function serializeAndDownload(data, filename, format = "csv") {
  let fileData, mimeType;
  if (format === "json") {
    fileData = JSON.stringify(data, null, 2);
    mimeType = "application/json";
  } else {
    // CSV: use array of objects. First row is header.
    if (!Array.isArray(data) || !data.length) {
      fileData = "";
      mimeType = "text/csv";
    } else {
      const fields = Object.keys(data[0]);
      const escape = (val) =>
        (val == null ? '' : '"' + String(val).replace(/"/g, '""') + '"');
      const header = fields.join(",");
      const rows = data.map(row =>
        fields.map(field => escape(row[field])).join(",")
      );
      fileData = [header, ...rows].join("
");
      mimeType = "text/csv";
    }
  }
  // Create blob and trigger download
  const blob = new Blob([fileData], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    window.URL.revokeObjectURL(url);
    a.remove();
  }, 500);
}
