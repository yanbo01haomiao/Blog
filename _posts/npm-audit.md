# 了解一点npm audit

## 建议阅读

[npm audit 二三事](http://eux.baidu.com/blog/fe/npm%20aduit%E4%BA%8C%E4%B8%89%E4%BA%8B)

[npm audit 官方文档](https://docs.npmjs.com/cli/audit.html)

## 背景

相信很多人和我一样，关注npm audit，是来自于`npm install`命令时，报出类似以下warning
```
$> npm install

added 987 packages from 668 contributors and audited 7878 packages in 12.261s
found 504 vulnerabilities (4 low, 11 moderate, 489 high) 
  run `npm audit fix` to fix them, or `npm audit` for details
```
报错已经提供了比较详细的信息了，大概意思就是安装的包可能存在安全风险，npm audit 提供了`npm audit fix`来帮助你自动修复安全风险，`npm audit`命令可以查看这些安全风险详情

## npm audit 查看风险详情

我们先试看看`npm audit`看看安全风险的详情,我们可以看到如下格式的安全风险数据
```
$> npm audit

┌───────────────┬──────────────────────────────────────────────────────────────┐
│ High          │ Prototype Pollution                                          │
├───────────────┼──────────────────────────────────────────────────────────────┤
│ Package       │ lodash                                                       │
├───────────────┼──────────────────────────────────────────────────────────────┤
│ Dependency of │ gulp [dev]                                                   │
├───────────────┼──────────────────────────────────────────────────────────────┤
│ Path          │ gulp > vinyl-fs > glob-watcher > gaze > globule > lodash     │
├───────────────┼──────────────────────────────────────────────────────────────┤
│ More info     │ https://npmjs.com/advisories/782                             │
└───────────────┴──────────────────────────────────────────────────────────────┘
```
这是今年（2019年）刚爆出lodash原型污染的一个漏洞[Lodash 库爆出严重安全漏洞，波及 400 万 + 项目](https://www.infoq.cn/article/k7C-ZvXKOHh284ToEy9K).点击More info给出的链接我们可以看到这个漏洞的来源、处理方法等。

这整个逻辑的流程大概是：

某人/组织发现了某个包存在安全漏洞 -> 反馈到npm/某个安全平台 -> npm通知给该包的维护者并在后台标记这个包存在安全缺陷。

包的用户依赖了这个包 -> 运行`npm install`后该命令请求npm的某个接口 -> 后台接口检查所安装的包中是否有存在安全漏洞的包并返回相关数据

## npm audit fix 修复安全风险

waring的提醒指示我们可以使用`npm audit fix`命令来修复安全风险
```
$> npm audit fix

+ axios@0.19.0
+ bootstrap@3.4.1
+ http-proxy-middleware@0.19.1
added 29 packages from 43 contributors, removed 1 package, updated 11 packages and moved 1 package in 9.232s
fixed 485 of 504 vulnerabilities in 7975 scanned packages
  13 vulnerabilities required manual review and could not be updated
  4 package updates for 6 vulns involved breaking changes
  (use `npm audit fix --force` to install breaking changes; or refer to `npm audit` for steps to fix these manually)
```
提示我们504四个包的安全风险已有485个被修复，剩下的有13个安全风险需要人工review并修复，4个包存在breaking changes，可以加上--force强行升级，但是一般并不推荐这样做。可以再次使用`npm audit`来查看剩下的包具体存在的问题再进一步处理。

因为大部分漏洞的修复可能是维护者更新包的一个小版本，所以使用npm audit fix能够修复的问题一般是同属于一个大版本内的包更新，比如你现在所依赖的4.17.4版本的lodash存在漏洞，维护者所发布的4.17.11版本修复了这个问题，那npm audit帮你把依赖升级到这个版本就行。因为同一个大版本内更新一般API是不会变的，所以直接更新依赖不会影响程序的正常运行。而需要使用`npm audit fix --force`强制升级的包一般都会跨至少一个大版本，比如1.0.2 -> 4.17.11这类的，你强制升级了，可能会影响程序正常运行。所以最好还是手动处理。另外，无法自动修复的，还有可能是官方未出修复补丁的包，或者其他情况等。

*上面这里关于大版本号的内容我本人其实并不确定，因为第三方包的作者不一定都会遵循"小版本不更改API"这条规则，猜测npm应该是有更加科学的方法去判断哪些包的缺陷可以自动更新，哪些需要手动处理*
