# 函数式编程初探

在学习React/Redux技术栈的时候我们常常会听人提到函数式编程。现如今函数式编程也慢慢地火了起来，成了一个老生常谈地话题，今天我对自己这段时间来对函数式编程的学习作一些总结。

## 函数是一等公民

函数不具有特殊性，和其他对象一样可以作为参数传递，赋值给变量，作为结果返回等等...这一点在JavaScript里没有问题。不过却常常遭到无视。

```js
var getServerStuff = function(callback){
    return ajaxCall(function(json){
        return callback(json)
    })
}
```
等价于
```js
var getServerStuff = ajaxCall
//想一下如果是JAVA这种“函数非一等公民”的语言..是否还能这样..
```

如果看不懂上面为何等价，下面是一个推倒
```js
// 这行
return ajaxCall(function(json){
    return callback(json)
})
// 等价于这行
return ajaxCall(callback);
// 那么，重构下 getServerStuffvar 
getServerStuff = function(callback){
    return ajaxCall(callback)
};
// ...就等于
var getServerStuff = ajaxCall;
```

## 数据不可变(Immutable)
JavaScript语言本身只有Object.freeze()这个函数和不可变有关系，他会修改对象的configurable和writable等为false去保证对象不被修改。在React中，一个组件不允许修改传入的prop值，也是遵循Immutable原则。大家更了解的就是在Redux中，我们的reducer不允许去修改state，只能返回一个新的state。也是体现了这个原则。

在讲到纯函数的时候，我们会去强调“纯函数没有任何可观察的副作用”，其实我觉得也是数据不可变的一个体现。也就是纯函数不应该对环境造成破坏。一个经常举到的例子就是splice函数，他会对调用这个函数的数组进行改变，而像slice就不会。

其实我认为数据不可变与其说是一种原则，不如说是一种可供选择的编程思想。我们在React里面说，组件不允许修改传入的prop值，但是某些需求下，又会希望通过传入的"函数类型的"prop去修改传入的prop值。某种情况下这破坏了Immutable原则。但我们应该意识到，我们之所以订立了数据不可变这一种编程思想，是因为这会帮助我们避免项目变得庞大时数据流变得混乱。代码的运行变得难以预测等等问题。但工程的质量必须建立于完成基本的需求之上。所以只要我们有充足的理由，打破数据不可变的原则，或者修改传入的prop等等也是可以的。函数式编程本身是一种优秀的思想，但是过于强求程序一定要完全符合函数式的规则，不要太原教旨主义了。

## 纯函数

> 纯函数的定义是，对于相同的输入，永远会得到相同的输出，而且没有任何可观察的副作用，也不依赖外部环境的状态。

联系中学数学课本对函数的定义，我们知道函数的输出完全由输入决定。纯函数便必须遵循这一规则。

```js
// 不纯的| 函数的输出不单由age决定，还由外部环境变量minimum决定
var minimum = 21;
var checkAge = function(age) {
    return age >= minimum;
};

// 纯的| 函数的输出完全由age决定
var checkAge = function(age) {
    var minimum = 21;
    return age >= minimum;
};
```

### 纯函数有什么优势？
1. 可缓存性

如果函数是纯函数，那么他的输出将完全由输入决定。我们就可以在第一次输入时将对应输出存入缓存。下次如果遇到相同的输入，则直接从缓存中找到该对应的输出返回，避免重复计算。如果函数不是纯函数，那么相同的输入也可能因为系统环境的变化产生不同的输出，这时如果还利用缓存就会得到错误的结果。
```js
//不太健壮的简单缓存实现
var memoize = function(f) {
    var cache = {};
    return function() {
        var arg_str = JSON.stringify(arguments);
        cache[arg_str] = cache[arg_str] || f.apply(f, arguments);
        return cache[arg_str];  
    };
};
var squareNumber  = memoize(function(x){ return x*x; });
squareNumber(4);//=> 16
squareNumber(4); // 从缓存中读取输入值为 4 的结果//=> 16
```
2. 可移植性/自文档化

```js
// 不纯的
var signUp = function(attrs) {
    var user = saveUser(attrs); 
    welcomeUser(user);
};
var saveUser = function(attrs) {
    var user = Db.save(attrs);
    ...
};
var welcomeUser = function(user) {
    Email(user, ...);
    ...
};
// 纯的
var signUp = function(Db, Email, attrs) {
    returnfunction() {
        var user = saveUser(Db, attrs);    
        welcomeUser(Email, user);  
    };
};
var saveUser = function(Db, attrs) {
    ...
};
var welcomeUser = function(Email, user) {
    ...
};
```
其实很容易理解，不纯的函数可移植性很差，我们想要移植这个不纯的signUp函数，我们还需要将系统环境的Db和Email也移植过去，而在纯函数里面，我们可以直接传入参数。而自文档化就更容易理解了，我们单纯地看纯函数signup的函数签名，就知道他将用到Db,Email,attrs这几个参数。

