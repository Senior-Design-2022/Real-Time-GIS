
// popup data table on marker click
export function clickMarker(e){
    var marker = e.target
    console.log("The id of this target is " + marker.CoT_Data.id)
    console.log(marker.CoT_Data)
    console.log(this)
    // alert(this.getLatLng())
}
