## 服务器通信与redux-thunk

我们在上一篇文章中所写的react-todo是一个纯粹的本地app。业务中没有涉及与服务器通信的过程。然而在实际的项目中，几乎不可避免地要与服务器进行通信。我懒得建一个新的工程了，我们直接在上一个react-todo里添加新的weather模块来学习与服务器通信和redux-thunk中间件。

我们先来看看**最终成果[在线查看TodoApp](https://caistrong.github.io/react-todo/) && [源码仓库](https://github.com/caistrong/react-todo)**

*在线查看存在跨域问题，请git clone源码仓库然后npm install npm start查看效果*

### 需求分析
- 有两个下拉框可以分别选择省份和城市，当选择完城市后，下面出现该城市当日的天气信息

### 模块文件
- src
  - weather
    - views
      - CitySelector.js
      - Weather.js
      - WeatherInfo.js
    - actions.js
    - actionTypes.js
    - config.js
    - index.js 
    - status.js
    - weatherReducer.js

### API与跨域问题
在这个项目中，我又遇到了跨域的问题。在经过了一番研究之后也对跨域相关问题有了更深入的理解。虽然与本文的目标较无关，但是我还是想在此做一些详细记录。
根据我们的需求分析，现在我们需要两个API接口，一个是可以查询中国所有省/直辖市然后之后可以查询每个省/直辖市下有几个地级市/区。另一接口是可以根据某个地级市/区查询该地今天的天气数据。
我为此找了两个开放的API服务[腾讯位置服务](http://lbs.qq.com/webservice_v1/guide-region.html),[和风天气API](https://www.heweather.com/documents/api/s6/weather-now)
之后我分别申请到了开发者key。并使用PostMan测试了这两个API，发现都正确地返回了数据。然后我将这两个URL以硬编码地方式分别写在actions.js和CitySelector.js的请求中.最后和风天气API顺利地接收到了数据，但是腾讯位置服务却收到了下面的报错
```
Failed to load http://apis.map.qq.com/ws/district/v1/list?key=XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX: No 'Access-Control-Allow-Origin' header is present on the requested resource. Origin 'http://localhost:3000' is therefore not allowed access. If an opaque response serves your needs, set the request's mode to 'no-cors' to fetch the resource with CORS disabled.
```
这个问题的原因在于：
我们的浏览器是有同源限制的，不管是腾讯位置服务，还是和风天气。这里的Ajax请求都是跨域的（域名、端口不同），所以都受到浏览器的同源限制。现代浏览器采用CORS机制来进行跨域。发送请求的时候浏览器自动添加Origin首部，收到响应的时候检查请求报文首部的Access-Control-Allow-Origin里面有没有请求报文首部的Origin的值，没有就报错，有就正常响应。[MDN CORS](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Access_control_CORS)

然而此时和风天气的API发送回的响应首部包含了Access-Control-Allow-Origin：*，因此我们的请求正常返回了数据，而腾讯位置服务的响应报文缺少了Access-Control-Allow-Origin：*，在腾讯位置服务的文档里，我们请求的API属于WebService API。所以腾讯限制了这个API的调用者应该是服务器程序，服务器程序并没有同源限制，自然也就无需往响应报文中添加Access-Control-Allow-Origin首部。这也是我用PostMan为什么能正常返回数据的原因，因为PostMan的底层应该是用一个nginx服务器来发送Ajax请求的。另外当我们在浏览器地址栏中直接输入http://apis.map.qq.com/ws/district/v1/list?key=XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX。我们也可以发现正确地返回了数据。这里我们不也是在浏览器里请求的吗？实际上这里的请求正是在同源（域名、端口相同）下的请求，这种请求不在浏览器同源限制政策的管辖下

找到问题的所在之后，我们开始来解决腾讯位置服务的跨域问题。最直接的解决方法就是，让腾讯的位置服务的后台为这个API添加Access-Control-Allow-Origin：*，当然这个我们目前做不到。其次在react的开发环境中，我们可以使用自带的一个简易的代理服务器来转发我们的请求，我们可以在package.json里添加一行
```js
"proxy": "http://apis.map.qq.com",
```
同时去掉我们CitySelector.js里面的绝对URL前面的域名直接请求./ws/district/v1/list?key=XXXXX-XXXXX-XXXXX-XXXXX-XXXXX-XXXXX。问题解决。在生产环境中，我们建议自己写一个代理服务器程序。同时由于我的react app是部署在github pages上，没有办法把我的代理服务器也部署上去，因此我们在线查看demo时无法拿到数据...至于jsonp的方法...我这里就不试了...

### weather模块的状态管理
在上篇文章中我们有讲到，并不是应用里的所有状态都要被存在状态树里由redux来管理的。redux最好是用来管理一些**组件间共享的状态**。我们新添加的weather模块会带来一些新的状态，包括但不限于省份列表、城市列表、当前选中城市的天气状态等。我这里把当前选中城市的天气状态放到了redux中，而把省份列表和城市列表的数据直接交给CitySelector来管理。扩展后的状态树如下：
```js
const initState = {
    //...todos、filter
    weather: {
        status: statusTypes.LOADING,
        info: null
    }
}
```
CitySelector自己管理的状态如下:
```js
this.state = {
  provincelist:[],
  curCity:'none',
  citylist:[],
}
```
*实际上我的做法不一定是最佳实践，curCity这个状态可能会其他组件共享，所以让redux去管理或许也很好*

### React组件访问服务器的生命周期

我们这里的CitySelector组件就不使用redux来管理状态，所以访问服务器的逻辑我也写在了组件代码里

**如何关联异步的访问服务器请求和同步的React组件渲染是一个首先面临的问题。**

我们**不可能**在React组件的生命周期中，比如说constructor()或者说componentWillMount()函数里去请求服务器数据，然后等到服务器返回数据后再render()然后将React组件Mount上DOM结构。这样的流程在逻辑上看似合理，但是却不可行。因为JavaScript是单线程的，所以如果让引擎同步地发送Ajax，然后等待服务器返回结果之后再执行下一步。就会导致JavaScript线程被阻塞。所以实际上浏览器是异步地发送Ajax，之后继续执行后面地代码。所以引擎执行render()的时候，你在componentWillMount()函数里发送地Ajax请求还未必收到响应了。

一个可行的解决方案是这样的：
1. 在装载的过程中，因为此时我们还未获得服务器返回的数据。所以我们渲染一个具有初始状态的组件。比如说我们的CitySelector。还未获得服务器数据的时候，省份和城市的下拉框都显示第一个option，显示类似"请选择城市..."
2. 我们在componentDidMount()函数里面发起一个访问服务器的请求，获取省份列表数据然后通过this.setState()方法更新组件的状态，这样框架就会重新执行一遍render()。我们就可以看到组件里显示来自服务端的真实数据了。之所以在componentDidMount()函数里发起服务器请求的原因有二，一是我们的服务器请求有可能依赖已经装载的内容，而是componentDidMount()只在浏览器中执行，所以在做服务端渲染时可以避免发送无意义请求。

我们的CitySelector.js除了选择完城市去获取该城市的天气信息时用到了fetchWeatherOf以外，基本上是自给自足的...
代码如下：(感觉写的比较渣欢迎指出缺陷

```js
//F:\caistrong\react-demo\todo_app\src\weather\views\CitySelector.js
import React,{Component} from 'react'
import { fetchWeatherOf } from '../actions'
import { tencentLbsKey } from '../config'
import { PropTypes } from 'prop-types'

class CitySelector extends Component {
    constructor(props){
        super(props)
        this.initProvinces = this.initProvinces.bind(this)
        this.onProvinceChange = this.onProvinceChange.bind(this)
        this.updateWeather = this.updateWeather.bind(this)
        this.state = {
            provincelist:[],
            curCity:'none',
            citylist:[],
        }
    }
    render(){
        return(
            <div>
                <select onChange={this.onProvinceChange}>
                {
                    [<option value='none' >请选择对应省份...</option>,
                    ...this.state.provincelist.map( (item)=>(
                        <option value={item.id}>{item.fullname}</option>
                    ))]
                }
                </select>
                <select onChange={this.updateWeather}>
                {
                    [<option value='none' selected={this.state.curCity === "none"}>请选择城市...</option>,
                    ...this.state.citylist.map( (item)=>(
                        <option selected={this.state.curCity === item.name} value={item.name}>{item.fullname}</option>
                    ))]
                }
                </select>
            </div>
        )
        // render的return好像必须返回一个“JSX对象”，暂且这样叫他吧。。
    }
    componentDidMount(){
        this.initProvinces()
    }
    onProvinceChange = async (event) =>{
        const apiUrl = `./ws/district/v1/getchildren?id=${event.target.value}&key=${tencentLbsKey}`
        try {
            const response = await fetch(apiUrl)
            if(response.status !== 200){
                throw new Error(`Fail to get response with status ${response.status}`)
            }
            const data = await response.json()
            this.setState({
                curCity: 'none',
                citylist: data.result[0]
            })
            this.context.store.dispatch(fetchWeatherOf())
            //为了避免选择完省份后，天气信息还是上一次选择的城市的Bug
        }catch (err) {
            console.error(err)
        }
    }
    initProvinces = async () => {
        const apiUrl = `./ws/district/v1/list?key=${tencentLbsKey}`
        try {
            const response = await fetch(apiUrl)
            if(response.status !== 200){
                throw new Error(`Fail to get response with status ${response.status}`)
            }
            const data = await response.json()
            this.setState({
                provincelist:data.result[0]
            })
        }catch (err) {
            console.error(err)
        }
    }
    updateWeather = (event) => {
        const city = event.target.value
        this.context.store.dispatch(fetchWeatherOf(city))
        this.setState({
            curCity: event.target.value
        })
    }
}

//这是一个坑！！！如果你想使用this.context.store。除了Provider外，你还需要下面这三行
CitySelector.contextTypes = {
    store: PropTypes.object
}

export default CitySelector
```

### Redux访问服务器与redux-thunk中间件

我们刚刚讲了怎么在解决组件的同步渲染的生命周期中完成异步服务器请求的问题。然而别忘了，我们的app还有一部分的状态是由redux来管理的。可惜的是：我们Redux也是一个同步的单项数据流的操作。views视图dispatch了一个action对象，action对象被分配给所有reducer函数，reducer函数处理完后去更改store上的数据。之后数据会立刻被同步给监听store状态改变的函数，然后引发views的更新过程，重新render()出组件。在我们上述的这个流程中，也没有一个合适的地方来插入异步的访问服务器操作。

实际上上述redux的流程并不完全精确，在redux的处理action对象的流程当中其实还存在着中间件。我们上一篇文章中有给了一个redux数据流图，如果在这个流图上加上redux中间件的位置，大体上如下：（我觉得实际上reducer应该也算是一个redux middleware，所以从逻辑上说reducer和middleware用同一个图例比较好。
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/redux-thunk-middleware/redux-data-flow.png)

当我们使用Store.dispatch()派发一个action对象时，这个action对象实际上不会直接进入reducer被处理，而是会经过一系列的中间件。我们这里要介绍的redux-thunk就是这样一个redux中间件。


我们先来看看我们怎样使用这个中间件：
```js
//F:\caistrong\react-demo\todo_app\src\Store.js
import thunk from 'redux-thunk'

const middlewares = [thunk]
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose
//我们这里还包括了启用redux-devtools中间件的逻辑，可以先不管他
const enhancers = composeEnhancers(applyMiddleware(...middlewares))

const store = createStore(reducer, initState, enhancers)

export default store
```

加了一个中间件的处理过程实际上并不会直接解决异步访问服务器的问题。实际上中间件的处理流程也是一个同步的过程，然而redux-thunk中间件却解决了异步访问服务器的问题，我们来看看其中的奥妙：

#### redux-thunk

**redux-thunk源码**
```js
//https://github.com/gaearon/redux-thunk/blob/master/src/index.js
function createThunkMiddleware(extraArgument) {
  return ({ dispatch, getState }) => next => action => {
    if (typeof action === 'function') {
      return action(dispatch, getState, extraArgument);
    }

    return next(action);
  };
}

const thunk = createThunkMiddleware();
thunk.withExtraArgument = createThunkMiddleware;

export default thunk;
```
以上就是redux-thunk这个中间件的全部源码，只有十几行。而我看懂他却花了不少功夫...

我们可以看到，我们的关键对象thunk是一个函数
```js
const thunk = ({ dispatch, getState }) => next => action => {
  if (typeof action === 'function') {
    return action(dispatch, getState, extraArgument);
  }

  return next(action);
};
```
我们把箭头函数转化为普通函数的写法后大概就是如下
```js
const thunk = function({dispatch, getState}){
  return function(next) {
    return function(action) {
      if (typeof action === 'function') {
        return action(dispatch, getState, extraArgument);
      }

      return next(action);
    }
  }
}
```
实际上这个连续的箭头函数和函数柯里化有一定的关系，核心思想就是，某一个函数要接收n个参数（在这里是dispatch、getState、next、action），然后可以使用JavaScript闭包的语法，先传入t个参数（在这里是dispatch、getState）。然后返回一个接收n-t个参数（next、action）的函数，这里重复了两次这个过程。

我们redux的中间件接口规定：

1. 每一个中间件（比如我们上面的thunk）都会接收到dispatch和getState这两个函数，对应的是Redux Store上两个同名的函数。不过并不是所有中间件都会用得上这两个函数（我们thunk把这两个函数作为参数传递给了action，所以可见，这个action是一个函数，不然咋接收参数啊）。

2. 每一个中间件都必须返回一个接收next参数的函数，这个接受next参数的函数又返回一个接受action参数的函数。（绕了一大圈，实际上就是一层层闭包，一层层封装。。）

所以一个啥都不干的中间件代码大概这样
```js
const doNotingMiddleware = function({dispatch, getState}){
  return function(next) {
    return function(action) {
      return next(action);
      //next是一个函数，调用next函数并传入action，代表把传进来的这个action对象传递给下一个中间件去处理
    }
  }
}
```
对比thunk中间件。我们发现thunk的所有操作实际上就是拦截了类型为function的action对象，然后把dispatch和getState传入action这个对象函数并执行而已。同时他放行了类型不为function的action对象。

所以说，当我们需要用redux-thunk来在同步的redux数据流中添加异步的访问服务器操作，我们就需要在代码中dispatch一个函数类型的action。这就需要我们有一个"function action"的creator。我们来看一下我们的app中的这个特殊的action creator，我们称之为async action creator。这个async action creator也是thunk中间件规定我们写的接口。我们在实际项目中想要执行一些异步的更改store状态的操作时就必须不断编写这样的async action creator
```js
//F:\caistrong\react-demo\todo_app\src\weather\actions.js
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
其中这个返回的 async (dispatch, getStatte) => {} 这个AsyncFuntion的实例，就是我们thunk中间件里面接收到的那个action对象。很明显 type action === 'function' 会是true，所以这个async (dispatch, getStatte) => {} 会被执行并且dispatch和getState都可以正确传入。

这一个async function就是我们实现在同步的redux数据流中完成异步访问服务器操作的关键所在。

我们可以看到，在这个函数里面，我们使用fetch去获取服务器数据，然后分别在获取过程的不同阶段通知应用当前获取的status，是正在获取中还是已经接收到返回的数据，通知的实现方式就是从新disptach一个action对象。这个action对象是一个plain object。不再是function。所以会被thunk放行而进入reducer。
我们也看一下这些 "同步的" action creator
```js
//F:\caistrong\react-demo\todo_app\src\weather\actions.js
export const fetchWeatherStarted = () => ({
    type: FETCH_STARTED,
})

export const fetchWeatherSuccess = (res) => ({
    type: FETCH_SUCCESS,
    result: res
})

export const fetchWeatherFailure = (err) => ({
    type: FETCH_FAILURE,
    error: err
})
```
然后我们的reducer再去处理这些(plain object) action对象。这能使我们的reducer保持在处理异步逻辑的时候依然使用和处理同步逻辑一样的普通的actiion对象去更改store的状态。我们的所有异步逻辑都被约束在了刚刚那个fetchWeatherOf函数
```js
//F:\caistrong\react-demo\todo_app\src\weather\weatherReducer.js
import {FETCH_STARTED,FETCH_SUCCESS,FETCH_FAILURE} from './actionTypes.js'
import * as statusTypes from './status.js'

export default (state={},action) => {
    switch(action.type){
        case FETCH_STARTED: {
            return {status: statusTypes.LOADING}
        }
        case FETCH_SUCCESS: {
            let data = action.result.HeWeather6[0]
            return {...state, 
                    status: statusTypes.SUCCESS, 
                    info: {
                        city: data.basic.location,
                        weather: data.now.cond_txt,
                        temp: data.now.tmp,
                        wind: data.now.wind_dir
                    }
                }
        }
        case FETCH_FAILURE: {
            return {status: statusTypes.FAILURE}
        }
        default: {
            return state
        }
    }
}
```

至此关于redux-thunk的整个流程也差不多完了，理解了redux-thunk实际上我们也可以自己来实现一个具有类似作用的中间件。

#### redux-promise

```js
export default function promiseMiddleware ({dispatch,getState}) {
  return (next) => (action) => {
    const {types, promise, ...rest} = action
    if( !(promise instanceof Promise) || !(action.types && action.types.length ===3) ){
      //不符合指定要去的action对象就放行它
      return next(action)
    }
    const [PENDING, DONE, FAIL] = types
    dispatch({...rest, type: PENDING})
    return action.promise.then(
      (result) => dispatch({...rest, result, type: DONE}),
      (error) => dispatch({...rest, error, type: FAIL})
    )
  }
}
```
使用方式如下
```js
import {FETCH_STARTED,FETCH_SUCCESS,FETCH_FAILURE} from './actionTypes.js'

export const fetchWeatherOf = (city) => {
  const apiUrl = `https://free-api.heweather.com/s6/weather/now?location=${city}&key=${HeweatherKey}`
  return {
    promise: fetch(apiUrl),
    types: [FETCH_STARTED, FETCH_SUCCESS, FETCH_FAILURE]
  }
}
```
我们发现fetchWeatherOf函数比上面简洁得多，我们在中间件地层面极其帅气地解决了需要写一堆dispatch(fetchWeatherStarted())这样地模板代码。同时action对象也不需要再是一个function类型了，但是action对象必须要满足一个promise属性值是Promise类型的对象还有types数组长度为3.blabla..

#### 参考资料
《深入浅出react和redux》第7章和第9章 程墨
