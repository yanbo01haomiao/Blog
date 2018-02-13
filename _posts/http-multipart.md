---
title: 今夜我们一起学习HTTP之multipart
date: 2018-02-06 20:55:45
tags: 
    - http
    - multipart
categories:
    - 计算机网络
    - HTTP
---

这篇简略说说关于multipart/form-data的知识

<!--more-->

我们在介绍HTML的form表单的时候讲过一种application/x-www-form-urlencoded大家可以在{% post_link html-form  HTML-form表单%}这里看到这种格式的GET和POST分别是怎样提交数据的。简单讲其实就是GET放在URL的queryString,而POST把数据以name=value的格式放在报文的Entity里。

然而实际上当我们不是上传纯文本数据而是一些图片和文字等二进制数据的时候，我们会在表单的特性里面使用enctype="multipart/form-data"来上传，不设置enctype的话默认就是application/x-www-form-urlencoded。表单数据会被urlencod哈
```html
<form method="post"action="http://cai.com/upload.do" enctype=”multipart/form-data”>

         <inputtype="text" name="desc">

         <inputtype="file" name="pic">

 </form>
```

这个时候发送的HTTP request就会大致变成下面的样子
```
POST /upload.do HTTP/1.1
User-Agent: SOHUWapRebot
Accept-Language: zh-cn,zh;q=0.5
Accept-Charset: GBK,utf-8;q=0.7,*;q=0.7
Connection: keep-alive
Content-Length: 60408
Content-Type:multipart/form-data; boundary=ZnGpDtePMx0KrHh_G0X99Yef9r8JZsRJSXC
Host: cai.com

--ZnGpDtePMx0KrHh_G0X99Yef9r8JZsRJSXC

Content-Disposition: form-data;name="desc"

Content-Type: text/plain; charset=UTF-8

Content-Transfer-Encoding: 8bit

[text数据]

--ZnGpDtePMx0KrHh_G0X99Yef9r8JZsRJSXC

Content-Disposition: form-data;name="pic"; filename="photo.jpg"

Content-Type: application/octet-stream

Content-Transfer-Encoding: binary

 
[图片二进制数据]

--ZnGpDtePMx0KrHh_G0X99Yef9r8JZsRJSXC--
```

浏览器会通过一个自动生成的boundary来作为边界，每一块可以放不同编码格式的数据，像我们上面有用UTF-8编码的纯文本，也有二进制数据。这也是multipart这个名字的内涵，有多个part,每个part可以有不同的编码格式。

服务器接收到这个request就会用提取headers里的boundary，把浏览器传过来的数据的boundary都去掉，把传来的二进制数据和文本数据分别保存起来。

#### 参考资料

[Multipart/form-data POST文件上传详解理论](http://blog.csdn.net/xiaojianpitt/article/details/6856536)
[stackoverflow:What is http multipart request](https://stackoverflow.com/questions/16958448/what-is-http-multipart-request)