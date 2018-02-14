---
title: CSS-长度单位
date: 2018-02-01 22:32:50
tags:
    - em
    - rem
    - px
categories:
    - CSS
---

em、rem、px是css当中常用的单位，再加上%。我们几乎可以完全只靠这几个单位来使用CSS。
但是他们有什么区别，各自的适用场景又是什么
<!--more-->

## px

有一些人可能会认为px是绝对长度单位，特别是在与em和rem比较的时候。但是实际上px也是一个相对长度单位，如果把物理像素定为是绝对的固定的长度单位就更是如此。

物理像素指的是我们常听的那个分辨率。比如说1080p(1080x1920)的屏幕720p(720x1280)的屏幕。

window对像有个属性window.devicePixelRatio.他的含义如下
```
物理像素 = css pixel * devicePixelRatio
```

*大部分安卓设备的css pixel尺寸都是360x640,但是他们的分辨率却有1080x1920还是720x1280之分，由此以知对于1080p分辨率手机，它的devicePixelRatio = 3，而720p手机的devicePixelRatio = 2*

我们在设计网页的时候可以使用这个360x640的标准来设计，不同分辨率的设备使用我们设计出来的网页时，区别只在于，我们的一个css像素，在更高分辨率的移动端设备中会有更多的物理像素来展现。

*而对于图片，比如一张实际大小100x100px的图片，并且width和height都设了100px(注意这里的px是css pixel)，实际占用了屏幕的像素数就是(假设devicePixelRatio是3)300x300px(注意这里的px是真实的屏幕像素)所以，如果希望网页的元素在高ppi设备上显示不模糊(比如1080x1920屏幕的手机)，位图应该做3倍的尺寸(比如做300x300px的图，然后在css中设width和height为100px)，svg(矢量图)就无所谓了。*

px像素的所谓相对，是相对于物理像素而言的，而由于devicePixelRatio一般我们也不会去改变，因此css pixel在我们的设计中可以看成是绝对的

### px使用场景
**当元素应该是严格不可缩放的时候**
在一个典型的 web 设计的过程中，不会有很多部分的你不能使用伸缩性设计的布局。 不过偶尔你会遇到真的需要使用显式的固定的值，以防止缩放的元素。

采用固定的尺寸值的前提应该是，如果被缩放的话，它的结构会被打碎。 这真的不常出现，所以你想拿出那些 px 单位之前，问问自己是否使用它们是绝对必要的。

## rem

当使用 rem 单位，他们转化为像素大小取决于页根元素的字体大小，即 html 元素的字体大小。 根元素字体大小乘以你 rem 值。
```css
html{
    font-size:16px;
}
div{
    padding:10rem;
    /* padding:160px */
}
```
### rem使用场景
1. 简单地说，一切可扩展都应该使用 rem 单位
2. 始终使用 rem 单位做媒体查询
3. 使用 rem 单位的字体大小，em 单位只在特殊的情况下使用

如果用户设定了浏览器的字体大小并且我们没有人工地设定html的font-size值，那么html的font-size会从浏览器的设定中继承。如果你人工地将html的值设定为一个固定的值如上面代码中设为了16px。那么就相当于剥削了用户自行调整页面字体大小的能力。因为html已经有font-size了，他不需要去继承用户设定中的字体大小。如果您确实需要更改 html 元素的字体大小，那么就使用em，rem单位，这样根元素的值还会是用户浏览器字体大小的乘积。

最佳实践
```css
html{
    font-size:1em;
    /* 或者1.5em等任意其他值也行 */
}
h1{
    font-size:2rem
}
div{
    padding:1.2rem
}
```

## em
有一个比较普遍的误解，认为 em 单位是相对于父元素的字体大小。 事实上，根据W3标准 ，它们是相对于使用em单位的元素的字体大小。
父元素的字体大小可以影响 em 值，但这种情况的发生，纯粹是因为继承

看下面的例子
```html
<div class="wrapper">
    <div class="inheritance_demo box">
        Inheritance with em units demo
    </div>
</div>
```
```css
html{
    font-size:16px
}
.wrapper {
  font-size: 1.25rem;
  /* 16x1.25=20px */
}

.inheritance_demo {
  font-size: 14px;
  /* 如果是font-size: 1.2em 他会先从父级继承20px这个值然后乘以1.2变成24px。此时下面的padding会变成1.5x24=36px*/
  padding: 1.5em;
  /* 14x1.5=21px */
}
```

### em的适用场景

举个简单例子
```css
.button1{
    font-size: 1.25rem;
    padding: 2.5rem;
}
```
上面设计navbar的效果是不如下面的方式的
```css
.button2{
    font-size: 1.25rem;
    padding: 2em;
}
```
对于上面的设计方式而言，在浏览器初始设定html的font-size为16px时。button1的里面字体的大小是1.25x16=20px。内边距是16x2.5=40px。内边距刚好是字体大小的两倍。但是当你想修改button1的字体大小，比如将其改为1.5rem。那么如果你想继续保持内边距是字体的两倍时，你也要将padding改为3rem。如果你还有margin,line-height等属性想保持一定的比例，那你就都得改。使用button2的方式padding永远是本元素font-size的2倍，你如果想改font-size直接改就是。

### 适用场景
**多列布局**
布局中的列宽通常应该是 %，因此他们可以流畅适应无法预知大小的视区。

然而单一列一般仍然应使用 rem 值来设置最大宽度。

例如:
```css
.container {
    width: 100%;
    max-width: 75rem;
}
```
这保持列的灵活，可扩展。又能防止变得太宽了。

#### 重要参考
[综合指南: 何时使用 Em 与 Rem](https://webdesign.tutsplus.com/zh-hans/tutorials/comprehensive-guide-when-to-use-em-vs-rem--cms-23984)