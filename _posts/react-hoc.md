#  以withRouter出发看React高阶组件

在使用connect(react-redux)和withRouter(react-router)这两个API的时候，当看到了他们的神奇效果之后，我很好奇他们做了什么事，有什么样的意义？
## withRouter的适用场景

1. 避免更新受阻
[react-router的官方文档中的Redux Integration](https://github.com/ReactTraining/react-router/blob/master/packages/react-router/docs/guides/redux.md)中讲了React Router与Redux在大部分时候都相处良好。但是有时候会存在问题，即当路由发生变化（即location对象变化）的时候。有以下两类组件会存在更新受阻的情况。
> 1. The component is connected to redux via connect()(Comp).
> 2. The component is not a "route component", meaning it is not rendered like so: <Route component={SomeConnectedThing}/>

其中1问题就是因为react-redux的connect高阶组件会为传入的参数组件实现shouldComponentUpdate 这个钩子函数，导致**只有prop发生变化时才触发更新相关的生命周期函数(含render)**而很显然，我们的location对象并没有作为prop传入该参数组件

官方推荐的做法是使用withRouter来包裹connect的return value，示例如下
```js
// before
export default connect(mapStateToProps)(Something)

// after
import { withRouter } from 'react-router-dom'
export default withRouter(connect(mapStateToProps)(Something))
```
2. 在组件中意图使用history来控制路由跳转
除了`<Link to="/some/path">`这样声明式的路由跳转，有时候我们也想要编程式的路由跳转。

为了实现编程式路由跳转，使用withRouter的示例如下
```js
import React from "react";
import {withRouter} from "react-router-dom";

class MyComponent extends React.Component {
  ...
  myFunction() {
    this.props.history.push("/some/Path");
  }
  ...
}
export default withRouter(MyComponent);
```
如果我们不使用withRouter来处理(MyComponent)，那么我们这里的this.props就取不到history，会报hitstory is undefiend之类的错。

关于这个适用场景在[react-router v4 使用 history 控制路由跳转](https://github.com/brickspert/blog/issues/3)这里有更详细的记载

## 拒绝做一个调包侠
为了避免成为一个调包侠，我们提两个问题：
1. withRouter除了上述的两种适用场景外，还有没有其他适用场景?
2. withRouter做了些什么，为什么withRouter()后我们的更新受阻的组件就能更新，为什么withRouter()我们就能访问this.props.history。

关于这两个问题的答案我们其实可以从[withRouter API](https://github.com/ReactTraining/react-router/blob/master/packages/react-router/docs/api/withRouter.md)这里找到一点答案。但我想知道更多一点原理。
## React高阶组件(Higher Order Component)

当我开始去了解React高阶组件的时候，我感觉十分惊喜。HOC（指高阶组件，下同）并不是React的一个新鲜的什么神奇的API。实际上他是一种代码（组件）复用的模式。体现了DRY的理念。同时也有函数式编程思想在里面（这一点在connect组件的柯里化中体现得更明显）。可能React框架在未来某一天将会没落，没有人再使用它来构建web app，但是类似的编程智慧将得以延续。

> 简单来说，一个高阶组件就是一个函数，这个函数接受一个组件作为输入，然后返回一个新的组件作为结果，而且，返回的新组件拥有了输入组件所不具有的功能

withRouter的源码并不复杂。我们直接来看下他的源码，结合上面那句话来理解高阶组件
```js
//https://github.com/ReactTraining/react-router/blob/master/packages/react-router/modules/withRouter.js
import React from "react";
import PropTypes from "prop-types";
import hoistStatics from "hoist-non-react-statics";
import Route from "./Route";

/**
 * A public higher-order component to access the imperative API
 */
const withRouter = Component => {
  const C = props => {
    const { wrappedComponentRef, ...remainingProps } = props;
    return (
      <Route
        children={routeComponentProps => (
          <Component
            {...remainingProps}
            {...routeComponentProps}
            ref={wrappedComponentRef}
          />
        )}
      />
    );
  };

  C.displayName = `withRouter(${Component.displayName || Component.name})`;
  C.WrappedComponent = Component;
  C.propTypes = {
    wrappedComponentRef: PropTypes.func
  };

  return hoistStatics(C, Component);
};

export default withRouter;
```

1. Component就是那个被withRouter包裹的组件，也就是withRouter这个高阶组件工厂函数的参数。
2. C这个组件就是即将被返回的那个**增强过的**新组件
3. **routeComponentProps**是我们上面两个适用场景起作用的关键。对react router比较熟悉的话应该能一眼明白我们的withRouter到底做了什么**增强**

如果没看明白关于routeComponentProps部分的话，我们一步一步来：

我们可以看到，我们最后返回的是一个`<Route/>`嵌套`<Component>`的已增强的新组件。
我们先查看[React Router 文档<Route>](https://reacttraining.com/react-router/web/api/Route)
这里我们使用的是children这个Route render methods，查看文档的children: func可以得到两个信息
1. children的这个render function无论该路由是否匹配都会执行渲染。
2. children的render function将接收route props作为参数。这个参数也就是我们上面提到的**routeComponentProps**

查看文档Route props部分可以看到，这个props包含下列三个对象
1. match(https://reacttraining.com/react-router/web/api/match)
2. location(https://reacttraining.com/react-router/web/api/location)
3. history(https://reacttraining.com/react-router/web/api/history)

所以withRouter这个函数到底对我们的参数组件做了什么**增强**，现在已经很明显了，他用Route包裹我们的参数组件，**然后把match、location、history作为props传入我们的参数组件**。

所以在我们的withRouter适用场景1里面，当路由变动，location对象发生了改变，而location对象已经作为props传入我们的参数组件里，这下也就会触发我们的参数组件进入更新过程。因为像connect()为我们实现的默认的shouldComponentUpdate函数就是通过比较Props是否有变动来决定要不要更新的。另外我们也能理解为什么`<Route component={SomeConnectedThing}/>`这样的组件不会更新受阻，就是因为他们本身就有location这个prop

另外，在我们的withRouter适用场景2里面。this.props.history直接使用了传下来的history这个props

这下：上面的两个问题，我想大家心里应该也有了答案，所以所谓withRouter的适用场景其实就是，当你想要访问match、location、history这三个对象的时候吧。

## One More Thing
//（《深入浅出React和Redux技术栈》中高阶组件一章有如何实现一个删减版connect的内容）
除了withRouter外，我们更常使用的connect(from react-redux)也是一个典型的高阶组件。准确的说，他是一个高阶组件构造函数。通过我们传入的mapStateToProps和mapDispatchToProps这两参数构造出一个高阶组件工厂函数。再将我们的只用props来渲染JSX的dumb component作为参数传入这个高阶组件工程函数。返回经过connect()()增强的smart component。其中connect还运用了函数式编程中函数柯里化的思想。简单讲就是
```js 
const add = a => b => a+b
const add1 = add(1)
console.log(add1(2)) //3
```
这里传入的参数1就类比我们传入的mapStateToProps和mapDispatchToProps。我们可以使用add,connect这样的函数来构造很多新的有用的函数，这可以避免我们写出模板代码。我们在配合redux-thunk时书写async action creator的时候，经常会写一些模板代码，例如以下
```js
export const fetchWeatherOf = (city) => {
    return async (dispatch,getState) => {
        const apiUrl = `https://free-api.heweather.com/s6/weather/now?location=${city}&key=${HeweatherKey}`
        dispatch(fetchWeatherStarted())
        try {
            let response = await fetch(apiUrl)
            if(response.status !== 200){
                throw new Error(`Fail to get response with status ${response.status}`)
            }
            let data = await response.json()
            dispatch(fetchWeatherSuccess(data))
        } catch (err) {
            dispatch(fetchWeatherFailure(err))
        }
    }
}
```
这里面的try catch，if(response.status !== 200){...}，还有dispatch的同步的action对象等等...都是一些模板代码。我最近在视图使用函数式编程中柯里化的思想来消除这些模板代码。将一些变量，如fetchWeatherStarted()这些以类似connect(mapStateToProps)的方式传入然后我们就可以生成一堆fetchWeatherOf、fetchCity、fetchUserdata等等函数了。当然具体实现可能会存在问题...这里先挖坑