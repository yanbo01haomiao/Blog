# 可扩展的Node.js

## 前言

可以说Node.js是生而为分布式的.这一点从他的名字也可见一斑。对于现在来说，任何一个稍有点体量的Web应用，都不可能是一个简单的单体应用，对于Node.js这样的单线程应用来说就更是如此。（传统的多线程应用可以利用开启多线程的方式来较为充分地利用服务器的CPU和内存等资源，而Node.js是单线程的只能利用单核，以及在64位机器上有大概1.7GB的内存限制），所以不管是为了承担更多的负载，还是为了容灾，我们都需要利用具有扩展性的解决方案来部署Node.js应用。

## 可扩展性的三个维度

在Martin L. Abbott和Michael T. Fisher的书《The Art of Scalability》中提出了一个模型scale cube，从三个维度中来介绍可扩展性

- X-axis: Cloning
- Y-axis: Decomposing by Service/Functionality
- Z-axis: Splitting by data partition

简单解释一下的话，我们对于一个传统的单体应用，他所处理的请求是有限的。可能大概每秒可以处理100个请求。（当然这一点对于具体的应用来讲差异非常大）很明显这样的负载是远远不够的。遇到这样的情况我们就需要扩展该应用。考虑到开发成本，最简单高效地就是沿X轴扩展，克隆n个该应用的副本，然后使用一定的策略，让每个应用去承担1/n的工作负载。同时我们也能沿Y轴扩展，将我们的服务按照不同的功能划分为不同的应用，诸如划分出单独的认证服务器，静态资源服务器，还有提供不同范畴的业务API服务器等等，微服务架构就是这种扩展的典型应用。最后一个维度就是从沿Z轴扩展，这种扩展主要会用在数据库，比如针对不同地区国家的人，或者使用hash table将用户做划分。让他们去访问不同实例的web应用，可能数据库也是分块的。一般情况下，Z轴应该在X和Y轴之后考虑。

## X：Cloning & Load Balancing

关于沿X轴扩展，也有有很多不同的解决方案...

### cluster module

讲到Node.js的可扩展性，就不得不提cluster这个核心模块，Node.js底层提供了这个模块，其实也从另一个角度说明了Node是生而为分布式的哈哈。

为了介绍cluster还是举个非常简单的例子，还是Hello World Server
```js
// app.js
const http = require('http')
const pid = process.pid

http.createServer((req, res) => {
    for(let i =1e7; i>0; i--) {} //模拟请求的处理时长
    console.log(`Handling Requesr From ${pid}`)
    res.end(`Hello World From ${pid}`)
}).listen(8080, ()=>{
    console.log(`Started Server ${pid}`)
})
```
我们在这里可以使用[siege](https://github.com/JoeDog/siege)这个工具来测试应用的负载
```bash
siege -c200 -t10s http://localhost:8080
```
在4核CPU下经测试的大概结果就是该应用可以在每秒处理90个请求，CPU利用率仅有20%。很明显，如果没有cluster，这将是Node.js的硬伤所在

利用cluster来cloning十分简单，下面是一个示例代码
```js
// clusteredApp.js
const cluster = require('cluster')
const os = require('os')

if(cluster.isMaster) {
    const cpus = os.cpus().length
    console.log(`Clustering to ${cpus} CPUs`)
    for(let i=0; i<cpus; i++){
        cluster.fork();
    }
} else {
    require('./app')
}
```
大概就是我们第一次启动clusteredApp的时候，cluster.isMaster会是true，执行cluster.fork()时cluster.isMaster变成了false,所以执行了工作线程app.js。大概如下图所示，其中Node.js在MasterProcess实现了一个round robin负载均衡算法，来将请求分配给不同的Worker Process

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/masterworker.png)

当我们再次使用`siege -c200 -t10s http://locahost:8080`来测试使用了cluster的web服务时，可以看到处理并发请求的能力达到了每秒270次，CPU利用率达到了90%.我们可以看到在这里，Node使用了fork出多个进程的方式来提高了对CPU和内存的使用率，弥补了相对于传统像JAVA之类的多线程Web服务的劣势。

