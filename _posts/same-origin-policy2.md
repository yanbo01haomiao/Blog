---
title: 浏览器同源策略-规避同源策略的方式
date: 2018-01-31 17:18:11
tags:
    - 同源策略
    - 跨域
categories:
    - web安全
---
虽然这些同源策略限制是必要的，但是有时很不方便，合理的用途也受到影响。下面，我将详细介绍，如何规避同源策略限制。
<!--more-->
关于浏览器同源策略的前置知识请查看本系列第一篇
{% post_link same-origin-policy1 浏览器同源策略-从iframe谈起%}

### 常见规避同源限制的方法
- document.domain
- window.name
- location.hash
- HTML5 API window.postMessage

## document.domain
*仅适用于相同主域的跨域*
在同源策略中cai.com和son1.cai.com和son2.cai.com被视为互不不同源，也受同源策略的限制。但是实际上他们之间具有相同的一级域名(主域)cai.com。想要绕过同源限制可以将不同页面的document.domain都指向主域就行
```js
document.domain = 'cai.com'
```
一个例子如下
```html
<!-- foo.com/a.html -->
<iframe id="ifr" src="http://img.foo.com/b.html"></iframe>
<script>
document.domain = 'foo.com';
function aa(str) {
    console.log(str);
}
window.onload = function () {
    document.querySelector('#ifr').contentWindow.bb('aaa');
}
// 现在获取iframe的DOM就不会报错了
</script>
```

```html
<!-- img.foo.com/b.html -->
<script>
document.domain = 'foo.com';
function bb(str) {
    console.log(str);
}

parent.aa('bbb');
</script>
```
## window.name
只要不关闭浏览器，window.name可以在不同页面加载后依然保持。尝试在浏览器打开百度baidu.com，然后在控制台输入window.name='aaa';回车，接着在地址栏输入qq.com转到腾讯首页，打开控制台输入window.name查看它的值，可以看到输出了"aaa"。

一个很hack的例子：子页面bar.com/b.html向父页面foo.com/a.html传数据。
```html
<!-- foo.com/a.html -->
<iframe id="ifr" src="http://bar.com/b.html"></iframe>
<script>
function callback(data) {
    console.log(data)
}
</script>
```
```html
<!-- bar.com/b.html -->
<input id="txt" type="text">
<input type="button" value="发送" onclick="send();">


<script>
var proxyA = 'http://foo.com/aa.html';    // foo.com下代理页面
var proxyB = 'http://bar.com/bb.html';    // bar.com下代理空页面

var ifr = document.createElement('iframe');
ifr.style.display = 'none';
document.body.appendChild(ifr);

function send() {
    ifr.src = proxyB;
}

ifr.onload = function() {
    ifr.contentWindow.name = document.querySelector('#txt').value;
    //当然这里也可以ifr.contentWindow.name = document.cookie;将cookie发送过去
    ifr.src = proxyA;
}
</script>

```
```html
<!-- foo.com/aa.html -->
top.callback(window.name)
```
这种方法的优点是，window.name容量很大，可以放置非常长的字符串；缺点是必须监听子窗口window.name属性的变化，影响网页性能。

## location.hash
URL的#号后面的部分，比如http://example.com/x.html#fragment 的 #fragment。如果只是改变片段标识符，页面不会重新刷新。这种做法和window.name很像，只是存放数据的地方不同而已

还是一个很hack的例子：获取子页面bar.com/b.html的高度及其他数据
```html
<!-- foo.com/a.html -->
<iframe id="ifr" src="http://bar.com/b.html"></iframe>
<script>
function callback(data) {
    console.log(data)
}
</script>
```
```js
<!-- bar.com/b.html -->
window.onload = function() {
    var ifr = document.createElement('iframe');
    ifr.style.display = 'none';
    var height = document.documentElement.scrollHeight;
    var data = '{"h":'+ height+', "json": {"a":1,"b":2}}';
    ifr.src = 'http://foo.com/aa.html#' + data;
    document.body.appendChild(ifr);
}
```
```js
<!-- foo.com/aa.html -->
var data = JSON.parse(location.hash.substr(1));
top.document.getElementById('ifr').style.height = data.h + 'px';
top.callback(data);
```

