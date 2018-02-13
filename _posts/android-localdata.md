---
title: 安卓3种数据持久化方式
date: 2018-01-27 20:06:11
tags:
    - 安卓
categories:
    - Android
---
Android系统中提供了3种方式用于简单地实现数据持久化，分别是 文件存储、SharedPreferences存储
、SQLite数据库存储

<!--more-->

### 文件存储

#### 存

**简介**
<img src="android-localdata/fileintro.png" width="100%"/>

**文件存储示例**
<img src="android-localdata/file1.png" width="100%"/>

**以上代码解释**
<img src="android-localdata/file2.png" width="100%"/>

#### 取
**简介**
<img src="android-localdata/file3.png" width="100%"/>
**从文件中读取数据示例**
<img src="android-localdata/file4.png" width="100%"/>
**以上代码的解释**
<img src="android-localdata/file5.png" width="100%"/>

### SharedPreferences存储
*感觉和web浏览器的localStroage类似*

**简介**
<img src="android-localdata/sp0.png" width="100%"/>

#### Android中提供了3种方法来用于得到SharedPreferences对象
<img src="android-localdata/sp1.png" width="100%"/>

**第一种方法来存储数据到SharedPreferences**
<img src="android-localdata/sp2.png" width="100%"/>

**SharedPreferences是使用XML格式来对数据进行管理的**
<img src="android-localdata/sp3.png" width="100%"/>

**存储完之后从SharedPreferences中读取数据**
<img src="android-localdata/sp4.png" width="100%"/>

**对以上代码的解释**
<img src="android-localdata/sp5.png" width="100%"/>

可使用SharedPreferences来实现记住密码的功能

### SQLite数据库存储

#### 安卓为什么需要一个本地的关系型数据库？
<img src="android-localdata/sqlite0.png" width="100%"/>

#### 安卓的SQLiteOpenHelper帮助类
**一些理论知识**
<img src="android-localdata/sqlite1.png" width="100%"/>
**首先建立一个MyDatabaseHelper类去继承SQLiteOpenHelper（我们必须有自己的帮助类）**
<img src="android-localdata/sqlite2.png" width="100%"/>
在onCreate()方法中调用了execSQL()这样能保证在数据库创建完成的同时还能成功创建Book表
**调用创建数据库的方法**
<img src="android-localdata/sqlite3.png" width="100%"/>
关键的代码是使用
private MyDatabaseHelper dbHelper
得到一个实例
然后调用构造函数
new MyDatabaseHelper(this,"BookStore.db",null,1)
来构造这个实例
然后再用这个实例使用相应的实例方法dbHelper.getWritableDatabase()

**升级数据库**
//比如想往数据库再新增一张表
修改MyDatabaseHelper（加粗是修改的内容）
<img src="android-localdata/sqlite4.png" width="100%"/>

**以上代码的解释**
<img src="android-localdata/sqlite5.png" width="100%"/>

修改完MyDatabaseHelper之后就是想办法让onUpgrade()方法执行了
<img src="android-localdata/sqlite6.png" width="100%"/>
**关键点:**数据库版本号是2，这时候就会new这个操作就会调用onUpgrade()

**添加数据**
<img src="android-localdata/sqlite7.png" width="100%"/>
#### SQLiteDatabase中提供了insert()update()delete()query()

##### insert()
<img src="android-localdata/sqlite8.png" width="100%"/>

**以上代码的解释**
<img src="android-localdata/sqlite9.png" width="100%"/>

##### update()
<img src="android-localdata/sqlite10.png" width="100%"/>

**以上代码的解释**
<img src="android-localdata/sqlite11.png" width="100%"/>

##### delete()
<img src="android-localdata/sqlite12.png" width="100%"/>
**以上代码的解释**
<img src="android-localdata/sqlite13.png" width="100%"/>

##### query()
<img src="android-localdata/sqlite14.png" width="100%"/>
**query示例**
<img src="android-localdata/sqlite15.png" width="100%"/>
**以上代码的解释**
<img src="android-localdata/sqlite16.png" width="100%"/>

#### 使用LitePal操作数据库
LitePal是一款开源的Android数据库框架，采用了ORM的模式

*突然感觉这里的ORM，和在前端里的DOM两种的思想有某种相似之处*

*对于ORM而言，O是Object,而R是relational,M是Mapping
Java应用程序需要和SQL数据库进行交互，无奈Java应用程序是用Java面向对象的思想来写的，而数据库是根据SQL结构化语言来写的，我们在这里做了一层Mapping，让我们用JAVA面向对象的方式来操作数据库*

*对于DOM而言，D是Document,而O是Object ,M是Model
在Web中，文档的内容是用HTML标签来表示的，而文档的逻辑是用JavaScript来实现的，我们把一个HTML标签对应地实现它相应的一个JavaScript Object（将HTML的attribute映射为object的key等等）我们可以用JavaScript来动态地修改HTML标签等等*