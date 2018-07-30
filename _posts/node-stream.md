# Node.js流编程初探

## Buffering versus Streaming

我们在Node.js里遇到的大多数异步API都是buffer mode的.所有的被加载的数据都会进入一个buffer里，当所有的数据加载完成之后，则被传递给回调函数去处理。

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream/buffer.png)

在时间点t1，数据正在被读取，有可能网络I/O，比如数据包正在传输，也可能是磁盘I/O，磁盘正在读取数据等等。直到时间点t2，数据全部read完毕，才会开始传递给consumer，可能是回调函数。对比如下的stream mode

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream/stream.png)

相比与上面的buffer mode，一个显著的特点就是stream mode一接收到数据就会发送给consumer。

我们可以显著地发现，strea mode 相对于 buffer mode 的优点：
1. Spatial efficiency（节省空间）
2. Time efficiency（节省时间）
3. **composability**（可组合的能力）

## Spatial efficiency

V8引擎的buffer有一个大小的限制，不能超过0x3FFFFFFF bytes（大概比1G小一点）。这也就意味着，如果我们去处理，比如说fs.readFile一些超过1G，又或者并发地去处理几个几百M的文件，那就很容易触碰到这个限制。举个具体的例子

```js
// gzip.js
const fs = require('fs');
const zlib = require('zlib');
const file = process.argv[2];

fs.readFile(file, (err, buffer) => {
  zlib.gzip(buffer, (err, buffer) => {
    fs.writeFile(file + '.gz', buffer, err => {
      console.log('File successfully compressed');
    });
  });
});
```
```bash
node gzip <path to file>
```

如果`<path to file>`这个文件超过了V8引擎的buffer大小限制，那么就会有RangeError的报错.

当我们使用stream mode的话
```js
const fs = require('fs');
const zlib = require('zlib');
const file = process.argv[2];
fs.createReadStream(file)
  .pipe(zlib.createGzip())
  .pipe(fs.createWriteStream(file + '.gz'))
  .on('finish', () => console.log('File successfully compressed'));
```
是的，除了我们的RangeError报错解除了以外，我们发现stream mode比上面的callback hell要简洁优雅得多。显然，我们可以使用async/await的方式来消除上面的callback hell带来的程序易读性的问题。但是另一方面来看，stream mode 的 pipe不管从语义上和场景的切合度，还是实际效率上其实都来得更加优雅。

## Time efficiency

我们现在来设想一个场景，当你压缩一个文件，并通过HTTP上传到远程的一个服务器上时，服务器将解压缩文件并存入自己的文件系统中。（在我们现在的前端开发中，我们经常会在测试和生产环境时使用一些脚本将webpack编译好的静态资源文件上传到cdn中，和这个需求很相似）

我们使用stream mode来完成上面那个压缩上传服务器的需求
```js
//gzipReceive.js 服务器端代码
const http = require('http');
const fs = require('fs');
const zlib = require('zlib');

const server = http.createServer((req, res) => {
  const filename = req.headers.filename;
  console.log('File request received: ' + filename);
  req
    .pipe(zlib.createGunzip())
    .pipe(fs.createWriteStream(filename))
    .on('finish', () => {
      res.writeHead(201, {
        'Content-Type': 'text/plain'
      });
      res.end('That\'s it\n');
      console.log(`File saved: ${filename}`);
    });
});

server.listen(3000, () => console.log('Listening'));
```
```js
//gzipSend.js 客户端代码
const fs = require('fs');
const zlib = require('zlib');
const http = require('http');
const path = require('path');
const file = process.argv[2];
const server = process.argv[3];
const options = {  
    hostname: server,  
    port: 3000,  
    path: '/',  
    method: 'PUT',  
    headers: {    
        filename: path.basename(file),    
        'Content-Type': 'application/octet-stream',    'Content-Encoding': 'gzip'  
    }
};
const req = http.request(options, res => {  
    console.log('Server response: ' + res.statusCode);}
);
fs.createReadStream(file)  
  .pipe(zlib.createGzip())  
  .pipe(req) 
  .on('finish', () => {    
    console.log('File successfully sent');
});
```
`node gzipReceive`和`node gzipSend <path to file> localhost`运行

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/node-stream/bufferstream.png)

stream mode在时间方面的效率相对于buffer mode是显而易见的，在buffer mode下，我们的每个文件都需要以文件为单位经历read、compress、...等等六个阶段，而compress这个阶段必须等待每个文件中的所有数据块的read阶段完成后才会开始。另一方面，当我们使用stream模式，则当文件的第一个数据块read阶段完成之后，该数据块就会直接进入compress阶段，尽管此时该文件的其他数据块也同时在进行read阶段。这听起来有些拗口，但是实际上却不难理解，stream模式就像我们工厂里的流水线一样，其实buffer也可以算是流水线，只不过stream的生产单位是数据块，而buffer则是文件。

## Composability

我们通过上面一些少量的流编程代码可以看到，像pipe()这个神奇的方法，正如其名字一样，流编程的对于数据的处理就像是让数据经过管道里的一些process unit，处理单元。当我们想为声明的gzipReceive/gzipSend程序添加一层数据加密的时候，我们可以很简单地对现有的程序进行如下的改造：
```js
// 客户端
const crypto = require('crypto');
// ...
fs.createReadStream(file)  
  .pipe(zlib.createGzip())
  .pipe(crypto.createCipher('aes192', 'a_shared_secret'))
  .pipe(req)  
  .on('finish', () => console.log('File succesfully sent'));
```

```js
// 服务端
const crypto = require('crypto');
// ...
const server = http.createServer((req, res) => {  
  // ...  
  req
    .pipe(crypto.createDecipher('aes192', 'a_shared_secret'))
    .pipe(zlib.createGunzip())    
    .pipe(fs.createWriteStream(filename))    
    .on('finish', () => { /* ... */ });});
```

我们只加了几行代码，就让我们的程序多了一层加密层，而且这里的代码实在是太简单易懂了，这样的编程范式我想不用我说，大家也很容易感受到其简洁优雅之处。由此，stream mode的可组合性优势也表现得很清楚了。
