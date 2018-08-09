# 异常处理

这里的异常处理思想，不仅限用于koa，只是koa为例，这里是自己小小的一点经验之谈和思考，谈不上最佳实践，仅供参考。

## 异常

我们在业务开发中，常常会遇到很多异常。这里我觉得大概可以将异常分为几类：

1. 程序错误：
- 比如说读取一个未定义对象的属性，`unvar.user`，会报can't read 'name' from undefined
- 一些语法错误，`JSON.parse('{"name":"蔡晓聪"errrror,}')` 会报Unexpected token e in JSON at position 13
- ...
程序错误是可以我们通过修改代码来规避的，比如使用 unvar ? unvar.user : {}这样的方式来避免读取一个未定义的对象的属性，至于语法错误则直接改正语法。程序错误可以称为是bug。

2. 操作异常：
- 连接数据库服务器失败：作为I/O操作的一种，有各种原因可能导致我们连接数据库出现失败
- 请求网络接口失败/超时：服务器宕机、服务器高负载崩溃、网速过慢等等都可能导致网络I/O失败
- 系统内存满载：某个操作需要申请内存，而内存已经满载了
- ...
这些异常算是偶现的异常，他随时有可能出现，捕获异常并处理可以保证我们的程序不会因为这些异常直接崩溃

3. 业务异常：
- 用户访问某个资源无权限：比如说用户cai想访问qq.com/chen/profile，这时候服务端返回的{code: '1000041', message: '暂无权限'}。这实际上不是error，而是一个正常返回的响应，告知前端该用户无权限
- 用户查询的某篇文章不存在：比如用户输入qq.com/posts?id=10000，这时可能会发请求去拿id为10000的文章，服务端一查数据库，发现没有这个文章。则返回{code: '1000404', message: '文章不存在'}
- ...
这些“异常”其实不是真正的异常，程序本身并没有出错，而是正常处理了请求，只是存在业务逻辑上的异常。用户做出了业务逻辑不允许的操作。

## 异常处理

业务开发中对异常的处理的需求比较多样，我这里说说自己见到过的一些常见的处理方法。

1. 打日志： 程序抛出异常时打日志到机器上或某个远程服务器上是最常见的作法，这可以方便程序员调试。
2. 告知调用方：返回状态码code和消息message给调用方也是常见的作法。特别是当调用方传了错误的参数（HTTP status code 400），或者服务器错误(HTTP status code 500)
3. 重试：一些诸如网络操作超时，可能只要重新执行操作就能成功的可以在异常处理中直接重试
4. 其他...

### 前端异常处理

这里插个题外话，对于一些HTTP Web接口，我们经常会定义一系列自定义的状态码和消息，例如：
```js
{code: '0', message: '成功', data: { name: '蔡晓聪' } }
{code: '1000041', message: '暂无权限'}
{code: '1000042', message: '登录失败'}
{code: '1000043', message: '网络超时'}
{code: '1000044', message: '支付失败'}
```
这是上面异常处理的`告知调用方`，这时候前端可以根据收到的这些状态码，对异常进行统一处理，比如说封装一下网络请求库，判断code的值，根据不同的code做出不同的处理，例如展示一些toast告知用户。我们在下面也将对这类处理做一点探讨。

## 业务开发中常见的问题

**多处异常处理，程序比较混乱**

```js
class UserService {
    async getUserInfo(ctx) {
        try { // 这里的try catch可以去掉
            return await new Promise((resolve, reject) => {
                setTimeout(resolve(JSON.parse('{"name":"蔡晓聪"errrror,}')), 100) //JSON.parse()这里会报错
            })
        } catch (err) {
            console.log('UserService | getUserInfo ERROR!: ', err) // Logger for Debug
        }
    }
}

class UserController {
    async getUser(ctx) {
        try {
            let result = await service.getUserInfo();
        } catch (err) {
            console.log('UserController | getUserInfo ERROR!: ', err) // Logger for Debug
        }
    };
}
router.get('user', UserController.getUser)
```
我们在后端可能会有一个类似Router->Controller->Service这样的异步调用链。

对于这样一个异步调用链而言，其实Service的Error是可以被Router或者像这里的Controller Catch的，因此可以只在Controller做异常处理即可

**统一异常处理有没有问题？**

1. 其实相对于 **程序比较混乱** 这样的问题而言，**程序不可用**的问题更严重一些。如果我们在getUserInfo中不处理异常，那我们需要程序里调用链最终调用getUserInfo的那个函数做了异常处理。或者是在koa web server最开头加入异常处理中间件来兜底，这点下面会提到。

2. 我们可能会在Service里新建一个`const logger = require('./log_util')('UserService')`然后在catch的块里使用这个logger来打印日志，在Service里不做异常处理我们就没办法把error日志打进UserService_20180807.log的日志文件了。不过只是在catch块里的错误日志无法打印，正常的请求、响应、耗时之类的日志是可以打印的。

