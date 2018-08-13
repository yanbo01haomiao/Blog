# 构建同构JavaScript应用

## 背景

JavaScript原先绝大多数的应用场景都只是在浏览器端当一些脚本做一些动画。开始学习Vue的时候，我很疑惑的是，我写运行在浏览器端的程序，却一开始要我装Node.js装NPM这些服务端的东西。其实Node.js最开始很大的作用就是来帮前端做工程化、模块化这些东西。我们现在快速搭建一个Vue工程的时候会使用vue/cli，然后会使用`vue init wepack demo`这样的语句来初始化一个工程。起初我只是照本宣科地打了这些命令，对为什么要做这些有些迷茫，前端难道不是应该写一个html页面，然后link一些css样式，然后script进一些js文件，在js文件里我们对html的一些元素绑定一些监听事件，如果我们需要用到jQuery **模块**的话我们就在我们的js文件之前使用script引入一个cdn上或者线下的jQuery.js的文件等等这样的步骤来写吗？

我大概是2016年开始接触前端的，当时的前端其实已经过了上面这样刀耕火种的时代，三大框架基本奠定了各自的地位，webpack应该也已经是冉冉升起。前端工程化早就成了既定的事实。但彼时的我其实对此有些懵懵懂懂，只觉得麻烦。废话少说，我想在此试图再说说我们用vue/cli或者create-react-app这些东西到底为了什么

vue/cli初始化完成后我们观察webpack.base.conf.js文件发现`./src/main.js`是我们前端工程的入口文件。webpack会通过分析这个入口文件，去找里面import/require的模块，然后层层分析，最后打包出一个bundle文件，我们接着在html里使用script引入这个bundle文件。感性一点的讲`<script src='bundle.js'></script>`这行伪代码简直是前端新时代同旧时代的接口。

我试图解释一下这一点：

在ES6之前的时代，JS是没有`模块化`的概念的，我们使用的很多有那么点像模块的东西，例如jQuery都是将自己的API附加在一个$的全局对象上以供后面的代码引用。直到后来Node.js出现了，既然Node.js想用JavaScript来写服务端，那么没有模块系统是完全不可能的，因此Node.js带来了CommonJS模块系统。我们得以使用`require`和`module.exports`来编写模块化的JavaScript程序。然而CommonJS虽然好用，但是也仅限Node.js服务端程序使用。这时候前端出现了一系列的打包工具，比如Browserify还有现在大行其道的Webpack，他们将使用了`require`、`module.exports`等的JS代码通过编译成类似模块模式的方式。使其能在浏览器端表现得像服务器端一样的具有模块系统。（如果对这一点的实现有什么疑惑的话，可以去了解一下Universal Module Definition。）

后来ES6带来了大家期待已久的ES6 Module，作为ES的新标准，目前浏览器端及Node都在推进支持这一新特性。在得到广泛的原生支持之前，我们仍将长期需要使用Webpack配合Babel来将其转译为功能等价的ES5代码以获得较好的兼容性。

绕了这么大的圈子，最后我想说为什么我说`<script src='bundle.js'></script>`这行伪代码简直是前端新时代同旧时代的接口呢。在`./src/main.js`这个文件里面，以及文件里所`require`或者`import`的任何模块里，我们可以随意地使用CommonJS和ES6 Module，当然还可以使用其他任何ES6乃至更新的语法。同时我们也可以引入Vue、Less、SCSS、PUG、PNG等等，Webpack都会将其当作JS模块进行打包。`./src/main.js`这边就是前端新时代的王国，我们可以享受无数现代框架、工具、语法，还有十分重要的一点是我们能够随意引用npm库里成千上万的package、甚至是部分Node.js的core module来编写我们的 **前端**代码，只需要在编写完之后经过Webpack 编译出一个bundle.js文件，编译的过程就是一个将未来的前端代码转换成兼容当前市场上各式各样浏览器的bundle.js文件，然后我们使用`<script src='bundle.js'></script>`将这个文件引入前端页面。完成前端新旧时代的连接。

