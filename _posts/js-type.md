---
title: JavaScript类型判断
date: 2018-02-12 15:52:57
tags:
    - JavaScript
    - 类型判断
categories:
    - JavaScript
---

我们知道JavaScript有七种数据类型,其中基本类型(Primitive types)有六种，分别是Undefined、Null、Boolean、Number、String、Symbol(ES6引入)。引用类型(Reference type)有一种，是Object(我们常见的Array、Date、RegExp等其实都属于Object)。

<!--more-->

## typeof

我觉得可以简单地把typeof理解为就是用来判断这7种类型的,即对JavaScript的任何一个value，在他前面使用typeof操作符，可以判断出他属于这七种类型的哪一种。但是存在一些特殊情况。

```js
typeof undvar // "undefined"
typeof undefined //"undefined"
typeof null //"object"
typeof true //"boolean"
typeof 123 //"number"
typeof "cai" //"string"
typeof Symbol('cai') //"symbol"
typeof {} //"object"
typeof [] //"object"
typeof function foo(){} //"function" (特殊情况)
```
特殊要点:
1. typeof null 返回"object": 我认为这可以当作是JavaScript的一个设计上的错误,不过在高程中解释为null(Null类型唯一一个值)表示空对象指针,如果定义的变量准备在将来用于保存对象，在变量初始化时可以初始化为null
2. typeof [] 返回"object": 这一点实际上不特殊,但是他是要点,首先JavaScript的数组也是对象,其次使我们明白了typeof只能判断那7种类型,没办法判断是哪种对象,我们可以使用instanceof或者其他方法,将在后文叙述。
3. typeof function foo(){} : 这一点也是特殊的地方,按typeof []返回"object"的逻辑上,实际上这里的typeof function foo(){}也应该返回"object",毕竟JavaScript的函数也是对象,不过在JavaScript中function一直具有特殊性,所以我们也能理解这种设计
4. typeof undvar: typeof是一种安全操作,对于未声明的变量也会返回"undefined",不过如果这个未声明的变量在暂时性死区内则会报错。

## instanceof 

由于typeof的局限性(对于引用类型只能判断是不是object而无法具体判断是哪种object),ECMAScript引入了instanceof操作符。

### 语法
```js
object instanceof constructor
```
简单一句话描述:**instanceof 运算符用来检测 constructor.prototype 是否存在于参数 object 的原型链上。**

我们来看一下instanceof操作符的实现原理(来自参考资料的连接)。
```js
function instanceof(L, R) { //L是表达式左边，R是表达式右边
    var O = R.prototype;
    L = L.__proto__;
    while(true) {
        if (L === null)
            return false;
        if (L === O)
            return true;
        L = L.__proto__;
    }
}
```
我们举个实际的例子,比如
```js
instanceof(a,Array)
```
用来判断a是不是Array的实例,是的话返回true，否则返回false.
这个时候我们取
```js
var O = Array.prototype //值就是 "实例原型" 这个对象
```
*也就是构造函数的prototype属性,这个时候你每用这个构造函数new一个新的实例出来的时候,这个实例就会关联一个`__proto__`属性,这个属性指向的就是构造函数的prototype属性的值,这个属性的值(我们称之为实例原型)是一个对象,这个对象包含constructor这个属性,又指向回构造函数。这方面不懂的话可以再仔细阅读[JavaScript深入之从原型到原型链 ](https://github.com/mqyqingfeng/Blog/issues/2)这篇文章。*

接着我们取
```js
L = a.__proto__; // 看看这个a关联的实例原型是哪个
```
用L去和O比较,如果一样则返回true,如果不一样则顺着a的原型链往下遍历
```js
L = L.__proto__;
```
因为原型链的末端是null,所以判断到null之后就可以返回false了

## constructor
每个对象实例都会有用`__proto___`关联的实例原型，这个实例原型有constructor属性指向他的构造函数。所以我们可以使用constructor来判断类型
```js
function Animal(){}
var a = new Animal()
a.constructor === Animal    // true
```

使用constructor来判断变量类型的适用范围和局限性与instanceof大同小异，不同之处主要有

1. constructor指向的是最初创建当前对象的函数，是原型链最上层的那个方法,而instanceof是顺着原型链的。
```js
a.constructor === Object //false
```
2. constructor可以用来判断基本数据类型，而instanceof不行
```js
'abc'.constructor === String // true
// 上面代码等价于
(new String('abc')).constructor === String
```

*constructor和instanceof方法的一个局限性在于有可能因为constructor属性被修改或者原型链被修改导致失效*

*constructor和instanceof类型判断的另一个局限在在于会存在跨窗口问题，这点具体查看参考资料*

## Object.prototype.toString() 

当学习完了typeof和instanceof两个简洁明朗的操作符之后。我本以为本文差不多就可以完结了,当我一开始了解用Object.prototype.toString()这种方式来进行类型检查时,我甚至没有明白这种丑陋的方法有什么存在的必要。

我所忽略的是，在判断某个值的类型时，往往我们无法预先知道他是否是对象，也就由此无法知道是该用instanceof还是typeof。我们知道前者只适用于对象(基本类型没有原型链)，后者只能判断是不是对象，而无法判断具体是哪种对象。一般来说得先用typeof再用instanceof。实在过于麻烦。同时也由于前面几种方法各自的局限性。

相较于前面几种方法而言，toString方法是最为可靠的类型检测手段，它会将当前对象转换为字符串并输出。

```js
var number = 1;          // [object Number]
var string = '123';      // [object String]
var boolean = true;      // [object Boolean]
var und = undefined;     // [object Undefined]
var nul = null;          // [object Null]
var sym = Symbol("cai"); // [object Symbol]
var obj = {a: 1}         // [object Object]
var array = [1, 2, 3];   // [object Array]
var set = new Set();     // [object Set]
var map = new Map();     // [object Map]
var date = new Date();   // [object Date]
var error = new Error(); // [object Error]
var reg = /a/g;          // [object RegExp]
var func = function foo(){}; // [object Function]

function checkType() {
    for (var i = 0; i < arguments.length; i++) {
        console.log(Object.prototype.toString.call(arguments[i]))
    }
}
checkType(number, string, boolean, und, nul, sym, obj, array, set, map, date, error, reg, func)
```
当然除了以下这样利用Object.prototype.toString()的方式
```js
Object.prototype.toString.call(1)==="[object Number]" //true
```
我们也可以编写如下的type api来利用Object.prototype.toString() 
```js
//代码来自jQuery改写
var class2type = {};
"Boolean Number String Function Array Set Map Date RegExp Object Error Null Undefined Symbol".split(" ").map(function(item,index){
    class2type["[object " + item + "]"] = item.toLowerCase();
})
function type(obj) {
    return typeof obj === "object" || typeof obj === "function" ?
        class2type[Object.prototype.toString.call(obj)] || "object" :
        typeof obj;
}
type(function foo(){}) //"function"
type(new Set()) //"set"
type(Object.create(null)) //"object"
type(Symbol('cai')) //"symbol"
type(1) //"number"
```

#### 参考资料
[JavaScript之instanceof实现原理](https://zhuanlan.zhihu.com/p/27943354)
[JavaScript专题之类型判断(上)](https://github.com/mqyqingfeng/Blog/issues/28)
[如何检查JavaScript变量类型](http://harttle.land/2015/09/18/js-type-checking.html)
[判断plainObject、EmptyObject、Window 对象、ArrayLike、isElement的实现方法](https://github.com/mqyqingfeng/Blog/issues/30)