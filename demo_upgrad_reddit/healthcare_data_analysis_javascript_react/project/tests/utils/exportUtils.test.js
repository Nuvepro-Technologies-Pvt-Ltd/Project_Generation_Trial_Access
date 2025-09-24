import { serializeAndDownload } from '../../src/utils/exportUtils';

// tests/utils/exportUtils.test.js
// Jest test suite for serializeAndDownload (client-side data export utility)
// Covers positive, negative, edge, and error scenarios

// Use Jest's mocks to handle global window, document and Blob

describe('serializeAndDownload', () => {
  let originalCreateObjectURL;
  let originalRevokeObjectURL;
  let originalCreateElement;
  let appendChildSpy;
  let clickSpy;
  let removeSpy;
  let blobSpy;

  beforeAll(() => {
    // Mock global Blob
    global.Blob = function(content, options) {
      this.content = content;
      this.options = options;
      return this;
    };
    blobSpy = jest.spyOn(global, 'Blob');
  });

  beforeEach(() => {
    originalCreateObjectURL = window.URL.createObjectURL;
    originalRevokeObjectURL = window.URL.revokeObjectURL;
    originalCreateElement = document.createElement;

    // Mock URL.createObjectURL & revokeObjectURL
    window.URL.createObjectURL = jest.fn(() => 'blob:url/test');
    window.URL.revokeObjectURL = jest.fn();
    // Mock document.createElement for 'a'
    clickSpy = jest.fn();
    removeSpy = jest.fn();
    document.createElement = jest.fn(() => ({
      style: {},
      set href(url) { this._href = url; },
      get href() { return this._href; },
      set download(val) { this._download = val; },
      get download() { return this._download; },
      click: clickSpy,
      remove: removeSpy,
    }));
    appendChildSpy = jest.spyOn(document.body, 'appendChild').mockImplementation(() => {});
    jest.useFakeTimers();
  });

  afterEach(() => {
    window.URL.createObjectURL = originalCreateObjectURL;
    window.URL.revokeObjectURL = originalRevokeObjectURL;
    document.createElement = originalCreateElement;
    appendChildSpy.mockRestore();
    jest.clearAllTimers();
  });

  afterAll(() => {
    blobSpy.mockRestore();
  });

  test('testJSONExport_ValidObject_TriggersBlobDownloadWithJSON', () => {
    const data = { a: 1, b: 'foo', c: null };
    serializeAndDownload(data, 'data.json', 'json');
    expect(blobSpy).toHaveBeenCalledWith([
      JSON.stringify(data, null, 2)
    ], { type: 'application/json' });
    expect(window.URL.createObjectURL).toHaveBeenCalledTimes(1);
    expect(document.createElement).toHaveBeenCalledWith('a');
    expect(appendChildSpy).toHaveBeenCalled();
    expect(clickSpy).toHaveBeenCalled();
    expect(removeSpy).not.toHaveBeenCalled(); // Not yet
    jest.runAllTimers();
    expect(window.URL.revokeObjectURL).toHaveBeenCalledWith('blob:url/test');
    expect(removeSpy).toHaveBeenCalled();
  });

  test('testCSVExport_ValidArrayOfObjects_ProperCSVDownload', () => {
    const data = [
      { name: 'Alice', age: 30, job: 'Engineer' },
      { name: 'Bob', age: 25, job: 'Artist' }
    ];
    serializeAndDownload(data, 'users.csv', 'csv');
    expect(blobSpy).toHaveBeenCalledWith([
      'name,age,job\r\n"Alice","30","Engineer"\r\n"Bob","25","Artist"'
    ], { type: 'text/csv' });
    expect(window.URL.createObjectURL).toHaveBeenCalled();
    expect(clickSpy).toHaveBeenCalled();
    expect(document.createElement).toHaveBeenCalled();
    jest.runAllTimers();
    expect(window.URL.revokeObjectURL).toHaveBeenCalled();
    expect(removeSpy).toHaveBeenCalled();
  });

  test('testCSVExport_EmptyArray_ProducesEmptyCSVFile', () => {
    serializeAndDownload([], 'empty.csv', 'csv');
    expect(blobSpy).toHaveBeenCalledWith([''], { type: 'text/csv' });
    expect(clickSpy).toHaveBeenCalled();
  });

  test('testCSVExport_InvalidInput_NotArray_ProducesEmptyCSV', () => {
    serializeAndDownload('not-an-array', 'invalid.csv', 'csv');
    expect(blobSpy).toHaveBeenCalledWith([''], { type: 'text/csv' });
    expect(clickSpy).toHaveBeenCalled();
  });

  test('testCSVExport_ArrayWithNullsAndQuotes_EscapesCorrectly', () => {
    const data = [
      { a: null, b: 'foo"bar', c: 42 }
    ];
    // should escape quotes and null as ""
    serializeAndDownload(data, 'escape.csv', 'csv');
    // Assembling expected CSV
    const expectedHeader = 'a,b,c';
    const expectedRow = '"","foo""bar","42"';
    const expectedCSV = expectedHeader + '\r\n' + expectedRow;
    expect(blobSpy).toHaveBeenCalledWith([expectedCSV], { type: 'text/csv' });
    expect(clickSpy).toHaveBeenCalled();
  });

  test('testCSVExport_MinimalFieldsAndNonString_HandlesTypes', () => {
    const data = [
      { i: 1, t: true, n: NaN, u: undefined, z: 0 }
    ];
    serializeAndDownload(data, 'types.csv', 'csv');
    // All fields, undefined and NaN result in quoted empty strings
    const expectedRow = '"1","true","NaN","","0"';
    const expectedCSV = 'i,t,n,u,z\r\n' + expectedRow;
    expect(blobSpy).toHaveBeenCalledWith([expectedCSV], { type: 'text/csv' });
    expect(clickSpy).toHaveBeenCalled();
  });

  test('testDefaultFormat_UsesCSV', () => {
    serializeAndDownload([{ a: 1 }], 'default.csv');
    const expectedCSV = 'a\r\n"1"';
    expect(blobSpy).toHaveBeenCalledWith([expectedCSV], { type: 'text/csv' });
    expect(clickSpy).toHaveBeenCalled();
  });

  test('testDownloadLink_AttributesSetProperly', () => {
    serializeAndDownload([{ x: 1 }], 'xyz.csv', 'csv');
    const createdLink = document.createElement.mock.results[0].value;
    expect(createdLink.href).toEqual('blob:url/test');
    expect(createdLink.download).toEqual('xyz.csv');
  });

  test('testRevokeObjectURL_CalledOnlyAfterClickAndTimeout', () => {
    serializeAndDownload([{ k: 1 }], 'xx.csv');
    expect(window.URL.revokeObjectURL).not.toHaveBeenCalled();
    jest.advanceTimersByTime(500);
    expect(window.URL.revokeObjectURL).toHaveBeenCalled();
  });

  test('testLargeArray_Performance_SuccessfulBlobCall', () => {
    // Note: Large structure, but not actual performance. Ensures no stack errors and blob call
    const data = Array.from({ length: 1000 }, (_, i) => ({ a: i, b: String(i) }));
    serializeAndDownload(data, 'large.csv', 'csv');
    expect(blobSpy).toHaveBeenCalled();
    expect(clickSpy).toHaveBeenCalled();
  });

  test('testIllegalFormat_FallsBackToCSV', () => {
    serializeAndDownload([{ x: 1 }], 'fallback.csv', 'BAD_FORMAT');
    // Should export as CSV
    const expected = 'x\r\n"1"';
    expect(blobSpy).toHaveBeenCalledWith([expected], { type: 'text/csv' });
    expect(clickSpy).toHaveBeenCalled();
  });

  test('testDownload_DocumentAppendAndRemove_Called', () => {
    serializeAndDownload([{ z: 99 }], 'foo.csv');
    expect(appendChildSpy).toHaveBeenCalled();
    jest.runAllTimers();
    expect(removeSpy).toHaveBeenCalled();
  });

  // Security test: ensure injected code isn't run; this just ensures download is safe (XSS mitigated by download attribute)
  test('testSecurity_InputInjection_SafeDownload', () => {
    const data = [{ x: '<script>alert(1)</script>', y: 'safe' }];
    serializeAndDownload(data, 'xss.csv', 'csv');
    // Just verifies literal output, not eval
    const expected = 'x,y\r\n"<script>alert(1)</script>","safe"';
    expect(blobSpy).toHaveBeenCalledWith([expected], { type: 'text/csv' });
    expect(clickSpy).toHaveBeenCalled();
  });

  // Negative test: Should not throw on null or undefined data (graceful empty csv)
  test('testNullOrUndefinedData_HandledGracefully', () => {
    expect(() => serializeAndDownload(null, 'null.csv', 'csv')).not.toThrow();
    expect(blobSpy).toHaveBeenCalledWith([''], { type: 'text/csv' });
    expect(() => serializeAndDownload(undefined, 'undef.csv')).not.toThrow();
    expect(blobSpy).toHaveBeenCalledWith([''], { type: 'text/csv' });
  });
});