**那要不还是不统一处理了还是到处都try catch把？**

一个我在业务中常见并且感觉比较困惑的例子：
```js
class UserService {
    async getUserInfo(ctx) {
        try {
            // 期待的返回 {name: '蔡晓聪'}
            let result = await user.findById(ctx.query.id); // 这里查数据库|网络超时|报错！跳到catch块
            return result; // |id查不到用户|的时候result也是undefined
        } catch (err) {
            console.log('UserService | getUserInfo ERROR!: ', err) // Logger for Debug
            // catch块里无return 语句，因此这个函数的返回值是undefined
        }
    }
}

class UserController {
    async getUser(ctx) {
        try {
            let result = await new UserService().getUserInfo();
            return result.name; // 以为能得到数据，但实际有可能result是undefined，这里也会抛错,只好return result ? result.name: ''
        } catch (err) {
            console.log('UserController | getUserInfo ERROR!: ', err) // Logger for Debug
            return {
                code: '500',
                msg: '服务器系统内部报错'
            }
        }
    };
}
router.get('user', UserController.getUser)
```
因为UserController里面使用了try catch但实际上是他根本不会捕获到new UserService().getUserInfo()的任何错误，这个函数的错误在内部已经被处理了。

所以 |该id查不到用户| 以及 |网络超时| 这两类异常对于UserController.getUser来说是透明的，他都是得到一个undefined的result。当我们想返回给用户错误信息的时候，只好笼统地返回
服务系统内部出错

当然我们也可以选择在UserService.getUserInfo里的catch返回 { code: '400', msg: '网络请求超时'}，然后判断if(!result) return {code: '400', msg: 'id查不到用户'}。
不过这样的话，在Controller.getUser()里的result.name就不会报错，而是返回undefined，毕竟result对象存在，只是没有name这个属性，只有code和msg属性。

我觉得上面的这些暴露一个问题：**程序是不可控的**，我不知道不可控是否用词准确，但是至少我觉得是难以维护。

**那有没有一套较好的异常处理实践呢？**

## koa 官方wiki

我在koa github的wiki里找到了[Error Handling](https://github.com/koajs/koa/wiki/Error-Handling)，这里提供了一些错误处理的建议

1. 在koa的第一个中间件里添加Error Handling Middleware，用来兜底异常。我们知道koa的洋葱模型，所以每一次调用最终结果返回之前经过的中间件就是第一个中间件，因此这个中间可以来兜底捕获异常

2. 在这个错误处理中间件里用ctx.app这个EventEmiter实例来emit一个error事件，然后app监听error事件来做异常的中心化处理

3. 使用ctx.throw来抛出异常

```js
const Koa = require('koa');
const app = new Koa();

// 统一的Error Handler
app.use(async (ctx, next) => {
    try {
        await next();
    } catch (err) {
        ctx.status = err.status || 500;
        ctx.body = err;
        if(ctx.status === 500){
            ctx.body = {
                code: 500,
                message: '服务器内部出错'
            }
        }//这个if是一个粗糙实现
        ctx.app.emit('error', err, ctx);
    }
});

app.use(async (ctx, next) => {
    let {id} = ctx.query
    if(!id) ctx.throw(400, {code: '100014', message: '未输入id参数'})
    await getUserInfo(ctx, id)
    ctx.body ='Hello World'
})

app.listen(3003, () => {
    console.log('Server running at 3003')
})

//监听error进行中心化处理
app.on('error', (err, ctx) => {
    console.log('logger error to file: ', err)
})

//模拟我们Service里的方法
async function getUserInfo(ctx, id) {
    let userInfo;
    // let name = userInfo.name; // 被动的抛错误
    userInfo = await user.findById(id);
    if(!userInfo) ctx.throw(404, {code: '100015', message: '找不到该用户'});
}
```
### 优势

根据这套解决方案，现在我们在引入了Error Handler Middleware之后，**理想情况下**在我们的业务逻辑任何地方都不需要再处理异常，只需要在恰当的时候抛出 **业务异常**即可，例如在上面，我们接收用户的请求，判断用户是否传了id过来，没有传的情况则直接ctx.throw抛出异常，抛出的同时带上一些code、message之类的信息即可。同时对于 **程序错误** 、**操作异常**我们无需关心，因为系统会替我们抛出异常。

ctx.throw抛出异常后，后面的代码逻辑将不再执行，而是直接跳到catch了这个异常的代码块，在我们这里的示例中只有Error Handler Middleware捕获了异常，所以我们得以执行该Middleware的catch代码块里的逻辑，赋值响应状态码，将err对象赋值给了响应体，emit一个Error事件等等。

之后在监听error事件的回调里面，我们将错误进行统一处理，如果是在生产环境我们可以给他打印到一个统一的Error_20180807.log之类的日志里。

### koa这里统一异常处理的一些说明

以上面那段demo代码为例，我做了一些异常处理的实践

1. 业务异常处理1

get localhost:3000

这时由于为传?id=4这个参数所以程序执行到
```js
if(!id) ctx.throw(400, {code: '100014', message: '未输入id参数'})
```
这条语句时抛错到Error Handler Middleware处理，ctx.body被设为这个error，同时app.on('error')这里也会打印日志
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/koa-error-handle/errorrsp.png)