3. 可测试性

测试纯函数比较容易，我们无需去伪造很多系统环境，无需每次都配置环境到某个状态。直接简单得给函数输入，然后断言输出即可。

4. 引用透明性

由于纯函数相同的输入返回相同的输出，那么一段代码就可以在不改变整个程序行为的前提下替换成他所执行的结果。有点类似于数学的等效替代法。我们可以利用这一特性重构代码。使代码更加简洁易懂。也可以利用这一方法来理解代码。

*<JS函数式编程> 第3章: 纯函数的好处/关于合理性有一段代码来解释这一优势*

## 函数柯里化(curry)

简单的概念：
> 只传递函数的一部分参数来调用它，让它返回一个函数去处理剩下的参数。

```js
const add = x => y => x+y
const increment = add(1)
const addFive = add(5)
add(2)(3) //5
increment(4) //5
addFive(0) //5
```

### 柯里化的价值

柯里化说白了就是上面的那一小段定义，就是如果有一个函数接收多个参数，可以先传一部分参数，创造出一个处理剩下参数的函数，就是这样而已。至于这样一个特性在工程实践中有什么价值其实完全见仁见智，又或者说，柯里化的工程价值就是，你能不能利用好这个特性写出更加简洁、易懂的代码。

在我眼里，柯里化的价值在于：**写出抽象程度更高的函数，复用参数，简化代码**

假设我们想从一个博客文章对象数组里提出某个属性
```js
//befor curry
var articles = [ {id:1,title:'hello js'}, {id:2,title:'js prototype'} ,{id:3,title:'js eventloop'} ]

articles.map( article => article.id )
articles.map( article => article.title )
```

```js
//affter curry
var curry = require('ramda').curry
//ES5写法
var get = curry(function(property,object){
    return object[property]
})
//ES6写法
var get = property => object => object[property]

articles.map(get(id))
articles.map(get(title)) 
```
其实这个`get`就是一个高阶函数，当你调用`get(id)`时是返回的其实就是`article => article.id`这个函数。

`get`也可以看作是一个抽象程度更高的函数，你可以通过对他传入第一个参数，像`id`,`title`这些。把get这种抽象的函数具体化一步，得到一个逻辑更具体的函数。这个过程可以叫做部分配置（partially configured）。有些类似OOP里我们写抽象类，抽象方法，在之后通过继承来复用抽象类、方法部分的代码逻辑。

假设现在我们又想要去提取一个用户对象数组的id属性
```js
var users = [ {id:1,title:'cai'}, {id:2,title:'wang'} ,{id:3,title:'chen'} ]

users.map(get(id))
```
我们可以像上面这样完成任务，这个例子看起来其实也不复杂，但是在实际的项目中的逻辑可能会比这复杂，这个时候如果我们之后又要去获取其他数组的id属性。我们一般会考虑封装一个新函数getIDs()
```js
// before curry
var getIDs = function(objects){
    return objects.map(get('id'))
}
getIDs(users)
getIDs(articles)
```
这样看起来问题解决得很好，不过假设现在我们又想要封装一个新的getTitles()，我们就需要
```js
var getTitles = function(objects){
    return objects.map(get('title'))
}
```
这看起来和上面的getIDs有很多相同的模板代码，所以我们可以考虑对map函数进行柯里化，以通过部分配置来消除模板代码
```js
//after curry
var cmap = fn => objects => objects.map(fn)
var getIDs = cmap(get('id'))
var getTitles = cmap(get('title'))
```
其实这个`cmap`就是和上面的`get`一模一样的作用。就是高阶函数。如果对React熟悉的话，其实就会发现这和React的高阶组件是一摸一样的，就连价值也是一摸一样的，无非就是代码复用，消除模板代码。

#### 一个较为具体的例子

有个response body如下
```json
{
    "user": "caixiaocong",
    "posts": [
        { "id":1, "title": "hello js", "contents": "..." },
        { "id":2, "title": "js prototype", "contents": "..." },
        { "id":3, "title": "js eventloop", "contents": "..." }
    ]
}
```
```js
//模拟Ajax
function fetchFromServer(){
    return new Promise((resolve,reject)=>{
        setTimeout(()=>resolve(data),3000)
    })
}
```
我们想要在首页展示文章标题列表
```js
//before curry
fetchFromServer()
    .then(JSON.parse)
    .then(data => data.posts)
    .then(posts => posts.map(post => post.title))
```

```js
//after curry
fetchFromServer()
    .then(JSON.parse)
    .then(get('posts'))
    .then(map(get('title')))
```
1. 减少中间变量

