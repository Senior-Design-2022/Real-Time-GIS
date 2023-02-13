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
            var marker = L.circleMarker([cot.lat, cot.lon], {radius: 3, fill: true, fillOpacity: 1.0}).bindPopup(cot.uid); // create marker for that point

            // get the layer group for the markers of this path
            var layerGroup = markerLayers.get(cot.uid);
            layerGroup.addLayer(marker); // add the new marker to the layer group

        } else { //if the target is not in the map yet
            //create path and append data to new path
            console.log(`New target [${cot.uid}] now being tracked.`);
            targets.set(cot.uid, L.polyline([], {color: generate_random_color()}).addTo(map)); //create line
            targets.get(cot.uid).addLatLng([cot.lat, cot.lon]); //add point
            
            // create new marker and layer group
            var marker = L.circleMarker([cot.lat, cot.lon], {radius: 3, fill: true, fillOpacity: 1.0}).addTo(map).bindPopup(cot.uid); // create marker for the point
            var newMarkerLayer = L.layerGroup().addLayer(marker).addTo(map); // create layer group for markers on this line
            markerLayers.set(cot.uid, newMarkerLayer); // add the new layer group to our map

            layerControl.addOverlay(newMarkerLayer, cot.uid); // add the layer to the layer control as an overlay layer
        }
    }
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
