# 了解一点package-lock.json

## 建议阅读

[npm install 生成的package-lock.json是什么文件？有什么用？【建议阅读xinbenlv和2dunn的回答】](https://www.zhihu.com/question/62331583)

[npm-package-lock.json 官方文档](https://docs.npmjs.com/files/package-lock.json.html)

## 背景

npm 5.x版本以后引入了package-lock.json，对于一个典型的node项目，一般都会有一个package.json文件，相信大家对这个文件已经比较熟悉，它一般包含该项目的一些元信息。包括它的名字、版本、作者、license、scripts、依赖等内容，这里最重要的还是它所依赖的其他包。然而新出现的这个package-lock.json又是什么，想解决什么问题，我有点好奇。所以借此机会简单了解了一下。

## 回顾package.json

我们在一个项目中，使用`npm install moment`这样的命令来安装一个新的依赖，他会在我们的package.json里面生成一条如下记录,并且在node_modules里面也实际安装了2.24.0版的moment
```json
  "dependencies": {
    "moment": "^2.24.0"
  },
```
其中2.24.0版本是moment在npm仓库的最新版本，而`^`则是表示向后（新）兼容，意思是如果后续moment更新了版本，比如作者发布了2.24.1版，此时package.json里面虽然仍然是`"moment": "^2.24.0"`，但是当我们再次执行`npm install`时发现moment已经更新了2.24.1版本，这个版本的大版本（2）仍与package.json里的相同，因此允许下载该大版本最新的包到本地，node_modules里面实际安装的是2.24.1版的moment。

本来这样的逻辑是没有问题的，但是部分第三方包的作者往往不遵守`同一个大版本包的API不能做改动`这样一条规则。所以会导致可能完全相同的一份源码，在不同的时间安装依赖部署并运行，却产生不同的结果。举个最典型的一个例子，你在本地开发一个项目，`npm install xyz`此时在本地node_modules安装了xyz包的1.0.0版本，你在本地开发，并测试功能正常完毕。将项目提交到代码库（一般node_modules不提交），准备在正式环境部署。在这期间，xyz包的作者发布xyz包的最新版本1.1.0，但是他不遵守`同一个大版本包的API不能做改动`的规则，更改了包的一个对外API的参数。此时你在正式环境使用`npm install`让npm去自动安装项目的依赖，当安装到xyz包的时候，发现了新版本1.1.0，和package.json里面定义的 ^1.0.0是同一个大版本，因此默认允许安装新的1.1.0版本的xyz。而此时你的源码里面对xyz包的使用仍然是基于旧的API，因此正式环境的代码可能无法正常运行。

## package-lock.json

package-lock.json通俗点说就是，在你npm install的时候生成了一份，记录当前状态下实际安装在node_modules里的所有包的具体来源和实际的版本号。以便后续重新安装时，可以依据这个文件重新生成相同的依赖，保证同个项目在不同机器、不同时间、不同镜像源等外部条件发生变化的情况下能有相同的运行结果。

## 重复npm install时规则的变化

上面两部分的内容不难理解，然而package-lock.json在实际使用中还是遇到不少波折，官方因此多次更改规则。

### npm 5.0.x版本

这个版本，使用`npm install`时npm会完全依赖package-lock.json里面的内容去安装依赖。也就是你手动改了package.json将上面声明的版本号升级，然后再次`npm install`，npm仍会按照package-lock.json的内容去安装，无视你在package.json上的手动更改

- 相关issue：[package-lock.json file not updated after package.json file is changed](https://github.com/npm/npm/issues/16866)

### npm 5.1.0版本

`npm install`忽略package-lock.json，还是按照package.json去下载安装依赖。（回到最初的起点？）
- 相关issue: [why is package-lock being ignored](https://github.com/npm/npm/issues/17979)

### npm 5.4.2版本

1. 如果只有package.json文件`npm install`会按照package.json去安装依赖并生成此刻相应的package-lock.json

2. 如果同时存在package.json和package-lock.json。当你`npm install`的时候，即使package.json里有向后兼容的新的版本可以下载，package-lock.json也不会改变，安装在node_modules的只会依据package-lock.json的内容安装

3. 如果你手动更改了package.json，并且里面的版本范围跟package-lock.json里实际的版本不再兼容。比如说package.json原先写的某个包是`^1.1.0`.package-lock.json安装的实际是1.1.0。后来，你手动把package.json里包的版本改为`^1.2.0`,由于package-lock.json已经不符合`^1.2.0`这个范围，因此npm会自动更新package-lock.json然后安装新的包

- 相关comments: [npm的维护者iarna的回答](https://github.com/npm/npm/issues/17979#issuecomment-332701215)