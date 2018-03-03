# JavaScript事件委托原理及实现

## 冒泡流和捕获流

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event-delegate/catch-buble.jpg)

```js
document.getElementById('a').addEventListener('click',handler) 
//冒泡流，useCaptrue默认是false
document.getElementById('a').addEventListener('click',handler,true)
//捕获流
document.getElementById('a').onclick = handler
//冒泡流
```

**以下是冒泡流示例**

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event-delegate/catch-buble.jpg)

```js
function handler (e) {
    console.log('target : '+ e.target.id + "-----" + 'currentTaget : ' + e.currentTarget.id )
}
document.getElementById('a').addEventListener('click',handler)
document.getElementById('b').addEventListener('click',handler)
document.getElementById('d').addEventListener('click',handler)
```

点击了最里层的d之后
```
target : d-----currentTaget : d
target : d-----currentTaget : b
target : d-----currentTaget : a
```

### 理清target和currentTarget的区别

想要理解事件委托的原理，首先要分清楚target和currentTarget的区别。

我们参照上面的示例讲，当一个event被触发的时候（在这里是“点击了最里层的d”这个click event），监听这个click event的元素上的eventHandler会被触发执行。这时候eventHandler会被传入一个对象参数e，这个e上面有两个属性一个是e.target，另一个是e.currentTarget。

**e.target和我们具体触发的event有关联**，比如我们如果点击的是d，那么所有因为这个click event而触发执行的eventHandler传入的参数e的target属性都指向d，如果我们点击c（绿色那圈），则e.target就会指向c。以此类推...

由于我们采用了冒泡流的方式，所以事件会向上冒泡，直到window对象为止。这时候如果我们点击了d，这时候会依d、c、b、a、body、html、window的顺序触发这个click event。然而只有d、b、a上面监听了click event。所以d、b、a上的click event的eventHandler会被按冒泡流的顺序依次执行。在d上注册的eventHanler里，因为我们点击的是d，所以参数e的target指向d，而**currentTarget则指向了该eventHandler被注册的元素**，也是d。接下去因为c上没有注册click event的eventHandler，所以跳过c，执行在b上注册的eventHandler。这时候这里的e.target也是指向d，而e.target却变成了b。以此类推。


## 事件委托

有了上面的基础知识后我们可以开始讲事件委托了。

我们假设有一个ul标签，里面的每个li都要注册一个click event的eventHandler
```html
<ul id="list">
    <li id="l1">1</li>
    <li id="l2">2</li>
    <li id="l3">3</li>
    <li id="l4">4</li>
</ul>
```
我们可以采用如下的方式添加
```js
l1.addEventListener('click', myHandler)
l2.addEventListener('click', myHandler)
l3.addEventListener('click', myHandler)
l4.addEventListener('click', myHandler)
```
这种方式至少存在2种缺点
1. 如果列表li的数目是不固定的，代码不是写死的，li会动态地增减，就会比较麻烦。需要为每个新的li也注册eventHandler。
2. 存在性能问题，假设列表li的数目有100、500个或者更多，那我们的eventHandler也需要同样的数目。

根据前面介绍的冒泡流，我们很容易想到一个解决方法。比如说我们点击
`<li id="l2">2</li>`的时候，由于冒泡流的机制，这个click event，也会冒泡到`<ul id="list"></ul>`。所以我们可以在ul上面注册一个evnetHandler来代替在各个li上面分别注册eventHandler。**这个解决方法就是事件委托**。而ul我们可以称之为代理(agent)。


## 事件委托封装的一种实现
```js
function delegate(agent,type,selctor,fn) {
  //agent.addEventListener(type,fn)如果是这样fn中的this会指向agent
  agent.addEventListener(type,function(e){
      let target = e.target         //target指向实际点击的最里层的元素
      let ctarget = e.currentTarget //ctarget会永远指向agent
      let bubble = true

      while(bubble && target != ctarget){
          if(target.matches(selctor)){
            //改变this的指向
            bubble = fn.call(target,e) === false ? false : true
          }
          target = target.parentNode //模拟事件冒泡
          if(!bubble){
            e.preventDefault()
          }
      }
  },false)
}
```

```js
var list = document.getElementById('list')
delegate(list,'click','li',function(e){
  console.log(`${e.target.innerText}   currentTarget : ${e.currentTarget.id}`)
})
delegate(list,'click','#l2',function(e){
  console.log(`${e.target.id}   currentTarget : ${e.currentTarget.id} `)
})
```

### return false in eventHandler
在我们事件委托的实现中，我写了一些丑陋的代码，如下
```js
bubble = fn.call(target,e) === false ? false : true

if(!bubble){
    e.preventDefault()
}
```
这些代码的作用是为了什么呢？

首先我们经常可以看到如下代码
```html
<a href='#' onclick='console.log(3.1415); return false;'>Click here !</a>
```
其中在onclick这个eventHandler中出现了返回值，return false产生的效果是，取消了a的默认行为。也就是相当于调用了event.preventDefault()。
在[whats-the-effect-of-adding-return-false-to-a-click-event-listener](https://stackoverflow.com/questions/128923/whats-the-effect-of-adding-return-false-to-a-click-event-listener)这个问题下，有人回答return false的效果相当于调用了

1. event.preventDefault();
2. event.stopPropagation();
3. Stops callback execution and returns immediately when called.

这个答案的正确性存疑，在这个回答的下面有人也回复了，在原生的JavaScript事件中return false只有1的效果，而2的效果是只在jQuery的 click event handler才会出现。

在我的实现中，我是模拟了jQuery的行为。如果return flase将会终止冒泡以及取消默认行为。

假设如下情况
```html
<div id="wrap">
    <div class="cai" id="caiouter">
      cai outer
      <div class="cai" id="caiinner">
        cai inner
      </div>
    </div>
    <div>
      <a href="http://www.baidu.com" class="cai" id="baidu">return false后不打开百度了</a>
    </div>
</div>
```
```js
var wrap = document.getElementById('wrap')
delegate(wrap,'click','.cai',function(e){
  console.log(`${e.target.id}   currentTarget : ${e.currentTarget.id}`)
  return false
})
```
这时候事件不会冒泡到cai outer，同时点击下面的链接也不会打开百度了

#### 参考资料
[event.target 和 event.currentTarget 的区别](http://www.calledt.com/target-and-currenttarget/)
[delegate实现原理(事件委托)--我觉得它封装的办法有不正确的地方，仅供参考](https://div.io/topic/1357)
