# JavaScript事件

*本文是之前记在印象笔记里的高程笔记，转移过来*

JavaScript是观察员模式的模型：用侦听器来预订事件的方式，支持页面的行为（JavaScript代码）与页面的外观（HTML和CSS代码）之间的松散耦合

起源是为了分担服务器运算负载

首先理下概念
事件event：click load mouseover...
事件处理函数eventHandler（侦听器）：onclick onload onmouseover...

## 事件流：
### 历史：
IE事件冒泡流（最深／具体的元素往最浅／不具体元素上传播，直到window对象），
Netscape事件捕获流（最不具体的节点更早接收事件，最具体的最后接受，从window对象开始捕获）
### 标准：DOM事件流
事件捕获阶段 (为截获阶段提供机会) 
处于目标阶段(接收到事件，做出响应)  
事件冒泡阶段(做出响应)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event/eventflow.png)

## 添加事件处理程序
1. HTML元素上有与事件处理程序同名的特性（attribute）
```html
<input type="button" value="Click Me" onclick="alert('Clicked')"/>
```
```html
<input type="button" value="Click Me" onclick="showMessage()"/>
<script type="text/javascript">
    function showMessage(){
        alert("Clicked");
    }
</script>
```
**缺点：**
- HTML与JavaScript紧密耦合，想更改事件处理程序得修改两处
- 用户可能在事件处理函数未加载完毕就触发了事件

2. DOM0级事件处理程序
```js
var btn = document.getElementById("mybtn")
btn.onclick = function(){
    alert("Clicked")
    alert(this.id)//"mybtn"
}

btn.onclick = null //删除事件处理程序
```
**缺点：**
- 无法为一个事件添加多个事件处理函数
- 无法指定冒泡还是捕获

3. DOM2级事件处理程序
＂DOM2级事件＂定义了两个方法，用于处理指定的删除事件处理程序的操作
EventTarget.addEventListener()和EventTarget.removeEventListener()
接收三个参数 1要处理的事件名 2作为事件处理程序的函数 3布尔值 true捕获阶段调用事件处理程序，false冒泡阶段调用时间处理程序，默认false

```js
var btn = document.getElementById("mybtn")
btn.addEventListener("click",function(){
   alert(this.id) //mybtn
},false)

//DOM2的好处之一是可以添加多个事件处理程序，如下
btn.addEventListener("click",function(){
   alert("Clicked") 
},false)

//这两个事件处理程序会按照添加他们的顺序触发

//没有用！无法移除。两个匿名函数不是同一个
btn.removeEventListener("click",function(){
   alert(this.id) //mybtn
},false)
```
通过addEventListener()添加的事件处理程序只能使用removeEventListener()来移除，移除时的参数和添加时的参数相同，这也意味着addEventListener()添加的匿名函数无法移除

4. IE事件处理程序（不知道这边是不是必须看，暂且看一遍）
类似的两个方法attachEvent()和detachEvent()
接收的参数  事件处理程序的名称和事件处理程序函数
```js
var btn = document.getElementById("mybtn")
btn.attachEvent("onclick",function(){  //onclick不是click
    alert("Clicked") 
    alert(this === window)   //true
})

//也可以添加多个事件处理程序 执行顺序与DOM相反
btn.attachEvent("onclick",function(){  //onclick不是click
    alert("Clicked(dispatched first)") 
})
```
//与DOM的一个巨大区别就是，DOM的事件处理程序的作用域会在所属元素的作用域内运行(this会绑定currentTarget那个元素对象)，而IE的事件处理程序会在全局作用域中运行

## 事件对象
在触发DOM上的某个事件时，会产生一个事件对象event，对象包含着与事件有关的信息，包括导致事件的元素，事件的类型，与特定事件相关的信息（鼠标操作：鼠标的位置，键盘操作：按下的键）

DOM中的事件对象
无论是DOM０还是DOM2，都会传入event对象
```js
var btn = document.getElementById("mybtn")
btn.onclick = function(event){
    alert(event.type) //"click"
}

btn.addEventListener("click",function(event){
   alert(event.type) //"click"
},false)
```

**在事件处理程序的内部，对象this始终等于currentTarget,而target则只包含事件的实际触发的目标。**

如果直接将事件处理程序指定给了目标元素，则this currentTarget和target包含相同的值
```js
var btn = document.getElementById("myBtn")
btn.onclick = function(event){
    alert(event.currentTarget === this)  //true
    alert(event.target === this) //true
}
```

包含值不同的例子
```js
document.body.onclick = function(event){
    alert(event.currentTarget === document.body) //true
    alert(this === document.body) //true
    alert(event.target === doucument.getElementById("myBtn")) //true 前提是你触发点击这个event是在点按钮的时候
}
```

event这个对象发生在事件发生时，以上两个例子的event产生的途径都是用户使用鼠标点击,**如果点击按钮的话 event.target就是那个按钮 如果点击一个标题的话event.target就是那个标题**。而event.currentTarget指向绑定了该事件处理函数的元素

