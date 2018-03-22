# koa2源码初探

今天浪费了一点时间看了koa2源码，心想时间都浪费了不然顺便做下记录...

## koa2简单使用
从需求驱动开发的思想出发，我们先来看看我们怎么使用koa
```js
//  ./middleware/logger-async.js
function log( ctx ) {
    console.log( ctx.method, ctx.header.host + ctx.url )
}

module.exports = function () {
  return async function ( ctx, next ) {
    log(ctx);
    await next()
  }
}
```

```js
// ./main.js
import Koa from 'koa'
import staticServeMiddleware from 'koa-static'
const loggerAsync  = require('./middleware/logger-async')

const app = new Koa()

app.use(loggerAsync())
app.use(staticServeMiddleware('./dist'))

app.listen(8080)
```

简略概括使用koa的过程就是，我们先new一个Koa（源码里的class Application）的实例，然后使用app.use()往里面添加一个个middleware，其中middleware一般来自开源npm库或者自己按middleware的接口规范编写。最后再使用app.listen()监听某个端口启动app。


## 源码初探
接下去我们探究一下上面那个过程的细节。
```js
const app = new Koa()
```
这行代码构造一个新的Koa()实例，所以自然是执行了Koa 源码里Application 这个类里的 constructor，我们来看看这里的代码
```js
//https://github.com/koajs/koa/blob/master/lib/application.js
const response = require('./response');
const context = require('./context');
const request = require('./request');

module.exports = class Application extends Emitter {
  constructor() {
    super();

    this.proxy = false;
    this.middleware = [];
    this.subdomainOffset = 2;
    this.env = process.env.NODE_ENV || 'development';
    this.context = Object.create(context);
    this.request = Object.create(request);
    this.response = Object.create(response);
  }
```
这里的代码不难理解，注意下middleware就行，其中./response，./context，./request是Koa源码的另外三个js文件，整个koa源码就由这三个js加上本身的application.js构成，短小精悍，感觉实在是不能更优雅了。

```js
app.use(loggerAsync())
```
接下去我们来看看上面的代码执行了什么
```js
//https://github.com/koajs/koa/blob/master/lib/application.js
use(fn) {
    if (typeof fn !== 'function') throw new TypeError('middleware must be a function!');
    if (isGeneratorFunction(fn)) {
      deprecate('Support for generators will be removed in v3. ' +
                'See the documentation for examples of how to convert old middleware ' +
                'https://github.com/koajs/koa/blob/master/docs/migration.md');
      fn = convert(fn);
    }
    debug('use %s', fn._name || fn.name || '-');
    this.middleware.push(fn);
    return this;
}
```
从use方法的逻辑，我们可以看到使用koa2时，传进app.use()里的async function都经历了什么，首先在koa1里中间件使用的是generator funtion，它会被convert成async function。另外这个app.use并不实际执行async function(中间件)的逻辑，而只是把这个async function(中间件)添加到middleware数组里。

