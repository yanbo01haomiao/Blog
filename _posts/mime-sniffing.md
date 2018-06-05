# MIME嗅探与X-Content-Type-Options

## Content-Type

当浏览器发出的网络请求接收到Response的时候，它通过Content-Type这个Response Header来判断Response Body的类型，并通过不同的类型采取不同的处理方式。比如说text/html就做html渲染，image/jpeg就用jpeg图片解码器进行处理等等。不过有些时候可能web服务器的程序员出现了疏忽，返回了错误的MIME TYPE。比如说下面这样的Response Body
```
<html>
<script>
alert(/xss/);
</script>
</html>
```
但是程序员返回的Response的Response Header却为text/plain。这会导致返回的Response Body以及程序员设置的Response Header中的Content-Type出现了偏差。浏览器也就没办法正确地处理Response Body。上面的html会被当成纯文本处理无法被渲染

## MIME sinffing

IE4引入了一个新的feature：MIME sniffing。这个feature的本意是为了兼容那些后端程序员没有正确设置头部的网站。比如说有一个返回text/html类型Body的Response被错误设置成了text/plain。这时候IE浏览器就通过对Response Body的前256个字节进行判断（嗅探），发现他实际是text/html。这个时候IE就用处理html的方式对其进行处理。因此我们上面提到的这个案例中的html文件就得到了正确的处理

## 安全问题

IE引入MIME sinffing的本意是好的，是为了使IE浏览器的兼容性更强，但是这一个feature却带来了严重的安全问题。比如会被用来利用图片进行跨站脚本攻击(XSS)。假设说有个网站允许用户上传图片，这个时候攻击者上传了一个含有javascript攻击代码的html文件，这个时候其他用户使用IE访问这张含有攻击代码图片时，虽然返回的Response Header的Content-Type是image/jpeg。但是IE浏览器通过嗅探，“自作聪明”地用处理html文件的方式渲染了这张“图片”。这样攻击者的JavaScript攻击代码就会在用户的IE浏览器上执行。

## IE8亡羊补牢

微软在IE8时引入了X-Content-Type-Options这个头部，问题解决的方法也十分简单粗暴。
```
X-Content-Type-Options: nosniff
```
收到含有这个Response Headers的Response后，IE就会直接禁用MIME sinffing。当然这个响应还是要由我们的后端程序员来设置。当然设置了这个Response Header之后，我们网站的后端程序员就必须保证自己设置的Content-Type和自己返回的Response Body是正确对应的。否则浏览器就无法保证能正确处理自己返回的Response。