**然而这一点和我们要讲的同构JavaScript有什么关系呢？**

我们知道，浏览器(Chrome)和Node.js是两个不同的运行环境（Runtime），虽然他们都使用V8作为JavaScript引擎。但是仍然存在着许多Runtime上的差异。例如在浏览器端我们有document、window、XMLHttpRequest这些对象而Node.js是没有的。Node.js有fs、process等等一些核心模块，这也是浏览器没有的。所谓同构JavaScript，其实就是能够运行在多个端的同一个JavaScript程序（我们这里主要指Node.js服务端和浏览器端，可能未来随着物联网的发展还会有更多跑JavaScript的终端出现）。那既然一段代码想要在Node.js和浏览器上同时运行，他就得避免使用依赖于环境的API.举个例子，比如对于一个网络请求库，用于发起一个Ajax请求，假设他是通过包装XMLHttpRequest对象的方法来实现的，那么这个网络请求库就只能在浏览器端使用。相反的，比如Node.js的fs模块，用于操作操作系统的文件系统。而浏览器端是不允许JavaScript脚本操作文件的，所以即使Webpack对像`http`、`assert`、`events`等提供了兼容浏览器的版本，但`fs`模块仍然不被兼容。

目前有越来越多的第三方库同时支持了浏览器和Node.js，比如axios网络请求库，虽然没有看过源码，但我还是猜测里面实现了类似于
```js
let ajax = env === browser ? wrap(XMLHTTPRequest) : wrap(http.request)
```
这个伪代码一样的逻辑，抹平了不同Runtime的差异提供了一套相同的http client接口。就像Node.js里的libuv所做的那样

## 跨平台开发的基础

统而言之，我们现在的目标就是让一个JavaScript应用能在多个Runtime中运行，在这里特指Node.js Runtime和Chrome等浏览器的Runtime。那么同构JavaScript的基础在于对于Node.js和浏览器，他们存在大部分的通用的代码，例如他们都实现了EcmaScript的标准语法，他们都有Date、Math、JSON等等这样的内置对象。而同构JavaScript的挑战在于不管是Node.js还是浏览器，他们都存在一些平台特殊（platform-specific）的东西。某些特定的对象/API仅在浏览器端/Node.js端实现。当我们编写同构的JavaScript程序的同时，就需要针对这些特殊的地方提供兼容两种环境的实现。我们有大致以下几种方法来做这个兼容：

- Runtime Code Branching
- Build-Time Code Branching
- Module Swapping

### 运行时代码分支（Runtime Code Branching）

我们在编写代码时使用类似如下的方式:
```js
// runtime_branching.js
if(typeof window !== "undefined" && window.document) {  
    //client side code  
    console.log('Hey browser!');
} else {  
    //Node.js code  
    console.log('Hey Node.js!');
}
```
这个思路特别简单易懂，我们使用`node runtime_branching.js`将会打印Hey Node.js
而在浏览器控制台运行时将会打印Hey browser...当然我们也就可以在client side code这个分支里使用document.innerHtml之类的client-side API。

这个思路虽然简单易懂，但他存在如下一些缺点：

1. 针对不同平台（Browser和Node.js）的代码糅合在同一个模块里被打包进最后的bundle里，当这个bundle代码运行在Browser时，Node.js分支的代码是unreachable code，这里存在冗余和浪费

2. 类似的runtime code branching被广泛使用时，将降低代码的可读性。代码中混合里业务逻辑代码以及这些纯粹为了跨平台兼容的适应代码。

3. 根据不同的平台动态加载模块时将把多个平台的模块代码都打包进bundle，如下：

```js
// webpack 打包是build-time还没到runtime所以无法知道这里的if condition是true还是false，因此将把两个require的module都打包进去
if(typeof window !== "undefined" && window.document) {         
    require('clientModule');       
} else {         
    require('serverModule');       
}
```