我们少了很多像data、posts这样的中间变量，这对使代码更清晰易读有很大意义！

2. 简化代码

当类似`posts => posts.map(post => post.title)`这样的代码逻辑再变得复杂起来的时候我们其实可以节省很多代码。
举个例子，假设我们有个需求是获取标题时该大写.则我们需要修改
```js
//before curry
posts => posts.map(post => post.title.toUpperCase())
```
如果只有此处的标题需要大写，那倒是无伤大雅，但如果除了这里以外，别的地方还需要标题大写的话，你就必须在不同地方加上.toUppercase()。
而重复是优秀设计的大敌。如果你刚刚柯里化了get.
```js
var get = property => object => (property === 'title' ? object[property].toUpperCase() : object[property])
// 上面after curry的代码无需更改
```

#### 使用柯里化做"转换头"

一个常见面试题
```js
['11', '22', '33'].map(parseInt)
//[11, NaN, NaN]
```
bug出现的理由如下：
> [window] parseInt(string, radix);
> [Array.prototype.map()] callback(currentValue, index, array){}

我们可以看到，parseInt接收2个参数，而map的callback会为parseInt注入3个参数。因此上面的代码执行类似于
```js
parseInt('11',0) //1
parseInt('22',1) //NaN
parseInt('33',2) //NaN
```
我们可以使用柯里化来然parseInt只能接收一个参数
```js
var cparseInt = radix => string => parseInt(string,radix)
var parseIntDec = cparseInt(10)
;['11', '22', '33'].map(parseIntDec)
//[11, 22, 33]
```
这里之前因为没加那个分号报错了，我也是醉了。。。原因如下：
[JavaScript 语句后应该加分号么？](https://www.zhihu.com/question/20298345/answer/14670020)

## 组合(compose)

先看一个例子来直观地理解组合
```js
var compose = (f,g) => x => f(g(x))
var toUpperCase = x => x.toUpperCase()
var exclaim = x => x+'!'

var shout = compose(exclaim,toUpperCase)
shout("hahaha")// HAHAHA!
```

### 组合与管道
从上面的例子我们可以看到组合是从右到左执行，先toUpperCase再exclaim
Ramda提供了一个API: [pipe](http://ramda.cn/docs/#pipe)可以从左到右执行
关于这个，我们再来看个例子

```js
var pipe = require('ramda').pipe

var reduce = fn => initValue => data => data.reduce(fn,initValue)
var head = x => x[0]
var reverse = reduce( (acc, x)=>[x].concat(acc) )( [] );

var compose_last = compose(head,reverse) 

compose_last(['jumpkick', 'roundhouse', 'uppercut']) //"uppercut"

var pipe_last = pipe(reverse,head)

pipe_last(['jumpkick', 'roundhouse', 'uppercut']) //"uppercut"
```

### 组合/管道的价值

举一个具体的例子：

现有一份某公司雇员某月的考核表，我们想统计所有到店餐饮部开发人员该月完成的任务总数，假设员工七月绩效结构如下：
```js
var data = [{
  name: 'Pony',
  level: 'p2.1',
  segment: '到餐'
  tasks: 16,
  month: '201707',
  type: 'RD',
  ...
}, {
  name: 'Jack',
  level: 'p2.2',
  segment: '外卖'
  tasks: 29,
  month: '201707',
  type: 'QA',
  ...
}
...
]
```
我们可以这样做：
```js
const totalTaskCount = compose(
  reduce(sum, 0),                              // 4. 计算所有 RD 任务总和
  map(person => person.tasks),                 // 3. 提取每个 RD 的任务数
  filter(person => person.type === 'RD'),      // 2. 筛选出到餐部门中的RD
  filter(person => person.segment === '到餐')  // 1. 筛选出到餐部门的员工
)
```
其中reduce、map、filter这些函数是需要我们经过柯里化的函数。像`reduce(sum, 0)`、`map(person => person.tasks)`这些表达式的结果应该是**接收一个待处理数据作为参数的函数**。这时候我们的待处理数据x就会在这个管道里流动，先后经过1、2、3、4四个函数的处理。

组合/管道在这个例子里体现出来的优势十分明显，通过将一个比较复杂的逻辑进行分割，变成一个个比较小的独立的片段。当我们出现其他需求比如说需要统计其他数据的时候，可以通过变换组合的方式来完成。这也较完美地实现了代码复用。

### 参考资料
[Why Curry Helps](https://hughfdjackson.com/javascript/why-curry-helps/)
[JS函数式编程指南](https://legacy.gitbook.com/book/llh911001/mostly-adequate-guide-chinese/details)
[函数式编程在Redux/React中的应用 By美团点评](https://tech.meituan.com/functional_programming_in_redux.html)