# Nodejs的异步模型

我相信Asynchronous（异步）一词是很多JavaScript学习者的梦魇。于我而言也是如此，同步阻塞式的编程相对于人类线性的思维来说要轻松得多，可是对于计算机来说执行却没那么高效。我想从现在的趋势看来，在web领域，人类还是不得不委屈自己去适应异步的思维和编程。Nodejs能从Java的天下夺下一部分蛋糕，靠的也正是异步带来的高效I/O。

## 同步/异步和阻塞/非阻塞

我们都知道，对于计算机而言，CPU的运行速度是很快的，而I/O设备却非常慢。从计算机诞生以来，人们在硬件设计、操作系统、上层应用等等不同层面做出了许多的努力，去帮助I/O设备跟上CPU的步伐。对于应用软件的运行速度这个木桶来说，I/O速度常常就是那个短板。Nodejs的诞生可以说也是想在高并发的web领域里解决I/O速度这个短板。

首先我们来分清一下这几个概念

- 同步阻塞I/O： 应用层软件运行时想读取硬盘里的一个文件，这时他向操作系统内核发出一个I/O调用，负责运行应用层软件的CPU在发出调用的地方停顿，等待I/O设备读取硬盘文件的结果数据返回，再接着执行应用层软件后面的代码。在等待I/O设备时应用程序的运行就被阻塞住了。因此称作阻塞I/O。

- 异步非阻塞I/O：应用层软件运行时想读取硬盘里的一个文件，这时他向操作系统内核发出一个I/O调用，负责运行应用层软件的CPU在发出调用之后继续执行后面的代码，等待I/O设备读取硬盘文件的结果数据返回，再执行应用层软件想要对这个文件的数据进行的操作。这里I/O调用没让CPU等待，后面的代码也没有因此阻塞，所以称为非阻塞I/O。

这里的阻塞/非阻塞时相对于 **应用层软件** 这个对象而言，如果软件发出I/O调用后后面的代码就不执行了这就是阻塞，发出I/O调用后，接着执行后面的代码，这就是软件没被阻塞。

另外一个容易混淆的概念同步/异步。在上面同一个场景下，同步/异步是相对于 **I/O调用** 而言。如果应用层软件发出了一个I/O调用，在I/O设备读取数据没完成之前，这个I/O调用就没完成不返回结果。这就是同步。而如果应用层软件发出一个I/O调用，这时虽然I/O设备还没读取到数据，但是I/O调用却会立即返回一个结果（不带数据）。之后等I/O设备读取完数据后再通过一定方式去告知应用软件。这种I/O调用就是异步。

*异步不代表着一定非阻塞，设想异步阻塞的情景，比如说应用层软件发出I/O调用，这时I/O调用立即返回结果（异步），但是应用层软件却不继续执行后面的代码，而是在原地等I/O调用的数据回来（阻塞）。*

## 高并发中的Node和Java

在介绍Node的异步I/O模型之前，我想先用一些直白的语言来描述我对Node的一点理解。在Web领域，谈到性能，几乎都是指服务端。想象一下，server一般运行在公司的服务器上，而client一般运行在用户的PC/手机上。client和server的关系可以看成是广义上的多对一（实际上server运行在集群上）。当在高并发的情景下，比如说双十一，或者小点说在大学里的抢课、四六级报名。这时server端会接到众多的client端的请求。在传统的Java web sever里，采用了多线程的模型来解决这个问题。当有一个client访问server就为他创建一个线程。CPU会以时间片的形式交替运行不同线程。而往往高并发的时候其实性能瓶颈也不在CPU，因为CPU真的很快，更多的时候其实是在I/O上。当高并发时每个client都需要去查询数据库的时候，所以server的设计时也会尽量避免查询数据库（Redis/Memcached），server的压力可想而知的大了。据我的了解，在12306抢票系统中，甚至把整个数据库运行在几T的内存上（因为内存相对硬盘I/O速度更快）。

