---
title: HTML-head标签
date: 2018-01-30 22:25:31
tags:
    - html
categories:
    - HTML
---
在页面加载完成的时候，标签head里的内容，是不会在页面中显示出来的。不像`<body>`元素的内容可以显示在浏览器中，head 的内容不会在浏览器中显示，它的作用是包含一些页面的元数据。它包含了像页面的`<title>`(标题) ,CSS(如果你想用CSS来美化页面内容)，图标和其他的元数据(比如 作者，关键词，摘要)。

<!--more-->
[MDN head新手入门](https://developer.mozilla.org/zh-CN/docs/Learn/HTML/Introduction_to_HTML/The_head_metadata_in_HTML)
## 相关代码
```html
<!DOCTYPE html>
<html lang="zh-CN">
<!-- 设置HTML文档的语言，文档就会被搜索引擎更有效地索引 (例如，允许它在特定于语言的结果中正确显示) -->
  <head>
    <meta charset="utf-8">
    <!-- //HTML5设定网页字符集的方式，推荐使用UTF-8 -->
    <meta name="keywords" content="博客，HTML，前端">
    <!-- 用于告诉搜索引擎，你网页的关键字 -->
    <meta name="description" content="热爱前端与编程,这是我的前端博客">
    <!-- 用于告诉搜索引擎，你网站的主要内容 -->
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- 为了适配移动端浏览器 -->
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
    <!-- 用于告知浏览器以何种版本来渲染页面(一般都设置为最新模式) -->
    <meta http-equiv="cache-control" content="no-cache">
    <!--指定请求和响应遵循的缓存机制,参考http缓存-->
    <title>My test page</title>
    <link rel="stylesheet" href="my-css-file.css">
    <script src="my-js-file.js"></script>
    <!-- 实际上，把js放在文档的尾部（在 </body>标签之前）是一个更好的选择 -->
  </head>
  <body>
  </body>
</html>
```

### 标签`<title>`

```html
<title>My test page</title>
```
title标签会显示在标签页，当页面被添加为书签时title的内容会被作为建议的书签名

### 元数据`<meta>`
HTML `<meta>` 元素表示那些不能由其它HTML元相关元素 (`<base>`, `<link>`, `<script>`, `<style>` 或 `<title>`) 之一表示的任何元数据信息.

许多`<meta>` 元素包含了name 和 content 特性:

- http-equiv 这个枚举属性定义了能改变服务器和用户引擎行为的编译,相当于HTTP的作用，比如说定义些HTTP参数啥的
- name 特性指定了meta 元素的类型; 说明该元素包含了什么类型的信息。
- content 指定了实际的元数据内容。为 http-equiv 或 name 属性提供了与其相关的值的定义。

一些参考:
[HTML meta标签总结与属性使用介绍](https://segmentfault.com/a/1190000004279791)
[MDN 完整meta标签文档](https://developer.mozilla.org/zh-CN/docs/Web/HTML/Element/meta) 

### 外部CSS`<link>` 内部CSS`<style>` 外部JS`<script>`

`<link>` 元素经常位于文档的头部，它有2个属性， rel="stylesheet"，表明这是文档的样式表，而 href,包含了样式表文件的路径
```html
<link rel="stylesheet" href="my-css-file.css">
```

`<script>` 部分没必要非要放在文档头部; 实际上，把它放在文档的尾部（在 `</body>`标签之前）是一个更好的选择 ，这样可以确保在加载脚本之前浏览器已经解析了HTML内容（如果脚本加载某个不存在的元素，浏览器会报错）。
```html
<script src="my-js-file.js"></script>
```
注意： `<script>`元素看起来像一个空元素，但它并不是，因此需要一个结束标记。您还可以选择将脚本放入`<script>`元素中，而不是指向外部脚本文件

#### 参考资料
[关于meta那个viewport可以看这篇](https://www.cnblogs.com/2050/p/3877280.html)