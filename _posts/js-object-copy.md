---
title: JavaScript深浅拷贝
date: 2018-02-13 17:49:49
tags:
    - JavaScript
    - 深拷贝
    - 浅拷贝
categories:
    - JavaScript
---

在面试美团实习生的时候被考到了深拷贝了...

<!--more-->

在被面试到之前一直没有专门地去了解JavaScript对象的深浅拷贝。今天在网上一搜突然发现这好像还是个面试日经问题，也是JavaScript老生常谈的话题了。网上有铺天盖地资料可以深入。我这里打算只做最简略的介绍。

## 浅拷贝

谈到要拷贝一个对象，假设我们像如下
```js
var obj = { a:1, arr: [2,3] };
var objCopy = obj; 
```

我觉得这里的objCopy也可以算是一个浅拷贝，不过这与我们常谈的浅拷贝不同。可以理解为这里的objCopy存了整个obj对象的引用，所以对objCopy的所有更改(例如objCopy.a=2)都会反应到obj上。而我们要实现的浅拷贝实际上是对待拷贝对象src的第一层属性进行拷贝，这样一来，像a之类的基本类型值就有了一份新的副本，而arr这样的引用类型还是只拷贝了引用。

**浅拷贝的实现如下:**

```js
var shallowCopy = function(obj) {
    // 只拷贝对象
    if (obj === null || typeof obj !== 'object') return obj;
    // 根据obj的类型判断是新建一个数组还是对象
    var newObj = obj instanceof Array ? [] : {};
    // 遍历obj，并且判断是obj的属性才拷贝
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            newObj[key] = obj[key];
        }
    }
    return newObj;
}
```
#### 数组浅拷贝hack
如果是数组的话，还有这两个hack方法可以实现浅拷贝，在数组的元素是基本类型值的话很有用。

```js
var arrCopy = arr.concat()
var arrCopy = arr.slice()
```
#### 对象浅拷贝hack
Object.assign() 方法可以把任意多个的源对象自身的可枚举属性拷贝给目标对象，然后返回目标对象。
```js
var x = {
  a: 1,
  b: { f: { g: 1 } },
  c: [ 1, 2, 3 ]
};
var y = Object.assign({}, x);
console.log(y.b.f === x.b.f);     // true 所以是浅拷贝
```

## 深拷贝

深拷贝实际上可以理解为每层递归地浅拷贝，也就是遇到属性是对象的时候不会只拷贝引用，而是递归进去把这个对象的属性又拷贝一份副本。

实际上，如果对象比较大，层级也比较多，深复制会带来性能上的问题。在实际的应用场景中，也是浅复制更为常用。不过仅为学习之用了解一下深拷贝的实现。

**一个漏洞较多的实现**

这个深拷贝基本上是在上文浅拷贝的基础上，加入判断obj[key]是不是对象来决定是递归调用自己还是直接赋值

```js
var deepCopy = function(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    var newObj = obj instanceof Array ? [] : {};
    for (var key in obj) {
        if (obj.hasOwnProperty(key)) {
            newObj[key] = typeof obj[key] === 'object' ? deepCopy(obj[key]) : obj[key];
        }
    }
    return newObj;
}
```

*存在的漏洞*

1. 这里有个问题是当obj是函数对象(也有可能obj是对象的一个属性，这个属性的值是函数)的时候。因为typeof obj 为返回"function"，所以这个function会被直接返回，那么这个属性为函数的值就会变成存着函数对象的引用，也就是浅拷贝。

2. 当我们遇到一种对象，比如var a = {} a.i = a 我们发现 x 变成了 { i:{ i:{ i:...} } }之类的，也就是在对象中存在循环引用，那么这时候我们上面的函数就会不停地递归调用直到上下文栈溢出。

**一个较为完善的实现**

```js
function deepCopy (obj,deep = true) { 
    if (obj === null || (typeof obj !== "object" && typeof obj !=="function")) { 
        //obj只有是基本类型值(或者null)才会执行这里
        return obj; 
    } 

    if (typeof obj ==="function") {
        //复制一个函数副本的骚操作
    	return new Function("return " + obj.toString())();
    }
    else {
        var name, target = obj instanceof Array ? [] : {}, value; 

        for (name in obj) { 
            value = obj[name]; 
 
            if (value === obj) {
                //这里就是为了探测是不是循环引用的，如果是的话会跳过当前循环执行下个循环
            	continue;
            }

            if (deep) {
                //深拷贝情况
                if ( typeof value === "object" || typeof value === "function" ) {
                    //如果是对象就递归调用
                    target[name] = deepCopy(value,deep);
                } else{
                    //如果是基本类型的值
                    target[name] = value;
                }
            } else {
                //浅拷贝的情况
            	target[name] = value;
            } 
        } 
        return target;
    }　        
}
```
*存在的漏洞*

1.  var x = {} , var y = {} , x.i = y , y.i=x  var z = deepCopy(x)。在这种情况下会报错。暂时也没有想到很好的解决方法。

### JSON黑科技

```js
var objCopy = JSON.parse(JSON.stringify(obj))
```
#### 参考资料
[javascript中的深拷贝和浅拷贝？知乎](https://www.zhihu.com/question/23031215)
[深入剖析 JavaScript 的深复制](http://jerryzou.com/posts/dive-into-deep-clone-in-javascript/)
[javaScript中浅拷贝和深拷贝的实现](https://github.com/wengjq/Blog/issues/3)
[JavaScript专题之从零实现jQuery的extend](https://github.com/mqyqingfeng/Blog/issues/33)