### 编译时代码分支（Build-time Code Branching）

既然运行时代码分支存在上述的缺点，我们再来看看编译时代码分支是怎么做的。

```js
// main.js
if (typeof __BROWSER__ !== "undefined") {
    console.log('Hey browser!');
} else {  
    console.log('Hey Node.js!');
}
```
看起来和运行时代码分支有点像..但是毫无疑问，我们这里的关键就是让`__BROWSER__`这个变量的值在编译时就得到确定。因此我们来看webpack.config.js文件
```js
const path = require('path');
const webpack = require('webpack');

const definePlugin = new webpack.DefinePlugin({
    "__BROWSER__": "true"
})

const uglifyJsPlugin = new webpack.optimize.UglifyJsPlugin({
    beautify: true,
    dead_code: true
})

module.exports = {  
    entry:  path.join(__dirname, "src", "main.js"),  
    output: {    
        path: path.join(__dirname, "dist"),    
        filename: "bundle.js"  
    },
    plugins: [definePlugin, uglifyJsPlugin]
}
```

Emmm...这里可以理解Webpack的Plugins是会改变编译时的处理流程(process pipeline)，可以简单理解，在编译开始时，definePlugin会给`__BROWSE__`赋值为"true"，这时UglifyJsPlugin就会发现
```js
else {  
    console.log('Hey Node.js!');
}
```
这里的代码是dead_code，也就是将永远不会被用到的部分代码，因此将会把他剔除。

编译时代码分支解决了运行时代码分支存在的一些问题比如剔除了unreachable code避免了冗余和浪费，然而还有一些问题仍未得到解决，比如说业务逻辑和兼容性代码混合在一起等等

### Module Swaping

除了上面两种Branching外还有一种解决该问题的思路是Module Swaping.

当涉及到具有平台特殊（platform-specific）的代码时，我们就针对不同的平台，例如Node.js和浏览器各写一份代码模块。如果是通用性的代码则公用代码模块。

例如我们针对不同的平台使用不同的策略来输出提示信息

```js
// alertServer.js (Node.js Side INFO module
module.exports = console.log
```

```js
// alertBrowser.js (Browser Side INFO module
module.exports = alert
```
以上就是有平台特殊（platform-specific）的地方，我们在Node.js使用控制台输出来提示用户，在浏览器使用alert弹窗来提示用户。而下面是同构公用的代码部分
```js
// main.js
const alert = require('./alertServer')
alert('Hello World!')
```

这下我们使用`node main.js`将在控制台看到打印的信息Hello World!.现在当我们想要在浏览器运行这段代码的使用我们应该怎么做呢？

直接将main.js复制进浏览器console然后执行吗？好吧当然不行，在背景里讲了，我们的浏览器不支持require，我们需要用webpack打包出一个bundle再script引进html。好那我们现在来看看怎样打包出这个bundle

```js
// webpack.config.js
const path = require('path')
const webpack = require('webpack')

const moduleReplacementPlugin = new webpack.NormalModuleReplacementPlugin(/alertServer.js$/, './alertBrowser.js');

module.exports = {
    entry: path.join(__dirname, "src", "main.js"),
    output: {
        path: path.join(__dirname, "dist"),
        filename: "bundle.js"
    }
    plugins: [moduleReplacementPlugin]
}
```
同样，plugin是影响process pipeline的，所以在编译的过程中，他把`require('./alertServer')`替换成了`require('./alertBrowser.js')`，因此在最后的bundle.js里我们是使用了alert而不是console.log来显示提示信息的，现在我们可以将bundle.js引入html，用浏览器打开看到alert弹窗的Hello World！了

将平台特殊（platform-specific）的地方分成两个模块写还带来了一个好处，比如说现在我们想在浏览器使用新的提示方式，改用开源的npm package toastr来提示信息，我们只要改变alertBrowser.js的代码为
```js
// alertBrowser.js
const toastr = require('toastr')
module.exports = toastr.info
```
其余一切皆无需改变即可适应新的需求

