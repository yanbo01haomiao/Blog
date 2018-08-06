# Node.js流编程基础

## 一些基本的事实

1. Node.js当中所有Stream的实现都来自于以下四个基本的抽象类(Base Abstract Classes)

- Stream.Readable
- Stream.Writable
- Stream.Duplex
- Stream.Transform

2. 同时这四个类都是EventEmitter的实例，因此Stream会有像end这样的事件可以在一个可读Stream完成读取时触发、error事件在产生异常时触发，等等这些特性。

3. Stream支持两种操作模式

- Binary mode（二进制模式）：This mode is where data is streamed in the form of chunks，such as buffers or strings

- Object mode（对象模式）：This mode is where streaming data is treated as a sequence of discrete objects（allowing us to use almost any JavaScript value）

## Stream.Readable

我习惯先从使用的角度来学习一种新东西。我们在Node.js中有很多基于Stream实现的API。我们先来看看我们平时是怎么使用他们的。

### process.stdin（Readable Streams）

首先就是process模块的stdin标准输入，我们从Readable Stream读取数据有两种模式，分别是`non-flowing`和`flowing`模式。
```js
// non-flowing mode
// "readable" event signals the availability of new data to read
// readable.read([size]) 从Readable Stream内部Buffer提取数据块，如果Stream在二进制模式下工作。返回的数据块则是Buffer对象(也可以使用setEncoding(encoding)来返回String)，有length有toString()。如果Buffer中没有更多的数据可用，则返回null。
process.stdin
  .on('readable', () => {
    let chunk;
    console.log('New data available');
    while ((chunk = process.stdin.read()) !== null) {
      console.log(
        `Chunk read: (${chunk.length}) "${chunk.toString()}"`
      );
    }
  })
  .on('end', () => process.stdout.write('End of stream'));
```
另一种模式，flowing mode，不再监听readable，而是监听data，同时数据块chunk也不用我们去调用`read()`,而是直接被传递给回调函数。随着Streams2的引入flowing模式不再是默认的工作模式，我这里不做过多介绍。
```js
// flowing mode
process.stdin
  .on('data', chunk => {
    console.log('New data available');
    console.log(
      `Chunk read: (${chunk.length}) "${chunk.toString()}"`
    );
  })
  .on('end', () => process.stdout.write('End of stream'));
```

### 自己实现可读取的Streams

如果想在自己的代码里实现一个类似process.stdin这种某种Readable Streams类的实例。我们需要在类中继承stream.Readable，并且实现`_read()`方法。

Readable类内部将调用我们这里实现的`_read()`方法，这个方法会使用push()填充内部的`buffer`。我们的使用者，读取的chunk数据块就是来自这个`buffer`。

```js
const stream = require('stream');
const Chance = require('chance'); // 一个npm module

const chance = new Chance();

class RandomStream extends stream.Readable {
  constructor(options) {
    super(options);
  }

  _read(size) {
    const chunk = chance.string(); //[1] 随机字符串
    console.log(`Pushing chunk of size: ${chunk.length}`);
    this.push(chunk, 'utf8'); //[2] push的数据是String因此指定编码为utf-8
    if (chance.bool({
        likelihood: 5
      })) { //[3] 5%的概率push null来在内部buffer里表示EOF
      this.push(null);
    }
  }
}

module.exports = RandomStream;
```
我们使用`chance.string()`生成一个随机的字符串，并且将字符串以指定的`utf-8`编码格式写入`buffer`中。同时使用`chance.bool()`使得有5%的概率push一个`null`到`buffer`中。

我们使用自己编写的这个Readable Stream的方式，基本是和使用`process.stdin`差不多的，如下所示:
```js
const RandomStream = require('./randomStream');
const randomStream = new RandomStream();

randomStream.on('readable', () => {
  let chunk;
  while ((chunk = randomStream.read()) !== null) {
    console.log(`Chunk received: ${chunk.toString()}`);
  }
});
```
## Stream.Writable

对于Writable Stream我们同样先来看使用。
### http.ServerResponse (Writable Streams)

```js
// res 是 http.ServerRespnse这个Writable Stream类的一个实例
//[3] res.write(chunk, [encoding], [callback]) encoding参数是可选的，其在chunk是String类型时指定（默认为utf8，如果chunk是Buffer，则忽略）；当数据块被刷新到底层资源中时，callback就会被调用，callback参数也是可选的

const Chance = require('chance'); // npm module
const chance = new Chance();

require('http').createServer((req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/plain'
  }); //[1] res.writeHead，这和Stream.Writable没关系 是http.ServerResponse实现的辅助方法
  while (chance.bool({
      likelihood: 95
    })) { //[2] 95%的概率
    res.write(chance.string() + '\n'); //[3]
  }
  res.end('\nThe end...\n'); //[4] res.end([chunk], [encoding], [callback]) 是为了表明没有更多的数据要被写入stream中了
  res.on('finish', () => console.log('All data was sent')); //[5]
}).listen(8080, () => console.log('Listening on http://localhost:8080'));
```

### Back-pressure

这是一个题外话，我们知道在stream mode编程中，我们的数据块chunk被write入buffer的同时就会有consumer，从buffer中read数据，倘若，chunk的write速度快于consumer从中read的数据，那么内部的buffer终有一天会超过`highWaterMark`（一般是16kb）限制。这时候我们再使用write方法写入chunk块时会失败，并且返回false。当buffer里的chunk块被consumer全部read完毕时，则会触发一个`drain`事件，提醒我们可以再次开始write了，这个机制就叫back-pressure

