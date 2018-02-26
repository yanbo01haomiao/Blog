# JavaScript async/await 基础

从几个月前学习node.js开始，我在JavaScript异步编程上面费了不少功夫。网上有很多文章讲了JavaScript异步编程从回调函数到Promise链式调用到tj/co+Generator函数到最后AsyncFunction的技术演变。我看过不少类似的文章。其中tj大神的co让我很是震撼，可以说AsyncFunction本质上也是co+Generator函数的那一套，ECMAScript 2017引入了async/await可以看作又是社区发展到最后成为标准的又一典例。我刚刚在自己电脑上测试了AsyncFunction，chrome和edge浏览器都可以顺利运行，既然已经成为了标准，那么async/await也便成为了JavaScript异步编程的未来，所以我今天想总结一下他的基础用法，并在今后的实践中使用它。

## 代码相关

先来一段MDN上的代码，感性认识一下AsyncFunction：
```js
function resolveAfter2Seconds() {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve('resolved');
    }, 2000);
  });
}

async function asyncCall() {
  console.log('calling');
  var result = await resolveAfter2Seconds();
  console.log(result);
  // expected output: "resolved"
}

asyncCall();
```
## AsyncFuntion

我们知道，在JavaScript中的函数也是对象，我们普通的函数可以使用new Function()这样的方式来调用，上面的asyncCall是一个AsyncFunction的实例，而AsyncFunction继承了Function，因此异步函数的使用方法也和普通函数差不多，也可以调用bind()、call()、apply()这些函数。比较重要的区别在于**await关键字只能出现在async函数定义的上下文中，即使是async内部的普通函数也不能使用await**

## await

async函数带来一个非常大的好处在于，**用同步写法来写异步操作**，如果单看AsyncFuncion，我们对这一点的体会可能不太深刻，所以你如果无法体会这个好处，建议再去试试用回调函数或者Promise链等等去写异步操作。

在AsyncFunction中，我们的**await后面跟的是一个Promise对象实例**，例如IO、Ajax、setTimeout之类的耗时操作就放在await后面。不过**前提是这些耗时操作的API要返回Promise对象**，比如说现在很火的Ajax网络库[axios](https://github.com/axios/axios)，他的API调用结果就是返回Promise对象的。

不过有些时候，我们还是会遇到一些回调函数式的异步操作API，比如说旧版node.js的fs模块的readFile。我们可以自己把它封装Promise式的异步操作。如下：
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
把像上面这样异步操作Promise化之后，我们就可以把这个操作放在async函数里的await后面了
```js
let result = await readFile('a.txt')
```
这个时候err（调用失败）或者data（调用成功）的值就会被传给result。

**假设await后面接的不是Promise对象**，而是一些基本类型的值，比如说
```js
let result = await 123
```
这时系统会调用Promise.resolve(123)，将其转为一个resolve的Promise对象，这时候其实相当于同步操作，我们一般不这样写。

还有一点是，比如一开头的那段代码中:

```js
var result = await resolveAfter2Seconds();
```
**resolveAfter2Seconds()这个函数的返回值是Promise对象实例，而result的结果却是那个string值为'resolved'，而不是Promise对象实例**

## 返回值

AsyncFunction的返回值也是一个Promise对象，所接收的值就是函数return的值。也可以理解就是系统又对这个值做了Promise.solve()，**如果AsyncFunction没有显示地return，则返回值是最后一个await后面接的那个Promise对象**，关于这里其实可以和生成器函数的yield做点对比，同时既然AsyncFunction的返回值也是一个Promise，**因此我们也可以在await后面接asyncCall()这样的异步函数的调用。**

## 异常处理

由于await后面是Promise对象，而这个对象有可能结果是rejected,所以最好把await命令放在try...catch代码块中，避免await后面的Promise对象被rejected之后导致整个AsyncFunction中断执行。
```js
async function foo() {
  // 放在try...catch里，这下somethingThatReturnsAPromise()被rejected也不怕了
  try {
    await somethingThatReturnsAPromise();
    // throws 'aha..error'  
    // 自己抛，自己接
  } catch (err) {
    console.log(err);
  }
  // throws 'woo..error'  
  //自己抛，调用foo的接
}
```

## 并发执行

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

####  参考资料

[MDN async function](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Statements/async_function)
[我眼中的 async/await](https://zhuanlan.zhihu.com/p/33932184)
[async 函数的含义和用法 by阮一峰](http://www.ruanyifeng.com/blog/2015/05/async.html)