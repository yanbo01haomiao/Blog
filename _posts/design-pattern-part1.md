# Node.js设计模式（上）

## 背景

实话说，作为一个程序员，我想大家都或多或少听过设计模式这个词，当然还有备受推崇的Gang of Four(GoF)的那本书以及他们总结的23种设计模式。我觉得关于设计模式这个话题一个毋庸置疑的结论是，**不要囿于所谓的模式**。就现在部分动态语言而言，对于许多所谓设计模式其实也早就隐含在语言的特性之中。以及像函数式编程的发展等等都在打破这种所谓 **模式**。其实实话说，自己于此也没有太深刻的理解，但是我依然相信我们能从设计模式的学习中发掘出写出优秀代码的奥秘。因此我们学习设计模式的关注点应该在于其封装、解耦等"思想"而非生搬硬套"模式"。

## Factory（分离对象的创建和执行过程）

Factory模式解耦了对象的创建和执行过程，例如有一个类如下：
```js
//Profiler 用于在开发环境记录函数执行效率的对象
class Profiler {
  constructor(label) {
    this.label = label;
    this.lastTime = null;
  }
  start() {
    this.lastTime = process.hrtime();
  }
  end() {
    const diff = process.hrtime(this.lastTime);
    console.log(
      `Timer "${this.label}" took ${diff[0]} seconds and ${diff[1]}
           nanoseconds.`
    );
  }
}
```
我们在代码中使用类的时候可能会用下面这样的方式
```js
function getRandomArray(len) {
    const p = new Profiler(`生成${len}个随机数`)
    p.start()
    const arr = []
    for(let i=0; i<len; i++){
        arr.push(Math.random())
    }
    p.end()
}
```
这样的方式看来没有什么问题，但假设我们现在在getRandomString、getRandomObject等等好几个函数使用了这样的代码。现在假设当我们要将这个应用部署到生产环境，这时候我们不想将`console.log`这样的脏代码也部署上去，这时我们就只好一个个函数去删掉new Profiler这些逻辑，这样也导致了我们想在开发环境调试的时候又得把逻辑恢复，遇到这种开发和生产环境需要不同逻辑情况，我想大部分人都能想到用`process.env.NODE_ENV`来Branching代码，而这个Branching的逻辑加在哪里呢？

我们想到在构造Profiler的时候加入这个逻辑。如下
```js
// profilerFactory.js
module.exports = function (label) {
    if(process.env.NODE_ENV === 'development'){
        return new Profiler(label)
    } else if (process.env.NODE_ENV === 'production'){
        return {
            start: f=>f,
            end: f=>f
        }
    } else {
        throw new Error('忘了设置NODE_ENV了哦')
    }
}
```
将上面的
```js
const p = new Profiler(`生成${len}个随机数`)
```
更换为
```js
const profilerFactory = require('./profilerFactory.js')
const p = profilerFactory(`生成${len}个随机数`)
```

### 小结
我觉得Factory模式的精髓就在于 **分离对象的创建和执行过程**，我们或许很经常写出这样的代码，即创建对象的逻辑代码 和 对对象的使用（访问）的代码 混合在一起，当我们意识到这种 **混合**带来了维护或者可读性的问题时，就应该考虑使用Factory模式来解耦。但同时应该避免过度设计，如果这种对象的创建和对象的使用耦合在一起的代码还没让你觉得焦头烂额的时候你完全可以抱着`fuck off design pattern`的心态，过度设计，强行加一层没有卵用的Factory美名其曰应用了工厂模式到头来只是增加了代码的复杂度而已。通俗点讲就是脱了裤子放屁哈哈

## Revealing Constructor（只有构造函数能改变内部状态）

关于这个模式一个很典型的应用场景就是`Promise`,我们在构造Promise的时候会传入一个函数作为参数，这个函数参数称为executor。Promise内部的`constructor`会把自己内部的两个函数resolve和reject作为参数传递给executor，内部的这两个函数能够更改Promise对象的state，能将pending这种state改为fulliled或者rejected。而在executor之外的任何地方，我们都不能再更改Promise的状态了。

