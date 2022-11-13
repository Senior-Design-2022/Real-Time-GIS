//create map
var map = L.map('map').setView([40.745152, -74.024345], 13);

//create map for tracking multiple targets
const targets = new Map(); // TODO

let test_line_points = [];
let test_line = L.polyline(test_line_points).addTo(map);

//init socket
const socket = new WebSocket('ws://' + location.host + '/feed');
//listen for a message from the server
socket.addEventListener('message', e => {
    console.log(e.data);
    const cot = JSON.parse(e.data);
    if(cot.id !== '') {
        console.log('creating marker...');
        L.marker([cot.lat, cot.lon]).addTo(map)
            .bindPopup(cot.id)
            .openPopup();
        test_line.addLatLng([cot.lat, cot.lon]);   
    }
});

L.tileLayer('/static/tiles/{z}/{x}/{y}.jpg', {
    maxZoom: 18,
    minZoom: 12,
    attribution: '&copy;'
    }).addTo(map);