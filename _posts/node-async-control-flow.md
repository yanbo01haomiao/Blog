# Node.js异步控制流

这里的异步控制流的方法其实并不仅限于Node.js，而应该说是属于EcmaScript的，对于浏览器侧以及服务器侧的JavaScript都是通用的。异步控制流这个话题实在是再老生常谈不过了。我相信每一个JavaScript程序员都会知道对于JavaScript从callback的callback hell到像async这样的库，再到之后ES6的Promise，TJ大神的co库和generator结合的解决方案。以及ES7受TJ大神启发而引入的async/await等等这段历程。JavaScript社区的程序员们和TC39为了优化JavaScript的异步编程体验做出的努力有目共睹。在《Node.js Design Pattern 2th》一书中，作者用chapter 3 / 4两章来介绍Node.js异步编程的一些历程。我阅读之后也有很多的启发。不过在这里，我不想再去重复这个历程，而是想总结一下在当今(2018)，JavaScript异步编程的一些最佳实践，我想这对在工作中写出可读性较好而且易维护的异步代码将有很大的帮助。

## callback spider
考虑到我们现在的一个需求，写一只网络爬虫去下载一个url的内容，并将其保存在本地磁盘
```js
const request = require('request'); // npm包
const fs = require('fs');
const mkdirp = require('mkdirp'); // npm包
const path = require('path');
const utilities = require('./utilities'); // 自己写的工具库

function spider(url, callback) {
  const filename = utilities.urlToFilename(url);
  fs.exists(filename, exists => {
    if (!exists) {
      console.log(`Downloading ${url}`);
      request(url, (err, response, body) => {
        if (err) {
          callback(err);
        } else {
          mkdirp(path.dirname(filename), err => {
            if (err) {
              callback(err);
            } else {
              fs.writeFile(filename, body, err => {
                if (err) {
                  callback(err);
                } else {
                  callback(null, filename, true);
                }
              });
            }
          });
        }
      });
    } else {
      callback(null, filename, false);
    }
  });
}
```
流程如下：
1. fs.exists检查该url是否已经被下载过，否的话进行下一步
2. request发起网络请求，去下载url里面的内容，下载完进行下一步
3. mkdirp创建相应的文件夹，创建完成进行下一步
4. fs.writeFile将下载到的数据写入文件，结束整个流程

我们发现这四步的API在Node.js里都是异步API，同时我们要求这些异步的API按照一定的流程去执行，第一步结束后才接着下一步，因此我们需要像这样层层去传回调函数。

像我们上面这样写的代码就是传说中的回调地狱，有以下两点缺点：
### callback hell
1. 可读性差：这一点不言而喻
2. 异常处理困难：每次callback第一个参数都是err，每次写逻辑都要先处理异常

## 串行控制流的最佳实践async/await spider
现在都已经8102年了，我们应该使用async/await来完成异步编程时的流程控制了。

### promisify API

稍有一点async/await基础的话，我们都知道，await后面是必须跟promise对象的，现在有很多比较新的库都会以promise based作为自己的亮点，比如说网络请求库axios，以及数据库操作的orm库sequelize，如果是这种promise based API的话，那我们可以很容易地与async/await很好地相处。当然如果是以传统的callback based API的话，那我们可能得需要先对他们做promisify

比如说旧版node.js的fs模块的readFile。我们可以自己把它封装Promise式的异步操作。如下：
```js
// 对 fs 模块进行 Promise 封装
const readFile = function(src) {
    return new Promise((resolve,reject) => {
        fs.readFile(src,(err,data) => {
            if(err) reject(err);
            resolve(data);
        })
    })
}
```
其实 **关键**就在于Promise的constructor中传入的那个function参数，我们的异步逻辑将写在这里。使用resolve传入data或者reject传入err，来在完成异步耗时处理之后将promise对象的由pending状态settle成fulfilled状态或者rejected状态

以下是一个通用的promisify代码
```js
// utilities.js
module.exports.promisify = function(callbackBasedApi) {
  return function promisified() {
    const args = [].slice.call(arguments);
    return new Promise((resolve, reject) => {
      args.push((err, result) => {
        // callbackBaseApi的回调函数通常放在参数的最后一位
        if (err) {
          return reject(err);
        }
        if (arguments.length <= 2) {
          resolve(result);
        } else {
          resolve([].slice.call(arguments, 1));
        }
      });
      callbackBasedApi.apply(null, args);
    });
  }
};
```
这或许已经是一个写得很好的promisify代码，但是如果是在生产环境使用，秉承着DRY的原则，我们还是建议找一些较好的第三方开源库中的实现。

### async/await spider
```js
const utilities = require('./utilities');
const request = utilities.promisify(require('request'));
const mkdirp = utilities.promisify(require('mkdirp'));
const fs = require('fs');
const readFile = utilities.promisify(fs.readFile);
const writeFile = utilities.promisify(fs.writeFile);

async function download(url, filename){
    try {
        console.log(`Downloading ${url}`);
        let response = await request(url);
        await writeFile(filename, response.body);
        console.log(`Downloaded and saved ${url}`) // callback
    } catch (err) {
        console.log(`download err: `, err);
    }
}
```
通过在asyncFunction里await一个promise对象，现在我们既可以保证，writeFile这个异步任务将在request这个异步任务之后执行，又可以避免写出callback hell的代码，还能较好地捕获异常

## 并行控制流的最佳实践promise.all

目前的async函数里的await耗时操作只能串行执行

来自MDN的例子
```js
async function add1(x) { 
  var a = await resolveAfter2Seconds(20); 
  var b = await resolveAfter2Seconds(30); 
  return x + a + b; 
}
```
也就是a有结果了才会去执行b的await。所以我们大概需要等2+2=4秒

换一种写法
```js
async function add2(x) {
  var a = resolveAfter2Seconds(20);
  var b = resolveAfter2Seconds(30);
  return x + await a + await b;
}
```
这下我们只需要等2秒就够了。这里a和b的resolveAfter2Seconds()是几乎“并行”调用的，但是a和b的结果依然是串行获得的。
如果想同时await多个Promise对象必须使用[Promise.all()](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)
```js
async function add3(x){
    var arr = await Promise.all([resolveAfter2Seconds(20),resolveAfter2Seconds(30)])
    // arr = [20,30]
    return x + arr[0] + arr[1]
}
```
`Promise.all`的参数应该是一个可迭代对象iterable，比如Array或String，一般情况下我们会传入一个由promise对象所组成的Array，但是另一方面这个Array也可以包含非promise对象的其他值。

await这个`Promise.all`将返回一个数组，如果`Promise.all`里的所有promise对象都被settle为fulfilled，那么这个数组将是这组promise所resolve的data。如果其中有一个promise被rejected了，那将返回reject的error