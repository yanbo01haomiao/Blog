# Node.js流编程管道

这里就略过Unix的 | 管道历史了

## 一些简介
> 从程序的角度而言流是有方向的数据，按照流动的方向分为三种流
1. 设备流向程序： readable
2. 程序流向设备： writable
3. 双向：duplex、transform
在Unix里的哲学是：一切皆文件，而Node.js里很多文件的处理多数使用流来完成。比如普通的文件（磁盘文件），I/O设备文件（stdin，stdout也就是键盘、显示器这些），网络文件（http、net、socket这些）

## pipe API

```js
readable.pipe(writable, [options])
```

关于这个API来一点注解，pipe()方法将从Readable Streams中发出的数据chunk抽取到所提供的Writable Streams中。 另外，当Readable Streams发出end事件（除非我们指定{end：false}作为options）时，Writable Streams将自动结束。 pipe()方法返回作为参数传递的Writable Streams，如果这样的stream也是可读的（例如Duplex或Transform Streams），则允许我们创建链式调用。

将两个Streams连接到一起时，则允许数据自动流向Writable Streams，所以不需要调用read()或write()方法；但最重要的是不需要控制back-pressure，因为它会自动处理。

### 关于pipe API的例子（电影流媒体服务器）

```js
const http = require('http');
const fs = require('http');

http.createServer((req, res) => {
    fs.createReadStream('./movies/小偷家族.mp4').pipe(res)
}).liseten(8080)
```
相对于我们使用`fs.readfile('./movies/小偷家族.mp4', (err, data)=>{ res.end(data)} )`这样的方式，使用Stream再pipe有诸多好处，这个我们在流编程初探里也有提到。主要是
1. 时间效率：不需要等到电影文件全部读取完再发送给客户端
2. 空间效率：不会把整个文件内容都读取到内存，避免高并发情形下内存不够用
3. 可组合性：我们如果想对电影内容做压缩，则只需要`fs.createReadStream('./movies/小偷家族.mp4').pipe(oppressor).pipe(res)`
## Combining Streams

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream-pipe/combined.png)

组合Streams其实很容易理解，我们将多个Streams组合起来，不关心多个Streams内部的具体实现，只把他们当作黑盒来使用。这同时也可以帮助我们简化错误管理。我们只需要为组合Streams的错误设置一个监听器即可。无需对每个Streams都做错误监听。

### 压缩和加密数据/解压和解密数据
我们看下面一小段代码，他非常简洁明了，我想这就是pipe的魅力。
```js
//combinedStreams.js
const zlib = require('zlib');
const crypto = require('crypto');
const combine = require('multipipe');
module.exports.compressAndEncrypt = password => {
  return combine(
    zlib.createGzip(),
    crypto.createCipher('aes192', password)
  );
};
module.exports.decryptAndDecompress = password => {
  return combine(
    crypto.createDecipher('aes192', password),
    zlib.createGunzip()
  );
};
```
好，现在我们可以用上面的两个方法来写一个小的压缩加密程序了
```js
//archive.js
const combine = require('multipipe');
const fs = require('fs');
const compressAndEncryptStream = require('./combinedStreams').compressAndEncrypt;
combine(
    fs.createReadStream(process.argv[3])
    .pipe(compressAndEncryptStream(process.argv[2]))
    .pipe(fs.createWriteStream(process.argv[3] + ".gz.enc"))
).on('error', err => {
    // 使用组合的Stream可以捕获任意位置的错误
    console.log(err);
});
```
使用方式如下所示
```
node archive mypassword /path/to/file.txt
```

## Forking Streams

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream-pipe/forking.png)

Forking Streams就是将单个Readable Stream `pipe`给多个Writable Streams。

### 多重校验和生成器
```js
const fs = require('fs');
const crypto = require('crypto');
const sha1Stream = crypto.createHash('sha1');
sha1Stream.setEncoding('base64');
const md5Stream = crypto.createHash('md5');
md5Stream.setEncoding('base64');
//其中sha1Stream和md5Stream应该是Transform Stream，既可读又可写
const inputFile = process.argv[2];
const inputStream = fs.createReadStream(inputFile);
inputStream
  .pipe(sha1Stream)
  .pipe(fs.createWriteStream(inputFile + '.sha1'));
inputStream
  .pipe(md5Stream)
  .pipe(fs.createWriteStream(inputFile + '.md5'));
```
- 当inputStream结束时，md5Stream和sha1Stream会自动结束，除非当调用pipe()时指定了end选项为false。

- Stream的两个分支会接受相同的数据块，因此当对数据执行一些副作用的操作时我们必须非常谨慎，因为那样会影响另外一个分支。

- 黑盒外会产生back-pressure，来自inputStream的数据流的流速会根据接收最慢的分支的流速作出调整。

## Merging Streams

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream-pipe/merging.png)

跟Forking Streams相反，Merging Streams其实就是将多个Readable Streams `pipe`到一个 Writable streams.s