back-pressure机制同样适用于Readable Stream，在Readable Stream中的_read()调用push()时也可能返回false.

我们将上面的代码加入back-pressure机制
```js
const Chance = require('chance');
const chance = new Chance();

require('http').createServer((req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/plain'
  });

  function generateMore() {
    while (chance.bool({
        likelihood: 95
      })) {
      const shouldContinue = res.write(
        chance.string({
          length: (16 * 1024) - 1
        }) //[1] 16KB - 1Byte，很快将达到highWaterMark
      );
      if (!shouldContinue) { //[2] 达到highWaterMark时 res.write返回 shouldContinue === false
        console.log('Backpressure');
        return res.once('drain', generateMore);
      }
    }
    res.end('\nThe end...\n', () => console.log('All data was sent'));
  }
  generateMore();
}).listen(8080, () => console.log('Listening on http://localhost:8080'));
```

### 自己实现可写入的Streams

这次我们尝试使用object mode，而不是binary mode。
他接收以下的对象格式
```js
{
  path: <path to a file>
  content: <string or buffer>
}
```
调用模块toFileStream.js如下（构造函数里声明objectMode）：
```js
const stream = require('stream');
const fs = require('fs');
const path = require('path');
const mkdirp = require('mkdirp');

class ToFileStream extends stream.Writable {
  constructor() {
    super({
      objectMode: true
    });
  }

  _write(chunk, encoding, callback) {
    mkdirp(path.dirname(chunk.path), err => {
      if (err) {
        return callback(err);
      }
      fs.writeFile(chunk.path, chunk.content, callback);
    });
  }
}
module.exports = ToFileStream;
```

## Stream.Duplex

Duplex Stream是既可读也可写的，当我们想要描述一个既是data source又是data destination的实体时，比如说`socket`时，这就显得很有用。我们可以从Duplex Stream中read()或write()数据。可以既监听readable又监听drain事件。
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream-base/duplex.png)
当只保留write这条线时，就是一个Wrtiable Stream，当只保留read这条线，就是一个Readable Stream。

## Stream.Transform

在Duplex Stream中，**从Stream中读取的数据，和写入的数据之间没有直接的关系**。以一个TCP socket为例，它只是向远程节点发送数据，和从远程节点接收数据。TCP socket自身意识不到输入和输出之间的关系。

而Transform Stream和Duplex不同，他有两边，Writable Side和Readable Side，他接收从Writable Side write() 进的chunk数据块，然后应用某种转换（transformation）将chunk块push进buffer以供Readable去read() 
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream-base/transform.png)
Duplex Stream和Transform Stream从外部的接口来看是完全相同的，我们同样既可以`read()`又可以`write()`来使用Duplex Stream和Transform Stream。不过在实现内部方法上却有不同。对于Duplex Stream我们需要实现`_read()`和`_write()`方法，并且他们使相互独立的。而对于Transform Stream，我们需要实现`_transform()`和`_flush()`

### 自己实现可转换的Streams

正如其名replaceStream，我们将输入部分的searchString替换为replaceString

```js
const stream = require('stream');
const util = require('util'); // 这里未使用

class ReplaceStream extends stream.Transform {
  constructor(searchString, replaceString) {
    super();
    this.searchString = searchString;
    this.replaceString = replaceString;
    this.tailPiece = '';
  }

  _transform(chunk, encoding, callback) {
    const pieces = (this.tailPiece + chunk) //[1] 这个replace算法具体实现不做细究
      .split(this.searchString);
    const lastPiece = pieces[pieces.length - 1];
    const tailPieceLen = this.searchString.length - 1;

    this.tailPiece = lastPiece.slice(-tailPieceLen);     
    pieces[pieces.length - 1] = lastPiece.slice(0,-tailPieceLen);

    this.push(pieces.join(this.replaceString));      
    callback();
  }

  _flush(callback) {
    this.push(this.tailPiece);
    callback();
  }
}

module.exports = ReplaceStream;
```

从`_transform`中的书写方法，对比`_write`和`_read`的写法，其实我们可以初见一点Stream的端倪。这里我做一点简单解释。

`_write`所执行的逻辑就是接收chunk块（来自于Writable Stream使用者的输入，例如服务端程序调用res.write()），接着`_write`函数把chunk块传输入某个buffer(例如直接写入硬盘，fs.writeFile，或者比如网络I/O写入socket的buffer。)

`_read`所执行的逻辑就是，从某个buffer(例如硬盘中，fs.readfile，或者网络I/O中，从socket的buffer)中拿到数据，并使用push将其推给某个暂时的buffer，以供外界`read()`。这里的push不同于write，但是名字容易混淆试听，让人觉得有那么点“写入buffer”的意思，其实大可以完全理解为push给调用read()的人就行。

因此，`_transform`就是综合了上述的逻辑，他接收的参数和`_write`一样，也就是他获取了使用者的输入chunk块，同时又把chunk push出去给调用者使用read()读取，这里可以很好地帮助我们理解Streams。

我们来看看怎么使用ReplaceStream
```js
const ReplaceStream = require('./replaceStream');

const rs = new ReplaceStream('World', 'Node.js');
rs.on('data', chunk => console.log(chunk.toString()));

rs.write('Hello W');
rs.write('orld!');
rs.end();
```
结果
```
Hel
lo Node.js
!
```