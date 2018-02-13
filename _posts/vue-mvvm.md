---
title: Vue-双向绑定原理
date: 2018-02-07 19:45:02
tags:
    - vue
    - 双向绑定
categories:
    - Vue
---

在文末所附的参考资料中极尽详细地剖析了Vue实现双向绑定的原理。本文可以视为那篇文章的梗概版。

<!--more-->

vue.js 实现双向绑定是采用数据劫持结合发布者-订阅者模式的方式，通过Object.defineProperty()来劫持各个属性的setter，getter，在数据变动时发布消息给订阅者，触发相应的监听回调

## 整体思路
 1. 实现一个数据监听器Observer，能够对数据对象的所有属性进行监听，如有变动可拿到最新值并通知订阅者 
 2. 实现一个指令解析器Compile，对每个元素节点的指令进行扫描和解析，根据指令模板替换数据，以及绑定相应的更新函数 
 3. 实现一个Watcher，作为连接Observer和Compile的桥梁，能够订阅并收到每个属性变动的通知，执行指令绑定的相应回调函数，从而更新视图 
 4. mvvm入口函数，整合以上三者

## 流程描述

以下我根据理解对整个流程做一个描述，可能出现理解有误。具体的逻辑到最后的参考资料去看。

首先我们整个流程的目的是要实现，将数据和视图绑定在一个vm实例中。然后改变数据的时候也动态改变试图上的数据。这仅仅只是单向绑定，即由更新数据->更新视图。但是双向绑定是在单向的基础上给可输入元素（input、textare等）添加了change(input)事件，来动态修改model和 view，并没有多高深。所以无需太过介怀是实现的单向或双向绑定。

好以下我来描述整个实现流程

```html
<div id="mvvm-app">{{ word }}</div>
```

```js
var vm = new MVVM({
        el: '#mvvm-app',
        data: {
            word: 'Hello World!'
        },
    });
```

我们最终要实现类似上面这样的一个ViewModel,其中el绑定了HTML也就是视图那边而data代表着数据，我们现在想要的是当我们改变数据
```js
vm.word = 'Hello New World'!
```
HTML上的视图也会相应的更新

首先我们需要用Object.defineProperty()来进行数据劫持，大致原理就是我们使用
```js
var dep = new Dep();
Object.defineProperty(data, word, {
        enumerable: true, // 可枚举
        configurable: false, // 不能再define
        get: function() {
            return val;
        },
        set: function(newVal) {
            console.log('哈哈哈，监听到值变化了 ', val, ' --> ', newVal);
            val = newVal;
            dep.notify();
        }
    });
```
这样我们就劫持了data这个数据的word属性，每次我们使用
```js
vm.data.word = 'New world'
```
这样的方式为word赋上一个新值的时候，我们就可以触发上面set这个函数，执行setter函数里定义的逻辑。那么在setter的逻辑里我们应该写些什么呢。首先对于data里的每一个数据，比如这里的word,我们应该为他实例化一个相对应的Dep实例dep
```js
var dep = new Dep();
```
然后在setter函数里我们调用
```js
dep.notify();
```
这个Dep类型的构造函数如下
```js
function Dep() {
    this.subs = [];
}
Dep.prototype = {
    addSub: function(sub) {
        this.subs.push(sub);
    },
    notify: function() {
        this.subs.forEach(function(sub) {
            sub.update();
        });
    }
};
```
我们的每一个数据，都有一个dep，这个dep里面有一个数组，这个数组里面包含了所有监听这个数据(我们这里是word)的视图(我们这里是#mvvm-app里的{{data}})

好了现在我们完成的逻辑就是下面这样，一旦word被 = 赋上新值了，他会触发dep.notify。我们可以在下面看到notify的逻辑，它遍历自己的订阅者然后执行他们的update()函数,等于是通知所有监听/依赖我的视图,告诉这些视图"喂(#`O′)我的数据已经更新啦，你们视图也该更新一下了"。

那么现在问题时我们怎么往dep里添加订阅者呢？

首先我们应该知道dep里面的订阅者应该是Watcher的实例,我们应该将我们每一个监听这个word数据的视图(双大括号插值、特性上绑定指令等等)都实例化一个watcher然后添加到数据word的dep内的sub数组上来

所以我们去遍历el绑定的元素和他的子元素，然后搜索所有绑定word这个数据的视图，为每个视图new一个Watcher
```js
//这里的Compile我们只考虑双大括号，其他的绑定指令啥的方法类似
//我们把绑定的那个el先提取出来
var el = document.querySelector(el)
var reg = /\{\{(.*)\}\}/	// {{}}表达式文本
var childNodes = el.childNodes
//将类数组对象转化为数组
[].slice.call(childNodes).forEach(function(node){
    var text = node.textContent;
    if(reg.test(text)){
        //我猜这里的RegExp.$1应该是指word
        new Watcher(vm,exp,callback);
    }
})
```
在new这个Watcher的过程中我们试图劫持word数据的getter函数，在word数据的getter函数里为word数据相关联的这个dep添加一个新订阅者，也就是我们在扫描el中扫描到的这个视图所new出来的Watcher
```js
// Observer.js
Object.defineProperty(data, key, {
	get: function() {
		// 由于需要在闭包内添加watcher，所以通过Dep定义一个全局target属性，暂存watcher, 添加完移除
		Dep.target && dep.addDep(Dep.target);
		return val;
	}
    // ... 省略
});
```
```js
function Watcher(vm, exp, cb) {
    this.cb = cb;
    this.vm = vm;
    this.exp = exp;
    // 此处为了触发属性的getter，从而在dep添加自己，结合Observer更易理解
    this.value = this.get();
}
Watcher.prototype = {
    update: function() {
        this.run();	// 属性值变化收到通知
    },
    run: function() {
        var value = this.get(); // 取到最新值
        var oldVal = this.value;
        if (value !== oldVal) {
            this.value = value;
            this.cb.call(this.vm, value, oldVal); // 执行Compile中绑定的回调，更新视图
        }
    },
	get: function(key) {
		Dep.target = this;
		this.value = data[key];	// 这里会触发属性的getter，从而添加订阅者
		Dep.target = null;
	}
}
```
好了，现在订阅者也添加好了。
现在我们每一次更改word这个数据的时候都会触发setter函数
setter函数会去通知自己的所有订阅者wather触发自己的update()函数。我们的单向数据绑定到此完毕了。


#### 参考资料
[剖析vue实现原理，自己动手实现mvvm](https://github.com/DMQ/mvvm)