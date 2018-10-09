var Graph = function () {
    this.nodes = {};
    this.edges = {};
    this.dirtyNodes = [];
};

var cleanNode = function (node) {
    node.f = 0;
    node.g = 0;
    node.h = 0;
    node.visited = false;
    node.closed = false;
    node.parent = null;
}

Graph.prototype.cleanDirty = function () {
    for (var i = 0; i < this.dirtyNodes.length; i++) {
        cleanNode(this.dirtyNodes[i]);
    }
    this.dirtyNodes = [];
};

Graph.prototype.markDirty = function (node) {
    this.dirtyNodes.push(node);
};

Graph.prototype.addNode = function (node) {
    this.nodes[node.flag] = node;
};

Graph.prototype.addEdge = function (fromNode, toNode) {
    if (!this.edges[fromNode]) {
        this.edges[fromNode] = [toNode]
    } else {
        this.edges[fromNode].push(toNode)
    }

    if (!this.edges[toNode]) {
        this.edges[toNode] = [fromNode]
    } else {
        this.edges[toNode].push(fromNode)
    }
};

Graph.prototype.forEachNode = function (callback) {
    for (var node in this.nodes) {
        callback(node);
    }
};

Graph.prototype.neighbors = function (node) {
    var flags = this.edges[node.flag];
    var ret = flags.map(flag => {
        return this.nodes[flag]
    })
    return ret;
};

module.exports = Graph