同时这种方式解决了几乎所有运行时代码分支带来的问题.业务逻辑和兼容代码不再糅合在一起，而是将兼容不同平台的处理提到了webpack编译的阶段解决。

### Vue-SSR里client-entry和server-entry

我想大多数人对于同构代码应该都会有一个疑惑，所以我们干嘛需要写一个能在浏览器端和Node.js服务端共同运行的代码？这是伪需求吗？我们在浏览器写的那些监听点击事件、提交Ajax请求到后台的前端程序，需要在Node.js运行？？Node.js里写的那些handle request的web API接口程序需要在浏览器里运行？？？

上面的问号确实是值得思考的问题，其实到目前为止，所为同构JavaScript应用，我所见的几乎所有使用的场景，都是为了服务端渲染（Server-Side-Rendering）。

Vue-SSR在服务端渲染时，同一份前端工程的代码，分别在前端和服务端使用，为了达到服务端渲染的目的（包括了不同平台的不同数据预取方式）时采取的兼容性策略，有别于我们上面所讲的所有策略，但同时又和Module Swaping有异曲同工之妙。

Vue-SSR和上面的Module Swaping的相同之处在于对于平台特殊（platform-specific）的地方也分成了两个模块写（client-entry和server-entry）。不同的地方在于Module Swaping只有一个webpack配置文件一次打包供前端使用，而Vue-SSR分别为浏览器端和Node.js端各写了一个配置文件，分两次打包。有两个入口。公用的代码则是前端main.js（app.js）里的代码

在这里我简单介绍下Vue服务端渲染的流程。

首先就是对于一个我们即将在服务端和前端都运行的vue前端代码，假设其入口为`src/app.js`，这一边就是我们会共用的前端代码...
```js
//src/app.js
export function createApp () {

  const store = createStore()
  const router = createRouter()

  sync(store, router)

  const app = new Vue({
    router,
    store,
    render: h => h(App)
  })

  return { app, router, store }
}
```
这个入口暴露出了一个API为createApp，由名字推测出这个API用于创建vue应用实例，当然这里还把router和store也暴露了出来，原因是等下在浏览器和Node.js不同的入口会对这两个有不同的处理。

Vue-SSR对前端工程在浏览器运行还是在Node.js服务端运行分为了两个接口，分别是entry-client和server-entry。并在这两个入口里面分别做了平台特殊（platform-specific）兼容性和业务逻辑的处理。

我们先来看我们熟悉的entry-client怎样去进入这个Vue应用实例，以下是一段简化的代码：

```js
//entry-client.js
import { createApp } from './app'

const { app, router, store } = createApp()
// 服务端渲染会将预取的数据放在window对象的__INITIAL_STATE__
if (window.__INITIAL_STATE__) {
  store.replaceState(window.__INITIAL_STATE__)
}

router.onReady(() => {
  // 客户端渲染的方式就是把Vue实例给挂载在Html的body下的一个div容器下
  app.$mount('#app')
})
```
我们在webpack编译的阶段时，为entry-client写了一个单独的配置文件（简化后如下：）
```js
//webpack.client.config.js
const webpack = require('webpack')
const merge = require('webpack-merge')
const base = require('./webpack.base.config')
const VueSSRClientPlugin = require('vue-server-renderer/client-plugin')

const config = merge(base, {
  entry: {
    app: './src/entry-client.js'
  }
  plugins: [
    // ...
    new VueSSRClientPlugin()
  ]
})

module.exports = config
```
其实这里也非常明了，以往我们完全的客户端渲染的逻辑是，用户请求一个index.html文件，这个index.html里面大概类似
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Vue.js App</title>
    </style>
  </head>
  <body>
    <div href="#app"></div>
    <script src="cdn.qq.com/path/to/bundle.js"></script>
  </body>
