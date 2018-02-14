---
title: HTML-web语义化
date: 2018-01-30 23:33:28
tags:
    - html
    - 语义化
categories:
    - HTML
---

语义化，指对文本内容的结构化（内容语义化），选择合乎语义的标签（代码语义化），便于开发者阅读，维护和写出更优雅的代码的同时，让浏览器的爬虫和辅助技术更好的解析（帮助机器读懂web内容）。
<!--more-->
## 代码相关
```html
<!-- 来自MDN上的一段示例 -->
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">

    <title>My page title</title>
    <link href="https://fonts.googleapis.com/css?family=Open+Sans+Condensed:300|Sonsie+One" rel="stylesheet" type="text/css">
    <link rel="stylesheet" href="style.css">

    <!-- the below three lines are a fix to get HTML5 semantic elements working in old versions of Internet Explorer-->
    <!--[if lt IE 9]>
      <script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
  </head>

  <body>
    <!-- Here is our main header that is used accross all the pages of our website -->

    <header>
      <h1>Header</h1>
    </header>

    <nav>
      <ul>
        <li><a href="#">Home</a></li>
        <li><a href="#">Our team</a></li>
        <li><a href="#">Projects</a></li>
        <li><a href="#">Contact</a></li>
      </ul>

       <!-- A Search form is another commmon non-linear way to navigate through a website. -->

       <form>
         <input type="search" name="q" placeholder="Search query">
         <input type="submit" value="Go!">
       </form>
     </nav>

    <!-- Here is our page's main content -->
    <main>

      <!-- It contains an article -->
      <article>
        <h2>Article heading</h2>

        <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Donec a diam lectus. Set sit amet ipsum mauris. Maecenas congue ligula as quam viverra nec consectetur ant hendrerit. Donec et mollis dolor. Praesent et diam eget libero egestas mattis sit amet vitae augue. Nam tincidunt congue enim, ut porta lorem lacinia consectetur.</p>

        <h3>subsection</h3>

        <p>Donec ut librero sed accu vehicula ultricies a non tortor. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Aenean ut gravida lorem. Ut turpis felis, pulvinar a semper sed, adipiscing id dolor.</p>

        <p>Pelientesque auctor nisi id magna consequat sagittis. Curabitur dapibus, enim sit amet elit pharetra tincidunt feugiat nist imperdiet. Ut convallis libero in urna ultrices accumsan. Donec sed odio eros.</p>

        <h3>Another subsection</h3>

        <p>Donec viverra mi quis quam pulvinar at malesuada arcu rhoncus. Cum soclis natoque penatibus et manis dis parturient montes, nascetur ridiculus mus. In rutrum accumsan ultricies. Mauris vitae nisi at sem facilisis semper ac in est.</p>

        <p>Vivamus fermentum semper porta. Nunc diam velit, adipscing ut tristique vitae sagittis vel odio. Maecenas convallis ullamcorper ultricied. Curabitur ornare, ligula semper consectetur sagittis, nisi diam iaculis velit, is fringille sem nunc vet mi.</p>
      </article>

      <!-- the aside content can also be nested within the main content -->
      <aside>
        <h2>Related</h2>

        <ul>
          <li><a href="#">Oh I do like to be beside the seaside</a></li>
          <li><a href="#">Oh I do like to be beside the sea</a></li>
          <li><a href="#">Although in the North of England</a></li>
          <li><a href="#">It never stops raining</a></li>
          <li><a href="#">Oh well...</a></li>
        </ul>
      </aside>

    </main>

    <!-- And here is our main footer that is used across all the pages of our website -->

    <footer>
      <p>©Copyright 2050 by nobody. All rights reversed.</p>
    </footer>

  </body>
</html>
```
以上代码对应以下网站
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/html-semantic/semantic-web.png)
**以上代码与具体网站的对应直观地展示了一部分HTML5新标签的语义**

## 语义化的重点
语义化标签说白了就是我们要用具有一定语义的标签来代替无语义的标签。web语义化是HTML5标准的一大目标。在HTML5之前我们表示网站结构可能会使用类似以下
```html
<div class="navbar"></div>
```
来表示网站的导航栏结构
自从HTML5新增了`<nav>`标签后。我们就可以使用
```html
<nav></nav>
```
来包裹网站的导航栏。
nav相比于div来说是具有语义的，这会使人类更容易阅读代码，但是更重要的意义在于帮助机器来理解文档。作为优秀的程序员，应该找到最符合语义的标签来编写HTML文档。同时不能纯粹为了显示一些样式而使用`<b> <em> <strong> <i> <u>`等一些标签。样式应该交给CSS去做。具体不同标签的语义可以参考下面的一些文档

### 一些参考
[HTML各个元素语义的描述-by顾轶灵](https://justineo.github.io/slideshows/semantic-html/)
[MDN HTML4之前的标签语义](https://developer.mozilla.org/zh-CN/docs/Learn/HTML/Introduction_to_HTML/HTML_text_fundamentals)
[MDN HTML5新增替代div的标签语义](https://developer.mozilla.org/zh-CN/docs/learn/HTML/Introduction_to_HTML/%E6%96%87%E4%BB%B6%E5%92%8C%E7%BD%91%E7%AB%99%E7%BB%93%E6%9E%84)
[MDN HTML5的文档节段和纲要](https://developer.mozilla.org/zh-CN/docs/Web/Guide/HTML/Sections_and_Outlines_of_an_HTML5_document)