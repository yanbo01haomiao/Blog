---
title: 今夜我们一起学习HTTP之Cookie
date: 2018-02-06 19:39:47
tags: 
    - http
    - cookie
categories:
    - 计算机网络
    - HTTP
---

HTTP是无状态协议，它不对之前发生过的请求和响应的状态进行管理。HTTP这一"无状态"的设定，保持了自身的简单性。是出色的。但是同时也带来了问题，特别是对要求登录认证的web应用来说。Cookie的提出解决了服务器无法进行状态管理(不记录已登陆的状态)这一问题。

<!--more-->

## Cookie的工作原理

首先客户端先发送一个没有Cookie信息的请求，比如

```
GET /caispace/ HTTP/1.1
Host: cai.com
```

假设这个请求的地址是需要登录的，那么服务器可能会发出一个重定向到登录页面的response。浏览器在登录页面里面填写账户和密码之类的blabla...，然后再发起一个请求到服务器，这时候服务器从数据库中查询这个账户和密码对应的sessionId(服务器在某个用户注册成功后会在服务器上为这个用户生成一个sessionId并保存下来，这个sessionId就对应了这个用户)。然后关键的步骤来了，这时候服务器要返回一个response。这个response的headers里会包含如下
```
HTTP/1.1 200 OK
Content-type: text/html
Set-Cookie: sid=1342077140226724;expires=Sat,03 May 2025 17:44:22 GMT
```

浏览器发现返回response包含Set-Cookie，就会把cookie的内容保存在本地。下次浏览器再发送请求到**这个**服务端时就会带上**这个**cookie
```
GET/1.1 /caispace/tag HTTP/1.1
Host: cai.com
Cookie: sid=1342077140226724
```

服务器收到这个请求后发现这个请求的request headers当中有Cookie,就把它拿出来，和数据库存储的sessionId进行对比，发现确实有这个用户，response用户所请求的数据，这时会把该用户的上一次结束操作时的状态返回(比如说你上次把一个物品保存进了购物车)，现在你重新去看购物车，发现上次加进去的东西还在。


### Cookie的可选项
下面是cookie的格式

```
Set-Cookie: value[; expires=date][; domain=domain][; path=path][; secure]
```

value就是纯文本格式的数据，最常用的方式是使用name=value格式来指定cookie的之。

expires是过期时间选项，如果浏览器发现某个cookie已经过了过期时间，那么他就会取消发送该cookie，随后将本地保存的这个cookie值删掉。如果cookie没有指定expires或者Max-Age的话，那么就会变成一个session期cookie，他仅在当前会话时有效，你关了浏览器之后这个cookie就会被浏览器删除。

domain和path定义了cookie的作用域，即cookie应该发送给哪些URL，domain如果不指定的话，默认为当前文档的主机(不包含二级域名)。如果设置 domain=mozilla.org，则Cookie也包含在子域名中（如developer.mozilla.org）
path的话就是指定哪些路径要发送cookie，如果是/就包含所有路径

secure和HttpOnly主要是为了安全。事实上敏感信息也不应该通过Cookie传输，因为Cookie有其固有的不安全性，Secure 标记也无法提供确实的安全保障。加了secure的话这个cookie只会在你使用https时才发，http不发。而HttpOnly的意思是，cookie只能用在http/https中。你不能用JavaScript的document.cookies或其他手段来操作cookie

#### 参考文档
[MDN HTTP cookies](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Cookies)
[HTTP cookies 详解](http://bubkoo.com/2014/04/21/http-cookies-explained/)
<图解HTTP> 第二章 使用cookie的状态管理