Node的出现实际上也没解决I/O的速度瓶颈，我只能说Node使用了单线程完成了Java多线程才能实现的高并发，因此避免了线程创建以及线程上下文切换带了的CPU资源浪费，同时也避免了烦人的锁、状态同步的问题。

再用通俗的讲法解释一下Node和Java面对高并发的解决方法的不同：

- 假设我们开了一家餐馆（Server），我们的生意红火（双十一），这时候我们有很多很多顾客（Client）一起冲进餐馆（高并发）。顾客进餐馆的第一件事就是找服务员。

- Java餐馆在面对这场景时的策略，每来一个顾客，Java就从服务员部（线程池）新派一个服务员（线程）。然后这个服务员就到后厨告诉厨师顾客想吃的菜（向操作系统内核发起I/O调用），然后厨师开始做菜（I/O），等到菜做好之前服务员就在后厨等着（阻塞）。厨师做好菜之后，服务员端给顾客（Response）。然后服务员回到服务员部等待下一个顾客来再被派遣出去。

- Node餐馆在面对这场景时显得更聪明一点，Node餐馆只派一个服务员(单线程)，每次有顾客来的时候，服务员到对讲机告诉后厨顾客想吃的菜，然后立即让顾客到餐桌上等（异步I/O调用立即返回不带数据的结果）。接着同样的策略继续服务下一个顾客（非阻塞）。当后厨菜做好之后，服务员再跑去后台把菜拿来给顾客（回调）。

- Node餐馆相比Java餐馆的优势就是无需新派很多服务员省钱（避免CPU资源浪费），同时还避免了可能不同的服务员还得相互问这个顾客你服务过没有（状态同步）等麻烦事。

## Node的异步I/O模型

我们知道，Node其实是一个runtime，可以算是一个运行在操作系统上的软件。提供Node App的运行环境。知道Node的异步非阻塞I/O的思想之后，我们来了解一下Node对此的具体实现方式

首先在操作系统层面，实现异步I/O调用有许多模型，比如说Windows的IOCP,和linux的AIO。这里我们不具体展开。Node的异步I/O模型在Windows下是借用IOCP，而在*nix下却自己用线程池的方式实现了一个异步I/O模型

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-async/aio.png)
*摘自《深入浅出Nodejs》by朴灵*

- 主线程即Node的那个“单线程”。然后主线程需要发起一个I/O调用的时候就从发起一个I/O线程，让该I/O线程去阻塞I/O读取硬盘数据。然后主线程自己不阻塞继续执行后面的代码。I/O线程读取完数据后再通知主线程。

同时Node提供了libuv作为抽象封装层，屏蔽了Windows的IOCP以及Node的自定义线程池的差异。整个结构如下：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-async/nodestruct.png)

我们最终的Node App跑在最上层的Nodejs Runtime，可以毫无后顾之忧地使用Node底层赋予我们的异步非阻塞I/O的能力

## 事件循环

