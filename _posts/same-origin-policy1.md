---
title: 浏览器同源策略-从iframe谈起
date: 2018-01-31 16:21:08
tags:
    - html
    - 同源策略
categories:
    - web安全
---
1995年，同源政策由 Netscape 公司引入浏览器。目前，所有浏览器都实行这个政策。
<!--more-->
### 所谓同源策略是指
- 协议相同
- 域名相同
- 端口相同

*(IE未将端口号加入到同源策略的组成部分之中，因此 http://company.com:81/index.html 和http://company.com/index.html  属于同源并且不受任何限制)*

### 同源策略的目的
*(这只是一个以cookie为例的例子，实际的作用远不止于此)*
同源政策的目的，是为了保证用户信息的安全，防止恶意的网站窃取数据。

设想这样一种情况：A网站是一家银行，用户登录以后，又去浏览其他网站。如果其他网站可以读取A网站的 Cookie，会发生什么？

很显然，如果 Cookie 包含隐私（比如存款总额），这些信息就会泄漏。更可怕的是，Cookie 往往用来保存用户的登录状态，如果用户没有退出登录，其他网站就可以冒充用户，为所欲为。因为浏览器同时还规定，提交表单不受同源政策的限制。

由此可见，"同源政策"是必需的，否则 Cookie 可以共享，互联网就毫无安全可言了。

### 同源限制的范围
- cookie、localStroage等
- DOM
- AJAX请求无法发送

### 不受同源限制的情况
- 多媒体元素标签`<img src=""> <video src=""> <audio src="">`
- 脚本标签`<script src="">`
- 样式标签`<link rel="stylesheet" href="">`
- 嵌入对象和java applet`<embed src=""> <object codebase=""> <applet codebase="">`
- `<frame>, <iframe>`
- `<a>`
- API: location.*, window.open()

### iframe标签的同源限制

**X-Frame-Options**
```
x-Frame-Options: DENY/SAMEORIGIN
```
HTTP响应报文首部可能会包含以上值，意思分别是拒绝响应主体被插在iframe标签里面，和仅允许同源域名下的页面用iframe把响应主体插在iframe标签里。

DOM提供了一些API来让我们获取iframe的内容
**在父页面获取iframe标签的内容**
```js
 var iframe = document.getElementById("iframe1");
 var iwindow = iframe.contentWindow;//获取iframe的window对象
 var idoc = iframe.contentDocument //获取iframe的document对象
 //也可以var idoc = iwindow.document;
```
**在iframe中获取父级内容**
```js
window.parent//获取上一级的window对象，如果还是iframe则是该iframe的window对象
window.top//获取最顶级容器的window对象，即，就是你打开页面的文档
```
以上的API仅在同源下有效，如果两个页面(父页面及子iframe引入的页面)不同源，就会报错
```js
document.getElementById("myIFrame").contentWindow.document
// Uncaught DOMException: Blocked a frame from accessing a cross-origin frame.
window.parent.document.body
// 在子窗口获取父窗口的DOM也报错
```
这里的同源策略合情合理，假设iframe之间获取DOM没有同源限制。那么我可以随便写一个网站
```html
<!-- 在cai.com下 -->
<iframe id="bankframe" src="bank.com"></iframe>
<script>
     var cookie = document.getElementById("bankframe").contentWindow.document.cookie
     //将你bank.com下的cookie发送到收集信息的服务器
</script>
```
然而在事实是浏览器有同源限制，因为以上两个页面不同源，所以获取DOM的操作会报错。

在某些情况下我们希望绕过同源策略，具体方法请查看本系列第二篇
{% post_link same-origin-policy2 浏览器同源策略-规避同源策略的方式%}