另外我们也可以很容易地实现容灾的需求，一方面是当某个服务挂掉之后我们可以将请求分配给还存活的服务，另一方面我们可以通过监控进程来实现进程的重启。如下：
```js
// clusteredApp.js
// ...
   if(cluster.isMaster) {
       // ...
       cluster.on('exit', (worker, code)=>{
           if(code !=0 && !worker.suicide) {
               console.log('Work crashed，Starting a new Worker');
               cluster.fork();
           }
       })
   } else {
       require('./app')
   }
```
当我们的进程服务因为故障down掉之后，我们可以很快开启一个新的进程来替代他。

- 在实际的生产环境中我们会使用一些工具来实现上面的逻辑，比如基于cluster的[pm2](https://github.com/Unitech/pm2)。提供了包括但不限于load balancing(负载均衡)、process monitoring(进程监控)、zero-downtime restarts(无损重启)等功能。 

- dealing with stateful communcations

使用cluster的一个很大的麻烦之处在于，对于处理有状态的连接，比如说状态存储于内存或者硬盘里，这些状态是不会在实例之间共享的。对于每个Node.js实例，属于不同的进程，都有自己不同的上下文，包括global啊，还有require的模块之类的都是各自独立的。而不像Java，在多线程之间是可以共享一部分状态的。

对于此的解决方法通常是不要把状态存储在本机的内存或者硬盘里，而应该让不同的实例都去增删改查一个公共的数据库，或者更好的方式是使用Redis和Memcached这样的内存存储。当然这或许就得对现有的代码进行改造

还有一种解决方法称作Sticky load balancing，大概就是在负载均衡器上，根据不同的用户（例如SessionId）将他们的请求分配到特定的服务上，这样每次该用户都会访问特定的服务器，就保证了该服务器存有用户上一次请求的状态。当然这样也就牺牲了我们服务的容错性。当某一台服务down掉之后，就会有一部分用户无法访问服务。

### reverse proxy

除了cluster模块，沿X轴扩展Nodejs web 应用还有一个选择就是使用反向代理服务器。这是一个比较传统的技术。但是依然十分实用。

大概就是所有的客户端请求，会先经过反向代理服务器，然后由反向代理服务器来做负载均衡，把请求转发给业务服务器，然后当得到业务请求的响应时，再将响应转发给客户端。

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/reverseproxy.png)

这个反向代理服务器所起的作用和cluster的master process有点类似，不同之处主要在于，使用reverse proxy时，Node.js实例监听不同的端口，同时可能运行在不同的机器上。一些流行的反向代理服务器一般都会提供上面说得sticky load balancing的功能。同时反向代理服务器是语言无关的，不仅限于Node.js 服务。我们在负载均衡算法的选择上也不仅限于cluster模块的round robin算法。同时反向代理服务器还可能提供URL重写，缓存，静态资源服务器之类的功能。

- 我们应当意识到，反向代理服务器本质上和cluster不是正邪对立的，甚至他们不是一个层面上的东西，只是在某些功能上有所重复，我们其实也可以很好地将二者结合。我们使用cluster来对Node.js做垂直维度上的扩展，也就是在一台机器上fork多个进程，充分利用服务器的CPU、内存资源。同时我们使用代理服务器来对Node.js进行水平维度的扩展，也就是将应用分布在多台服务器上。使用代理服务器来做反向代理将请求转发到不同服务器上的Node.js节点。

我们以nginx为例，来简单看一下nignx的使用。首先是编写nginx.conf配置文件：
```conf
// 具体详细配置查看nginx文档
http {
   upstream node_demo_app {
       server 127.0.0.1: 8081;
       server 127.0.0.1: 8082;
       server 127.0.0.1: 8083;
       server 127.0.0.1: 8084;
       server 192.168.130.66: 8081;
   } 
   server {
       listen 80;

       location / {
           proxy_pass http://node_demo_app;
       }
   }
}
```
配置文件本身也简洁明了，之后使用`nginx -s reload`重载配置文件，完事。
我们访问`http://localhost`（http默认是80端口）即可访问到我们真实的服务。

