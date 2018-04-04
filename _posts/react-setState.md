# React-探究setState

## 出现问题
最近养成了每每遇到API出现问题都会想去看源码的习惯，我上周就在使用setState时就遇到了一个问题，我想实现一个标签，点击编辑会出现输入框，并且自动聚焦和全选的需求，简化后如下：
```js
import React,{Component} from 'react'

class LabelInput extends Component {
    constructor(props) {
        super(props)
        this.state = {
            isEditing: false,
            text: "输入文字.."
        }
    }
    handleEdit() {
        this.setState({
            isEditing: true
        })
        this.inputDom.focus()
        this.inputDom.select()
    }
    render() {
        return (
            <div>
                {
                    this.state.isEditing ?
                    <input ref={(c) => {this.inputDom = c}} type="text" value={this.state.text} />
                    : <label>{this.state.text}</label>
                }
                <button onClick={this.handleEdit.bind(this)}>edit</button>
            </div>
        )
    }
}
export default LabelInput
```
当我点击编辑时的报错如下：
> TypeError: Cannot read property 'focus' of undefined

## 为什么？
通过chrome 的devtools，我查看了this.inputDom，发现是undefined，也就是`<input>`的ref回调函数并没有执行。没有执行的原因是isEditing是false所以`<input>`并没有被render。

但是，我们已经使用了this.setState({ isEditing: true })，难道不应该重新触发render，并且isEditing就变成了true所以`<input>`会被渲染，inputDom就不再是undefined了吗？

原因就在于我一开始并不知道，this.setState是一个异步操作，甚至，this.setState还可以传递回调函数作为第二个参数。

## 解决问题
```js
    //...
    handleEdit() {
        this.setState({
            isEditing: true
        },() => {
            this.inputDom.focus()
            this.inputDom.select()
        })
    }
``` 
修改handleEdit()为如上代码，这时候this.inputDom.focus()这些会在render之后执行了，所以问题解决了。

*关于以上需求我的解决方法可能不是最好的，同事的建议是使用style.display的none和block来显示隐藏input*