2. 业务异常处理2

get localhost:3000?id=4

这次传了id了，但是我们假设
```js
userInfo = await user.findById(id);
if(!userInfo) ctx.throw(404, {code: '100015', message: '找不到该用户'})
```
这句代码，这里在数据库没找到该id的用户，所以userInfo为undefined，这里其实和1是一样的，这些都是上面讲的异常类型3 业务异常

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/koa-error-handle/errorrsp2.png)

3. 程序错误处理

get localhost:3000?id=4 并去掉// let name = userInfo.name; 这行代码的注释

这里我们访问了一个undefined对像的name错误，这里应该报一个程序错误，这就不是业务异常了，而是服务器错误，我们在这里没有像1、2那样使用ctx.throw抛错。因为其实系统会帮我们自动throw Error。这个Error呢，也会被Error Handler Middleware所处理，由于默认是500错误，因此我们就判断`if(ctx.status === 500)`返回服务器内部的message
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/koa-error-handle/errorrsp3.png)

4. 调用链外的异常捕获

在写这篇文章的时候，我去调研了下阿里的企业级node框架egg里处理异常的方式[egg异常处理](https://eggjs.org/zh-cn/core/error-handling.html)，里面提到了一个问题，就是：

当我们使用async await这样的异步编程模型时，我们的koa中的一个又一个中间件，其实是串起来的一个异步调用链，可以去看koa的源码，koa的app里有个属性middleware数组，到后面其实是用了compose(...middleware)。不太严谨的说，可以看成只有一个asyncFunction我们的代码中的所有异步操作都被用await串起来。只要是在调用链内的错误，就都能被我们上面那个Error Handler Middleware所捕获处理。

**那调用链外的呢？**

改写我们的getUserInfo为以下语句（读取userinfo的name属性将报错）：
```js
async function getUserInfo(ctx, id) {
    //...
    let userInfo;
    setImmediate(async () => {
        let name = await new Promise(resolve => {
            resolve(userInfo.name)
        })
    })
    //...
}
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/koa-error-handle/uncaughtasync.png)
我们发现这里的异常没被我们那个统一的Error Handler Middleware所捕获，客户端接收到了正常的响应Hello World，然后控制台接收到了这个异常，输出如上。

对于调用链外的异常，我们只好单独去捕获，如下：

```js
async function getUserInfo(ctx, id) {
    //...
    let userInfo;
    setImmediate(async () => {
        try {
            let name = await new Promise(resolve => {
                resolve(userInfo.name)
            })
        } catch (err) {
            console.log('跳出作用链的错误: ', err);
        }
    })
    //...
}
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/koa-error-handle/caughtasync.png)

*关于这点，我没有想到什么具体的业务场景会需要调用链外捕获异常，所以这个丑陋的方法应该也不会太常用*

5. 异常被提前截取

当我回过头去看项目里的框架代码的时候，我发现实际上框架是有做统一的异常处理的，有一个error_handler中间件，同时还定义了BusinessError来表示我们的业务异常。但是在实际项目中，我发现这个error_handler并没有真正处理到这些异常，原因是我们在业务逻辑中，**还是使用了try catch**。我下面讲一下这样的作法可能带来的问题：

我们将我们的service里的getUserInfo方法改为以下：
```js
async function getUserInfo(ctx, id) {
    try {
        let userInfo;
        if(!userInfo) ctx.throw(404, {code: '100015', message: '找不到该用户'})
    } catch (err) {
        ctx.body = err
    }
}
```
我们可能觉得在这里把异常处理了，同时设定为ctx.body = err，这样前端也会和我们统一处理Error Handler Middleware一样，将{code: '100015', message: '找不到该用户'}返回给用户。

然而实际上get localhost:3000?id=4之后我们发现
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/koa-error-handle/helloworld.png)
**异常信息没有返回！**
原因是
```js
await getUserInfo(ctx, id)
ctx.body ='Hello World'
```
虽然在getUserInfo里我们的catch块执行了，并且把ctx.body设置为我们想返回的结果了，但是后面的业务逻辑可能又把ctx.body改成其他的了。而统一的Error Handler Middleware本来就是一个 **兜底**的中间件，只可能他修改别人改好的ctx.body，他设置的不可能被别人修改。这个 **兜底** 很重要，因此在koa的洋葱模型中，统一error middleware放在第一个，而在express中一般放在最后一个。这就是原因之一。所以我觉得如果我们有了统一处理异常的Error Handler Middleware之后，应该尽量就不要在业务逻辑中直接使用try catch了