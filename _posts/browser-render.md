# 浏览器渲染机制及css,js加载方式

关于浏览器的渲染机制在网上有一篇流传甚广的神作[How Browser Works](https://www.html5rocks.com/zh/tutorials/internals/howbrowserswork/)。从被翻译的语言的版本之多也可以看出其经典之处。我也建议大家可以看看这篇文章。不过今天我打算讲一些我觉得从开发人员的角度来说比较实用一点的知识。

关于 **浏览器的渲染机制** 这样的问题，由于源码比较复杂，所以真正看过像chrome的源码的人特别稀少，网上有太多太多的人在写 **浏览器的渲染机制** 相关的博文无外乎就是从别的博文抄一点，或者是通过把浏览器当一个黑盒写一些例子去运行由此猜下浏览器的渲染机制。我觉得除非真正看过源码，否则很难真正理解他的运行渲染机制。很遗憾，我也没有看过源码。因此本文也只能讲一些浏览器浮于表面的表现。并且不保证正确。期待大家以批判的眼光阅读。

## 名词解释

- 呈现引擎：可能也称作渲染引擎，负责显示请求的内容，如果请求的内容是HTML，他就负责解析HTML和CSS内容，并将解析后的内容显示在屏幕上。具体的有像Firefox使用的Gecko,还有Safari的Webkit。

- JavaScript解释器：用于解析和执行JavaScript代码，例如大名鼎鼎的V8。这里要理解JavaScript代码分为解析(含词法分析和语法分析)和执行(含：预编译(预处理))两个过程。解析差不多就是把我们的代码进行词法分析和语法分析，形成抽象语法树(AST)。预编译差不多就是先对某个代码块里的代码做`函数声明`、`变量声明`。而执行就是创建全局执行上下文栈、创建全局执行上下文、创建函数执行上下文然后等函数执行完弹出函数执行上下文等等这个反复的动态过程。

- 解析：解析是指通过以文档所遵循的语法规则将文档通过词法分析和语法分析两个过程产出一个解析树的过程。HTML文档得到DOM节点树，解析CSS文档得到CSS规则树(rule tree)。
    - HTML解析
    ```html
    <html>
    <body>
        <p>
        Hello World
        </p>
        <div> <img src="example.png"/></div>
    </body>
    </html>
    ```
    ![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/browser-render/htmldom.png)

    - CSS解析
    ![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/browser-render/cssom.png)
    这里的CSS解析是Webkit的机制，Gecko的机制中解析成CSS规则树需要依赖于HTML的解析。这里主要解释解析这个词的含义，关于二者的区别不细说，可以看How Browser Works。

    - JS解析
    就是对JavaScript文本代码通过词法和语法分析形成抽象语法树，是JS代码执行前必须经过的步骤

- 加载：在之后讲HTML文档里面引用外部CSS、JS、IMG等资源时经常用到。我觉得基本上可以理解为下载。

## 浏览器渲染的流程图

整个浏览器的渲染流程大致如下：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/browser-render/render-process.jpg)

现在我大概来描述一下这个过程：

1. 浏览器访问某个网站例如 https://github.com。 这个时候先从服务器得到一个github首页的html文件。这个html文件里面可能会引入外部的css、js、img等资源。（根据我对github网站的实验，我发现浏览器不会等html完全下载完才开始解析html，而是下载一部分就开始解析，解析的时候浏览器发现了html文档里面引用了外部资源，则会prefetch(预加载)这些外部资源。

**我们看到蓝色横条表示Content Download而github.com这个html还没下载完，后面的两个css文件和svg就开始了Content Download。如果被弹窗挡住，可以看上面的横条**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/browser-render/githubnetwork.png)

2. 根据1一旦浏览器接收到一部分html他的呈现引擎就开始从上到下解析html文件，根据上面我们对解析的名词解释，解析html文件就是生成DOM树。

解析的过程可能会遇到`<link>`引入外部css,css不阻塞html的加载和解析，但是会阻塞后续js代码的执行，因为js代码可能会通过CSSOM API来操作css,既然js代码依赖css的加载那么js代码的执行就要等css解析完毕。js代码阻塞了，所以可能间接导致html的解析，因为js代码是会阻塞html的解析的。

解析的过程可能会遇到`<script>`无论是内联script还是外联script，浏览器都会停止解析html，转而解析和执行这些js代码。而js代码可能通过DOM API更改我们的DOM树。所以html解析可能会往回重新解析，而不是单纯地自上而下。也正因js代码会改变html的解析成果DOM树，所以浏览器才会停止解析html。

解析的过程还可能会遇到`<img>`图片资源或者其他外部资源，据悉，这些其他资源既不阻塞html解析，也不阻塞js执行

关于这一点，我也通过访问github官网做了一个实验，结果如下：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/browser-render/githubperformance.png)

其中蓝色条的Parse HTML代表的就是html文件解析的过程，我们可以发现中间穿插着Evaluate Script（执行js），直到一条蓝色竖线切断时，即DOMContentLoad事件触发时才表示html文档解析完毕，这个时候我们从上栏蓝竖线后的小图里看到，我们的用户已经能看到最终的页面了，这就表示paint已经完成了

3. 在html解析完毕后，我们从上面的流程图可以看到html和css和js最后会到一个construt的过程。这个过程后形成一个Rendering Tree(在Gecko引擎里的术语是Frame Tree)。这个Rendering Tree大概可以理解为我们最终看到的页面的一个数据结构。可以简单理解为是一颗DOM树，但是这个DOM树的每个节点上都有样式上下文，比如说这个DOM节点的color是什么啊，font-size是多少啊，margin-top多少啊这些。我们的浏览器根据这个Rendering Tree会做一个layout的动作，大概就是去计算每个元素的位置啊这些信息。然后再调用Native GUI API去把这个Rendering Tree Paint 出来，就是用户最终看到的界面。

- 同时当我们的在解析html的时候遇到了一个比较耗时的js代码，这时js代码阻塞了html的解析。**这时浏览器会先将已经解析好的一部分html先construt出来并且paint出来，所以用户会先看到其中一部分页面**，关于这一点我没有做实验，而这里有个小伙伴动手做了实验[聊聊浏览器的渲染机制](https://segmentfault.com/a/1190000007766425)，大家可以看一下，这是也是一篇很好的文章。
