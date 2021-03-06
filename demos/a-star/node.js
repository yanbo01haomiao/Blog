function GridNode(flag, lng, lat) {
    this.flag = flag;
    this.lng = lng;
    this.lat = lat;
    this.f = 0;
    this.g = 0;
    this.h = 0;
    this.visited = false;
    this.closed = false;
    this.parent = null;
}
function toRad(d) {
    return d * Math.PI / 180;
}

function getDisance(lat1, lng1, lat2, lng2) {
    // lat为纬度, lng为经度, 一定不要弄错
    var dis = 0;
    var radLat1 = toRad(lat1);
    var radLat2 = toRad(lat2);
    var deltaLat = radLat1 - radLat2;
    var deltaLng = toRad(lng1) - toRad(lng2);
    var dis = 2 * Math.asin(Math.sqrt(Math.pow(Math.sin(deltaLat / 2), 2) + Math.cos(radLat1) * Math.cos(radLat2)
        * Math.pow(Math.sin(deltaLng / 2), 2)));
    return dis * 6378137;
}
GridNode.prototype.getCost = function (fromNeighbor) {
    return getDisance(this.lat, this.lng, fromNeighbor.lat, fromNeighbor.lng)
};

module.exports = GridNode;
