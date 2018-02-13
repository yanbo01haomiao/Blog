---
title: CSS布局-positioned
date: 2018-02-02 22:39:28
tags:
    - 布局
categories:
    - CSS
---
定位允许您从正常的文档流布局中取出元素，并使它们具有不同的行为，例如放在另一个元素的上面，或者始终保持在浏览器视窗内的同一位置

<!--more-->

### 文档流
我们在前面已经讲过一次文档流了，让我们再总结一次。

> 首先，环绕元素内容添加任何内边距、边界和外边距来布置单个元素盒子——这就是 盒模型 ，我们前面看过。 默认情况下，块级元素的内容宽度是其父元素的宽度的100％，并且与其内容一样高。内联元素高宽与他们的内容高宽一样。您不能对内联元素设置宽度或高度——它们只是位于块级元素的内容中。 如果要以这种方式控制内联元素的大小，则需要将其设置为类似块级元素 display: block;。

这只是解释了单个元素，但是元素相互之间如何交互呢？ 正常的布局流（在布局介绍文章中提到）是将元素放置在浏览器视口内的系统。默认情况下，块级元素在视口中垂直布局——每个都将显示在上一个元素下面的新行上，并且它们的外边距将分隔开它们。

内联元素表现不一样——它们不会出现在新行上；相反，它们互相之间以及任何相邻（或被包裹）的文本内容位于同一行上，只要在父块级元素的宽度内有空间可以这样做。如果没有空间，那么溢流的文本或元素将向下移动到新行。

如果两个相邻元素都在其上设置外边距，并且两个外边距接触，则两个外边距中的较大者保留，较小的一个消失——这叫外边距折叠, 我们之前也遇到过。

先建好准备要探究的试验田
```html
<h1>Basic document flow</h1>

<p>I am a basic block level element. My adjacent block level elements sit on new lines below me.</p>

<p class="positioned">By default we span 100% of the width of our parent element, and we are as tall as our child content. Our total width and height is our content + padding + border width/height.</p>

<p>We are separated by our margins. Because of margin collapsing, we are separated by the width of one of our margins, not both.</p>

<p>inline elements <span>like this one</span> and <span>this one</span> sit on the same line as one another, and adjacent text nodes, if there is space on the same line. Overflowing inline elements will <span>wrap onto a new line if possible (like this one containing text)</span>, or just go on to a new line if not, much like this image will do: <img src="https://mdn.mozillademos.org/files/13360/long.jpg"></p>
```
```css
body {
  width: 500px;
  margin: 0 auto;
}

p {
  background: aqua;
  border: 3px solid blue;
  padding: 10px;
  margin: 10px;
}

span {
  background: red;
  border: 1px solid black;
}
```
<img src="css-layout3/normal.png" width="100%">
### 静态定位static
```css
.positioned{
    position: static;
}
```
这个没什么特别的，因为他是position的默认值

### 相对定位relative
```css
.positioned{
    position: relative;
    background: yellow;
    top: 30px;
    left: 30px;
}
```
<img src="css-layout3/relative.png" width="100%">
发现div相对自己原来的位置偏移了，往右往下各30px。同时原来占据的空间没有被其他元素占据。relative是不脱离文档流的。

### 绝对定位absolute
```css
.positioned{
    position: absolute;
    background: yellow;
    top: 30px;
    left: 30px;
}
```
<img src="css-layout3/absolute.png" width="100%">

可以看到他相对于html元素离压面的边缘的顶部和左侧都相距30px。并且脱离了文档流。原来占据的空间被其他还在文档流的元素占据了。

*绝对定位的元素不再存在于正常文档布局流程中。相反，它坐在它自己的层独立于一切。这是非常有用的——这意味着我们可以创建不干扰页面上其他元素的位置的隔离的UI功能 ——例如弹出信息框和控制菜单，翻转面板，可以在页面上的任何地方拖放的UI功能等。*

#### 定位上下文
我们把body改为相对定位
```css
body{
    position: relative;
}
```
这下我们的positioned这个div由相对html改为相对body定位了
<img src="css-layout3/absolute1.png" width="100%">

**绝对定位相对于其自身元素的(第一个被positioned，且positon不能为static的)祖先元素定位**

而z-index可以决定，谁在图层(暂且这么叫)的上方，谁在下方

### 固定定位

还有一种类型的定位覆盖——fixed。 这与绝对定位的工作方式完全相同，只有一个主要区别——绝对定位固定元素是相对于 `<html>` 元素或其最近的定位祖先，而固定定位固定元素则是相对于浏览器视口本身。 这意味着您可以创建固定的有用的UI项目，如持久导航菜单。

*有那么一点像em和rem。绝对定位是em,固定定位是rem*

#### 参考资料
[MDN 定位](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/%E5%AE%9A%E4%BD%8D)
[css绝对定位、相对定位和文档流的那些事](https://www.cnblogs.com/tim-li/archive/2012/07/09/2582618.html)