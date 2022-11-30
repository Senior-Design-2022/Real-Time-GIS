//create map
var map = L.map('map').setView([40.745152, -74.024345], 13);

//create map for tracking multiple targets
const targets = new Map();

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
var lastMarker = null
//listen for a message from the server
socket.addEventListener('message', e => {
    console.log(e.data);
    const cot = JSON.parse(e.data);
    if(cot.id !== '') {

        if (targets.has(cot.id)) { //if this target is already in the map
            const lastCoT = targets.get(cot.id)._latlngs.slice(-1)[0]

            //append data to path
            targets.get(cot.id).addLatLng([cot.lat, cot.lon]); //add point

            if (showMarkers) {

                if (lastMarker != null){ // remove previous markers
                    map.removeLayer(lastMarker)
                }

                lastMarker = new L.Marker([cot.lat, cot.lon])
                map.addLayer(lastMarker)
                lastMarker.bindPopup(cot.id).openPopup()

            }

        } else { //if the target is not in the map yet
            //create path and append data to new path
            console.log(`New target [${cot.id}] now being tracked.`);
            targets.set(cot.id, L.polyline([], {color: generate_random_color()}).addTo(map)); //create line
            targets.get(cot.id).addLatLng([cot.lat, cot.lon]); //add point
            
            if (showMarkers) {
                lastMarker = new L.Marker([cot.lat, cot.lon])
                map.addLayer(lastMarker)
                lastMarker.bindPopup(cot.id).openPopup()
            }
        }
    }
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);