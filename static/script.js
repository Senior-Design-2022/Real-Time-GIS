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
    'a-f-A-C' : 'static/images/FRD_AIR.png',
    'a-f-G-C' : 'static/images/FRD_GND.png',
    'a-f-S-C' : 'static/images/FRD_SEASURFACE.png',
    'a-f-U-C' : 'static/images/FRD_SUB.png',
    'a-h-A-C' : 'static/images/HOS_AIR.png',
    'a-h-G-C' : 'static/images/HOS_GND.png',
    'a-h-U-C' : 'static/images/HOS_SUB.png',
    // 'a-h-S-C' : 'static/images/HOS_SEASURFACE.svg.png' dont have hostile sea yet,
    'a-n-A-C' : 'static/images/NEU_AIR.png',
    'a-n-G-C' : 'static/images/NEU_GND.png',
    'a-n-U-C' : 'static/images/NEU.png',
    'a-u-A-C' : 'static/images/UNK_AIR.png',
    'a-u-G-C' : 'static/images/UNK_GND.png',
    'a-u-U-C' : 'static/images/UNK_SUB.png',
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
                iconUrl: icons[cot.type],
                iconAnchor: [18, 41],
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
                iconUrl: icons[cot.type],
                iconAnchor: [18, 41],
                popupAnchor: [1, -34]
            })}).addTo(map).bindPopup(cot.uid); 
            var newMarkerLayer = L.layerGroup().addLayer(marker).addTo(map); // create layer group for markers on this line
            markerLayers.set(cot.uid, newMarkerLayer); // add the new layer group to our map
            var markersArray = [];
            var clickedArray = [];
            markersArray.push(marker);
            markerArrays[cot.uid] = (markersArray, clickedArray);
            layerControl.addOverlay(newMarkerLayer, cot.uid); // add the layer to the layer control as an overlay layer
            map.removeLayer(marker)
        }
    }
});

L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
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
    let filepath = document.getElementById('replay-file').value;
    let speed = document.getElementById('replay-speed').value;
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

// Changes the background of the map -- requires internet connection
async function changeMapBackground() {
    /*
        current options are:
        satellite-day
        leaflet-default
        street-light
        street-dark
    */
    let selection = document.getElementById('online-map-selection').value;
    let mapUrl, properties;

    //can add more maps here
    //source used: http://leaflet-extras.github.io/leaflet-providers/preview/index.html
    switch (selection) {
        case "satellite-day":
            mapUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
            properties = {
                attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                maxZoom: 19
            }
            break;
        case "leaflet-default":
            mapUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
            properties = {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }
            break;
        case "street-light":
            mapUrl = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png';
            properties = {
                attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
                maxZoom: 19
            }
            break;
        case "street-dark":
            mapUrl = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png';
            properties = {
                attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
                maxZoom: 19
            }
            break;
        default:
            //something went wrong
            return;
    }

    console.log(`changing map to ${mapUrl}`);

    L.tileLayer(mapUrl, properties).addTo(map);

    return;
}

// Gets the filenames of all the overlays in the static/overlays folder
// and populates the dropdown accordingly
async function getOverlays() {
    // get the files from the backend route which gives us a list of filenames
    // in the overlays folder
    let files = await fetch(backendUrl + '/getoverlays', {method: "GET"})
    .then(function parse(response) {
        return response.json();
    });

    // get the html dropdown
    let overlaySelector = document.getElementById('overlay-selection');

    // clear out the dropdown
    overlaySelector.innerHTML = '';

    // for each of the overlays, add an option to the dropdown
    files.forEach(
        file => {
            var option = document.createElement('option');
            option.value = file;
            option.text = file;
            overlaySelector.appendChild(option);
        }
    )
}

// Gets the current selected overlay from the overlays dropdown
// and adds that overlay to the map.
async function addOverlay() {
    // get the filename of the overlay we want to add
    let overlay_filename = document.getElementById('overlay-selection').value;

    // Load kml file
    fetch('static/overlays/' + overlay_filename)
    .then(res => res.text())
    .then(kmltext => {
        // Create new kml overlay
        const parser = new DOMParser();
        const kml = parser.parseFromString(kmltext, 'text/xml');
        const track = new L.KML(kml);
        map.addLayer(track);

        // Adjust map to show the kml
        const bounds = track.getBounds();
        map.fitBounds(bounds);
    });
}

let selected = "";

function openMenuItem(id) {

    let items = document.getElementsByClassName("menu-options");
    // hide all elements before showing selection
    for (let i = 0; i < items.length; i++) {
        items[i].hidden = true;
    }

    if (selected !== id) {
        document.getElementById(id).hidden = false;
        selected = id;
    } else {
        selected = "";
    }
}