---
title: JavaScript遍历
date: 2018-02-12 21:35:33
tags:
    - JavaScript
    - 遍历
    - 循环
categories:
    - JavaScript
---
遍历数组，遍历对象属性，甚至是遍历字符串、Map、Set等一切可迭代的对象。是我们在编程中经常要做的事情。JavaScript也提供了诸多方法来实现遍历。

<!--more-->

## 原始的遍历方式

```js
for (var index = 0, len = myArray.length; index < len ; index++) {
  console.log(myArray[index]);
}
```

说实话，这样的遍历方式虽然原始，但是如果平时我们用于简单遍历数组的时候，感觉除了写起来比较不简洁美观，也没有太多缺点，相反他是效率最高的遍历方法（前端的数据量一般都比较小，所以效率不是首要考虑的，无需过早优化，应该把可读性，可维护性，可测试性放到首位）。

## 遍历数组forEach

```js
[1, 2, , 4].forEach(function (value) {
  console.log(value);
});
//1、2、4
```
可以到[MDN forEach](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach)这里去看forEach的polyfill实现。

Array.prototype除了forEach还有map、filter、reduce等方法，应该考虑语义和可读性选用相应的遍历方法:
> 如果你需要将数组按照某种规则映射为另一个数组，就应该用 map.
如果你需要进行简单的遍历，用 forEach 或者 for of.
如果你需要对迭代器进行遍历，用 for of.
如果你需要过滤出符合条件的项，用 filter.
如果你需要先按照规则映射为新数组，再根据条件过滤，那就用一个 map 加一个 filter.

## 遍历对象for...in

for...in语句以任意顺序遍历一个对象的可枚举属性（key值）。包括对象从其构造函数原型中继承的属性。但是有以下几个要点:

1. for...in不应该用于迭代一个Array，原因是Array重视迭代顺序。
2. 如果你只要考虑对象本身的属性，而不是它的原型，那么使用 getOwnPropertyNames() 或执行 hasOwnProperty() 来确定某属性是否是对象本身的属性

更详细的清参考[MDN for...in](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Statements/for...in)

## ES6引入的神器for..of

可迭代对象（ iterable ）是包含 Symbol.iterator 属性的对象，与迭代器紧密相关。这个 Symbol.iterator 知名符号定义了为指定对象返回迭代器的函数。**在 ES6 中，所有的集合对象（数组、 Set 与 Map ）以及字符串都是可迭代对象，因此它们都有默认的迭代器，所以我们可以很容易地遍历这些可迭代对象**。可迭代对象被设计用于与 ES 新增的 for-of 循环配合使用。更具体的请参考文末所附的参考资料中的深入浅出ES6中的内容.

**遍历数组、Set、Map：他们分别有keys()、values()、entries()三个迭代器**
```js
let colors = [ "red", "green", "blue" ];
let tracking = new Set([1234, 5678, 9012]);
let data = new Map();

data.set("title", "Understanding ES6");
data.set("format", "print");

// 与使用 colors.values() 相同
for (let value of colors) {
    console.log(value);
}

// 与使用 tracking.values() 相同
for (let num of tracking) {
    console.log(num);
}

// 与使用 data.entries() 相同
for (let entry of data) {
    console.log(entry);
}
```
**遍历字符串**
```js
var message = "A 𠮷 B";

for (let c of message) {
    console.log(c);
}
//A (blank) 𠮷 (blank) B
```
**遍历NodeList**
```js
//以前循环一个Nodelist有很多困难，现在Nodelist也有默认的迭代器了
let articleParagraphs = document.querySelectorAll("article > p");

for (let paragraph of articleParagraphs) {
  paragraph.classList.add("read");
}
```

**循环一个拥有enumerable属性的对象**
我们自己的对象,如果没有包含Symbol.iterator属性,有一个默认的迭代器的话是无法进行遍历的,但我们可以配合**Object.keys()方法**,Object.keys()和for...in遍历的区别只在于Object.keys()不会去找原型链的可迭代属性,可以理解为Object.keys()=for...in+hasOwnProperty()

```js
for (var key of Object.keys(someObject)) {
  console.log(key + ": " + someObject[key]);
}
```


#### 参考资料
[MDN forEach](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Array/forEach)
[MDN for...in](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Statements/for...in)
[JS-对象无效属性与forEach——一个考题引起的思考](https://www.jianshu.com/p/21719de4951b#fn1)
[深入浅出ES6-迭代器与生成器-可迭代对象与 for-of 循环](https://sagittarius-rev.gitbooks.io/understanding-ecmascript-6-zh-ver/content/chapter_8.html)