### service registry

动态去为应用程序扩容和缩容（dynamic scaling）也是一件很有意义地事，对于云计算服务商，这可以很有效地节约成本。同时也很有实用性。用户访问暴增时就扩容以承担更多的用户请求，到深夜就缩容以节约成本。这样的实现想想就觉得十分美妙。实现这个美妙的想法的一个策略叫做service registry。

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/serviceregistry.png)

service registry除了让负载均衡服务器可以清晰地看到我们的服务实时的运行实例以外，还能对服务进行分类等等。为了启用service registry我们可能需要到nginx官网再看看相关的配置然后重启我们的nginx服务。

为学习而言，我们也可以使用Node.js来实现一个包含service registry的，我们自己的“简陋nginx”。

```js
// 业务服务的代码
const http = require('http');
const pid = process.pid;
const consul = require('consul')();
const portfinder = require('portfinder');
const serviceType = process.argv[2];

portfinder.getPort((err, port) => {        // [1]  
  const serviceId = serviceType+port;  consul.agent.service.register({ // [2]    
    id: serviceId,    
    name: serviceType,    
    address: 'localhost',    
    port: port,    
    tags: [serviceType]  
  }, () => { 
    const unregisterService = (err) => {   // [3]     
      consul.agent.service.deregister(serviceId, () => {  
        process.exit(err  1 : 0);      
      });    
    };    
    process.on('exit', unregisterService); // [4]    
    process.on('SIGINT', unregisterService);    
    process.on('uncaughtException', unregisterService);   
    http.createServer((req, res) => {      // [5]  
    //具体业务    
      for (let i = 1e7; i> 0; i--) {}      
      console.log(`Handling request from ${pid}`);      
      res.end(`${serviceType} response from ${pid}\n`);    
    }).listen(port, () => {     
         console.log(`Started ${serviceType} (${pid}) on port ${port}`);   
     });  
    });
});
```
这里的代码大概就是实现了一个在启动服务之前，将服务通过consul提供的API做service registry以及当服务down掉或者我们主动关闭之后的unregistry之类的逻辑。portfinder主要的作用在于找到可用的端口。这里我们也利用了serviceType对服务做了分类