### 将多个源文件压缩为一个压缩包
```js
//mergeTar.js
const tar = require('tar');
const fstream = require('fstream');
const path = require('path');
const destination = path.resolve(process.argv[2]);
const sourceA = path.resolve(process.argv[3]);
const sourceB = path.resolve(process.argv[4]);
const pack = tar.Pack();
pack.pipe(fstream.Writer(destination));
let endCount = 0;

function onEnd() {
  if (++endCount === 2) {
    pack.end();
  }
}

const sourceStreamA = fstream.Reader({
    type: "Directory",
    path: sourceA
  })
  .on('end', onEnd);

const sourceStreamB = fstream.Reader({
    type: "Directory",
    path: sourceB
  })
  .on('end', onEnd);

sourceStreamA.pipe(pack, {end: false});
sourceStreamB.pipe(pack, {end: false});
```
使用方法
```
node mergeTar dest.tar /path/to/sourceA /path/to/sourceB
```
- 这里在pipe指定end为false其实和上面的Forking Streams一个意思。指定了{end: false}我们就不会在Readable Streams这遍结束时（this.push(null)）而导致Writable Streams这边以触发end事件，关闭管道停止继续写入Writable。
- onEnd这个事件就是在手动控制Writable Stream这边end事件的触发

## Multiplexing & Demultiplexing

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream-pipe/muanddemu.png)

<Node.js Design Pattern 2th>一书中写了一个例子，创建一个远程的logger日志记录来讲多路复用和多路分解。其中有一个小程序来启动子进程，并将其标准输出和标准错误都重定向到远程服务器，服务器接受它们然后保存为两个单独的文件。

这里我们一开始的Readable Stream可能有多个来源，比如多个子进程的`console.log()`标准输出，会作为这个远程日志服务的输入。然后他们复用一个TCP socket传输这些日志到远程服务器。在远程服务器端再从这个TCP socket 中读取数据接着再`pipe`到磁盘保存下来为止。

我们直接看代码，我相信代码写得还是十分一目了然的。并且看懂了这个代码，我们将对IP、TCP和UDP等等多路复用和分解等的技术更加熟悉

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream-pipe/datapackage.png)

### 远程日志完整代码

#### 客户端
```js
const child_process = require('child_process');
const net = require('net');

function multiplexChannels(sources, destination) {
  let totalChannels = sources.length;

  for(let i = 0; i < sources.length; i++) {
    sources[i]
      .on('readable', function() { // [1] stdout/stderr(readable)
        let chunk;
        while ((chunk = this.read()) !== null) {
          const outBuff = new Buffer(1 + 4 + chunk.length); // [2]参考数据包格式
          outBuff.writeUInt8(i, 0);
          outBuff.writeUInt32BE(chunk.length, 1);
          chunk.copy(outBuff, 5);
          console.log('Sending packet to channel: ' + i);
          destination.write(outBuff); // [3]destination是TCP socket
        }
      })
      .on('end', () => { //[4]多个源全read()完才触发socket.end()
        if (--totalChannels === 0) {
          destination.end();
        }
      });
  }
}

const socket = net.connect(3000, () => { 
  const child = child_process.fork(
    process.argv[2],
    process.argv.slice(3), {
      silent: true
    }
  );
  multiplexChannels([child.stdout, child.stderr], socket);
});
```

#### 服务端
```js
function demultiplexChannel(source, destinations) {
  let currentChannel = null;
  let currentLength = null;
  source
    .on('readable', () => { //[1] source是TCP socket，TCP socket是一个Duplex Streams
      let chunk;
      if(currentChannel === null) {          //[2]为了知道来自哪个channel
        chunk = source.read(1);
        currentChannel = chunk && chunk.readUInt8(0);
      }
    
      if(currentLength === null) {          //[3]为了知道数据长度
        chunk = source.read(4);
        currentLength = chunk && chunk.readUInt32BE(0);
        if(currentLength === null) {
          return;
        }
      }
    
      chunk = source.read(currentLength);        //[4]我们知道从内部Buffer中拉出多少数据，所以我们尝试读取所有数据
      if(chunk === null) {
        return;
      }
    
      console.log('Received packet from: ' + currentChannel);
    
      destinations[currentChannel].write(chunk);      //[5]destinations是磁盘文件数组
      currentChannel = null;
      currentLength = null;
    })
    .on('end', () => {            //[6] 等待TCP socket end之后去触发所有磁盘文件end
      destinations.forEach(destination => destination.end());
      console.log('Source channel closed');
    })
  ;
}

net.createServer(socket => {
  const stdoutStream = fs.createWriteStream('stdout.log');
  const stderrStream = fs.createWriteStream('stderr.log');
  demultiplexChannel(socket, [stdoutStream, stderrStream]);
})
  .listen(3000, () => console.log('Server started'))
;
```

使用方法
```js
//generateData.js
console.log("out1");
console.log("out2");
console.error("err1");
console.log("out3");
console.error("err2");
```
```
node server
```
```
node client generateData.js
```
