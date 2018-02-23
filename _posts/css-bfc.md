# CSS-Block Formatting Contexts 

曾经在知乎上看人讨论[CSS为什么这么难学](https://www.zhihu.com/question/66167982/answer/239709754)，有人回答因为CSS不正交。即a属性的设置和b属性的设置是相互关联影响的。假设ab属性各有两个值，则有4种情况。我大体上同一这一观点。答案说是因此，CSS学习要多试，我对此也不做反驳。但是除了试以外，我觉得了解类似CSS中视觉表现模型是如何工作的之类的原理性知识，应该是相对于试以外更加事半功倍的方法。今天我就想简单了解下Block Formatting Contexts (块级格式化上下文)

## 布局上下文

所谓上下文(context)，在计算机领域许多地方都会用到这一个词，比如JavaScript的执行上下文。在我的理解中，上下文就是一个环境，在JavaScript中它可能是函数执行的环境。而在CSS中，也可以把BFC理解为是一个布局上下文环境，也就是一个容器。在这个容器里的box(包括inline,block两种)的布局，与这个容器外毫不相干。我们这里应该意识到，除了BFC外，还存在普通容器，也就是没有触发BFC的时候，页面上的块级元素都是包含在普通容器下。而BFC 具有普通容器没有的一些特性，例如可以包含浮动元素。

```html
<!DOCTYPE html>
<html>
	<head></head>
	<body>
		<div>
            <p>hello world</p>
		</div>
	</body>
</html>
```
一个元素的布局上下文就是该元素的包含块，它由离该元素最近的块级元素担任。上面的p元素的布局上下文就是div。这时候div就可以看成一个普通容器，p元素在这个容器里(盒模型的content)，同时div又在一个由根元素触发的BFC容器里。

*如果该元素是position:abosulte定位的元素，则它的布局上下文即包含块，则是向上找positioned(position值非static)的块级元素，该块级元素则是该元素的容器/定位原点。*

我们可以从[MDN BFC](https://developer.mozilla.org/zh-CN/docs/Web/Guide/CSS/Block_formatting_context)上了解到哪些情况可以触发BFC。其中常见包括如下：
- 根元素或其它包含它的元素
- 浮动元素 (元素的 float 不是 none)
- 绝对定位元素 (元素的 position 为 absolute 或 fixed)
- 内联块元素 (元素具有 display: inline-block)
- 弹性元素 (display: flex 或 inline-flex元素的子元素)

### 常用触发BFC的方式
```css
.bfc {
  overflow:hidden;
  zoom:1; /*为了兼容IE的hasLayout*/
}
```
## BFC的特性

从整体上看，BFC 是隔离了的容器，这个具体可以表现为三个特性：
1. BFC 会阻止外边距折叠

两个相连的 div 在垂直上的外边距会发生叠加，这时如果触发其中的一个div为BFC，这时候这个div就会表现为一个隔离的容器而阻止了外边距的折叠。

2.  BFC 可以包含浮动的元素

触发浮动元素父元素的 BFC 特性，可以包含浮动元素，闭合浮动。

W3C 的原文是“'Auto' heights for block formatting context roots”，也就是 BFC 会根据子元素的情况自动适应高度，即使其子元素中包括浮动元素。

3. BFC 可以阻止元素被浮动元素覆盖

浮动元素的块状兄弟元素会无视浮动元素的位置，尽量占满一整行，这样就会被浮动元素覆盖，为该兄弟元素触发 BFC 后可以阻止这种情况的发生。

至于BFC这些特性可以在什么情况下帮到我们，具体可以看文末所附参考2，3。


### 参考资料
1. [结合了BFC的Normal Flow](https://swordair.com/css-positioning-schemes-normal-flow/)
2. [详说 Block Formatting Contexts (块级格式化上下文)](http://kayosite.com/block-formatting-contexts-in-detail.html)
3. [understanding-block-formatting-contexts-in-css](https://www.sitepoint.com/understanding-block-formatting-contexts-in-css/)
4. [understanding-block-formatting-contexts-in-css的中文不完整翻译](https://www.jianshu.com/p/fc1d61dace7b)
5. [CSS的一些大杂烩坑](https://www.cnblogs.com/yexiaochai/archive/2013/05/20/3086697.html)