至于负载均衡服务器：
```js
const routing = [{
  path: '/api',
  service: 'api-service',
  index: 0
}, {
  path: '/',
  service: 'webapp-service',
  index: 0
}];

const proxy = httpProxy.createProxyServer({});
http.createServer((req, res) => {
  let route;
  routing.some(entry => {
    route = entry;
    //Starts with the route path?
    return req.url.indexOf(route.path) === 0;
  });

  consul.agent.service.list((err, services) => {
    const servers = [];
    Object.keys(services).filter(id => {
      if (services[id].Tags.indexOf(route.service) > -1) {
        servers.push(`http://${services[id].Address}:${services[id].Port}`)
      }
    });

    if (!servers.length) {
      res.writeHead(502);
      return res.end('Bad gateway');
    }

    route.index = (route.index + 1) % servers.length;
    proxy.web(req, res, {target: servers[route.index]});
  });
}).listen(8080, () => console.log('Load balancer started on port 8080'));
```
## Y: Decomposing by Service/Functionality

除了沿X轴扩展这种看起来比较简单粗暴有效的扩展方式。我们还可以通过对Web应用按照功能模块进行解耦。这种方式不仅可以有效地使我们的服务具有可扩展的能力。同时也化解了逻辑较为复杂的单体应用的复杂性。

### Monolithic architecture

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/monoarch.png)

这是一个典型的单体应用结构图，单体应用的结构一般也是模块化的。然而这里的每个模块都是整体的一部分，是作为应用的一部分运行的。所以应用里的每个组件/模块如果崩溃，例如说抛出了一个uncaught exception，就将会导致整个应用的崩溃。
另外，单体应用的模块间一般是高耦合的，这会在应用的迭代和扩展中逐渐变得难以维护。当然单体应用也不是毫无优势，通常来说单体应用模块间的互相调用是轻而易举的。

### Microservice architecture

微服务是一种现在非常流行的构建大型Web应用的架构。相比于单体应用，微服务将一个单体应用按不同的服务/功能划分成许多不同的模块，各自独立部署。从程序本身提高了Web应用的可扩展性。相比于单体应用而言，微服务结构的某个模块崩溃将不会导致整体应用的崩溃。只会影响到模块本身，以及需要依赖该模块的模块接口。同时根据经验，当模块本身提供的功能是高内聚的，并且专注于一处的，则每个模块服务本身将是可单独扩展（这里的模块在实际上就是一个Node.js应用，只不过提供的功能相对专一），同时也必然是高可复用的。

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/microarch.png)

微服务体系结构的示意图如上所示，同时Microservice architecture自然也不是完美无缺的，一个公认的挑战就是如何去链接每一个单独的微服务。微服务体系结构的集成策略应该怎么样做？

- API Proxy（API Gateway）
上面说的问题有一个可选的解决方案就是API Proxy。我们先直接看图

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/apiproxy.png)

这里的API Proxy的作用和我们上面使用http-proxy以及consul所实现的“简陋nginx”有一些相同之处。大致上这个API Proxy的作用如下：

1. 映射请求，可能是不同的URL path到不同的Service 服务节点上。
2. 为服务节点做负载均衡，将请求转发到提供同样Service的不同服务节点上。

- API orchestration

这个解决方案是Netflix的VP Daniel Jacobson在设计Netflix API时发布在他的博客上的。

大致的逻辑就是在前端工程的调用和服务接口的提供之间多了一层名为API Orchestrator。

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/apiorch.png)

以上图为例，举个具体的例子。假设用户在前端页面点击了【购买】这个按钮，那么直接请求的将是completeCheckout()这个接口，这个接口首先去调用一个结账相关的checkoutService/pay的接口这个接口可能完成支付的功能。之后再去调用购物车相关的cartService/delete接口，将这些已经结完账的物品从购物车里删除。最后再去调用产品库存相关的productsService/update，更新产品的库存。

- message broker

上面讲的API orchestration这种解决方案看起来很美妙，但是实际上也存在着一些显而易见的问题。中间API Orchestrator是一种被称为God Object的反模式。我们在编写API Orchestrator显然是需要知道所有底层Service的一些具体接口的情况，同时这也会导致这一层的高耦合低内聚。

当我们从刚开始讨论微服务的集成策略到现在为止，一直在避免的一个方式就是业务服务节点之间的互相调用，例如在上面的购物流程中，我们在CheckoutService里直接去调用CartService这样的实现方式。我想几乎不用多说，这样的业务服务之间的互相调用，将会在我们的系统结构迭代的过程中变得极为复杂，和难以维护，模块间的耦合也将变得非常强。

message broker是一种允许我们实现中心化的发布/订阅模式，同时也是观察者模式在分布式系统中的一种最佳实践。

我们来看看message broker的示意图：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-scalability/messagebroker.png)

对于同样的一个购物的流程，现在我们的前端直接调用结账相关的checkoutService/pay接口，这时候该接口在处理完请求后，emit一个`purchased`事件，而与购物车相关的cartService业务服务节点，和与库存相关的productService业务服务节点分别去监听`purchased`事件，当事件触发时，则执行类似清空购物车，更新库存这样的业务逻辑。message broker的解决方案听起来也十分美妙，但是同样也有一些问题有待解决，例如维持消息队列，以及保证消息触发的顺序等等，这些在《Nodejs Design Pattern 2th》的chapter 11会有更加详细的阐述

## Z: Splitting by data partition

《Nodejs Design Pattern 2th》这本书没有具体介绍Z轴上扩展的方式，我们姑且任务，对于大多数Web应用只要做好了X轴和Y轴的扩展或许已经足够了。但是鉴于母校“止于至善”的校训（其实是强迫症），我在这里还是将Z轴的标题加上。当我们的应用程序完美地实现了X、Y轴的扩展之后，或许我们可以在数据的分块上做文章。关于这一点怎么做，还是另请高明把。