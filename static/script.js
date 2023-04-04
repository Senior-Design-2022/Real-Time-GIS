// url to make call to backend flask app
const backendUrl = 'http://' + location.host;

//create map
var map = L.map('map').setView([40.745152, -74.024345], 13);
var layerControl = L.control.layers().addTo(map); // add the layer control to the map for hiding markers

//create map for tracking multiple targets
const targets = new Map();
const markerLayers = new Map(); // keeps track of the layers added for each path

const showMarkers = true; //just in case they get overwhelming, can stop markers from being added

// generates a random color for each new path
function generate_random_color() {
    let r = Math.floor(Math.random() * 255);
    let g = Math.floor(Math.random() * 255);
    let b = Math.floor(Math.random() * 255);
    return `rgb(${r},${g},${b})`;
}
var markerArrays = {} // will hold the arrays of each path's markers to manage how many we would like to display at a time

icons = {
    'a-f-A-C' : 'static/images/FRD_AIR.svg.png',
    'a-f-G-C' : 'static/images/FRD_GND.svg.png',
    'a-f-S-C' : 'static/images/FRD_SEASURFACE.svg.png',
    'a-f-U-C' : 'static/images/FRD_SUB.svg.png',
    'a-h-A-C' : 'static/images/HOS_AIR.svg.png',
    'a-h-G-C' : 'static/images/HOS_GND.svg.png',
    'a-h-U-C' : 'static/images/HOS_SUB.svg.png',
    // 'a-h-S-C' : 'static/images/HOS_SEASURFACE.svg.png' dont have hostile sea yet,
    'a-n-A-C' : 'static/images/NEU_AIR.svg.png',
    'a-n-G-C' : 'static/images/NEU_GND.svg.png',
    'a-n-U-C' : 'static/images/NEU.svg.png',
    'a-u-A-C' : 'static/images/UNK_AIR.svg.png',
    'a-u-G-C' : 'static/images/UNK_GND.svg.png',
    'a-u-U-C' : 'static/images/UNK_SUB.svg.png',
}

//init socket
const socket = new WebSocket('ws://' + location.host + '/feed');
//listen for a message from the server
socket.addEventListener('message', e => {
    console.log(e.data);
    const cot = JSON.parse(e.data);
    if(cot.uid !== '') {

        if (targets.has(cot.uid)) { //if this target is already in the map
            //append data to path
            targets.get(cot.uid).addLatLng([cot.lat, cot.lon]); //add point to path
            // create marker for that point
            var marker = L.marker([cot.lat, cot.lon], {icon: L.icon({
                iconUrl: "static/images/HOS_AIR.svg.png", // icons[cot.type]
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            })}).bindPopup(cot.uid).addTo(map);
            
            markerArrays[cot.uid].push(marker);
            // get the layer group for the markers of this path
            var layerGroup = markerLayers.get(cot.uid);
            if(markerArrays[cot.uid].length > 1) { // checks if markers array has more than 5 values, if so, remove oldest
                var oldestMarker = markerArrays[cot.uid].shift();
                layerGroup.removeLayer(oldestMarker)
            }

            layerGroup.addLayer(marker); // add the new marker to the layer group
            path.on('click', function(e) {
                // Display an alert with the message "You clicked on the path!"
                var clickedLatLng = e.latlng;
                var popup = L.popup()
                .setLatLng(clickedLatLng)
                .setContent(cot.uid)
                .openOn(map);
            });
        } else { //if the target is not in the map yet
            //create path and append data to new path
            console.log(`New target [${cot.uid}] now being tracked.`);
            var path = L.polyline([], {color: generate_random_color()})
            path.on('click', function(e) {
                // Display an alert with the message "You clicked on the path!"
                var clickedLatLng = e.latlng;
                var popup = L.popup()
                .setLatLng(clickedLatLng)
                .setContent(cot.uid)
                .openOn(map);
            });
            targets.set(cot.uid, path.addTo(map)); //create line
            targets.get(cot.uid).addLatLng([cot.lat, cot.lon]); //add point
            
            // create new marker and layer group
            // create marker for the point
            var marker = L.marker([cot.lat, cot.lon], {icon: L.icon({
                iconUrl: "static/images/HOS_AIR.svg.png",
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            })}).addTo(map).bindPopup(cot.uid); 
            var newMarkerLayer = L.layerGroup().addLayer(marker).addTo(map); // create layer group for markers on this line
            markerLayers.set(cot.uid, newMarkerLayer); // add the new layer group to our map
            var markersArray = [];
            var clickedArray = [];
            markersArray.push(marker);
            markerArrays[cot.uid] = (markersArray, clickedArray);
            layerControl.addOverlay(newMarkerLayer, cot.uid); // add the layer to the layer control as an overlay layer
        }
    }
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);


// send a request to start recording the input feed
async function startRecording() {
    //make http request
    /**
     * 
     * TODO: ERROR CHECK HERE IF HTTP REQUEST COMES BACK AS FAILED
     * i.e. IF IT'S ALREADY RECORDING, CHANGE THE BUTTON TO REFLECT
     * THAT AND DO NOTHING
     * 
     */
    document.getElementById("start-recording-button").hidden = true;
    document.getElementById("stop-recording-button").hidden = false;
    fetch(backendUrl + '/recording/start', {method: "GET"});
}

// send a request to stop recording the input feed
async function stopRecording() {
    //make http request
    document.getElementById("stop-recording-button").hidden = true;
    document.getElementById("start-recording-button").hidden = false;
    fetch(backendUrl + '/recording/stop', {method: "GET"});
}

// send a request to start a replay
// this will send JUST name of the file
async function requestReplay() {
    filepath = document.getElementById('replay-file').value;
    speed = document.getElementById('replay-speed').value;
    console.log(filepath);
    if (!filepath) return "Error: must select a file"; //make sure they selected something

    filename = filepath.substring(filepath.lastIndexOf("\\") + 1)

    const response = await fetch(backendUrl + '/replay', {
        method: "POST",
        body: JSON.stringify({
            path: filename,
            speed: speed
        }),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "Accept": "application/json"
        }
    });
    console.log(response);
    return "Success" // TODO: recieve the json coming back in the response
}