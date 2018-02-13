---
title: CSS布局-喜大普奔flexbox
date: 2018-02-02 23:09:17
tags:
    - 布局
categories:
    - CSS
---

Flexbox是一种新技术，但在如今各个浏览器都广泛支持的情况下，它已经开始准备广泛应用了。 弹性盒子提供了工具，允许快速创建曾经被证明用CSS很难实现的一些复杂，灵活的布局和功能。
<!--more-->

以下简单的布局要求是难以或不可能用这样的工具（ floats 和 positioning）方便且灵活的实现的：

- 垂直居中父内容的里一块内容。
- 使容器的所有子项占用等量的可用宽度/高度，而不管有多少宽度/高度可用。
- 使多列布局中的所有列采用相同的高度，即使它们包含的内容量不同。

在没有flexbox之前我们用来解决上面一部分问题的奇技淫巧
[CSS 居中大全 by司徒正美](https://www.cnblogs.com/rubylouvre/p/3274273.html)
[把简单做好也不简单-css水平垂直居中](https://zhuanlan.zhihu.com/p/24419350)

flexbox目前存在跨浏览器兼容性的问题,所以我们有些时候仍然需要上面这些骚操作

大多数浏览器都支持 flexbox，诸如 Firefox, Chrome, Opera, Microsoft Edge 和 IE 11，较新版本的 Android/iOS 等等。但是你应该要意识到仍旧有被人使用的老浏览器不支持 flexbox （或者支持，但是只是支持非常非常老版本的 flexbox ）。
flexbox 相较其他一些 CSS 特性可能更为棘手。 例如，如果浏览器缺少 CSS 阴影，则该网站可能仍然可用。 但是假如不支持 弹性盒子功能就会完全打破布局，使其不可用。



我想我自己再怎么样也写不出比MDN 的这篇文档更好的flexbox教程了。

[MDN flexbox](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Flexbox)

所以也就不想写了，在下面做一点总结

在flexbox的容器中
```css
.container{
    display: flex;
    /* 声明为flexbox */
    flex-direction: column;
    /* 默认是row */
    flex-wrap: wrap;
    /* 自动换行，默认是nowrap */
    flex-flow: column wrap;
    /* 上面两个属性的缩写 */
    align-items: center;
    /* 沿着交叉轴的对齐方式 默认是stretch */
    justify-content: space-around;
    /* 沿着主轴的对齐方式  默认是flex-start*/
}
```
在flex-item中
```css
.xxx-item{
    flex:1;
    /* 这是一个无单位的比例值，表示每个 flex 项沿主轴的可用空间大小 */
}
.xxx-item:nth-of-type(3){
    order:-1;
    /* 越小排越前面 */
    flex:2;
    /* 第3个item讲比别的item多占一倍的可用宽度 */
    flex:2 200px;
    /* 这表示“每个flex 项将首先给出200px的可用空间，
    然后，剩余的可用空间将根据分配的比例共享“ */
}
```

#### 参考资料
[Flex 布局教程：语法篇 by阮一峰](http://www.ruanyifeng.com/blog/2015/07/flex-grammar.html)
[Flex 布局教程：实例篇 by阮一峰](http://www.ruanyifeng.com/blog/2015/07/flex-examples.html)
[这里有一个用flex布局的例子，并且对比了一种新兴的网格布局](https://zhuanlan.zhihu.com/p/26415902)