event.type这个属性可以用来在一个处理函数里面处理多个事件。例如
```js
var btn = document.getElementById("myBtn")
var handler = function(event){
    switch(event.type){
         case "click":
              alert("clicked");
              break;
         case "mouseover":
              alert("mouseovered");
              break;
    }
}

btn.onclick = handler
btn.onmouseover = handler
```

### event.PreventDefault()
用来阻止特定事件的默认行为
例如，a 的默认行为就是在被点击时会导航到其href特性指定的URL。如果想阻止链接导航这一默认行为，则通过链接的onclick事件处理程序可以取消他
```js
var link = document.getElementById("mylink")
link.onclick = function(event){
    event.preventDefault()
}
```
### event.stopPropagation()
用于立即停止事件在DOM层次中的传播，即取消进一步的事件捕获或冒泡
```js
//直接添加到一个按钮的事件处理程序可以调用stopPropagation()，从而避免触发注册在document.body上面的事件处理程序

var btn = document.getElementById("myBtn")

btn.onclick = function(event){
     alert("button clicked")
     event.stopPropagation() 
     //不加的话button click和body click都会触发
}

document.body.onclick = function(event){
    alert("Body clicked")
}
```

### eventPhase属性
eventPhase属性来确定事件当前正位于事件流的哪个阶段，捕获阶段=1，处于目标对象=2，冒泡阶段调用的事件处理程序中=3
```js
var btn = document.getElementById("myBtn")
btn.onclick = function(event){
    alert(event.eventPhase) //2
}

document.body.addEventListener("click",function(event){
   alert(event.eventPhase) //1
},true)  //true是捕获阶段

document.body.onclick = function(event){
   alert(event.eventPhase)  //3
} 
```
事件处理程序执行期间，event对象才存在，事件处理程序执行完成后event销毁

### IE中的事件对象

DOM0级添加事件处理程序时event对象作为window对象的一个属性存在
attachEvent的话event对象是作为参数被传入事件处理函数中的

IE中的event对象（和非IE的DOM中的对应关系在说明中）

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event/ie-event.png)

## 事件类型（type）

web浏览器中可能发生的事件有很多类型，不同事件类型有不同信息

DOM3级事件规定了以下几类事件
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event/event-type.png)

### UI事件
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event/ui-event.png)
### 焦点事件
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event/focus-event.png)
### 鼠标和滚轮事件
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event/mouse-event.png)

#### 鼠标事件的event对象的特殊信息
1. 客户区坐标位置clientX  clientY
2. 页面坐标位置pageX  pageY
3. 屏幕坐标位置screenX  screenY
4. 修改键，按下鼠标时键盘上的某些键的状态也可以影响到所要采取的操作`Shift` `Ctrl` `Alt` `Meta`键
  鼠标事件event含有四个属性shiftKey,ctrlKey,altKey,metaKey.这些属性中包含的都是布尔值，如果相应的键被按下了，则值为true,否则为false
5. 相关元素
  relatedTarget属性
  mouseover和mouseout事件，这两个事件会涉及鼠标指针从一个元素的边界之内移动到另一个元素边界之内的情况
  mouseover主目标是获得光标的元素，此时event对象的relatedTarget属性是失去光标的元素，mouseout则反之，主目标是失去光标的元素，relatedTarget是获得光标的元素
6. 鼠标按钮
  button属性
7. 更多信息
  detail属性
8. 鼠标滚轮事件
  mousewheel事件
9. 触摸设备
（1）不支持dblclick事件
（2）轻击可单击元素（被指定了onclick事件处理程序的元素）会触发mousemove事件，如果这个操作会导致内容变化，将不再有其他事件发生。如果屏幕没有因此发生变化，那么会依次发生mousedown,mouseup和click事件。
（3）mousemove事件也会触发mouseover和mouseout事件
（4）两个手指放在屏幕上且页面随手指移动而滚动时会触发mousewheel和scroll事件



### 键盘和文本事件
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-event/keyboard-text-event.png)

用户按了一下键盘上的字符键时，**依次触发keydown -> keypress ->keyup事件**
其中keydown和keypress都是在文本框发生变化之前被触发的，而keyup是文本框已经变化之后触发的，如果按住一个字符键不放会重复触发keydown和keypress事件

如果是非字符键，就没有keypress事件

键盘事件也支持修改键，详情查看鼠标事件的4

键盘事件的event
1. event.keyCode
键码(数值)
2. event.charCode
字符编码(按下那个键所代表字符的ASCII编码)
DOM3级事件中的鼠标事件**不再包含charCode属性**，而是包含两个新属性key和char
key的值是字符串，按下某个字符键，key的值就是相应的文本字符（如“k”或“M”），按下非字符键时是相应键的名（如“Shift”，“backspace”）
3. event.getModifierState()
参数可以是"Shift","Control","AltGraph","Meta"按下的话返回true否则返回false
4. **textInput事件（DOM3）**
和keypress类比，但仍有不同。当用户在可编辑区域输入字符时就会触发这个事件。这个用于替代keypress的textInput事件的行为稍有不同。区别之一就是任何可以获得焦点的元素都可以触发keypress事件，但是只有可编辑区域才能触发textInput事件。区别之二是textInput事件只会在用户按下能够输入实际字符的键时才触发，而keypress事件则在那些能够影响文本显示的键时也会触发（例如退格键）
textInput的event对象还包含了一个data属性，属性值就是用户输入的字符
同时还有一个inputMethod的属性，表示文本输入文本框的方式

