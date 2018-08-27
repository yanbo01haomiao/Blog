# Node.js设计模式（下）

## Strategy（分离通用和可变逻辑）

Strategy模式，笼统讲就是分离代码的通用和可变逻辑。考虑如下场景：某个项目的支付模块，需要计算购物车里的所有商品总价，减去相应的优惠、折扣等等算出应付总价，然后让用户选择支付方式，不同的支付方式可能又会有不同的优惠。这里存在两个部分，一部分是所有支付方式都相同的逻辑，即计算购物车商品总价，减去优惠折扣。另一部分则根据用户所选择的支付方式，有不同的业务逻辑。当遇到类似的场景时，可以考虑Strategy模式来将可变的逻辑和通用逻辑分离开来。这符合 **关注点分离**的思想。

如下图所示：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/design-pattern-part2/strategy.png)

这里就是通过可变换的对象Strategy来使对象Context支持其逻辑中的变化，以上面的支付场景为例，Strategy对象就是来支持可变的支付方式。

举一个更为具体的例子：
**场景**
在应用程序开发中，我们经常会编写一些config，里面包含了链接的数据库的url啊、服务器监听的port啊等等配置。其中配置应该提供一些简单的接口让我们来get或者set配置。同时我们希望支持将配置序列化和反序列化成 **多种格式的配置文件,例如JSON、INI或YAML**，这里加粗的需求就是Strategy模式的用武之地。

完整代码如下：
```js
// config.js
const fs = require('fs');
const objectPath = require('object-path');

class Config {
  constructor(strategy) {
    this.data = {};
    this.strategy = strategy;
  }

  get(path) {
    return objectPath.get(this.data, path);
  }

  set(path, value) {
    return objectPath.set(this.data, path, value);
  }

  read(file) {
    console.log(`Deserializing from ${file}`);
    this.data = this.strategy.deserialize(fs.readFileSync(file, 'utf-8'));
  }

  save(file) {
    console.log(`Serializing to ${file}`);
    fs.writeFileSync(file, this.strategy.serialize(this.data));
  }
}

module.exports = Config;
```
关于objectPath，不熟悉的同学可以看一下[object-path(npm)](https://www.npmjs.com/package/object-path)。我们通过Config这个class暴露出来的get和set很容易地去设置和获得config。这是代码中通用部分的逻辑，但这不是今天的重点，重点在于`this.strategy`，也就是实现可变逻辑的部分。`read`和`save`这两个函数的执行将不是写死的代码，而是根据所选择的不同的strategy有不同的具体执行的代码。我们来看看具体怎么实现不同的策略。

```js
// strategies.js
const ini = require('ini'); // https://npmjs.org/package/ini

module.exports.json = {
  deserialize: data => JSON.parse(data),
  serialize: data => JSON.stringify(data, null, '  ')
}

module.exports.ini = {
  deserialize: data => ini.parse(data),
  serialize: data => ini.stringify(data)
}
```
这个strategies里面有针对不同格式的序列化和反序列化方法的实现，我们看一下如何将上面的config.js(即Context)和strategies.js(即Strategy)结合在一起，以供使用不同的策略。

```js
// configTest.js
const Config = require('./config');
const strategies = require('./strategies');
const jsonConfig = new Config(strategies.json); // 使用json策略
jsonConfig.read('samples/conf.json');
jsonConfig.set('book.nodejs', 'design patterns');
jsonConfig.save('samples/conf_mod.json');

const iniConfig = new Config(strategies.ini); // 使用ini策略
iniConfig.read('samples/conf.ini');
iniConfig.set('book.nodejs', 'design patterns');
iniConfig.save('samples/conf_mod.ini');
```
关于Strategy模式可以使用以下一个极其简洁的伪代码来表示
```js
function context(strategy) {...} // strategy是变量、参数
```

## State（动态的Strategy）

State是Strategy的一种变体，Strategy模式中，当Context选定了一种策略，那么在该Context剩余的寿命期间将保持这种策略不变。例如上文最后的那个jsonConfig对象。而State模式会随着Context的状态变化而改变策略，因此称State是动态的Strategy，示例图如下：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/design-pattern-part2/state.png)

考虑以下一个适合State模式的技术场景：现在我们需要实现一个fail-safe socket，这个socket需要满足以下的需求：
1. 当服务器处于offline状态时，客户端将所要发送的数据进行排队，等待连接重新建立后立即尝试发送。
2. 当服务器处于online状态时，则客户端正常发送数据
这里涉及的需求，就很适合State，根据状态的不同来选择不同的策略。
*实际上这里的逻辑，不就是if/else吗？个人认为如果状态没有特别多，状态对应的策略也没有特别复杂，且不考虑可扩展性等问题，完全不需要刻意去用State模式*

