// Decode an uplink message from a buffer
// payload - array of bytes
// metadata - key/value object

/** Decoder **/

// decode payload to string
var payloadStr = decodeToString(payload);
// decode payload to JSON
var data = decodeToJson(payload);
var deviceData = hexToBytes(data.data);

// use assetName and assetType instead of deviceName and deviceType
// to automatically create assets instead of devices.
// var assetName = 'Asset A';
// var assetType = 'building';

// Result object with device/asset attributes/telemetry data
if(deviceData[0] == 0x01){
    var result = {
    // Use deviceName and deviceType or assetName and assetType, but not both.
       deviceName: "IoTBoatTracker",
       deviceType: "Lol",
    // assetName: assetName,
    // assetType: assetType,
       attributes: {
           model: 'Model 1',
           serialNumber: 'SN1337',
           integrationName: metadata['integrationName']
       },
       telemetry: {
            lat: bytesToFloat([ deviceData[1], deviceData[2], deviceData[3], deviceData[4]]),
            lon: bytesToFloat([ deviceData[5], deviceData[6], deviceData[7], deviceData[8]]),
            speed: byteArrayToInt([deviceData[9], deviceData[10]]),
       }
    };
}

if(deviceData[0] == 0x02){
    var result = {
    // Use deviceName and deviceType or assetName and assetType, but not both.
       deviceName: "IoTBoatTracker",
       deviceType: "Lol",
    // assetName: assetName,
    // assetType: assetType,
       attributes: {
           model: 'Model 1',
           serialNumber: 'SN1337',
           integrationName: metadata['integrationName']
       },
       telemetry: {
            x: bytesToFloat([ deviceData[1], deviceData[2], deviceData[3], deviceData[4]]),
            y: bytesToFloat([ deviceData[5], deviceData[6], deviceData[7], deviceData[8]]),
            temp: byteArrayToInt([deviceData[9], deviceData[10]]),
       }
    };
}

if(deviceData[0] == 0x03){
    var result = {
    // Use deviceName and deviceType or assetName and assetType, but not both.
       deviceName: "IoTBoatTracker",
       deviceType: "Lol",
    // assetName: assetName,
    // assetType: assetType,
       attributes: {
           model: 'Model 1',
           serialNumber: 'SN1337',
           integrationName: metadata['integrationName']
       },
       telemetry: {
            z: bytesToFloat([ deviceData[1], deviceData[2], deviceData[3], deviceData[4]]),
            alt: bytesToFloat([ deviceData[5], deviceData[6], deviceData[7], deviceData[8]]),
            battvM: byteArrayToInt([deviceData[9], deviceData[10]])/10,
       }
    };
}

/** Helper functions **/

function decodeToString(payload) {
   return String.fromCharCode.apply(String, payload);
}

function decodeToJson(payload) {
   // covert payload to string.
   var str = decodeToString(payload);

   // parse string to JSON
   var data = JSON.parse(str);
   return data;
}

function hexToBytes(hex){
    for(var bytes = [], c = 0; c < hex.length; c += 2)
        bytes.push(parseInt(hex.substr(c,2), 16));
    return bytes
}

function bytesToFloat(byteArray){
    var buf = new ArrayBuffer(4);
    // Create a data view of it
    var view = new DataView(buf);
    
    // set bytes
    byteArray.forEach(function (b, i) {
        view.setUint8(i, b);
    });
    
    // Read the bits as a float; note that by doing this, we're implicitly
    // converting it from a 32-bit float into JavaScript's native 64-bit double
    return view.getFloat32(0);
}

function byteArrayToInt(byteArray) {
    var value = 0;
    for (var i = byteArray.length - 1; i >= 0; i--) {
        value = (value * 256) + byteArray[i];
    }
    return value;
}

return result;
