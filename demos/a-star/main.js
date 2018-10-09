const fs = require('fs')
const UGraph = require('./ugraph')
const Node = require('./node')
const nodes = require('./nodes.json')
const astar = require('./astar')

let ugraph = new UGraph()
for(let flag of Object.keys(nodes)) {
    let node = new Node(flag, nodes[flag][0], nodes[flag][1])
    ugraph.addNode(node)
}

let text = fs.readFileSync('./road.txt', 'utf-8')

const edgepattern = /e\s(\d+)\s(\d+)/g

let edge = edgepattern.exec(text)
while(edge){
    ugraph.addEdge(edge[1],edge[2])
    edge = edgepattern.exec(text)
}

// 至此ugraph数据已经装填完成

let start = 10;
let end = 15

let path = astar.search(ugraph, ugraph.nodes[start], ugraph.nodes[end])

let pathStr = path.map(node=>{
    return node.flag
}).join(' -> ')

let pathLong = path[path.length-1].f
console.log(`路径为${start} -> ${pathStr}，全程距离为 ${pathLong}`)
