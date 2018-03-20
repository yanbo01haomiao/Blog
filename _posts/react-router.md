# react router及code spilting

这篇博文介绍比较基础的react-router 4.0的用法以及如何实现代码分片。（深入的我也介绍不来。。）

## react-router v4.0

react router V4.0有哪些API，怎么实现嵌套路由，默认路由什么的请看[react-router doc](https://reacttraining.com/react-router/web/example/basic)。其实基本上把Examples里的例子过一遍就可以了，大部分情况下都能在里面找到相应的example参考

### 静态路由和动态路由

在react router v3.0我们会写类似这样一个路由文件
```js
//src/Routes.js
import {Router, Router, browserHistory} from 'react-router'
//...
const Routes = () => (
    <Router history={browserHistory}>
        <Route path='/' component={App}>
            <Route path='about' component={About}/>
            <Route path='contact' component={Contact}/>
            //...
        </Route>
    </Router>
)
export default Routes
```
然后将这样的路由文件像引用组件一样引进app里
```js
import Routes from './Routes.js'

ReactDOM.render(
    <Routes />,
    document.getElementById('root')
)
```
这样的方式使用路由，形式上是使用组件的方式，实际上这些组件并没有像render之类的方法。他的工作流程类似以下：Router组件根据所有的子组件Route，生成全局的路由表，路由表中记录了path与UI组件的映射关系，然后Router监听path的变化，当path变化时，根据新的path，找出对应所需的所有UI组件，按一定层级将这些UI组件渲染出来。

笼统地说静态路由就是我们app在渲染组件之前写下一个静态的路由配置文件。虽然说这样的react-router也依然运作良好，但是react router官方却不满足这样的方式。在react router v4.0里，加入了动态路由的概念。所谓动态路由：
> When we say dynamic routing, we mean routing that takes place as your app is rendering, not in a configuration or convention outside of a running app. That means almost everything is a component in React Router

说实话，脱离代码实践想要真正理解什么是动态路由和静态路由的区别是什么这些问题是很困难的。

### Personal Blog demo
我这里以一个简单的博客系统的路由来介绍一下react-router，当然这更多地是为后面的code spilting做准备。

#### 需求分析
- 顶栏有一个TopMenu，其中有【主页】【博客】【关于】三个tab
- 当点击【关于】时出现侧边栏，有【默认】【学校】【年龄】【名字】几个按钮，点击会展示相应的视图

这个需求很粗糙。。不过我们主要就是为了简单介绍react router的用法，【关于】的侧边栏是为了展示嵌套路由的用法。

#### 文件结构(src下)
- components
  - AboutPage
  - BlogPage
  - IndexPage
  - SideBar
  - TopMenu
  - TextBlock
- App.js
- index.js

#### 引入BrowserRouter
```js
//F:\caistrong\react-demo\react-router-demo\src\index.js
import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(
<BrowserRouter>
    <App />
</BrowserRouter>, 
document.getElementById('root'));
registerServiceWorker();
```
如果不在app顶层引入BrowseRouter，那么直接在App里面使用<Route/><Link/>这些东西会报错。

#### App.js里面路由布局
```js
//F:\caistrong\react-demo\react-router-demo\src\App.js
class App extends Component {
  render() {
    return (
      <div className="App">
        <TopMenu/>
        <Switch>
          <Route exact path="/" component={IndexPage}></Route>
          <Route path="/blog" component={BlogPage}></Route>
          <Route path="/about" component={AboutPage}></Route>
          <Route component={NotFound}></Route>
        </Switch>
      </div>
    );
  }
}
```
#### TopMenu
```js
//F:\caistrong\react-demo\react-router-demo\src\components\TopMenu\index.js
const TopMenu = () => (
    <nav>
        <ul className="top-list">
            <li><Link to="/">主页</Link></li>
            <li><Link to="/blog">博客</Link></li>
            <li><Link to="/about">关于</Link></li>
        </ul>
    </nav>
)
```
#### AboutPage
IndexPage和BlogPage里面大概都类似
```js
const BlogPage = () => (
    <div>博客页</div>
)
```
所以主要介绍下AboutPage,因为这里有嵌套路由
```js
//F:\caistrong\react-demo\react-router-demo\src\components\AboutPage\index.js
const AboutPage = () => (
    <div className="about-page">
        <SideBar></SideBar>
        <div className="about-detail">
            <Route path="/about/age" render={()=>(TextBlock({text:'18'}))}></Route>
            <Route path="/about/school" render={()=>(TextBlock({text:'xiamen university'}))}></Route>
            <Route path="/about/name" render={()=>(TextBlock({text:'cai'}))}></Route>
            <Route exact path="/about" render={()=>(TextBlock({text:'关于默认'}))}></Route>
        </div>
    </div>
)
//*render: func这个Props是一个简便的渲染组件的方法，和传component效果是一样的*
```
react router v4版本的嵌套路由不用再像v3那样在<Route/>里面嵌套<Route/>，而是直接在你想加入的组件里用<Route/>这种写法很自由。现在可以把<Route/>当作一个真正的组件来看待。考虑 UI=render(state) 这时你把location也当作一种state。当location发生改变时，path与之相match的<Route/>组件将得到render。这样的路由系统的思想很“React”

### Code Spilting

在create-react-app默认的webpack配置下，我们的应用最后的所有逻辑会被打包成一个JavaScript文件bundle。所有使用我们App的用户在初次访问我们的app都会下载这一个bundle.js。我偷偷看了我的小demo打包出来的bundle.js大小有185kb。毫无疑问随着我们应用的逻辑边复杂这个bundle.js将会越来越大。这样到最后会导致用户第一次访问我们的App时将长时间等待bundle.js文件下载。我们解决这个问题的策略就是[webpack doc Code Spilting](https://webpack.js.org/guides/code-splitting/)。

我们讲一下webpack文档介绍的三种方法中的Dynamic Imports
实际上在[react router doc Code Splitting](https://reacttraining.com/react-router/web/guides/code-splitting)和[jamiebuilds/react-loadable](https://github.com/jamiebuilds/react-loadable)这里也有较为详细的使用方法

以我们的demo为例，我们可以在BlogPage组件里按我们原来写组件的方法写好组件
```js
//F:\caistrong\react-demo\react-router-demo\src\components\BlogPage\index.js
const BlogPage = () => (
    <div>博客页</div>
)

export default BlogPage
```
在需要引入这个BlogPage的地方
```js
//F:\caistrong\react-demo\react-router-demo\src\App.js
import Loadable from 'react-loadable'

const LoadableBlogPage = Loadable({
  loader: () => import('./components/BlogPage'),
  loading: () => (
      <div>加载中...</div>
    )
})
<Route path="/blog" component={LoadableBlogPage}></Route>
```

或者也可以直接在模块里暴露出LoadableComponent
```js
//F:\caistrong\react-demo\react-router-demo\src\components\IndexPage\index.js
import Loadable from 'react-loadable'

const LoadableIndexPage = Loadable({
    loader: () => import('./IndexPage'),
    loading: () => (
        <div>加载中...</div>
    )
})

export default LoadableIndexPage
```
这样需要引用的地方直接
```js
import IndexPage from './components/IndexPage'
<Route exact path="/" component={IndexPage}></Route>
```

当我们在代码里使用了import()来动态加载组件之后，并且我们的webpack.config里面有
```js
output: {
    chunkFilename: 'static/js/[name].[chunkhash:8].chunk.js',
}
```
然后
```js
npm run build
```

之后我们可以发现F:\caistrong\react-demo\react-router-demo\build\static\js下除了bundle.js之外还有三个xxx.chunk.js啥的。我们成功把代码分片！

实际效果就是，我们在进入首页的时候，只会下载bundle.js和index.chunk.js。而BlogPage和AboutPage的逻辑我们不会下载，只有在我们点击Blog按钮跳转到BlogPage这个组件时，后台才去下载blog.chunk.js。

*我code spliting之后bundle变成190kb,比之前更大了，而各个chunk.js都只有2k左右这样子，猜测时因为BlogPage的组件逻辑太过于简单，为了实现懒加载引入的代码大于分出去的chunk的代码。所以在懒加载组件的时候不应该所有组件都懒加载，最好是对那种逻辑复杂并且不出现在首屏、不常用的组件懒加载带来的收益最大。*