至于这个模式有什么用呢...我想Promise这样设计有他的道理..其他的应用场景我也不知道...我再举个用了类似模式的例子补充一下，创建一个只读的Event Emitter
```js
const EventEmitter = require('events')

module.exports = class Roee extends EventEmitter {
    constructor (executor) {
        super()
        const emit = this.emit.bind(this)
        this.emit = undefined
        executor(emit) // Promise的executor传递的就是resolve和reject
    }
}
```
额。这里的话对于Roee创造出来的对象，只能在exector里，也就是创建对象的时候emit event，其他时候就只能监听event了呢，所以就是read-only event emitter.

## Proxy （Controls Access to Subject）

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/design-pattern-part1/proxy.png)

> A proxy is an object that controls access to another object, called a subject

光看上面的话看不懂。可以结合下面的代码
```js
// createProxy
function createProxy(subject) {
  return {
    // 代理方法
    hello: () => (subject.hello() + ' world!'),
    // 委托方法
    goodbye: () => (subject.goodbye.apply(subject, arguments))
  };
}
```
我们可以看到，createProxy创造出来的代理对象，你可以访问这个对象的hello和goodbye方法，其实这两个方法真正去调用的是subject的两个方法，其中在proxy里还能插入自己的一些逻辑，比如加上一个` world!` 哈哈。总之这是符合上面的定义的controls access to subject。

关于Proxy模式的一个实际例子，创建logging Writable stream，也就是再每次我们写入一个流的时候，都将日志打印出来。
```js
// loggingWritable.js
// 使用这种模式来创建代理的一个缺点在于。我们虽然只想代理write方法，但却不得不手动委托剩下的其他方法
const fs = require('fs');

function createLoggingWritable(writableOrig) {
  const proto = Object.getPrototypeOf(writableOrig);

  function LoggingWritable(writableOrig) {
    this.writableOrig = writableOrig;
  }

  LoggingWritable.prototype = Object.create(proto);

  LoggingWritable.prototype.write = function(chunk, encoding, callback) {
    if(!callback && typeof encoding === 'function') {
      callback = encoding;
      encoding = undefined;
    }
    console.log('Writing ', chunk);
    return this.writableOrig.write(chunk, encoding, function() {
      console.log('Finished writing ', chunk);
      callback && callback();
    });
  };

  LoggingWritable.prototype.on = function() {
    return this.writableOrig.on
      .apply(this.writableOrig, arguments);
  };

  LoggingWritable.prototype.end = function() {
    return this.writableOrig.end
      .apply(this.writableOrig, arguments);
  };

  return new LoggingWritable(writableOrig);
}
```
这里我们override了write方法，在调用subject的write方法的基础上还加上了logging的逻辑，另外将on和end这两个方法简单地代理到了subject上。我们看看我们怎样使用这个类。
```js
const writable = fs.createWriteStream('test.txt');
const writableProxy = createLoggingWritable(writable);

writableProxy.write('First chunk');
writableProxy.write('Second chunk');
writable.write('This is not logged');
writableProxy.end();
```

看到上面的这个loggingWritable，我想起了，在《Spring in Action 4th》这本书里，我记得作者在讲Spring的AOP时，讲了一个例子，也类似说记录骑士这个类的一些行为的日志，不应该耦合在骑士这个类里。我觉得AOP也是代理模式的一个体现。同样还有就是我们会使用async_hooks这个node.js核心模块，为每一个后端请求诸如一个独一无二的requestId，方便问题的追踪，这也是代理模式的一种体现。

## Decorator（为对象的某一实例添加新方法）

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/design-pattern-part1/decorator.png)

不同于类的继承，然后在基类的基础上添加新的方法这样的逻辑，Decorator模式只为类的某一个而不是所有实例显示地增加新的方法。

代码如下：
```js
function decorate(component) {
    // new method
    component.greeting = () => {
        //...
    }
    return component
}
```

至于Decorator模式有什么作用呢，我这里举一个例子，假设我们有一个数据库db对象，我们现在想记录所有对db的更新操作，并且更新了的是`tweet`这种类型的记录。我们这里写一个插件，来做这个事情，听起来云里雾里的把，我们直接看代码

```js
// levelSubscribe.js
module.exports = function levelSubscribe(db) {
  db.subscribe = (pattern, listener) => {
    db.on('put', (key, val) => {  
      const match = Object.keys(pattern).every(
        k => (pattern[k] === val[k])
      );
      
      if(match) {
        listener(key, val);
      }
    });
  };
  return db;
};
```
我们这里暴露出的levelSubscribe的这个方法，其实就是decorate，和上面那个简单的例子一样。