## setState
虽然我们的问题解决了，不过像setState这样极其常用的API，对他有足够的了解显然能够让我们避免掉许多坑。于是我决定去看一下他的源码，不过...嗯实在是太过于复杂了...即使是看别人的源码阅读笔记，也感觉底层的实现有些繁琐，看起来也似懂非懂[React 源码剖析系列 － 解密 setState](https://zhuanlan.zhihu.com/p/20328570)。实际上如果有一个比较好的心境，比较闲/宁静的时候，仔细看一下源码也是比较好的。不过我最近是静不下心来看了。因此我吃了点快餐，看了程墨的三篇关于setState的文章[setState：这个API设计到底怎么样](https://zhuanlan.zhihu.com/p/25954470)

### 何时修改this.state？
既然this.setState是“异步”的，不会马上修改this.state，因此在this.setState之后的代码也无法立刻获得this.state。那么何时修改this.state呢？

一次setState会引发一次组件的更新生命周期函数：下面四个函数会被依次调用：
1. shouldComponentUpdate
2. componentWillUpdate
3. render
4. componentDidUpdate

*BTW: 在上面四个函数里面使用this.setState()会导致死循环*

以我们上面的代码做个实验
```js
class LabelInput extends Component {
    //...
    shouldComponentUpdate(nextProps,nextState) {
        console.log(`[shouldComponentUpdate]this.state.isEditing: ${this.state.isEditing}`)
        console.log(`[shouldComponentUpdate]nextState.isEditing: ${nextState.isEditing}`)
        return true
    }
    componentWillUpdate(nextProps,nextState) {
        console.log(`[componentWillUpdate]this.state.isEditing: ${this.state.isEditing}`)
        console.log(`[componentWillUpdate]nextState.isEditing: ${nextState.isEditing}`)
    }
    render() {
        console.log(`[render]this.state.isEditing: ${this.state.isEditing}`)
        console.log(`[render]this.state.text: ${this.state.text}`)
        //...
    }
}
```
点击编辑之后
1. [shouldComponentUpdate]this.state.isEditing: false
2. [shouldComponentUpdate]nextState.isEditing: true
3. [componentWillUpdate]this.state.isEditing: false
4. [componentWillUpdate]nextState.isEditing: true
5. [render]this.state.isEditing: true
6. [render]this.state.text: 输入文字..

所以我们可以看出来，**修改this.state的这一过程在componentWillUpdate和render这两个生命周期函数之间**

### 多次setState函数调用产生的效果会合并

```js
    //...
    handleEdit() {
        this.setState({
            isEditing: true
        })
        this.setState({
            isEditing: false
        })
        this.setState({
            text: "再输入文字.."
        })
    }
```
点击编辑之后
1. [shouldComponentUpdate]this.state.isEditing: false
2. [shouldComponentUpdate]nextState: false
3. [componentWillUpdate]this.state.isEditing: false
4. [componentWillUpdate]nextState.isEditing: false
5. [render]this.state.isEditing: false
6. [render]this.state.text: 再输入文字..

我们发现虽然有3个this.setState，但是组件的更新周期函数并不会调用3遍，说明React会将多个this.setState产生的修改放在一个队列里。React会对这些setState做一个智能的merge动作（从上面的测试结果完全可以看出这个merge的逻辑），所以上面的handleEdit()其实完全等同于
```js
    //...
    handleEdit() {
        this.setState({
            isEditing: false,
            text: "再输入文字.."
        })
    }
```

### 同步修改this.state？
有两种黑科技可以绕过React，"同步"修改state状态
#### 1. setTimeout/setInterval
```js
    //...
    handleEdit() {
        setTimeout(()=>{
            this.setState({
                isEditing: true
            })
            console.log(`[handleEdit(setTimeout)]: ${this.state.isEditing}`)
        },0)
        console.log(`[handleEdit(outer)]: ${this.state.isEditing}`)
    }
```
控制台打印的结果很有意思：

1. **[handleEdit(outer)]: false**
2. [shouldComponentUpdate]this.state.isEditing: false
3. [shouldComponentUpdate]nextState: true
4. [componentWillUpdate]this.state.isEditing: false
5. [componentWillUpdate]nextState.isEditing: true
6. [render]this.state.isEditing: true
7. [render]this.state.text: 输入文字..
8. **[handleEdit(setTimeout)]: true**

从结果看：handleEdit()里面的代码执行顺序是这样的
1. 遇到setTimeout，浏览器引擎先把()=>{this.setState({isEditing: true})console.log(`[handleEdit(setTimeout)]: ${this.state.isEditing}`)}这个匿名函数添加到事件队列
2. 执行console.log(`[handleEdit(outer)]: ${this.state.isEditing}`)，因此打印的就是初始值false
3. 执行放入事件队列的匿名函数
4. 先执行this.setState({isEditing: true})，这里由于他是setTimeout里的回调，绕过了React的batchedUpdates函数，因此“同步执行”。上面2-7的代码就被this.setState触发，同步执行。
5. 下面的console.log(`[handleEdit(setTimeout)]: ${this.state.isEditing}`)等到上面的this.setState({isEditing: true})执行完之后再执行。因为componentWillUpdate到render这些生命周期函数都已经执行了，因此this.state自然已经更新了，所以这里打印的是true

#### 2. 原生DOM事件
```js
    //...
    componentDidMount() {
        document.querySelector('#editbutton').addEventListener('click',this.handleEdit.bind(this))
    }
    handleEdit() {
        this.setState({
            isEditing: true
        })
        console.log(`[handleEdit(DomEvent)]: ${this.state.isEditing}`)
    }
```
点击编辑
1. [shouldComponentUpdate]this.state.isEditing: false
2. [shouldComponentUpdate]nextState: true
3. [componentWillUpdate]this.state.isEditing: false
4. [componentWillUpdate]nextState.isEditing: true
5. [render]this.state.isEditing: true
6. [render]this.state.text: 输入文字..
7. **[handleEdit(DomEvent)]: true**

过程应该是和setTimeout有点像，同样是绕过React的batchedUpdates，因此不再“异步”，同时也不再“积攒在setState队列里，智能merge”。就不具体分析了