## HTML5 API window.postMessage

### 语法
```js
otherWindow.postMessage(message, targetOrigin, [transfer]);
```
- otherWindow
其他窗口的一个引用，比如iframe的contentWindow属性、执行window.open返回的窗口对象、或者是命名过或数值索引的window.frames。
- message
将要发送到其他 window的数据。它将会被结构化克隆算法序列化。这意味着你可以不受什么限制的将数据对象安全的传送给目标窗口而无需自己序列化。
- targetOrigin
通过窗口的origin属性来指定哪些窗口能接收到消息事件，其值可以是字符串"\*"（表示无限制）或者一个URI。在发送消息的时候，如果目标窗口的协议、主机地址或端口这三者的任意一项不匹配targetOrigin提供的值，那么消息就不会被发送；只有三者完全匹配，消息才会被发送。这个机制用来控制消息可以发送到哪些窗口；例如，当用postMessage传送密码时，这个参数就显得尤为重要，必须保证它的值与这条包含密码的信息的预期接受者的origin属性完全一致，来防止密码被恶意的第三方截获。如果你明确的知道消息应该发送到哪个窗口，那么请始终提供一个有确切值的targetOrigin，而不是"\*"。不提供确切的目标将导致数据泄露到任何对数据感兴趣的恶意站点。
```js
window.addEventListener("message", receiveMessage, false);
function receiveMessage(event){
    //处理逻辑。可以获取ecent.data,event.origin,event.source 
}
```
监听的事件名为'message', function(e)回调函数第一个参数接收 Event 对象，有三个常用属性：
- data
从其他 window 中传递过来的对象。
- origin
调用 postMessage  时消息发送方窗口的 origin . 这个字符串由 协议、“://“、域名、“ : 端口号”拼接而成。例如 “https://example.org (隐含端口 443)” 、“http://example.net (隐含端口 80)” 、 “http://example.com:8080” 。请注意，这个origin不能保证是该窗口的当前或未来origin，因为postMessage被调用后可能被导航到不同的位置。
- source
对发送消息的窗口对象的引用; 您可以使用此来在具有不同origin的两个窗口之间建立双向通信。

1. 再来一个不那么hack的例子：一个简单的父页面foo.com/a.html 和子页面 bar.com/b.html建立通信
```html
<!-- foo.com/a.html -->
<iframe id="ifr" src="http://bar.com/b.html"></iframe>
<script>
window.onload = function () {
    var ifr = document.querySelector('#ifr');
    ifr.contentWindow.postMessage({a: 1}, '*');
}
window.addEventListener('message', function(e) {
    console.log('bar say: '+e.data);
}, false);
</script>
```
```html
<!-- bar.com/b.html -->
<script>
window.addEventListener('message', function(e){
    console.log('foo say: ' + e.data.a);
    e.source.postMessage('get', '*');
}, false)
</script>
```
2. 另一个例子
localStorage的同源限制无法通过document.domain的方式解除，但可以通过postMessage

```js
// cai.com/a.html
window.onmessage = function(e) {
  if (e.origin !== 'http://cai.com') {
    //如果不是发给自己的就不接收
    return;
  }
  var payload = JSON.parse(e.data);
  localStorage.setItem(payload.key, JSON.stringify(payload.data));
};
```
```js
var win = document.getElementsByTagName('iframe')[0].contentWindow;
var obj = { name: 'Jack' };
win.postMessage(JSON.stringify({key: 'storage', data: obj}), 'http://cai.com');
```

### 主要参考资料
[浏览器同源政策及其规避方法 by阮一峰](http://www.ruanyifeng.com/blog/2016/04/same-origin-policy.html)
[新手学跨域之iframe by亦秋](https://segmentfault.com/a/1190000000702539)
[MDN postMessage](https://developer.mozilla.org/zh-CN/docs/Web/API/Window/postMessage)


前两篇文章一直都没有提到跨域的重头戏ajax,将在下一篇中讲解
{% post_link same-origin-policy3 浏览器同源策略-跨域Ajax%}