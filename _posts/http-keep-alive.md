---
title: 今夜我们一起学习HTTP之keep-alive
date: 2018-02-06 14:37:14
tags: 
    - http
    - keep-alive
categories:
    - 计算机网络
    - HTTP
---

关于HTTP请求头中keep-alive的作用

<!--more-->

我们经常可以在http中request headers中的看到
```
Connection:keep-alive
```
他代表着什么呢有什么作用呢

HTTP协议属于应用层的协议，他的实现需要依赖处于传输层的TCP协议(不是必须依赖TCP，但目前通常是依赖TCP协议的)。我们知道TCP协议在建立连接的时候需要经过三次握手，断开连接的时候需要经过四次挥手。那么是不是每次发起一次HTTP请求和收到HTTP响应都要建立和断开一次TCP连接呢?

在HTTP协议的初始版本中，每进行一次HTTP通信就要断开一次TCP连接。过程如下图所示:

<img src="nokeepalive.png" width="100%" >

这样的模式在HTTP协议最初被用来进行小容量的文本传输，一个请求可能就把所有要返回的数据取到的情况下来说是没有太大问题的。但是随着web的发展，文档中开始包括了大量的图片、脚本文件、css文件等资源，现在要展现一张完整的页面需要很多个HTTP请求才能完成。如果依然采用一次HTTP一次TCP就会带来很多弊端，如下图所示

<img src="nokeepalive1.png" width="100%" >

无疑这当中有许多无谓的TCP连接建立和断开，会增加通信量的开销。

为了解决上述问题，HTTP/1.1和一部分HTTP/1.0想出了HTTP keep-alive(也称持久连接)的解决方案。HTTP/1.1中所有的连接默认都是开启了HTTP Keep-Alive。我们可以在http request headers上看到
```
Connection:keep-alive
```
这就标明了已经开启了HTTP Keep-Alive。关闭的方式是Connection:close。
开启之后HTTP的通信模式类似下图:

<img src="keepalive.png" width="100%" >


HTTP Keep-Alive的意义就是可以复用已有的TCP连接，减少了TCP连接的重复建立和断开所造成的额外开销，减轻了服务器端的负载。同时HTTP请求和响应也能够更早地结束，这样Web页面的显示速度也就相应提高了。

*除了HTTP的Keep-Alive外，还存在一个TCP的keepalive概念，TCP通过发送空数据包给另一头，如果收到了响应说明另一头还未下线*

持久化连接使得多数请求以管线化(pipeling)方式成为可能。
我再网上没有查到太多关于管线化的技术资料，目前也不太清楚对于前端而言深入这一部分知识的价值在哪里，所以先留下以下一点信息，日后有该技术需求再深入学习。

<img src="pipeling.png" width="100%" >

*仅HTTP/1.1支持此技术（HTTP/1.0不支持），并且只有GET和HEAD要求可以进行管线化，而POST则有所限制。*
