# 启发式搜索-Astar搜寻算法

## 三言两语讲Astar算法

首先用不太严谨，但是可以基本上概括的整个算法基本思路地讲下Astar算法。网络上已经有很多用类似2d游戏地图的方格来讲解了，我们这里因为题目的要求是无向图，因此就用无向图来讲，实际上和2d游戏地图的方格差不离。

考虑如下无向图，求从点a到点f的最短路径

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/a-star/graph.png)


首先从a出发，目的地是f，与a相邻的节点有b和c，这时有了两种选择，我们应该走b还是c呢，Astar启发式算法有个公式来做这个抉择

> f = g + h

我们会对b和c两个节点分别计算出一个f值。

比如我们先计算b的这个f值，其中g代表从起点a到当前节点（即b）的代价（移动的距离），这里是20。而h代表从b到目的节点的代价，即预估的移动到目的节点的距离。这里预估的方法是有一个评估函数，例如最常用的为曼哈顿，当然还有像欧几里得距离，切比雪夫距离等等。这里我们采用曼哈顿距离评估函数。从图中可以看出来，Manhattan_Distance(c,f) = Manhattan_Distance(b,f)。这里我随便假设个数字为65。我们可以发现，实际上b到f要走的距离是70，而c到f要走的距离是60，总之都不是65，也不相等。因此，如果使用曼哈顿距离这个评估函数，不能保证所得的是确切的最优解，而只是近似最优解。综上b节点的f值为20 + 65。而c节点的f值为50 + 65。所以我们选择先走b。

> 在平面上，p1点坐标(x1,y1)和p2点坐标(x2,y2)曼哈顿距离为 | x1 - x2 | + | y1 - y2 |

之后的每一次，也都是先找出当前所在点的相邻节点，计算每一个相邻节点的f值，然后选择最小的f值作为下一点，直到走到目的节点位置。为了方便后续寻找路径，每走一步是会将走到的节点的parent属性指向上一个节点。

## 算法具体实现

上面一小结只是简单讲了一下Astar算法的大概思路，忽略了许多具体实现时应该考虑的细节。这一节我通过具体的实现该算法的过程来使得对Astar算法有更清晰具体的认识。
[本教程astar算法源码地址](https://github.com/caistrong/Blog/tree/master/demos/a-star)
### 数据预处理

```js
// javascript处理json数据很容易，直接require
const nodes = require('./nodes.json')

let ugraph = new UGraph()
// 遍历nodes的所有对象然后添加到upgraph里面
for(let flag of Object.keys(nodes)) {
    let node = new Node(flag, nodes[flag][0], nodes[flag][1])
    ugraph.addNode(node)
}
```

```js
// 读取txt文件
let text = fs.readFileSync('./road.txt', 'utf-8')
// txt文件中边的数据的格式
const edgepattern = /e\s(\d+)\s(\d+)/g
// 正则表达式匹配提取边的数据然后插入edges这个数据格式
let edge = edgepattern.exec(text)
while(edge){
    ugraph.addEdge(edge[1],edge[2])
    edge = edgepattern.exec(text)
}
```

### 数据结构

- Node

```js
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
```
查看如下的表格

属性|描述
----|----
flag | 节点的标记、key值，比如a、b这种
lng | 该节点的经度
lat | 该节点的维度
f | 该节点的f值，即g + h
g | 即起点到该节点的移动代价
h | 即该节点到目标节点的预估代价(这里是曼哈顿距离)
visited | 遍历相邻节点时判断是否遍历过的标志
closed | 是否属于关闭集closeset
parent | 上一个节点是谁，便于输出路径

- Graph

```js
var Graph = function () {
    this.nodes = {};
    this.edges = {};
    this.dirtyNodes = [];
};
```

属性|描述
----|----
nodes | 所有的节点
edges | 所有的边
dirtyNodes | 算法中每走一步都得重新计算相邻节点f值，这是一个辅助数组

**nodes数据示例**
```js
nodes: { 
    '11652': {
        flag: '11652',
        lng: 118.08064974999999,
        lat: 24.480862,
        f: 0,
        g: 0,
        h: 0,
        visited: false,
        closed: false,
        parent: null 
    } 
    '173': {
        flag: '173',
        lng: 118.110184,
        lat: 24.496513,
        f: 0,
        g: 0,
        h: 0,
        visited: false,
        closed: false,
        parent: null 
    }
}
```

**edges数据示例**
```js
edges: {
  '11646': [ '11645', '4614' ],
  '11647': [ '3155', '4597' ],
  '11648': [ '4590', '6698' ],
  '11649': [ '4587', '4590' ],
  '11650': [ '4577', '11651' ],
  '11651': [ '11650', '11652' ]
}
```

### 核心算法

```js
// 只截取了重要的步骤，完整源码请看astar.js
var astar = {
    search: function (graph, start, end) {
        graph.cleanDirty();
        var heuristic = astar.heuristics.manhattan; // 选择了曼哈顿评估函数
        var openHeap = getHeap(); // 二叉堆
        start.h = heuristic(start, end); // f = g + h
        graph.markDirty(start); // 评估过了
        openHeap.push(start);
        while (openHeap.size() > 0) {
            // 拿到f值最小的节点以进行下一步，最小堆帮我们保持顺序
            var currentNode = openHeap.pop();
            // 到达终点的情况下：
            if (currentNode === end) {
                return pathTo(currentNode);
            }
            // 还未结束的情况下：
            currentNode.closed = true;
            // 找出所有邻近节点
            var neighbors = graph.neighbors(currentNode);
            for (var i = 0, il = neighbors.length; i < il; ++i) {
                var neighbor = neighbors[i];
                if (neighbor.closed) {
                    // 如果是在关闭集，则跳过这个邻近节点
                    continue;
                }
                // 计算这个邻近节点的g值，其实就是当前节点的g值加上当前节点走向该邻近节点的代价
                var gScore = currentNode.g + neighbor.getCost(currentNode);
                var beenVisited = neighbor.visited;
                if (!beenVisited || gScore < neighbor.g) {
                    // 找到了一个目前为止的最优路径，计算该邻居节点各种值
                    neighbor.visited = true;
                    neighbor.parent = currentNode;
                    neighbor.h = neighbor.h || heuristic(neighbor, end);
                    neighbor.g = gScore;
                    neighbor.f = neighbor.g + neighbor.h;
                    graph.markDirty(neighbor);
                    if (!beenVisited) {
                        // 根据计算出来的邻居节点的f值，将该节点放进最小堆里的合适的位置
                        openHeap.push(neighbor);
                    } else {
                        // 已经检查过该节点了，但是又重复计算f组，这时在最小堆中重新安排他的位置
                        openHeap.rescoreElement(neighbor);
                    }
                }
            }
        }
        // 未找到路径返回空数组
        return [];
    }
};
```

### 运行结果

```js
// main.js里测试例子
let start = 10;
let end = 15

let path = astar.search(ugraph, ugraph.nodes[start], ugraph.nodes[end])

let pathStr = path.map(node=>{
    return node.flag
}).join(' -> ')

let pathLong = path[path.length-1].f
console.log(`路径为${start} -> ${pathStr}，全程距离为 ${pathLong}`)
```
- 运行方式

```bash
node main.js
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/a-star/result.png)