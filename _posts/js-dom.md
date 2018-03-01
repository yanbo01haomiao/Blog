# JavaScript-DOM操作

首先应该清楚DOM不仅限于HTML还包括XML。其次DOM是语言无关的除了JavaScript外，Java也实现了DOM API。

前端开发目前已经接受了数据驱动的开发，摒弃了jQuery式的操作DOM开发。不过即使如此，对于DOM操作的熟练掌握也是十分重要的。类似DOM这类API的学习其实无外乎就是知道每个API的输入输出，适用场景。本文的主要目的也就是提供一个简化的API文档，方便自己日后查询使用。

首先先来一张图看看Node节点继承的层次关系
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-dom/nodetree.png)

## Node类型

- nodeType,nodeName,nodeValue属性
nodeType取值有...Node.ELEMENT_NODE(1),Node.ATTRIBUTE_NODE(2),Node.TEXT_NODE(3)...（括号里是常量对应的数值）,nodeName一般是元素标签名,nodeValue元素的类型不同值不同

- childNodes属性
不用解释..保存的是NodeList这种**类数组**对象，可以用[]或者item()方法来访问当中的节点
*插一句，可以使用Array.prototype.slice.call(someNode.childNodes,0)来将类数组转换为数组*

- parentNode、firstChild、lastChild、previousSibling、nextSibling属性

- appendChild()
```js
parentNode.appendChild(newChildNode)
//如果neChildNode已经是文档的一部分，则效果变成将这个Node移到新位置。
//返回值就是这个 newChildNode
```

- insertBefore()
```js
parentNode.insertBefore(newChildNode,referNode)
//返回值就是这个 newChildNode
```

- replaceChild()
```js
parentNode.replaceChild(newChildNode,willremovedNode)
```
被移除的节点仍然为文档所有，只不过没了自己的位置，变成“孤儿”.willremovedNode必须是parentNode的子节点,下同。

- removeChild()
```js
parentNode.removeChild(willremovedNode)
```

- cloneNode()
```js
var someNodeCopy = someNode.cloneNode(true) //true为深复制。false为浅复制
```
someNodeCopy是“孤儿”节点，要用上面几个方法添加到文档

- normalize()

## Document类型
浏览器中的document对象是HTMLDocument（继承自Document类型）的一个实例,document对象是该类型最常见的应用了
nodeType === Node.DOCUMENT_NODE(9)
nodeName === "#document"

- compatMode属性
告诉开发人员浏览器采用了哪种渲染模式，值为"CSS1Compat"是标准模式，"BackCompat"是混杂模式

- documentElement属性
document.documentElement 取得对`<html>`的引用

- head属性
document.head 取得对`<head>`的引用

- body属性
document.body 取得对`<body>`的引用

- doctype属性
document.doctype 取得对`<!DOCTYPE>`的引用

- title属性
document.title 取得对`<title>`的内容（字符串）

- charset属性
document.charset 取得`<meta>`charset特性的值（字符串）

*以下三个属性的信息存储在请求的HTTP头部*

- URL属性
document.URL 取得完整的URL，不可设置

- referrer属性
document.referrer 取得来源页面的URL，不可设置

- domain属性
document.domain 取得域名，可设置，但有限制，只能从子域名到父域名，这个属性可以解决一部分跨域问题

*以下是document对象的一些特殊集合，这些集合都是HTMLCollection对象*

- anchors属性
document.anchros 包含带有name特性的`<a>`元素

- forms属性
document.forms 包含文档中所有`<form>`元素

- links属性
document.links 包含文档中所有带有href特性的`<a>`属性

- getElementById()
传入的id区分大小写，"mydiv"和"myDiv"不同

- getElementsByTagName()
返回一个HTMLCollection对象，类似于NodeList,访问方法也是[数字or字符串]、item(数字),(独有)namedItem(字符串)

- createElement()
```js
var newDiv = document.createElement("div")
//标签名在HTML中不分大小写，在XML/XHTML中分
```
- createTextNode()
```js
var textNode = document.createTextNode("hello world!")
// textNode目前是孤儿node.需要append到文档去
```

- createAttribute()
```js
var classAttr = document.createAttribute("class")
classAttr.value = "redStyle"
el.setAttributeNode(classAttr)
// attr无法通过append添加到文档
```

- implementation.hasFeature()
```js
document.implementation.hasFeature("CSS2","2.0")
//检测浏览器对标准的实现程度
```

- write()、writeln()、open()、close()

## Element类型
nodeType === Node.ELEMENT_NODE(1)
tagName === nodeName === 元素标签名的大写

所有HTML元素都由HTMLELement类型及其子类型表示
```js
var el = document.getELementById("myDiv")
```

- id、title、className...属性

- getAttribute()、removeAttribute()
```js
el.getAttribute("id")
el.removeAttribute("class")
```
- setAttribute()
```js
el.setAttribute("class","redStyle")
```

- attributes属性
Element类型是使用attributes属性的唯一一个DOM节点类型，该属性包含了一个NamedNodeMap对象,这个也与NodeList类似，因此也可以用[]、item()、getNamedItem()等来访问Attr节点

### 一个元素子节点坑
```html
<ul id="myList">
    <li>1</li>
    <li>2</li>
    <li>3</li>
</ul>
```
```js
var mylist = document.getElementById("myList")
console.log(mylist.childNodes.length) // 7
//包括3个li元素节点，和4个空白的text节点
//如果想获得只包含li子元素的NodeList
var lis = mylist.getElementsByTagName("li")
//或者遍历mylist.childNodes,判断nodeType是不是1
```
或者可以参考下面的children属性