```js
// failsafeSocket.js
const OfflineState = require('./offlineState');
const OnlineState = require('./onlineState');

class FailsafeSocket {
  constructor (options) { // [1]
    this.options = options;
    this.queue = [];
    this.currentState = null;
    this.socket = null;
    this.states = {
      offline: new OfflineState(this),
      online: new OnlineState(this)
    };
    this.changeState('offline');
  }

  changeState (state) { // [2]
    console.log('Activating state: ' + state);
    this.currentState = this.states[state];
    this.currentState.activate();
  }

  send(data) { // [3]
    this.currentState.send(data);
  }
}

module.exports = options => {
  return new FailsafeSocket(options);
};
```
其中`this.queue`是当服务器处于offline状态时，数据将被存储的地方。`this.state`代表着该FailsafeSocket对象可能存在的几种状态。`changeState()`则是使得对象能在几种状态之间切换。而`this.currentState`是 **重点**，表示当前的状态，值是`OfflineState`的实例或`OnlineState`的实例。从这里可以看出`OfflineState`的实例和`OnlineState`的实例必须实现`activate()`和`send()`这两个方法。

接下来我们看看两个状态的代码：

```js
// offlineState.js
const jot = require('json-over-tcp'); // [1]

module.exports = class OfflineState {

  constructor (failsafeSocket) {
    this.failsafeSocket = failsafeSocket;
  }

  send(data) { // [2]
    this.failsafeSocket.queue.push(data);
  }

  activate() { // [3]
    const retry = () => {
      setTimeout(() => this.activate(), 500);
    };

    this.failsafeSocket.socket = jot.connect(
      this.failsafeSocket.options,
      () => {
        this.failsafeSocket.socket.removeListener('error', retry);
        this.failsafeSocket.changeState('online');
      }
    );
    this.failsafeSocket.socket.once('error', retry);
  }
};
```
我们从上面的failsafeSocket.js里可以看到，我们是将failsafeSocket的实例作为参数传进OfflineState || OnlineState的，这时OfflineState || OnlineState把这个实例保存在了自己内部的`this.failsafeSocket`里面。然后实现了`send()`和`activate()`，离线状态时的`send()`就是把数据推进`queue`里，`activate()`就是每500秒不停地尝试重新连接服务器（其中连接的服务器host/port之类的配置在options里），如果连接上了，就`changeState()`把状态改为在线状态。

```js
// onlineState.js
module.exports = class OnlineState {
  constructor(failsafeSocket) {
    this.failsafeSocket = failsafeSocket;
  }

  send(data) { // [1]
    this.failsafeSocket.socket.write(data);
  };

  activate() { // [2]
    this.failsafeSocket.queue.forEach(data => {
      this.failsafeSocket.socket.write(data);
    });
    this.failsafeSocket.queue = [];

    this.failsafeSocket.socket.once('error', () => {
      this.failsafeSocket.changeState('offline');
    });
  }
};
```
在线状态时的`send()`就是直接把数据写进`socket`里了，注意这里的socket是一个Duplex Streams，既可读又可写。而`activate()`则是将离线时缓存在`queue`的数据也写入`socket`。同时监听`error`事件，当socket又连接不上服务器的时候，则又`changState()`状态为offline。

下面是这个failsafeSocket的一个使用示例，我们分别用这个socket来构建server和client
```js
// server.js
const jot = require('json-over-tcp');
const server = jot.createServer({
  port: 5000
});
server.on('connection', socket => {
  socket.on('data', data => {
    console.log('Client data', data);
  });
});

server.listen({
  port: 5000
}, () => console.log('Started'));
```

```js
// client.js
const createFailsafeSocket = require('./failsafeSocket');
const failsafeSocket = createFailsafeSocket({
  port: 5000
});
setInterval(() => {
  // 每隔1000毫秒发送当前内存使用状态
  failsafeSocket.send(process.memoryUsage());
}, 1000);
```
测试时，可以启动server.js再启动client.js，之后将server.js重启来观察state变化时功能的变化。

## Template（就是模板这个词的意思）

我们在很多的场景下也会提到模板，做PPT的时候，套个精美的模板，然后把需要改的地方标题内容什么的改一下，完成。用Vue的时候把组件的模板写好，会变动的地方则用{{this.state.data}}代替。总而模板就是一个框架，其中有部分地方需要我们具体去实现。理解以下的示意图：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/design-pattern-part2/template.png)

