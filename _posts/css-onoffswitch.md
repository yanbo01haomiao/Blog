# CSS 实现左右滑动开关

首先我们来看一下要实现的效果
[纯CSS实现的滑动开关](https://caistrong.github.io/Blog/demos/css-onoffswitch/demo.html)

这个滑动开关在html中可以看成是一个`<input type="checkbox">`，选中就是on，未选中就是off。

我们在创建一些表单元素的时候，经常会见到`<label>`这个元素，比如一个输入框`<input type="text" id="name">`，我们可以创建一个`<label for="name">name</label>`和输入框进行绑定。

在我们这个CSS滑动开关的实现中，我们也创建一个`<label>`和这个`<input type="checkbox">`进行绑定,
这样的时候我们点击`<label>`标签的内容也可以checked。

根据上面，我们看一下这个开关的HTML结构

```html
<div class="onoffswitch">
    <input type="checkbox" name="onoffswitch" class="onoffswitch-checkbox" id="myonoffswitch" checked>
    <label class="onoffswitch-label" for="myonoffswitch">
        <span class="onoffswitch-inner"></span>
        <span class="onoffswitch-switch"></span>
    </label>
</div>
```

我们的主要思路是这样的

1. 我们先给整个`div元素.onoffswitch`添加一个固定的宽高，这是这个组件的大小

2. 我们的`input元素.onoffswitch-checkbox`最后会被设置为**display:none**。也就是默认的那个小正方形框的checkbox会被隐藏。

3. 因为2，所以我们最后在页面上显示的元素就只有`label元素.onoffswitch-label`下的两个span。

4. 关于第一个`span元素.onoffswitch-inner`我们给它设置一个**200%**，这样的话他的宽度会变成我们组件的2倍。

5. 对于我们的`span元素.onoffswitch-inner`。我们给它添加两个伪元素分别是::before和::after，对于这两个元素。我们设置他的宽为**50%**。这个**50%**是相对于他的父元素`span元素.onoffswitch-inner`而言的。所以这两个伪元素的宽度实际上等同于组件的宽度。

6. 我们将`span元素.onoffswitch-inner`设置一个负边距margin-left: -100%;这样相当于把`span元素.onoffswitch-inner`左移一个组件宽度的距离，这样我们把::after这个伪元素暴露出来。

7. 对于::before和::after这两个伪元素，我们采用了height:3rem; line-height: 3rem;text-align: center;这两个技巧对文字进行水平垂直居中。

8. 对于`span元素.onoffswitch-switch`，他就是开关上的那个小白圆圈，只要为他设置好width、heigt、border-radius。然后用position: absolute; top: 0; bottom: 0; margin: auto;这种hack技巧为他做个垂直居中即可

关键代码如下：

```css
.onoffswitch {
    position: relative;
    width: 7rem;
    height: 3rem;
}
.onoffswitch-inner {
    display: block;
    width: 200%;
    margin-left: -100%;
}
.onoffswitch-inner::before, .onoffswitch-inner::after {
    display: block;
    float: left;
    line-height: 3rem;
    text-align: center;
    width: 50%;
}
.onoffswitch-inner::before {
    content: 'ON';
    background-color: #34A7C1;
}
.onoffswitch-inner::after {
    content: 'OFF';
    background-color: #EEEEEE;
}
.onoffswitch-switch {
    display: block;
    position: absolute;
    top: 0;bottom: 0; margin: auto;
    right: 4.5rem;
    width: 1.5rem; height: 1.5rem; border-radius: 50%;
    background: white;
    border: 2px solid #999999;
}
```

进行上述步骤之后的代码效果大致如下：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-onoffswitch/step0.png)

9. 我们可以使用:check这个伪类选择器来渲染当checkbox被checked时的样式。在我们这里主要把margin-left: 0;
刚刚把`span元素.onoffswitch-inner`左移了，现在移回来，等同于又把::before元素又换回来。把::after又隐藏了。

10. `span元素.onoffswitch-switch`这个元素也差不多是类似的方式，变换的参数变成了绝对定位的right。

```css
.onoffswitch-checkbox {
    display: none;
}
.onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-inner {
    margin-left: 0;
}
.onoffswitch-checkbox:checked + .onoffswitch-label .onoffswitch-switch {
    right: 1rem;
}
```
进行上述步骤之后我们点击了组件checked后效果大致如下：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-onoffswitch/step1.png)

11. 然后使用transition为上面的margin-left和right之类的属性变化过渡添加一个时间轴，也就是让这两个属性的变化在一段时间完成。

12. 最后我们使用overflow: hidden;隐藏突出的伪类元素，然后**display:none**隐藏`input元素.onoffswitch-checkbox`，为整个按钮添加border-radius美化下样式。

```css
.onoffswitch-inner {
    transition: all 0.3s ease-in 0s; 
}
.onoffswitch-switch {
    transition: all 0.3s ease-in 0s; 
}
.onoffswitch {
    overflow: hidden;
    border-radius: 5rem;
}
.onoffswitch-checkbox {
    display: none;
}
```

完成！

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-onoffswitch/step2.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/css-onoffswitch/step3.png)

#### 参考资料
[onoff  proto.io](https://proto.io/freebies/onoff/)