## Text类型
nodeType === Node.TEXT_NODE(3)
nodeName === "#text"
nodeValue === data === 节点所包含的文本
parentNode 是一个Element
没有子节点

```html
<div id="myDiv">hello world!</div>
```
```js
var mydiv = document.getElementById("myDiv")
mydiv.childNodes.length // 1
mydiv.childNodes[0].data //"hello world!"
```
- appendData(text)、deleteData(offset, count)、insertData(offset, text)、replaceData(offset, count, text),splitText(offset),substringData(offset, count)

- normalize()
合并相邻文本节点,和splitText()的作用相反
```js
var el = document.createElement("div")
var tnode1 = document.createTextNode("Hello")
el.appendChild(tnode1)
var tnode2 = document.createTextNode(" world!")
el.appendChild(tnode2)
document.body.appendChild(el)

console.log(el.childNodes.length) // 2
el.normalize()
console.log(el.childNodes.length) // 1
```

## DocumentFragment 类型

*DocumentFragment一般用在频繁的DOM操作的时候通过减少浏览器reflow的次数用来优化性能，不过似乎现代浏览器已经对reflow的流程做了优化，现在这一骚操作的意义已经不太大*

未优化版本
```js
var ulnode = document.createElement("ul")
var li = null

for(let i = 0; i < 100; i++){
    linode = document.createElement("li")
    linode.appendChild(document.createTextNode("Item "+(i+1)))
    ulnode.appendChild(linode)
}
// (旧浏览器) 需要100次reflow
```

优化版本
```js
var ulnode = document.createElement("ul")
var lisfragment = document.createDocumentFragment()
var linode = null

for(let i = 0; i < 100; i++){
    linode = document.createElement("li")
    linode.appendChild(document.createTextNode("Item "+(i+1)))
    lisfragment.appendChild(linode)
    //实际上就是将fragment作为一个暂存DOM结构的仓库
}

ulnode.appendChild(lisfragment)
// (旧浏览器) 只需1次reflow
//文档片段本身永远不会成为文档树的一部分，实际上只会将文档片段的所有子节点添加到相应位置上
```

### 操作表格
HTML DOM为 `<table>` 添加了一些属性和方法以方便我们对表格进行DOM操作。

- caption、tBodies、tFoot、tHead、rows等属性

- createTHead()、createTFoot()、createCaption()、...insertRow(pos)、deleteRow(pos)等等方法

### NodeList
NodeList及其"近亲"NamedNodeMap和HTMLCollection。这三个集合是**动态的**。也就是文档结构发生变化时，他们都会得到更新。他们始终保存最新、最准确的信息。

*以下代码会无限循环*
```js
var divs = document.getElementsByTagName("div"),
    div
for(let i = 0; i < div.length; i++){
//for(let i = 0, len = div.length; i < len; i++)
// 以上代码可以解决无限循环的问题
    div = document.createElement("div")
    document.body.appendChilde(div)
}
```

## Selector API

- querySelector()
接受CSS选择符(如body、#myDiv、.selected、img.button)作为参数，返回与该模式匹配的**第一个元素**

- querySelectorAll()
参数同上，返回一个与该模式匹配的**NodeList实例**

## Element Traversal API

- childELementCount, firstElementChild, lastElementChild, previousELementChild, nextElementSibing

firstChild和firstElementChild的区别就是前者会包含Node.TEXT_NODE(3),而后者只考虑Node.ELEMENT_NODE(1)

## HTML5 

HTML5新增了一些API，致力于简化CSS类的用法

- getElementsByClassName()
```js
var allRed = document.getElementsByClassName("redStyle")
//allRed是NodeList对象
```

- classList属性
原先的className属性是一字符串，因此添加删除操作需要拼接字符串不太方便也不安全。HTML5就为所有元素都添加了classList属性。这个属性是新的集合类型DOMTokenList的实例。这个类型同样有length属性，可以用[]、item()来访问单个元素。此外还包括
  - add(value)、contains(value)、remove(value)、toggle(value)
其中value是字符串

- 自定义特性
```html
<div id="myDiv" data-appId="123" data-myname="cai"></div>
```
```js
var mydiv = document.getElementById("myDiv")
var appId = mydiv.dataset.appId //自定义特性存在dataset里
var myName = mydiv.dataset.myname //
```

- innerHTML属性

对一个div读这个属性会返回他的所有子节点的HTML标记字符串，对一个div写这个属性时,写进去的字符串会被解析为div的DOM子树，替换div原来所有的子节点。

*这里要注意防止XSS攻击*

- outerHTML属性
与innerHtml基本相同，差别在于div.outerHTML包括了div本身及其子节点，div.innerHTML不包括div本身

*为了优化性能，要防止过于频繁设置innerHTML和outerHTML*

- innerText属性
对一个div读这个属性返回所有文本子节点的内容，写的话则插入包含相应文本值的文本节点。如果值当中有HTML语法字符（大于小于号引号等）会进行编码，`complie < to $lt` 这样,也即HTML escape

- outerText属性
他与innerText的区别参考outerHTML属性下的描述  

- children属性
和childNodes基本一致，区别在于children不包括TextNode，同时这个属性是HTMLCollection实例。具体可以看上面的**一个元素子节点坑**

- contains()
检测某节点是不是另一个节点的后代

#### 参考资料

《JavaScript高级程序设计 第三版》第10章和第11章
 第12章内容未涉及