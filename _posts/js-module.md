# 长篇大论JavaScript模块机制

## 背景
在JavaScript中，最高级别的函数外定义的变量都是全局变量。老道在《JavaScript语言精粹》一书中将这一点批判为JavaScript语言的糟粕、毒瘤。全局变量的机制会带来许多问题，比如“命名空间污染”。对于这个JavaScript语言自身带来的问题，我在这里不深入探讨。说这个问题只是想说明，JavaScript语言自身这个糟粕，是谈论JavaScript模块机制的背景。大部分现代编程语言自始自终就有模块的概念，比如Java中的package。对于Java而言，就无需像下面一样我们长篇大论去讲他的模块机制。

## 模块模式
JavaScript在ES5之前没有模块机制，但是程序员们却有模块的需求，所以有很多人走了一条野路子，利用立即执行函数来创造一个局部的作用域。如下：
```js
var myGradesCalculate = (function () {

   // 在函数的作用域中下面的变量是私有的
  var myGrades = [93, 95, 88, 0, 55, 91];

  var average = function() {
    var total = myGrades.reduce(function(accumulator, item) {
      return accumulator + item;
      }, 0);

    return'Your average grade is ' + total / myGrades.length + '.';
  };

  var failing = function() {
    var failingGrades = myGrades.filter(function(item) {
        return item < 70;
      });

    return 'You failed ' + failingGrades.length + ' times.';
  };

  // 将公有指针指向私有方法

  return {
    average: average,
    failing: failing
  }
})();

myGradesCalculate.failing(); // 'You failed 2 times.' 
myGradesCalculate.average(); // 'Your average grade is 70.33333333333333.'
```
嗯，幸运的是我们现在无需使用这样的野路子了。但是立即执行函数创建局部作用域的hack技巧在某些时候或许也是有用的。

## CommonJS

上述的模块模式是存在缺陷的，缺陷之一是作为开发者，如果要引入这些模块的时候，必须清楚了解引入依赖的正确顺序。假设模块B.js依赖模块A.js，你在main.js里想要使用模块B.js的时候，你必须现在main.ja里引入A.js，之后再引入B.js。针对模块模式的缺陷，民间提出了许多JavaScript的模块机制方案，CommonJS就是其中较为流行的一种。CommonJS在目前(2018-02-19)依然是很常用，特别是其被作为nodejs的规范。

### CommonJS语法
```js
const fs = require('fs')
exports.fs = fs
module.exports = fs
```
关于module和module.exports区别是：

> exports对象是module.exports对象的一个引用，类似于执行了var exports = module.exports,require方能看到的只有module.exports这个对象，看不到exports对象。

如果还不明白，请看[Node.js模块里exports与module.exports的区别?](https://www.zhihu.com/question/26621212)

### AMD和UMD
CommonJS以服务器优先的方式来同步载入模块，假使我们引入三个模块的话，他们会一个个地被载入。不过这样的模式在浏览器端并不适合，因为读取网络文件比本地要更加耗时，这就导致如果你在浏览器端的js文件里使用require('a')就会导致后面的代码被阻塞。直到a模块载入完毕。所以Asynchronous Module Definition（异步模块定义规范），简称AMD流行了起来，而UMD则是创造了一种同时使用AMD和CommonJS两种规范的方法。一开始大家还比较喜欢在浏览器上采用这种异步小模块的加载方式，但并不是银弹。随着 Node.js 流行和 Browsersify 的兴起，运行时异步加载逐渐被构建时模块合并分块所替代。

## ES6 Modules

ES6带来了官方的模块机制。在不久的将来，这应该会是唯一的标准。Nodejs也在慢慢地向这一标准靠，好像Nodejs 8.5版本已经可以使用import/export语法了，这点不太确定，在这也不深究。而浏览器方面应该也在慢慢实现ES6 Module了吧，目前还是得利用babel转译。

### ES6 Modules语法

```js
import fs from 'fs'
import {default as fs} from 'fs'
import * as fs from 'fs'
import {readFile} from 'fs'
import {readFile as read} from 'fs'
import fs, {readFile} from 'fs'

export default fs
export const fs
export function readFile
export {readFile, read}
export * from 'fs'
```

更具体的使用方法可以查看[深入理解ES6 第十三章 用模块封装代码](https://sagittarius-rev.gitbooks.io/understanding-ecmascript-6-zh-ver/content/chapter_13.html)

## CommonJS和ES6 Modules的差异

ES6 模块跟 CommonJS 模块的不同，主要有以下两个方面：

1. ES6 模块输出的是值的引用，输出接口动态绑定，而 CommonJS 输出的是值的拷贝。

CommonJS可以理解为：在每个模块里有一个module.exports对象，当require侧引入了一个模块，那么这个模块的代码就会执行并且暴露出module.exports这个对象。重复引入这个模块不会重复执行模块的代码。对于module.exports对象的属性，如果属性是基本类型则require侧复制一个副本，属性是引用类型，则复制该引用类型的地址的副本。**可以把require()看作是对module.exports这个对象做一次浅拷贝然后通过赋值语句赋给变量(Left Value)**

ES6的话无论基本类型还是引用类型，你import进来的都是模块export出去的值的引用，也就是说即使export let foo = 1。此时你import { foo } from './a'。这里的foo 也不是模块中变量foo的副本，而是模块中foo的地址。对于export 引用类型则更是如此。

2. ES6 模块编译时执行，而 CommonJS 模块总是在运行时加载

> ES6 模块编译时执行会导致有以下两个特点
> 1. import 命令会被 JavaScript 引擎静态分析，优先于模块内的其他内容执行。
> 2. export 命令会有变量声明提前的效果。

这里的ES6模块编译时执行让我实在有点费解，js代码也要“编译”了？说实话我不是很清楚里面具体的机制，但是[论ES6模块系统的静态解析by贺师俊](http://hax.iteye.com/blog/1829042)这篇文章里面可以感受一下这一特性的高瞻远瞩。我目前所知的部分在于，ES6模块的这个特性似乎在解决模块循环依赖上比CommonJS胜一筹，而CommonJS在循环加载上遇到的问题可以在 [JavaScript 模块的循环加载](http://www.ruanyifeng.com/blog/2015/11/circular-dependency.html)略窥一二

## 模块打包

一般来讲，我们用模块化组织代码的时候，都会把模块划分在不同的文件和文件夹里，也可能会包含一些诸如React和Underscore一类的第三方库。

而后，所有的这些模块都需要通过`<script>`标签引入到你的HTML文件中，然后用户在访问你网页的时候它才能正常显示和工作。每个独立的`<script>`标签都意味着，它们要被浏览器分别一个个地加载。

这就有可能导致页面载入时间过长。

为了解决这个问题，我们就需要进行模块打包，把所有的模块合并到一个或几个文件中，以此来减少HTTP请求数。这也可以被称作是从开发到上线前的构建环节。

这一部分和前端工程化有千丝万缕的关系，具体可以查看参考资料

#### 参考资料
[JavaScript 模块化入门Ⅰ：理解模块](https://zhuanlan.zhihu.com/p/22890374)
[JavaScript 模块化入门Ⅱ：模块打包构建](https://zhuanlan.zhihu.com/p/22945985)
[深入理解 ES6 模块机制](https://zhuanlan.zhihu.com/p/33843378?utm_source=qq&utm_medium=social)
[require，import区别？by寸志](https://www.zhihu.com/question/56820346/answer/150743994)