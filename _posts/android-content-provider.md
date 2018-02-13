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

### 一个图示
<img src="android-content-provider/cp0.png" width="100%"/>

### 为什么需要内容提供器？
<img src="android-content-provider/cp1.png" width="100%"/>

### 内容提供器简介
<img src="android-content-provider/cp2.png" width="100%"/>

**访问其他程序中的数据**
<img src="android-content-provider/cp3.png" width="100%"/>

### ContentResolver的基本用法
**增删改查**
<img src="android-content-provider/cp4.png" width="100%"/>
<img src="android-content-provider/cp5.png" width="100%"/>
<img src="android-content-provider/cp6.png" width="100%"/>
<img src="android-content-provider/cp7.png" width="100%"/>

#### 读取联系人
<img src="android-content-provider/cp8.png" width="100%"/>
<img src="android-content-provider/cp9.png" width="100%"/>
<img src="android-content-provider/cp10.png" width="100%"/>

**以上代码解释**
<img src="android-content-provider/cp11.png" width="100%"/>

### 学会了消耗别人的内容提供器，现在我们来创建自己的内容提供器
<img src="android-content-provider/cp12.png" width="100%"/>
<img src="android-content-provider/cp13.png" width="100%"/>
<img src="android-content-provider/cp14.png" width="100%"/>
<img src="android-content-provider/cp15.png" width="100%"/>
<img src="android-content-provider/cp16.png" width="100%"/>
<img src="android-content-provider/cp17.png" width="100%"/>
<img src="android-content-provider/cp18.png" width="100%"/>
<img src="android-content-provider/cp19.png" width="100%"/>
<img src="android-content-provider/cp20.png" width="100%"/>
<img src="android-content-provider/cp21.png" width="100%"/>

**//注意内容提供器也是四大组件之一，所以我们也必须在AndroidManifest.xml中进行注册**
<img src="android-content-provider/cp22.png" width="100%"/>

还有一个更为详尽的实践可以到<第一行代码>第二版去看