var map = L.map('map').setView([40.745152, -74.024345], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

//
// basic marker
//

markers = [
    {
        'lat':40.745152,
        'lon':-74.024345,
        'popup':'Quack'
    }
]

for (marker of markers) {
    console.log(marker)
    L.marker([marker.lat, marker.lon]).addTo(map)
    .bindPopup(marker.popup)
    .openPopup();
}

//
// creating a path
//

latlngs = [
    [40.742029, -74.028380],
    [40.745784, -74.027226],
    [40.745602, -74.026211],
    [40.747672, -74.025585],
    [40.747335, -74.023922],
    [40.745689, -74.023209],
    [40.744230, -74.023574],
    [40.742885, -74.025838],
    [40.741759, -74.026562]
]
var polyline = L.polyline(latlngs, {color: 'red'}).addTo(map);
map.fitBounds(polyline.getBounds());


    