</html>
```
然后浏览器去下载script里的bundle.js这个bundle.js就是我们以我们上面的entry-client.js为入口用webpack打包后的js文件，这个js文件把编译好的vue组件，mount挂在到这个id为#app的div下，然后我们看到了视图blabla，这个相信不必多说熟悉单页应用的大家都懂。

这种客户端渲染的方式除了SEO以外最大的问题就是首页渲染时间太慢，先下index.html再下bundle.js，再DOM操作挂载Vue组件，Vue组件再发Ajax请求去拿数据，拿完数据再rerender一遍视图...

所以服务端渲染的其实说到底就是当我们的用户第一次加载首页的时候，我们就将直接返回给用户带有视图和数据的html而不是一个空的html，例如
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Vue.js App</title>
    </style>
  </head>
  <body>
    <div href="#app"><h1>Hello Cai!</h1></div>
    <script src="cdn.qq.com/path/to/bundle.js"></script>
  </body>
</html>
```
这下SEO和首页渲染的问题都搞定了，这里我们依然去引入bundle.js，依然保留了客户端的入口，以 **激活**Vue引用，除了首次加载之外（不一定是首页）的其他页面的渲染还是交给客户端来。

那怎么去做服务端渲染呢，我们看一下服务端入口entry-server.js
```js
import { createApp } from './app'

export default context => {
  return new Promise((resolve, reject) => {
    const { app, router, store } = createApp()
    // 这个逻辑可以使我们不止渲染cai.com，还能使cai.com/about，cai.com/posts/1等页面都能用服务端渲染
    const { url } = context
    router.push(url) 

    router.onReady(() => {
      const matchedComponents = router.getMatchedComponents()
      // 这里的逻辑就是数据预取
      Promise.all(matchedComponents.map(({ asyncData }) => asyncData && asyncData({
        store,
        route: router.currentRoute
      }))).then(() => {
        // window.__INITIAL_STATE__ = context.state
        context.state = store.state
        resolve(app)
      }).catch(reject)
    }, reject)
  })
}
```
同样我们为entry-server.js编写一个webpack配置
```js
// webpack.server.config.js
const webpack = require('webpack')
const merge = require('webpack-merge')
const base = require('./webpack.base.config')
const VueSSRServerPlugin = require('vue-server-renderer/server-plugin')

module.exports = merge(base, {
  target: 'node',
  devtool: '#source-map',
  entry: './src/entry-server.js',
  output: {
    filename: 'server-bundle.js',
    libraryTarget: 'commonjs2'
  },
  plugins: [
    //...
    new VueSSRServerPlugin()
  ]
})
```
这个时候理论上我们也打包出了一个bundle，我们这里称他server-bundle,以区分客户端渲染script引入的那个bundle。这个bundle怎么用呢...

看一下我们的server.js：
```js
const fs = require('fs')
const path = require('path')
const express = require('express')
const { createBundleRenderer } = require('vue-server-renderer')

const app = express()

const template = fs.readFileSync(path.resolve(__dirname, './src/index.template.html'), 'utf-8')
const bundle = require('./dist/vue-ssr-server-bundle.json')
const clientManifest = require('./dist/vue-ssr-client-manifest.json')
let renderer = createBundleRenderer(bundle, {
    template,
    clientManifest
})

app.get('*',(req, res) =>{
  const context = {
    title: 'Vue HN 2.0', // default title
    url: req.url
  }
  renderer.renderToString(context, (err, html) => {
    res.send(html)
  })
})

const port = process.env.PORT || 8080
app.listen(port, () => {
  console.log(`server started at localhost:${port}`)
})
```
这里关键就在于`createBundleRenderer`和`renderToString`，最后得到的那个带视图带数据的html页面就被我们`res.send(html)`.

至于React应用的服务端渲染，基本上做的事情也和Vue-SSR一样，只不过所使用的API，数据预取等等方式不太一样。这里或许应该找个机会把Vue-SSR和React-SSR都实现一个demo可能会理解得更透彻一点。先挖个坑。
