# 我们是不是真的需要bindActionCreators
## bindActionCreators(actionCreators, dispatch)
最近在公司项目里面发现了有使用这一API，光看代码有点云里雾里所以去看了源码，发现源码还挺易懂的。

### 参数
**actionCreators (Function or Object)**: An action creator, or an object whose values are action creators.
**dispatch (Function)**: A dispatch function available on the Store instance.

### 返回值
(Function or Object): An object mimicking(模仿) the original object, but with each function immediately dispatching the action returned by the corresponding(相应) action creator. If you passed a function as actionCreators, the return value will also be a single function.

### 使用场景
假设我们有一个action creator
```js
//actions.js
function getContent(id) {
    const url = `cai.com/articles/${id}`
    return async (dispatch) => {
        dispatch( {type: GET_ARTICLE_START} )
        try {
            let res = await fetch(url)
            if(res.status !== 200){
                throw new Error(`Fail to get response with status ${response.status}`)
            }
            let data = await response.json()
            dispatch( {type: GET_ARTICLE_SUCCESS} )
        }catch (err) {
            dispatch( {type: GET_ARTICLE_FAILURE} )
            alert("获取文章内容失败")
        }
    }
}
export default {
    getContent
}
```
这个时候我们的一个组件，比如说ArticleView想要使用这个action creators
```js
//ArticleView.js
import artAction from './actions.js'

class ArticleView extends Component {
    render(){
        //...
    }
    componentDidMount(){
        this.props.getContent(123)
        //组件装载完毕后就dispatch一个action来更改状态树，Store状态树改变后，render的视图就会刷新
    }
}
const mapDispatchToProps = dispatch => ({
    ...bindActionCreators(artAction, dispatch),
})
// 如果我们不使用bindActionCreators则mapDispatchToProps
const mapDispatchToProps = dispatch => ({
    getContent: () => dispatch(artAction.getContent)
})
export default connect(null,mapDispatchToProps)(ArticleView)
```

## bindActionCreators.js源码
```js
//https://github.com/reactjs/redux/blob/master/src/bindActionCreators.js
function bindActionCreator(actionCreator, dispatch) {
  return function() {
    return dispatch(actionCreator.apply(this, arguments))
  }
}

export default function bindActionCreators(actionCreators, dispatch) {
  if (typeof actionCreators === 'function') {
    return bindActionCreator(actionCreators, dispatch)
  }

  if (typeof actionCreators !== 'object' || actionCreators === null) {
    throw new Error(
      `bindActionCreators expected an object or a function, instead received ${
        actionCreators === null ? 'null' : typeof actionCreators
      }. ` +
        `Did you write "import ActionCreators from" instead of "import * as ActionCreators from"?`
    )
  }

  const keys = Object.keys(actionCreators)
  const boundActionCreators = {}
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i]
    const actionCreator = actionCreators[key]
    if (typeof actionCreator === 'function') {
      boundActionCreators[key] = bindActionCreator(actionCreator, dispatch)
    }
  }
  return boundActionCreators
}
```

### 关键代码
```js
function bindActionCreator(actionCreator, dispatch) {
  return function() {
    return dispatch(actionCreator.apply(this, arguments))
  }
}
```
我们传入的getContent最后会作为actionCreator传入，这个时候返回一个新的匿名函数，这个匿名函数就是我们最后在视图里使用的this.props.getContent(123).

当我们在视图的componentDidMount()钩子函数，调用this.props.getContent(123)，实际上就是调用了如下一个函数
```js
(function() {
   return dispatch(actionCreator.apply(this, arguments))
})(123)
```
这个时候就相当于调用了
```js
dispatch(actionCreator.apply(this, arguments))
```
并把结果返回（这里我们在componentDidMount()没有接收这个返回值），arguments是为了接收参数，比如这里的id123
```js
dispatch(
    async (dispatch) => {
        dispatch( {type: GET_ARTICLE_START} )
        try {
            let res = await fetch(url)
            if(res.status !== 200){
                throw new Error(`Fail to get response with status ${response.status}`)
            }
            let data = await response.json()
            dispatch( {type: GET_ARTICLE_SUCCESS} )
        }catch (err) {
            dispatch( {type: GET_ARTICLE_FAILURE} )
            alert("获取文章内容失败")
        }
    }
)
```
### 误区
本文对于bindActionCreators的使用不符合[redux文档对bindActionCreators的适用场景的描述](https://cn.redux.js.org/docs/api/bindActionCreators.html)，所以可能不是最佳实践

## 结论
bindActionCreators这个函数的源码看起来并不那么神奇，实际上他做的事情也很少，无非就是帮我们做了dispatch(action creator)这一步。我们使用bindActionCreators的作用可能只限于避免写出
```js
const mapDispatchToProps = dispatch => ({
    getContent: () => dispatch(artAction.getContent),
    getUserinfo: () => dispatch(artAction.getUserinfo),
    getWeather: () => dispatch(artAction.getWeather),
})
```
这样的模板代码。我觉得使用bindActionCreators确实会比上面这样的模板代码好看一点。但是他同样带来了缺点
```js
const mapDispatchToProps = dispatch => ({
    ...bindActionCreators(artAction, dispatch),
})
```
我们无法在mapDispatchToProps里面直观地看出props有多少属性。同时像React里面这样的数不胜数的框架、库、API不计其数（例如redux-actions）。每次一有类似的需求就引入一个新的库、框架、API。不仅会使我们应用的依赖趋于复杂，同时也会增加后人理解代码看懂代码的难度。我们需要去考虑这样的交易是否值得。