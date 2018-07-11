# 我们使用require引入一个模块的时候都发生了什么

关于Node的模块系统，网络上充斥着各种各样的教程文章。比如分析module.exports和exports的区别，比如专门开题讲node的循环依赖。比如分析ES modules和CommonJS模块系统的异同。我并不是想批判这样的文章不好，毕竟我之前也看过/写过这样的文章。而是在某种程度上，我们去从源码的角度了解一下Node是如何实现模块系统的可能可以带来事半功倍的效果，因为实际上他并不太复杂。今天我从《Node.js Design Patterns 2th》中看到了相关的内容。他提供了简化过的模块系统demo代码。

## 模块系统的使用

根据需求驱动开发的原则，我们先来看下我们怎么使用Node的模块系统。
```js
// 加载另一个模块
const dependency = require('./anotherModule');
// 模块内的私有函数
function log() {
  console.log(`Well done ${dependency.username}`);
}
// 通过导出API实现共有方法
module.exports.run = () => {
  log();
};
```
待会看源码demo的时候可以对照这里的调用方式看。

## resolve算法

require.resolve函数是看懂Node模块系统demo代码的基础，所以我先讲一下resolve。不过由于该函数的实现较为复杂，所以我在这里把他当成黑盒，只去看相应的输入输出效果。

该函数的输入形参我们定为moduleName，输出我在这里定义为fileName（其实更接近filePath）.

moduleName分为两种情况

1. 不以/或./开头，则resolve算法首先在Nodejs核心模块(path、http、fs..)中搜索，有则返回，没有则搜索当前目录下的node_modules，没有则搜上层目录下的node_modules直到文件系统的根目录。还是没有则抛错。

2. 以/或./开头。如果以/则是绝对路径(很少用)，./则是相对路径，相对使用require模块的位置开始计算。

对于文件模块和模块包，当moduleName不带后缀或者为文件名时，resolve算法将按顺序尝试匹配以下内容：

1. `<moduleName>.js`
2. `<moduleName>/index.js`
3. `<moduleName>/package.json`的main值下声明的文件或目录


require.resolve将返回文件在文件系统中的绝对路径(这是一个唯一值)

## loadModule函数

```js
function loadModule(filename, module, require) {
  const wrappedSrc = `(function(module, exports, require) {
         ${fs.readFileSync(filename, 'utf8')}
       })(module, module.exports, require);`;
  eval(wrappedSrc);
}
```

我们看一些关键点：

- wrappedSrc里面除了插入了我们读取的filename的内容以外，还用一个IIFE（立即执行函数）包裹，目的是为了通过函数，创建一个独立的作用域，不污染全局作用域。

- 我们在I/O读取文件的时候使用同步的readFileSync而不是异步的readFile

- module（对象）、module.exports（对象）、require（函数）被作为参数传进了模块，所以我们在模块中的代码可以直接引用module、exports、require。（这下知道我们的模块使用里的第一句require这个函数是哪来的了吧）

- eval存在安全隐患，是不被提倡的做法，这里我们只是做一个例子。

## 重头戏require函数

还是先看代码
```js
const require = (moduleName) => {
  console.log(`Require invoked for module: ${moduleName}`);
  const id = require.resolve(moduleName);
  // 是否命中缓存
  if (require.cache[id]) {
    return require.cache[id].exports;
  }
  // 定义module
  const module = {
    exports: {},
    id: id
  };
  // 新模块引入，存入缓存
  require.cache[id] = module;
  // 加载模块
  loadModule(id, module, require);
  // 返回导出的变量
  return module.exports;
};
require.cache = {};
require.resolve = (moduleName) => {
  /* 通过模块名作为参数resolve一个完整的模块 */
};
```
我们可以来看下当我们使用require引入一个模块的时候都发生了什么：

1. 模块名称moduleName被作为参数传入，然后我们使用require.resolve()找到我们引入的模块地址。并赋值给id，准备作为键值。

2. 如果模块不是第一次被加载，那么应该可以在缓存中找到，所以直接return缓存中的数据。函数结束。（这里可以保证我们的程序中多次引入一个模块将得到一样的输出）

