# JavaScript-BOM

## window对象--是BOM的核心

window表示浏览器的一个实例，具有双重角色，一是javascript访问浏览器窗口的一个接口。二是作为ECMAScript规定的global对象

**所有在全局作用域中声明的变量和函数都会变成window对象的属性和方法**
```js
var age = 29  //使用var添加的window属性的[[Configurable]]特性被设置为false
window.color = "red"

delete window.age  //return false
delete window.color  //return true

alert(window.age)  //29
alert(window.color) //undefined

var newValue = oldValue          //抛出异常 (使用未定义的标识符会报错)
var newValue = window.oldValue   //显示undefined  (属性查询不会抛出错误)
```
location navigator screen history实际上是window对象的属性

### 窗口关系及框架
如果页面中包含框架，则每个框架都有自己的window对象，并且保存在frames集合中
接下去讲了一些关于窗口位置，窗口大小相关的东西
window.screenLeft     window.screenX
window.screenTop     window.screenY 
window.moveTo()   window.moveBy
window.innerHeight  window.outterHeight
window.innerWidth   window.outterWidth

window.open打开弹出窗口


## 间歇调用(每隔指定的时间就执行一次代码)和超时调用(在指定的时间过后执行代码)

调用setTimeout()之后会返回一个数值ID，表示超时调用，这个超时调用ID是计划执行代码的唯一标识符
如果想要取消尚未执行的超时调用计划，可以调用clearTimeout()并将相应的超时调用ID作为参数传递给他
(只要是在指定的时间尚未过去之前调用了clearTimeout()，就可以完全取消超时调用)
超时调用的代码是在全局作用域中执行的，因此超时调用传入的函数中的this在非严格模式下指向window

间歇调用setInterval()，接受的参数和超时调用一样，传入的时间变成了重复执行代码的时间间隔。直到间歇调用被取消(
即调用了clearInterval()并传入了相应的间歇调用ID)，或者页面被卸载时停止.
（在开发环境下，其实很少使用真正的间歇调用，因为有可能出现（在间歇时间小于调用的操作的执行时间），后一个间歇调用在前一个间歇调用结束之前启动）

可以用以下方式用setTimeout来模拟setInterval
```js
function incrementNumber(){
    num++;
    //在还没到达停止下来的条件时持续触发setTimeout
    if(num<max){
        setTimeout(incrementNumber,500);
    }else{
        alert("Done")
    }
}

setTimeout(incrementNumber,500)
```
接下去讲了alert() confirm() prompt()方法。不常用 略过

## location对象(很有用)

window.location = document.location（引用了同一个对象）

location对象↓

属性名    | 例子                   | 说明
:--------|:-----------------------|:-----
hash     | "#content"             |返回URL中的hash(#，包括后面跟着的字符)
host     | "www.wrox.com:80"      | 服务器主机名加端口号
hostname | "www.wrox.com"         |不带端口号的主机名
href     | "http://www.wrox.com"  |完整URL
pathname | "/wileyCDA/"           |目录和文件名
port     | "8080"                 |端口号
protocol | "http"                 |协议
search   | "?q=javascript"        |查询字符串。包括问号在内

解析查询字符串的方法
```js
function getQueryStringArgs(){
    //用substring去掉问号
    var qs = (location.search.length>0? location.search.substring(1):""),
        //初始化一个保存数据的对象
        args = {}
        //取得每一项
        items = qs.length ? qs.split("&") :[],
        item = null,
        name = null,
        value = null,

        i=0,
        len = items.length

       for(i=0;i<len;i++){
           item = items[i].spilt("=")
           //使用decodeURI是因为查询字符串是编码过的
           name = decodeURIComponent(item[0])
           value = decodeURIComponent(item[1])

           if(name.length){
               args[name] = value
           }
       }
       return args
}
``` 
关于上面的decodeURICoponent有一些知识点
```js
encodeURI("https://cai.com?username=蔡") 
//"https://cai.com?username=%E8%94%A1"
encodeURIComponent("https://cai.com?username=蔡") 
//"https%3A%2F%2Fcai.com%3Fusername%3D%E8%94%A1"

decodeURI("https://cai.com?username=%E8%94%A1")
//"https://cai.com?username=蔡"
decodeURIComponent("https://cai.com?username=%E8%94%A1")
//"https://cai.com?username=蔡"

decodeURI("https%3A%2F%2Fcai.com%3Fusername%3D%E8%94%A1") 
//"https%3A%2F%2Fcai.com%3Fusername%3D蔡"
decodeURIComponent("https%3A%2F%2Fcai.com%3Fusername%3D%E8%94%A1")
//"https://cai.com?username=蔡"
```


**位置操作**
```js
location.assign("http://www.wrox.com";)   立即打开新的URL,并在浏览器的历史记录中产生一条记录。
window.location = "http://www.wrox.com";
location.href = "http://www.wrox.com"; （最常用）
```
上面这两句的效果和第一句也一样 
同时也可以只做局部修改
```js
location.hash = "#section1"
location.search = "?q=css"
...
```
每次修改location的属性（hash除外）页面都会以新的URL重新加载，并在浏览器的历史记录中生成一条新的记录
```js
location.replace("http://www.wrox.com/";)  //浏览器的位置改变，却不会生成新纪录

location.reload()              //重新加载(有可能从缓存中加载)
location.reload(true)          //重新加载(强制从服务器重新加载)
```
## navigator对象
他有很多属性和方法
识别客户端浏览器的事实标准
检测浏览器中是否安装了特定的插件是一种常见的检测例程   有  plugins

## screen对象   只用来表明客户端的能力，包括浏览器窗口外部的显示器信息，屏幕的水平垂直之类

## history对象  
保存着用户上网的历史记录，从窗口被打开那一刻算起
```js
//后退一页
history.go(-1)    //history.back()
//前进一页 
history.go(1)     //history.forward()
//前进两页
history.go(2)

//跳转到最近的包含该字符串的第一位置 可能后退也可能前进
history.go("wrox.com")
```
