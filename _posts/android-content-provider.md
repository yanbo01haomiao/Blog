---
title: 四大组件之Content Provider
date: 2018-01-27 20:46:47
tags:
    - 安卓
categories:
    - Android
---
数据持久化提到的技术所保存的数据只能在当前的应用程序中访问，内容提供器突破了这一限制
<!--more-->

数据持久化提到的技术所保存的数据只能在当前的应用程序中访问，内容提供器突破了这一限制
<!--more-->

### 一个图示
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp0.png)
### 为什么需要内容提供器？
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp1.png)

### 内容提供器简介
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp2.png)

**访问其他程序中的数据**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp3.png)

### ContentResolver的基本用法
**增删改查**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp4.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp5.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp6.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp7.png)

#### 读取联系人
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp8.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp9.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp10.png)

**以上代码解释**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp11.png)

### 学会了消耗别人的内容提供器，现在我们来创建自己的内容提供器
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp12.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp13.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp140.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp15.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp16.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp17.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp18.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp19.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp20.png)
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp21.png)
**//注意内容提供器也是四大组件之一，所以我们也必须在AndroidManifest.xml中进行注册**
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/android-content-provider/cp22.png)
还有一个更为详尽的实践可以到<第一行代码>第二版去看