*该部分参考[浏览器和NodeJS中不同的Event Loop](https://github.com/kaola-fed/blog/issues/234)*

我们上面的异步I/O模型更多的是讲操作系统底层对异步I/O的实现方式。而Nodejs的libuv利用系统底层异步I/O实现了一个事件循环模型。这也是和我们普通开发者比较相关的部分。我们上层代码中的异步任务直接在libuv的这个事件循环模型中被处理。

每一个Node进程启动时，Node便会创建一个类似与While(true)的循环，每一个循环体被称为是一个Tick。该循环即为事件循环

我们承接上面Node餐馆的例子来通俗讲解一下事件循环：

- 首先我们的服务员（Node的那个JavaScript执行"单线程"），这个服务员在前台会处理各种各样的顾客请求，比如说有的顾客半小时想吃炒饭（setTimeout），有的顾客想喝咖啡（网络I/O）。相同的是这些顾客的请求都是比较耗时的，或者换句话说是服务员没办法立即给他。这时服务员会把顾客点的菜告诉后厨，半小时炒饭的需求告诉定时后厨（Timer模块），想喝咖啡需求告诉咖啡师（网络I/O模块）。咖啡师做完咖啡后，把咖啡放在一个线性的送菜区（任务队列），定时后厨在时间到了之后，也把炒饭送到送菜区（任务队列）。

- 这时候后厨和服务员之间的通知员（事件循环）登场了。每当通知员看到没有餐馆里没有新来的顾客了（主线程执行栈为空）。就会去看看送菜区（任务队列）里面有没有做好的菜（待执行的任务）。如果有，通知员就会跑去告诉服务员，服务员再跑到送菜区将咖啡送给顾客喝（执行回调函数），接着看任务队列里还有炒饭又把炒饭送给顾客。

## direct style 和 continuation-passing style

这两个名词是来自于《Nodejs Design Patterns 2th》的Chapter2里的。代表两种的代码风格，其中我们在Nodejs里会看到很多continuation-passing style的代码，不同于以往的同步阻塞式的编程（例如php），大多采用direct style的代码。

**同步direct style**
```js
function add(a, b) {
  return a + b;
}
```
**同步continuation-passing style**
```js
function add(a, b, callback) {
  callback(a + b);
}
```
我们可以看到 direct style 就是直接将结果使用return给调用者。 continuation-passing style不将结果直接return。而是将结果传递（passing）给传进来的callback函数。

很多时候同步continuation-passing style的代码风格可能会让代码有点迷惑性
```js
const result = [1, 5, 7].map(element => element - 1);
console.log(result); // [0, 4, 6]
```
其中Array.prototype.map这个函数虽然有像callback一样的传入的函数，然而实际上它是同步的

而continuation-passing style更多时候是用在异步编程的，如下面的代码：

**异步continuation-passing style**
```js
function additionAsync(a, b, callback) {
 setTimeout(() => callback(a + b), 100);
}
```

得益于在JavaScript中的函数的“一等公民”。我们可以把函数当作参数来传递，这使得continuation-passing style很容易实现。我们发起一个异步I/O，同时把怎样处理I/O得到的结果的回调函数也传进去了。异步逻辑十分清晰。Nodejs里面有很多异步的API也是continuation-passing style这种风格。

## callback模式的异常处理

Nodejs的callback有一个称作Error come first惯例。也就是异步continuation-passing style函数中产生的任何错误，比如说fs.readFile这个CPS函数，有可能出现你想读取的文件不存在这个err，当出现错误的时候，错误的信息会作为callback的第一个参数传入callback进行处理。

```js
fs.readFile('foo.txt', 'utf8', (err, data) => {
  if (err)
    handleError(err);
  else
    processData(data);
});
```

上面是我们调用CPS函数的示例，关注点在调用时我们的callback要对 **传进来** 的err进行判断处理，而当我们自己编写CPS函数时

```js
const fs = require('fs');

function readJSON(filename, callback) {
  fs.readFile(filename, 'utf8', (err, data) => {
    let parsed;
    if (err)
    // 如果有错误产生则退出当前调用
      return callback(err);
    try {
      // 解析文件中的数据
      parsed = JSON.parse(data);
    } catch (err) {
      // 捕获解析中的错误，如果有错误产生，则进行错误处理
      return callback(err);
    }
    // 没有错误，调用回调
    callback(null, parsed);
  });
};
```

在我们编写CPS函数时关注点变为将错误作为参数 **传出去**给callback。

## promise和async/await

尽管Nodejs诞生时异步编程的模式是伴随着callback的，但随着callback模式的问题不断暴露，Nodejs社区和EcmaScript标准委员会也渐渐意识到问题并推出像Promise和async/await的方式来优化异步编程体验。现在也取代了callback成为了更佳的异步编程实践。