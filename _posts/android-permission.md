---
title: 安卓的运行时权限
date: 2018-01-27 20:37:04
tags:
    - 安卓
categories:
    - Android
---

运行时权限是安卓6.0引入的新特性
<!--more-->
### 运行时权限
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission0.png)
### 安卓运行时权限详解
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission1-1.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission1-2.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission1-3.png)

### 如何在程序运行时申请权限

//以申请CALL_PHONE这个权限为例

**主页面的Java代码**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission2.png)

**AndroidManifest.xml中声明一下权限**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission3.png)

写完这两边的代码。功能就实现了，并且在安卓6.0以下的手机都可以正常运行。然而在安卓6.0以上会报Permission Denial的错误

**修复这个问题之后的Java代码**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission4.png)

**以上代码的解释**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-permission/permission5.png)