其中Template的`foo()`、`bar()`就是模板中那些不变的地方，而`templateMethod()`就是我们需要具体去实现的地方。对于Template里的这个`templateMethod()`，我们需要一个类似`占位符`之类的东西来替代。在C++中，可能是一个抽象函数或虚函数，表明子类继承Template时需要具体的`templateMethod()`实现。在JavaScript中，则是将他变成一个未定义方法或者总是抛错new Error('需要实现templateMethod')的方法来实现这个模式。

我觉得这里Template模式和Strategy模式的适用场景也太像了。试想一下我们在Strategy购物车支付场景，用户选择不同的支付方式，也可以是Template这里的templateMethod()来实现。

我们这里通过Template模式再一次实现我们在Strategy模式中实现的Config来比较二者的异同。

```js
// ConfigTemplate.js
const fs = require('fs');
const objectPath = require('object-path');
class ConfigTemplate {
  read(file) {
    console.log(`Deserializing from ${file}`);
    this.data = this._deserialize(fs.readFileSync(file, 'utf-8'));
  }
  save(file) {
    console.log(`Serializing to ${file}`);
    fs.writeFileSync(file, this._serialize(this.data));
  }
  get(path) {
    return objectPath.get(this.data, path);
  }
  set(path, value) {
    return objectPath.set(this.data, path, value);
  }
  _serialize() {
    throw new Error('_serialize() must be implemented');
  }
  _deserialize() {
    throw new Error('_deserialize() must be implemented');
  }
}
module.exports = ConfigTemplate;
```
具体各个函数的功能我们上面讲过了，这里不同的地方在于我们不再使用this.strategy.serialize来完成`save()`和`read()`的具体实现，而是交给内部的templateMethod也就是这里的`_serialize`。上面的文件只是模板，没办法直接用。我们现在看看我们怎么来“套模板”。

```js
// jsonConfig.js
const util = require('util');
const ConfigTemplate = require('./configTemplate');
class JsonConfig extends ConfigTemplate {
  _deserialize(data) {
    return JSON.parse(data);
  };
  _serialize(data) {
    return JSON.stringify(data, null, ' ');
  }
}
module.exports = JsonConfig;
```
好了，我们现在通过套模板，提供_deserialize && _serialize的具体实现来完成一个真正可用具有完整功能的的JsonConfig。这个JsonConfig就是我们上面示例图里的ConcreteX，接着再测试一下我们写的代码
```js
//jsonConfigTest.js
const JsonConfig = require('./jsonConfig');

const jsonConfig = new JsonConfig();
jsonConfig.read('samples/conf.json');
jsonConfig.set('nodejs', 'design patterns');
jsonConfig.save('samples/conf_mod.json');
```
现在回想我们在自己实现一个Readable Streams时覆写的`_read()`，实现一个Writable Streams覆写的`_write()`等等，是不是觉得恍然大悟哈哈，这正是运用了模板模式。

## Command（分离操作的定义和调用）

Command模式是Node.js里一个很重要的设计模式，在其最通用的定义中，命令模式封装了主体对象信息，并对主体对象执行一个动作，而不是在主体对象上直接调用一个方法或一个函数，我们创建一个对象invocation执行这样一个 调用；那么实现这个意图将是另一个组件的责任，将其转化为实际行动。传统上，这个模式是围绕着四个主要的组件，如下图所示：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/design-pattern-part2/command.png)

Command模式的实现比较灵活，例如以下的模式：任务模式，也算是Command模式的一种简单版本。
```js
function createTask(target, args) {
  return () => {
    target.apply(null, args);
  }
}
```
关于Command模式有点类似于封装一个Command主体对象，在这个Command上面定义了Command被执行时具体的操作，但是Command内部只是定义而不去执行。至于执行则交给外部的Invoker去调用这些命令，也就是将执行一个操作，分离成操作的定义、操作的调用两部分。举个最简单的例子，就是将原本的
```js
target.apply(null, args);
```
分离成Command的定义（这里createTask函数是一个Factory，返回Command）
```js
function createTask(target, args) {
  return () => {
    target.apply(null, args);
  }
}
```
以及Command的调用（一个Command的调用器，不止针对单一Command）
```js
class Invoker {
  run(cmd) {
    cmd();
  }
}
```
最后在使用
```js
let invoker = new Invoker()
let command = createTask(target, args)
invoker.run(command)
```
我们发现饶了一大圈子，其是最后这行代码是和直接`target.apply(null, args);`是等价的。然而命令模式将业务的定义和调用的逻辑分开了。我们举一个比较复杂的例子来看看这样“脱了裤子放屁”绕了一大圈的好处。

