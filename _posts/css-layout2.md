---
title: CSS布局-烦人的float
date: 2018-02-02 20:59:59
tags:
    - 布局
categories:
    - CSS
---

极端的来讲，我觉得所谓的CSS布局讨论来讨论去，唯一的目的就是为了创建多列布局。由于在normal flow中。块级元素的排列都是另起一行的。浮动，甚至其他的布局技术其实都是为了打破块级元素的这一默认设置。创建多列布局。

<!--more-->

```css
div{
    float:left;
}
```
### 浮动的规则
浮动的规则用通俗的白话描述就是
  **假如某个div元素A是浮动的，如果A元素上一个元素也是浮动的，那么A元素会跟随在上一个元素的后边(如果一行放不下这两个元素，那么A元素会被挤到下一行)；如果A元素上一个元素是标准流中的元素，那么A的相对垂直位置不会改变，也就是说A的顶部总是和上一个元素的底部对齐。**

### 使用浮动创建多列布局

**顶上的h1在文档流中，因此下面的3个div的顶部会和h2的底部对齐**

```html
<h1>3 column layout example</h1>
<div>
  <h2>First column</h2>
  <p> Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla luctus aliquam dolor, eu lacinia lorem placerat vulputate. Duis felis orci, pulvinar id metus ut, rutrum luctus orci. Cras porttitor imperdiet nunc, at ultricies tellus laoreet sit amet. Sed auctor cursus massa at porta. Integer ligula ipsum, tristique sit amet orci vel, viverra egestas ligula. Curabitur vehicula tellus neque, ac ornare ex malesuada et. In vitae convallis lacus. Aliquam erat volutpat. Suspendisse ac imperdiet turpis. Aenean finibus sollicitudin eros pharetra congue. Duis ornare egestas augue ut luctus. Proin blandit quam nec lacus varius commodo et a urna. Ut id ornare felis, eget fermentum sapien.</p>
</div>

<div>
  <h2>Second column</h2>
  <p>Nam vulputate diam nec tempor bibendum. Donec luctus augue eget malesuada ultrices. Phasellus turpis est, posuere sit amet dapibus ut, facilisis sed est. Nam id risus quis ante semper consectetur eget aliquam lorem. Vivamus tristique elit dolor, sed pretium metus suscipit vel. Mauris ultricies lectus sed lobortis finibus. Vivamus eu urna eget velit cursus viverra quis vestibulum sem. Aliquam tincidunt eget purus in interdum. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.</p>
</div>

<div>
  <h2>Third column</h2>
  <p>Nam consequat scelerisque mattis. Duis pulvinar dapibus magna, eget congue purus mollis sit amet. Sed euismod lacus sit amet ex tempus, a semper felis ultrices. Maecenas a efficitur metus. Nullam tempus pharetra pharetra. Morbi in leo mauris. Nullam gravida ligula eros, lacinia sagittis lorem fermentum ut. Praesent dapibus eros vel mi pretium, nec convallis nibh blandit. Sed scelerisque justo ac ligula mollis laoreet. In mattis, risus et porta scelerisque, augue neque hendrerit orci, sit amet imperdiet risus neque vitae lectus. In tempus lectus a quam posuere vestibulum. Duis quis finibus mi. Nullam commodo mi in enim maximus fermentum. Mauris finibus at lorem vel sollicitudin.</p>
</div>
```
```css
* {
  box-sizing: border-box;
  /* 这个设定可以保证我们的div即使添加了多少padding、border也不会因为width变大被挤到下面去 */
  /* 因为border-box如果新增了border、padding。挤压的是content-box的空间 */
}

/* 多列布局的长度单位一般是% */
body {
  width: 90%;
  max-width: 900px;
  margin: 0 auto;
}

div:nth-of-type(1) {
  width: 36%;
  float: left;
}

div:nth-of-type(2) {
  width: 30%;
  float: left;
  margin-left: 4%;
}

div:nth-of-type(3) {
  width: 26%;
  float: right;
}
/* 我们设置了列的宽度以便它们都能匹配——36% + 30% + 4% + 26% = 96%，在第二和第三列之间留下一个4%的余数。 */
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-layout2/3column.png)
### 清除浮动的规则

**对于CSS的清除浮动(clear)，一定要牢记：这个规则只能影响使用清除的元素本身，不能影响其他元素。**

```css
.clearbox{
    clear:both;
    /* 还有left,right。both最常用 */
}
```
当你把clear 属性应用到一个元素上时，它主要意味着"此处停止浮动"——这个元素和源码中后面的元素将不浮动，除非您稍后将一个新的float声明应用到此后的另一个元素。

添加了clear属性之后，这个属性的顶部会和他前面的一堆被floated的元素中最高的一个的底部对齐。感觉有点像是那些被floated的元素又回到了文档流，占领了他们本来占领着的空间。

### 清除浮动的示例

接着上面的三列布局。假设我们现在想给html文档添加一个footer元素，在布局上放在上面3个并排的div下面。并且和他们有一定的边距。

我们先在div下添加footer
```html
<footer>
    <p>&copy;2016 your imagination. This isn't really copyright, this is a mockery of the very concept. Use as you wish.</p>
</footer>
```
```css
footer{
  border: 3px dotted red;
}
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-layout2/beforeclear.png)
添加了清除浮动的代码
```css
footer{
  clear: both;
  border: 3px dotted red;
}

```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-layout2/clear.png)
接下去我们想让这个footer往上推开一个上外边距，我们设置
```css
footer{
  clear: both;
  border: 3px dotted red;
  margin-top:100px;
}
```
我们发现这并不起作用，除了这个问题以外，浮动还有以下问题
1. 首先，他们在父元素中所占的面积的有效高度为0 ——尝试在浏览器中加载 1_three-column-layout.html 并用开发工具查看 <body> 的高度，你将会看到我们的意思是什么——所报告的正文高度只有 <h1> 的高度 。这个可以通过很多方式解决，但是我们所依赖的是在父容器的底部清除浮动，如我们在我们的当前示例所做的那样。 如果检查当前示例中正文的高度，您应该看它的高度是行为本身。
2. 其次，非浮动元素的外边距不能用于它们和浮动元素之间来创建空间——这是我们在这里眼前的问题，我们将在下面实施修复。
3. 还有一些关于浮动的奇怪的事情——[Chris Coyier优秀的关于Floats文章](https://css-tricks.com/all-about-floats/)概述了其他一些以及修复这些。

我们来解决这些问题
在`<footer>`上方添加
```html
<div class="clearfix"></div>
<!-- 如果您没有一个可用的元素来清除您的浮动(比如我们的页脚)，在您想要清除的浮动之后添加一个看不见的“clearfix div”是非常有用的
 -->
```
移除footer的clear:both,添加
```css
.clearfix {
  clear: both;
}
```
这下footer的margin-top生效了

#### 一个能体现float优于其它布局的例子

使用绝对定位的效果不如浮动

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-layout2/floatdemo.png)

#### 参考资料
[CSS浮动通俗讲解 by杨元](https://www.cnblogs.com/iyangyuan/archive/2013/03/27/2983813.html)
[MDN 浮动](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Floats)