我们这里为db这个对象新添加的方法就是subscribe这个new method，我们先不去管这个方法的实现，结合下面对这个db的使用将会更加明显。

```js
// levelSubscribeTest.js
const level = require('level');
const levelSubscribe = require('./levelSubscribe');

let db = level(__dirname + '/db', {valueEncoding: 'json'});

db = levelSubscribe(db);
db.subscribe(
  {doctype: 'tweet', language: 'en'},
  (k, val) => console.log(val)
);

db.put('1', {doctype: 'tweet', text: 'Hi', language: 'en'});
db.put('2', {doctype: 'company', name: 'ACME Co.'});

```
我们看到`db = levelSubscribe(db)`这行代码，其实就是在这里对db对象进行装饰的，经过装饰之后的db对象就拥有了subscribe这个方法。所以我们后面就使用了这个方法。

这个新方法的逻辑就是当db进行了put操作时，看看他是不是和pattern这个参数相匹配，是的话就console.log记录这条put操作，后面两次的put操作，很明显第一次会被记录。这个函数的逻辑其实是其次。重点在于我们通过装饰者模式，使得原本没有subscribe的db对象拥有了这个新的方法。

## Adapter（提供一个不一样的接口去调用Adaptee）

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/design-pattern-part1/adapter.png)


关于Adapter模式，这里我提供一个很完整的用例。背景如下：我们都知道fs是Node.js的核心模块，以及在浏览器端是无法直接读写磁盘文件的。假设现在我们使用Node.js编写了一个爬虫程序，这个爬虫程序爬取某个网站的数据并将它写入本地的磁盘文件中。那么目前该爬虫显然只能在Node.js端运行。那假设我现在想将该爬虫运行在浏览器端呢? 假设我们这里转变思路，将爬虫下来的数据存在LevelDB/IndexedDB等浏览器也能使用的持久化存储。这时我们就需要为LevelUP API做一个适配器，让其与fs模块兼容。

说了这么多，其实总结起来就是我们要实现，在浏览器端使用`fs.writeFile`的时候，实际上是调用了`db.put`就是了，以下贴出代码全文：
```js
// Node.js端爬虫程序的读写文件
const fs = require('fs');

fs.writeFile('file.txt', 'Hello!', () => {
  fs.readFile('file.txt', {encoding: 'utf8'}, (err, res) => {
    console.log(res);
  });
});

// 试图读取不存在的文件
fs.readFile('missing.txt', {encoding: 'utf8'}, (err, res) => {
  console.log(err);
});
```
上面这段代码没办法抑制到浏览器端直接运行，下面我们来写适配器
```js
// fsAdapter.js
const path = require('path');

module.exports = function createFsAdapter(db) {
  const fs = {};

  fs.readFile = (filename, options, callback) => {
    if (typeof options === 'function') {
      callback = options;
      options = {};
    } else if(typeof options === 'string') {
      options = {encoding: options};
    }

    db.get(path.resolve(filename), {
        valueEncoding: options.encoding
      },
      (err, value) => {
        if(err) {
          if(err.type === 'NotFoundError') {
            err = new Error(`ENOENT, open "${filename}"`);
            err.code = 'ENOENT';
            err.errno = 34;
            err.path = filename;
          }
          return callback && callback(err);
        }
        callback && callback(null, value);
      }
    );
  };

  fs.writeFile = (filename, contents, options, callback) => {
    if(typeof options === 'function') {
      callback = options;
      options = {};
    } else if(typeof options === 'string') {
      options = {encoding: options};
    }

    db.put(path.resolve(filename), contents, {
      valueEncoding: options.encoding
    }, callback);
  };

  return fs;
};
```
写完这段适配器代码后，我们在浏览器端将`const fs = require('fs')`简单地替换为
```js
const levelup = require('level');
const fsAdapter = require('./fsAdapter');
const db = levelup('./fsDB', {
  valueEncoding: 'binary'
});
const fs = fsAdapter(db);
```
我们的爬虫程序就可以在浏览器端运行了！

*Adapter和Proxy我觉得有一点类似的地方，主要区别我认为在于，Adapter为Subject提供了不同的接口，而Proxy是控制对Subject的访问，接口并没有转换*