我们看这个个例子，首先是下面的一个小对象statusUpdateService，他负责来向Twitter这样的服务发送状态更新
```js
const statusUpdateService = {
  statusUpdates: {},
  sendUpdate: function(status) {
    console.log('Status sent: ' + status);
    let id = Math.floor(Math.random() * 1000000);
    statusUpdateService.statusUpdates[id] = status;
    return id;
  },
  destroyUpdate: id => {
    console.log('Status removed: ' + id);
    delete statusUpdateService.statusUpdates[id];
  }
};
```
主要就是一个statusUpdates对象数据结构来存储更新的数据，另外sendUpdate可以往该数据结构中添加新的状态，destoryUpdate则可以删除某个状态。statusUpdateService这个对象的职责很像后端分层时的Service，是由他来负责具体的操作。

现在我们创建一个命令，这个命令本身表示新状态更新的发布（
同时提供撤销以及序列化的功能）：
```js
function createSendStatusCmd(service, status) {
  let postId = null;
  const command = () => {
    postId = service.sendUpdate(status);
  };
  command.undo = () => {
    if (postId) {
      service.destroyUpdate(postId);
      postId = null;
    }
  };
  command.serialize = () => {
    return {
      type: 'status',
      action: 'post',
      status: status
    };
  };
  return command;
}
```
`createSendStatusCmd`函数是一个Factory，调用这个函数时将生产`sendState`命令对象，这个命令实现了以下三个功能：
1. `command()`本身是一个函数，当调用它时，它将触发`statusUpdateService`对象上的操作
2. `command.undo()`函数，该函数恢复command本身操作产生的效果。在我们的例子中，我们只是调用目标服务上的destroyUpdate()方法。
3. `command.serialize()`函数，它构建一个json对象，该对象包含重建同一个命令对象所需的所有信息。 
在此之后，我们可以构建一个调用程序,完整代码如下：

```js
class Invoker {
  constructor() {
    this.history = [];
  }
  // 执行命令
  run(cmd) {
    this.history.push(cmd);
    cmd();
    console.log('Command executed', cmd.serialize());
  }
  // 延迟执行命令
  delay(cmd, delay) {
    setTimeout(() => {
      this.run(cmd);
    }, delay)
  }
  // 撤销执行命令产生的效果
  undo() {
    const cmd = this.history.pop();
    cmd.undo();
    console.log('Command undone', cmd.serialize());
  }
  // 远程服务器上执行命令
  runRemotely(cmd) {
    request.post('http://localhost:3000/cmd', {
        json: cmd.serialize()
      },
      err => {
        console.log('Command executed remotely', cmd.serialize());
      }
    );
  }  
}
```
我们可以看到在这个Invoker调用程序里面我们可以尽情地对Command提供的各种操作进行组合、调用。已完成我们想要的逻辑。之后我们的客户端可以用类似如下的方式来使用这个Command
```js
const invoker = new Invoker();
const command = createSendStatusCmd(statusUpdateService, 'HI!');
// 用户更新了Twitter 发了条'HI!'的状态
invoker.run(command);
```
当我们在客户端的逻辑里，假设犯了一个错误，想要撤销Command操作产生的影响，例如说像业务逻辑中，用户发了条Twitter状态，现在想撤回该状态，则
```js
invoker.undo();
```
用户决定延迟一个小时再发送这条状态
```js
invoker.delay(command, 1000 * 60 * 60);
```
或者，我们可以通过将任务迁移到另一台机器来分配应用程序的负载：
```js
invoker.runRemotely(command);
```
最后我觉得，只有找到十分充分的理由我们才应该使用Command模式，例如我们的某个操作，需要为他提供撤销、延迟、转换等等命令式的操作，我们才需要考虑引入这个花里胡哨的Command的模式，否则的话，这反而会使我们的代码绕了一个大弯子变得极其难以理解。

## Middleware（用过koa/redux的都懂）

关于Middleware模式，我不想再举一些demo来描述这种模式是什么。我想所有用过koa的同学都对洋葱模型、Koa的中间件系统等都有了解，另外,redux在处理action对象的时候也实现了一套中间件系统，例如像`redux-thunk`这样的中间件。因此这里就略过了，如果有不了解并且感兴趣的同学可以自行移步koa2/redux官方文档、相关参考资料去实际地了解Middleware模式。