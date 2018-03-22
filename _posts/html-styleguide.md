# <script src="index.js"/>引发的血案

```js
<script src="index.js"/>
```
我在想我应该不是第一次遇到这个坑了，而且他还不报错。。只能人工排雷。。我在想不知道前几次我遇到这个坑的时候，可能也是误打误撞地把他改成
```js
<script src="index.js"></script>
```
然后就不管他了

今天我想要研究一下lie源码的时候，新建了一个html如下
```js
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
</head>
<body>
    <script src="node_modules/lie/dist/lie.js"/>
    <script src="index.js"/>
</body>
</html>
```
结果是当我打开chrome devtools时 lie.js和index.js都没有成功引入，我将自闭合标签去掉之后，代码成功运行了。正当我打算forgot it然后开始接着研究lie库实现的Promise时。突然觉得自己不应该放过这个坑。自己学习编程有时候太急功近利了，太热衷于什么高大上的东西，而忽视这样的细枝末节，当我深入一点去了解这个问题的时候，才发现或许这才是成为优秀程序员的关键。

查了一些资料把我引到了w3c的规范来
[w3c spec void-element](https://www.w3.org/TR/html/syntax.html#void-element)
> Raw text, escapable raw text, and normal elements have a start tag to indicate where they begin, and an end tag to indicate where they end. The start and end tags of certain normal elements can be omitted, as described below in the section on [[#optional tags]]. **Those that cannot be omitted must not be omitted.** Void elements only have a start tag; end tags must not be specified for void elements. Foreign elements must either have a start tag and an end tag, or a start tag that is marked as self-closing, in which case they must not have an end tag.

总而言之Raw text（script标签属于这一类）, escapable raw text, and normal elements这三类元素一般都要有开始和结束表签。其中这里有一些元素可以省略开始或者结束标签。不能省略的就不能省略。完了之后规范还规定了void elements（空元素）只能有开始标签不能有结束标签。

于是我试了一下input（input属于void elements）
```js
<input type="text"></input>
```

然后发现浏览器没有错误，浏览器正常地展现了我们想要的效果。
所以结论是**浏览器也不按w3c的规范来**

不过当我打开chrome devtools时在elements tag下发现它自动把`</input>`去掉了。然后我在`<input>`和`</input>`之间随便加了点字，发现出现了两个input框。。

总之。浏览器不按w3c的规范来有他的道理，如果直接给上面这种不规范的代码报错，那么互联网上可能将会有一大堆同样不按规范的网站将出错。但是不规范的代码很容易引起匪夷所思的bug。比如你像我一样在`<input>`和`</input>`之间随便加了点字。然后如何避免自己写出不规范的代码？显然...熟读规范是最严谨的方法...不过它实在是太枯燥了。

然后我就发现了[谷歌代码规范](https://google.github.io/styleguide/)里面不仅仅有HTML的代码规范...总之是神器

另外在[谷歌代码规范之HTML/CSS](https://google.github.io/styleguide/htmlcssguide.html)里他推荐了一个神奇的验证HTML网页是否规范的工具网站[Nu Html Checker](https://validator.w3.org/nu/)，嗯，简直是前端利器！