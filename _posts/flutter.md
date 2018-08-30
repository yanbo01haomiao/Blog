# 移动端跨平台技术flutter

本文所写的相关技术，自己也刚处在了解学习阶段，没有实践经验，这里强调 **仅供参考**。

## 背景

不管是桌面端还是移动端，工程师对于跨平台技术方向的努力从未停歇。B/S架构也因为其天生跨平台的特性而大受欢迎。随着移动互联网的发展，目前绝大多数公司在开发一款新的app产品时都需要同时开发和维护Android和iOS两个版本。这带来了人力成本的上升以及双版本的同步等问题。据我粗略的了解，在PC端，目前很多公司的项目使用了Electron来使得一套代码同时兼容Windows及Mac客户端。游戏开发领域的Unity3d也是实现了跨平台开发（把runtime也打包进游戏）。对于Electron和Unity3d的跨平台实现策略我没有很深入地去了解，举这两个例子只是说明了参考不同领域的发展，我觉得移动端对于跨平台技术的需求也不是伪需求。所以我觉得目前之所以大部分APP还是采用Native开发的方式来维护两个版本的APP，最重要的原因还是没有出现一套真正较为完美的跨平台解决方案。

## Hybrid APP和React Native

- Hybrid App

所谓Hybrid App就是Native和Web两种形式Hybrid的APP，我们知道原生APP开发中一般会有一个webview组件，我们可以通过这个webview组件来加载html文件。如果有一个APP，里面使用了webview来引入web page来实现部分的业务逻辑，那么这个APP就是Hybrid APP。

最极端的Hybrid APP就是整个APP的Native部分仅有一个webview以及一些支撑webview的逻辑，没有业务逻辑，业务逻辑的实现完全靠Web来实现。当然这不代表Hybrid APP就是一个浏览器套壳的Web APP.实际上js还可通过jsBridge之类的方式来调用Native的一些js没有的API，例如截图、获取手机各项信息、GPS、拍照等等。

- React Native

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/flutter/rn.png)


上图中RN的这个Bridge和我么那上面讲的jsBridge有一定相同的地方，比如说都用来做js调用Native或者Native调用js之类的通信。RN的js代码都是通过使用JavaScriptCore来执行的。和Hybrid App有点不同，RN的运行环境（runtime）不是浏览器（webkit可以简单看作一个简陋的浏览器吧），我的大致理解是RN的业务部分我们只需要编写js代码，然后JavaScriptCore执行我们编写的js代码，RN不渲染真正展现的组件，只产出Virtual DOM，而最后通过Bridge（好像是JavaScriptCore来实现）去调用、操作、渲染上图中OEM Widgets。这个Widgets就是原生的组件。同时如果想要使用Native API也是让js通过Bridge去调用。这和Hybrid的能力有点类似，然而由于RN不是运行在webview，所以也就失去了DOM、BOM这些能力，据我所知，这和微信小程序是一样的。

- 对比

 类型 | Native App | Web App | Hybrid App | React Native App
 -----|------------|--------|------------|----------------
原生功能体验 | 优秀 | 差 | 良好 | 接近优秀
渲染性能 | 非常快 | 慢 | 接近快 | 快
是否支持设备底层访问 | 支持 | 不支持 | 支持 | 支持
网络要求 | 支持离线 | 依赖网络 | 支持离线(资源存本地情况) | 支持离线
更新复杂度 | 高(几乎总是通过应用商店更新) | 低(服务器端直接更新) | 较低(可以进行资源包更新) | 较低(可以进行资源包更新)
编程语言 | Android(Java),iOS(OC/Swift) | js+html+css3 | js+html+css3 | 主要使用JS编写,语法规则JSX
社区资源 | 丰富(Android,iOS单独学习) | 丰富(大量前端资源) | 有局限(不同的Hybrid相互独立) | 丰富(统一的活跃社区)
上手难度 | 难(不同平台需要单独学习) | 简单(写一次,支持不同平台访问) | 简单(写一次,运行任何平台) | 中等(学习一次,写任何平台)
开发周期 | 长 | 短 | 较短 | 中等
开发成本 | 昂贵 | 便宜 | 较为便宜 | 中等
跨平台 | 不跨平台 | 所有H5浏览器 | Android,iOS,h5浏览器 | Android,iOS
APP发布 | App Store | Web服务器 | App Store | App Store

## Flutter
上面简单说了传统跨平台解决方案，我们再回过头看看Flutter的解决方案，Flutter跨平台最核心的部分，是它的高性能渲染引擎（Flutter Engine）。Flutter不使用浏览器技术，也不使用Native的原生控件，它使用自己的渲染引擎来绘制widget。

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/flutter/flutter.png)

Flutter和RN一个最大的不同点在于，RN是写完Virtual DOM通过Bridge去调用、渲染Native组件，而Flutter实现了自己的渲染引擎自己提供了UI框架，只需不同Native平台提供Canvas（画布）即可。当然还有一个根本上的不同就是Flutter不是用JavaScript编写的而是使用了Dart预言，因此从根本上就不需要什么webview和JavaScriptCore。（其实强行把Flutter和RN进行对比只是他们同样是跨平台解决方案而已，并没有其他太多共性）

有一点是，Dart语言同样不是Native开发的语言（JAVA/OC），因此虽然自己构筑了UI框架来替代Native的UI框架，但还是没有实现自己的Service，也就是地理位置、蓝牙、相机、传感器之类的API仍然需要做一些转换。这里的Platform Channels做的就是这个转换的工作。实现的逻辑有点像RPC调用。

