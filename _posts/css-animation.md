# CSS-动画基础

CSS中和动画比较有关的属性差不多就transform、transition、animation这三个。这篇文章我们来简单了解一下他们的基础使用方式。

[查看配套的简单demo点击这里](https://caistrong.github.io/Blog/demos/css-animation/demo.html) 

## transform

首先我们从最简单的transform开始
```css
trandform: rotate(30deg);
```

> CSS transform 属性允许你修改CSS视觉格式模型的坐标空间。使用它，元素可以被平移（translate）、旋转（rotate）、缩放（scale）、倾斜（skew）

想要知道所有的变换和它们的使用方法请查看[MDN transform](https://developer.mozilla.org/zh-CN/docs/Web/CSS/transform)

简单说transform就是各种变换，不过最重要的是，**这种变换发生在瞬间**，也就是不管我们的变换是旋转还是平移缩放，他都是在瞬间完成的，我们只可以看到变换完成后的结果。这称不上是动画。所以我们需要transitions

## transition

transitions为CSS指定了时间轴，在不指定transition的时候，所有CSS属性的变化，比如width、backgroud-color之类的属性变化都是在瞬间完成的，有了transition，我们可以让这些变化在一段持续的时间完成。

想知道哪些属性的变换可以使用transition来过渡请查看[可动画属性的列表](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_animated_properties)

transition是transition-property、transition-duration、transition-timing-function、transiton-delay的简写属性。四个子属性分别代表 要控制的属性，持续时间，变换函数，延迟变换。

简写语法如下，box是那个你想“控制”它的属性变化持续时间的元素
```css
#box {
    /* transition: <property> <duration> <timing-function> <delay>; */
    transition: all, 1s, ease, 0.5s;
}
```

同时transition提供了一个事件transitioned来监听过渡完成。

更详细的可以查看[MDN transition](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_Transitions/Using_CSS_transitions)

transiton和transform的配合可以完成很多简单的动画，但是也存在一些局限。
>（1）transition需要事件触发，所以没法在网页加载时自动发生。

>（2）transition是一次性的，不能重复发生，除非一再触发。

>（3）transition只能定义开始状态和结束状态，不能定义中间状态，也就是说只有两个状态。

## animation

由于transition+transform的组合存在上述的局限性，因此CSS 3引入了Animation。CSS Animation可以看成是一套独立的动画系统。

举个例子（demo的实现代码）
```css
@keyframes mya {
            50% {
                background: rgb(175, 29, 29);
            }
            to {
                background: rgb(65, 167, 61);
                transform: rotate(30deg);
            }
        }
.run2{
            -webkit-animation: mya 3s ease 0.5s infinite;
            animation: mya 3s ease 0.5s infinite;
        }
```

这套系统通过animation-name将@keyframes和animation联系了起来。

其中@keyframes声明式地写出了动画过程的状态，作用类似于transform，但也存在不同之处，transform其实是定义了末状态，而@keyframes以%可以定义某个特定进度的状态。

而animation这个简写属性很像是增强了的transition。他的子属性也有animation-delay、animation-duration、animation-timing-function这些名字和作用都和transition相应子属性很像。但是除了这些以外，还有animation-direction、animation-iteration-count之类的增强的子属性。


更详细可以查看[MDN CSS Animations](https://developer.mozilla.org/zh-CN/docs/Web/CSS/CSS_Animations/Using_CSS_animations)

### Animate.css

在线上，我们可以使用一些现成的比如说Animate.css这个CSS动画库，一些常用的动画我们就无需自己写@keyframes

[Animate.css Github](https://github.com/daneden/animate.css)

#### 参考资料
[CSS动画简介](http://www.ruanyifeng.com/blog/2014/02/css_transition_and_animation.html)