### HTML5事件
1. contextmenu事件
上下文菜单
contextmenu事件是冒泡的。因此可以为document指定一个事件处理程序，用以处理页面发生的所有此类事件。这个事件的目标是发生用户操作的元素。通常使用contextmenu来显示自定义的上下文菜单，使用onclick来隐藏该菜单
Page389的示例不错，还利用了clientX clientY属性来确定contextmenu的位置
2. beforeunload事件
3. DOMContentLoaded事件，不像window的load需要在一切加载完毕才触发，该事件在形成完整的DOM树后就会触发不理会图像，JavaScript文件，css文件等等是否下载完毕
4. readystatechange事件
事件对象有一个readyState属性
5. pageshow和pagehide(后退和前进按钮)
6. **hashchange事件**
vue-router的实现的关键事件
URL的参数列表（#号后面的所有字符串）发生变化的时候触发这个事件
这个事件的事件处理程序必须添加给window对象
事件对象包含了oldURL和newURL两个新属性（包含变化前后的完整URL）

### 设备事件

1. orientationchange/MozOrientation/deviceorientation事件
屏幕方向翻转的时候会触发该事件
2. devicemotion事件
通过devicemotion可以检测设备是不是正在往下掉或者是不是被正在走着的人拿在手里

### 触摸与手势事件
这是由于iOS和Android的新增了一些专有事件，导致w3c开始制定Touch Events规范

1. touchstart事件：当手指触摸屏幕时触发。
2. touchmove事件： 当中手指在屏幕上滑动时连续触发。
3. touchend事件：当手指从屏幕移开时触发。
4. gesturestart事件：当一个手指已经按在屏幕上而另一手指又触摸屏幕时触发。
5. gesturechange事件：当触摸屏幕的任何一个手指的位置发生改变时触发。
6. gestureend事件：当任何一个手指从屏幕上移开时触发。

这些事件都是冒泡事件，所以将事件处理程序放在文档上也可以处理所有手势事件，此时事件的target就是两个手指都位于其范围内的那个元素
手势事件的event对象会包含额外两个属性rotation和scale。rotation属性表示手指变化引起的旋转角度，scale属性表示两个手指间距离的变化情况

## 内存与性能

在JavaScript中，添加到页面上的事件处理程序数量将直接关系到页面的整体运行性能，原因一是函数会占用内存，二是加载函数，访问DOM会延迟整个页面的交互就绪时间

### 事件委托

事件委托是“事件处理程序过多”问题的解决方案。利用事件冒泡，只指定一个事件处理程序，就可以管理某一类型的所有事件。
例如：click事件会一直冒泡到document层次，也就是我们可以为整个页面（比如在document上）指定一个onclick事件处理程序，而不必给每个可单击的元素分别添加事件处理程序。
（区分点击的是哪个可以用event.target这个属性对象来区分，例如event.target.id之类）

最适合采用事件委托技术的事件包括click、mousedown、mouseup、keydown、keyup、keypress。虽然mouseover和mouseout事件也冒泡，但是要适当处理它们并不容易

### 移除事件处理程序

内存中留有那些过时不用的“空事件处理程序”也是造成web应用程序内存与性能问题的主要原因

从文档中移除带有事件处理程序的元素时，有两种方式，一是使用removeChild()和replaceChild这类DOM操作，二是直接用innerHTML替换页面中的一部分。二这种方式可能造成元素的事件处理程序无法被GC当垃圾回收

解决方法，在移除DOM时，先手工移除事件处理程序
```js
btn.onclick = function(){
    //先执行某些操作
    btn.onclick = null //手工解除对事件处理函数的引用，以便GC垃圾回收
　　　
　　btn,innerHTML = "你已点击过该按钮"
}
```
如果事先知道某个元素将来要被innerHTML替换，那么可以不将事件处理程序添加在该元素上，而是添加在他的较高层次能处理该区域的元素中（利用事件委托）

在页面卸载之前，也可以先通过onunload事件处理程序来移除所有事件处理程序（这也是事件委托技术的体现）

### 模拟事件
在测试web程序时，这是一个有用的技术

DOM中的事件模拟
```js
var btn = document.getElementById("myBtn")

//创建事件对象
var event = document.createEvent("MouseEvents") 
//参数是要创建事件类型的字符串，是"UIEvents","MouseEvents","MutationEvents","HTMLEvents"这几个字符串之一

//初始化事件对象，参数跟事件的类型不同而不同
event.initMouseEvent("click",true,true,document.defaultView,0,0,0,0,0,false,false,false,false,0,null)

//初始化完了之后使用dispatchEvent()触发该事件
btn.dispatchEvent(event)
```

#### 参考资料
《JavaScript高级程序设计》 第十三章