Flutter框架的整个架构如下：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/flutter/flutter-struct.png)

其中这里的Framework这部分主要就是一个UI框架，Skia则是那个渲染引擎。其中Material是Android设计风格的UI组件，而Cupertino则是iOS设计风格的UI组件。这些都是Flutter内置的Widget，这解决了传统跨平台框架没办法很好地适配操作系统设计风格的问题。除非APP在不同平台下公用一套设计，否则以往的跨平台框架将还是存在很多麻烦的地方。

## Flutter的特性

以下大部分来自官网[flutter中文官网](https://flutterchina.club/)

1. 热重载
Flutter提供了2种代码编译执行的方式，一种是JIT(Just-In-Time)、另一种是AOT(Ahead-of-Time).其中在开发环境下，使用的JIT，很好地支持了热重载，节省了开发时改动代码之后需要经常等编译这个头疼的事。

2. 响应式

这个就是学React的，API名字都是setState...

```Dart
class CounterState extends State<Counter> {
  int counter = 0;

  void increment() {
    // 告诉Flutter state已经改变, Flutter会调用build()，更新显示
    setState(() {
      counter++;
    });
  }

  Widget build(BuildContext context) {
    // 当 setState 被调用时，这个方法都会重新执行.
    // Flutter 对此方法做了优化，使重新执行变的很快
    // 所以你可以重新构建任何需要更新的东西，而无需分别去修改各个widget
    return new Row(
      children: <Widget>[
        new RaisedButton(
          onPressed: increment,
          child: new Text('Increment'),
        ),
        new Text('Count: $counter'),
      ],
    );
  }
}
```

3. Platform Channels

同样是去调用Native Service的API，传统跨平台技术RN和Hybrid APP都是使用Bridge的技术来调用。而Flutter提供了Platform Channels来让Dart代码和Native Service API进行互操作。我感觉这种方式用起来是比较舒服的，据说性能也好过Bridge。

```Dart
// 获取系统电量信息的异步方法
Future<Null> getBatteryLevel() async {
  var batteryLevel = 'unknown';
  try {
    int result = await methodChannel.invokeMethod('getBatteryLevel');
    batteryLevel = 'Battery level: $result%';
  } on PlatformException {
    batteryLevel = 'Failed to get battery level.';
  }
  setState(() {
    _batteryLevel = batteryLevel;
  });
}
```

## 优劣势

优势有很多，包括上面讲的热重载、响应式还有像因为自己实现了UI框架，因此有很强的可扩展性，不像RN囿于Native提供的OEM Widgets。另一方面就是提供了AOT,在release版本中使用AOT的方式，可以将Dart代码编译成Native，在移动端可以直接执行Native代码，这算是极大的性能优势。关于其他优势[flutter中文官网](https://flutterchina.club/)也一一列举出了好多条。有兴趣可以去看看。我这里讲讲目前框架还存在的痛点：

- 组件编写可读性和体验待完善

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/flutter/item.png)

为了实现上面这样一个组件，我们需要编写类似以下的代码：
```Dart
 //返回一个居中带图标和文本的Item
  _getBottomItem(IconData icon, String text) {
    //充满 Row 横向的布局
    return new Expanded(
      flex: 1,
      //居中显示
      child: new Center(
        //横向布局
        child: new Row(
          //主轴居中,即是横向居中
          mainAxisAlignment: MainAxisAlignment.center,
          //大小按照最大充满
          mainAxisSize : MainAxisSize.max,
          //竖向也居中
          crossAxisAlignment : CrossAxisAlignment.center,
          children: <Widget>[
            //一个图标，大小16.0，灰色
            new Icon(
              icon,
              size: 16.0,
              color: Colors.grey,
            ),
            //间隔
            new Padding(padding: new EdgeInsets.only(left:5.0)),
            //显示文本
            new Text(
              text,
              //设置字体样式：颜色灰色，字体大小14.0
              style: new TextStyle(color: Colors.grey, fontSize: 14.0),
              //超过的省略为...显示
              overflow: TextOverflow.ellipsis,
              //最长一行
              maxLines: 1,
            ),
          ],
        ),
      ),
    );
  }
```
这里的痛点（或许有人会觉得是特性）在于：

1. 这种写组件UI的方式给我的感觉就像没了JSX的React，没了Template的Vue。我们需要嵌套地使用React.createElement这种API用JavaScript来写UI渲染出Virtual DOM那种意思。
2. 诸如Center、Padding这类明显和样式相关的东西，我们在Flutter里也是用组件（术语Widgets）来写，样式以及结构糅合在一起，这有点不符合关注点分离的思想。另外像主轴居中，这类传统使用CSS来实现的逻辑，也变成了组件的属性。这里和传统的Native原生开发里写在XML的attribute那里的布局属性有点像。

*我没有说这种写UI的方式不好，而只是说可能对于前端程序员来说有点不习惯。*

- 太新了

对于技术而言，太新了往往不是好事

Flutter虽然不是2018年才发布的项目，但是差不多就是在2018年3月份开始才在社区慢慢活跃起来，目前官网提供的仍是0.6的beta版本。

因为太新了，所以现在第三方库还比较少，生态还不完善，实践中上手时应该还有不少坑需要慢慢填。目前根据我查询的资料而言，就腾讯的NOW直播以及阿里的闲鱼实践了该技术。

- Dart语言有点小众

对于开发人员而言，应该很少有Dart语言经验的程序员。尽管他也学习了很多JavaScript的语法，例如Future（学Promise），还有async/await，但也需要一定的学习成本，毕竟Dart比JavaScript要更OOP一点。