3. 如果模块是首次加载，那么我们初始化一个模块对象，里面有一个exports空对象。我们把这个模块对象存入缓存

4. 然后我们加载模块，加载模块用了上面那个loadModule函数，可以看成是执行了下面这个代码：

```js
const module = {exports: {},id: id};
const require = (moduleName) => { ... };
//IIFE
(function(module, exports, require) {
    //↓模块内容
    const dependency = require('./anotherModule');
    function log() {
        console.log(`Well done ${dependency.username}`);
    }
    module.exports.run = () => {
        log();
    };
})(module, module.exports, require);
```
我想这很容易理解，差不多就是下面两点
- 传进module,require这些，然后把模块代码执行一遍
- 模块代码中通过给exports.run这样的方式，**填充**原本的空对象module.exports

5. 最后把这个被填充了模块想要导出的内容的module.exports返回出去

## 万变之宗

现在我们大概知道了require函数都做了什么，也对Node的模块系统有了一定的了解。我们可以来看看以前困惑我们的一些问题的答案。

### module.exports和exports

```js
// ✔ 
exports.hello = () => {
  console.log('Hello');
}

// ✖
exports = () => {
  console.log('Hello');
}

// ✔
module.exports = () => {
  console.log('Hello');
}
```

根据上面我们分析的源码demo:

- 实参是module.exports，形参是exports，所以函数传参的时候相当于执行了 exports = module.exports = {}（初始是空对象）
- 第二种方法直接把exports指向了一个新的对象（hello函数），exports失去了对module.exports的引用。所以此时module.exports 还是等于 {}
- 第一种方法使用exports.hello = ()=>{...}这时exports指向module.exports，所以exports = module.exports = { hello: ()=>{...} }
- 第三种方法则是exports = module.exports = () => {...}

### 循环依赖

- 模块a.js
```js
exports.loaded = false;
const b = require('./b');
module.exports = {
  bWasLoaded: b.loaded,
  loaded: true
};
```

- 模块b.js
```js
exports.loaded = false;
const a = require('./a');
module.exports = {
  aWasLoaded: a.loaded,
  loaded: true
};
```

- main.js
```js
const a = require('./a');
const b = require('./b');
console.log(a);
console.log(b);
```

分析main.js的执行：

1. 首先require('./a')由于是第一次加载，所以执行a.js的代码。
2. 执行a代码执行到require('./b')时，由于b也是第一次加载，所以转向执行b.js代码。
3. 执行b代码执行到require('./a')时由于非首次加载，所以从缓存中直接拿a的module.exports的值，此时为{ loaded:false }（因为1执行a.js时其实只执行了第一行）
4. 接着执行b代码，b代码完全执行完。module.exports的结果为{ aWasLoaded: false, loaded: true }
5. 返回2那里刚刚a代码执行到第二行，接着执行完后面的代码。modules.exports的结果为 { bWasLoaded: true, loaded: true }
6. 回到main.js代码，接着从第二行执行require('./b')。非首次执行，直接从缓存里读到{ aWasLoaded: false, loaded: true }
7. 最终结果
```
{
  bWasLoaded: true,
  loaded: true
}
{
  aWasLoaded: false,
  loaded: true
}
```

### require是同步操作

```js
//serverConfig.js
const config = {}
getRemoteConfigAsync('configserver.qq.com/config', (err,res)=>{
    if(err) handleErr(err)
    config.port = res.config.port
})
module.exports = config
```

```js
//app.js
const http = require('http')
const config = require('./serverConfig') 

http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello World\n');
}).listen(config.port || 3000, '127.0.0.1');

console.log('Server running at', host, port);
```

这里是一个例子，假设我们启动app的配置需要去远程服务器上取。因为require是同步的，所以在这个例子中我们从./serverConfig里拿到的config永远是空对象{}，所以我们的app将永远启动在3000端口。

我们可以将serverConfig.js的代码改为
```js
const config = {}
config.port = getRemoteConfigSync('configserver.qq.com/config')
module.exports = config
```
**我们应该注意到在源码的Demo里使用readFileSync而不是readFile，正是因为这一原因**