最后是我们的重头戏
```js
app.listen(8080)
```
这一行短小的代码实际上做了很多的事，完成了整个app的启动工作
```js
//https://github.com/koajs/koa/blob/master/lib/application.js
listen(...args) {
    debug('listen');
    const server = http.createServer(this.callback());
    return server.listen(...args);
}
```
listen(8080)里面直接引用了node的http模块来创建一个服务器程序，其中传进去的this.callback()就是Nodejs里的[requestListener](https://nodejs.org/dist/latest-v8.x/docs/api/http.html#http_http_createserver_requestlistener)

按照[w3schools的说法](https://www.w3schools.com/nodejs/func_http_requestlistener.asp)
> The requestListener is a function that is called each time the server gets a request.

我们可以简单地理解为this.callback()这个函数会再每次服务器接收到请求地时候被调用。

我们先来看一下用node创建一个hello world server app
```js
var http = require('http');
http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.write('Hello World!');
  res.end();
}).listen(8080);
```
这里我们可以得到2个信息
1. koa的listen其实就是对node http模块的http.createServer的封装而已
2. 我们传入的this.callback这个requestListener会被注入Nodejs的requset和respone这两个参数

接下去我们来看一下this.callback()这个函数的逻辑
```js
//https://github.com/koajs/koa/blob/master/lib/application.js
const compose = require('koa-compose');
callback() {
    const fn = compose(this.middleware);

    if (!this.listeners('error').length) this.on('error', this.onerror);

    const handleRequest = (req, res) => {
      const ctx = this.createContext(req, res);
      return this.handleRequest(ctx, fn);
    };

    return handleRequest;
}
```
这里使用了koa-compose这个模块并把我们的middleware中间件数组传了进去，这里的compose是决定我们Koa中间件编写规范以及执行顺序的的关键，我们来看一下这个compose函数的源码
```js
//https://github.com/koajs/compose/blob/master/index.js
function compose (middleware) {
    //...
  return function (context, next) {
    // last called middleware #
    let index = -1
    return dispatch(0)
    function dispatch (i) {
      if (i <= index) return Promise.reject(new Error('next() called multiple times'))
      index = i
      let fn = middleware[i]
      if (i === middleware.length) fn = next
      if (!fn) return Promise.resolve()
      try {
        return Promise.resolve(fn(context, function next () {
          return dispatch(i + 1)
        }))
      } catch (err) {
        return Promise.reject(err)
      }
    }
  }
}
```
我们可以看到在
```js
Promise.resolve(fn(context, function next () {
          return dispatch(i + 1)
        }))
```
传进入context和next参数，我们回忆一下我们的koa中间件规定的写法，啊！几乎一目了然
```js
async function ( ctx, next ) {
    log(ctx);
    await next()
  }
```
我们的async fucntion的await后面必须接一个promise对象，next函数返回的dispatch(i+1)调用结果正好就是promise对象

我们总结一下
```js
const fn = compose(this.middleware);
```
这行代码的逻辑，我们的this.middleware是一个有诸多async function(中间件)对象的数组，使用compose后，这些多个async function(中间件)被整合成一个function，也就是我们上面的fn,这个fn里面包括了我们的koa app所有对request的处理逻辑。参照我们的koa中间件模型，这个fn可以说就是整个构建整个"洋葱"，或者我们参照DOM 的事件机制，这个fn就是整个app收到request请求时的“事件处理函数”
### koa的中间件模型
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/koa-source/koa-middleware.png)

官方给了一段代码和解释来介绍这个模型
```js
const Koa = require('koa');
const app = new Koa();

// x-response-time

app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  ctx.set('X-Response-Time', `${ms}ms`);
});

// logger

app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  console.log(`${ctx.method} ${ctx.url} - ${ms}`);
});

// response

app.use(async ctx => {
  ctx.body = 'Hello World';
});

app.listen(3000);
```
> 下面以 “Hello World” 的响应作为示例，首先请求流通过 x-response-time 和 logging 中间件来请求何时开始，然后继续移交控制给 response 中间件。当一个中间件调用 next() 则该函数暂停并将控制传递给定义的下一个中间件。当在下游没有更多的中间件执行后，堆栈将展开并且每个中间件恢复执行其上游行为。

*下游 对应洋葱模型可以理解为 内层，上游则是外层*

接下去我们继续看callback()里的代码
```js
//https://github.com/koajs/koa/blob/master/lib/application.js
//callback()...
    const handleRequest = (req, res) => {
      const ctx = this.createContext(req, res);
      return this.handleRequest(ctx, fn);
    };

return handleRequest;
```
我们最后这个return 的这个handleRequest就是Nodejs里的[requestListener](https://nodejs.org/dist/latest-v8.x/docs/api/http.html#http_http_createserver_requestlistener)
参照nodejs helloworld
```js
var http = require('http');
http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.write('Hello World!');
  res.end();
}).listen(8080);
```
我们的handleRequest就相当于传入http.createServer的那个匿名函数，也就是说我们传入createContext的那两个参数req和res其实就是nodejs的request对象和response对象
接着我们看看createContext()这个方法

```js
//https://github.com/koajs/koa/blob/master/lib/application.js
createContext(req, res) {
    const context = Object.create(this.context);
    const request = context.request = Object.create(this.request);
    const response = context.response = Object.create(this.response);
    context.app = request.app = response.app = this;
    context.req = request.req = response.req = req;
    context.res = request.res = response.res = res;
    request.ctx = response.ctx = context;
    request.response = response;
    response.request = request;
    context.originalUrl = request.originalUrl = req.url;
    context.cookies = new Cookies(req, res, {
        keys: this.keys,
        secure: request.secure
    });
    request.ip = request.ips[0] || req.socket.remoteAddress || '';
    context.accept = request.accept = accepts(req);
    context.state = {};
    return context;
}
```
我们创建了context.request和context.response这两个koa的req和res对象，同时
nodejs里的req和res赋值给了context.req和context.res这两个属性。关于这一点在[koa的文档](https://koa.bootcss.com/)里上下文（context）也有说到。最后返回的这个context。也就是我们在中间件中经常使用的那个ctx。我们把ctx传入handleRequest()里。
```js
//https://github.com/koajs/koa/blob/master/lib/application.js
 handleRequest(ctx, fnMiddleware) {
    const res = ctx.res;
    res.statusCode = 404;
    const onerror = err => ctx.onerror(err);
    const handleResponse = () => respond(ctx);
    onFinished(res, onerror);
    return fnMiddleware(ctx).then(handleResponse).catch(onerror);
  }
```
```js
//https://github.com/koajs/koa/blob/master/lib/application.js
function respond(ctx) {
  
  let body = ctx.body;
  const code = ctx.status;
  //...省略一些健壮性，缓存等处理
  body = JSON.stringify(body);

  res.end(body);
}
```
respond可以视为我们的最**内层**的中间件，所以没有next，作用就是返回响应给客户端。fnMiddleware就是我们刚刚那个“洋葱”，当request以异步的方式被这个洋葱一层一层处理完之后，会返回一个promise。我们在then里面添加最后一层异步逻辑，待“洋葱”处理完request后返回响应给客户端。

### 参考资料
[koa2 中文文档](https://koa.bootcss.com/)
[w3schools Node.js requestListener() Function](https://www.w3schools.com/nodejs/func_http_requestlistener.asp)
[github koa](https://github.com/koajs/koa)
[github koa-compose](https://github.com/koajs/compose)