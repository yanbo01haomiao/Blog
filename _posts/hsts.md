# HSTS

关于HTTP Strict Transport Security，我看了一篇写的挺好的文章[HSTS详解](https://www.jianshu.com/p/caa80c7ad45c)，大家也可以参考这篇文章。

这里我仍然以百度贴吧(未开启HSTS)以及Github(开启了HSTS)这两个产品来说明HSTS的作用

当我在Chrome的地址栏输入tieba.baidu.com的时候，等待加载完页面我们发现了地址栏上面为
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/hsts/baidu-url.png)

看起来好像浏览器默认以HTTPS协议向百度的服务器发起了请求，其实不然，我们还是F12打开devtool Network
我们发现对tieba.baidu.com/index.html有两次请求(注意第一次请求的url中的协议及状态码)

1. 第一次http请求
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/hsts/baidu-http.jpg)

2. 第二次https请求
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/hsts/baidu-https.jpg)

众所周知https相对于http而言的一大安全之处就是可以防范中间人攻击，我们看到百度贴吧的做法是很粗糙的，当我们第一次访问的时候，发出的请求时http请求，然后后台接到这个请求直接重定向到https版本的url。我们可以在第一次请求的Response Headers中的Location看到这步操作。这也意味着，**我们的第一次http请求是存在中间人攻击的风险的**。我们知道http报文是明文传输的，我们可以在Request Headers里看到当我的Cookie信息(已被我涂黑)。当我们的Cookie信息泄漏时，攻击者可以利用这个Cookie信息来伪装成我们进行操作

*以下是我利用Postman对百度用户信息接口进行调用，可以看到带Cookie的请求得到了正确的响应，不带cookie的请求返回了null，我们的用户信息随着Cookie的泄漏而泄漏，除此之外，攻击者还可能利用我们的Cookie进行发帖删帖等恶意活动*
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/hsts/baidu-userinfo.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/hsts/baidu-userinfo-cookie.jpg)

之后，我们来看看Github是怎么做的

首先还是在Chrome的地址栏输入github.com,同样等页面加载完，打开devtool NetWork。我们同样发现了有两个对github.com主页的请求
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/hsts/github-http.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/hsts/github-https.jpg)

所以这是不是意味着Github也和百度一样存在着安全风险呢？毕竟他看起来也存在一次`http请求`。

不过我们可以看到这次`http请求`有点奇怪，他也没有Location来告诉我们重定向到哪里，Response Headers还有Non-Authoritative-Reason: HSTS这种莫名的头部。我根据307这个状态码在维基百科上看到一条解释[HTTP 307](https://zh.wikipedia.org/wiki/HTTP_307)
> 用途：该响应码被用于Chrome，用来在本地对已经缓存的HSTS站点进行重定向。[5]

我换了个浏览器Edge，同样输入github.com，发现调试工具只有一个https的请求，可见，维基百科诚不欺我。

所以Chrome这个所谓的`http请求`实际上并没有被发送到网络，而是直接在本地被重定向了，因此也就不存在中间人攻击的风险。