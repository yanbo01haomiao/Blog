# Node.js观察者模式

## 简介
首先厘清观察者模式的几个对象：

1. subject 主体(被观察者)
2. observer(listener) 观察者/监听者

观察者模式简而言之就是，当subject发生了状态的改变，可以去通知它的所有observer。

看起来和回调函数有点像，但是观察者模式更加强大，回调模式在使用传统的continuation-passing style的模式只能拥有一个回调函数，而观察者模式对于一个subject一般可以有多个观察者

对于传统的面向对象编程而言，实现观察者模式通常需要接口，还有具体类。而对于Nodejs而言，一切都变得简单得多，观察者模式是Nodejs内建在自己的核心之中的。我们可以通过EventEmitter这个类来实现对一个事件注册多个监听器，当事件触发时，监听器会得到执行。话不多说，我们来看看代码怎么实现。

```js
const EventEmitter = require('events').EventEmitter;
const eeInstance = new EventEmitter();
```

其中eeInstance实例主要有以下4个方法

- on(event, listener) : 给event这个事件注册一个监听器linstener
- once(event, listener) : 给event这个事件注册一个监听器linstener,当这个event事件第一次被emit(触发))之后移除该监听器
- emit(event, [arg1], [...]) : 触发一次event事件，**并传递一系列参数arg1、arg2...给注册在该事件上的监听器们**
- removeListener(event, listener) : 方法为event这个事件移除listener这个监听器可以视为on的逆操作

**所有前面所说的4个方法都将返回eeInstance实例以供链式调用**

## 组合式实践

我们通过一段小代码来看观察者模式实践的优雅之处：

```js
const EventEmitter = require('events').EventEmitter;
const fs = require('fs');

function findPattern(files, regex) {
    const emitter = new EventEmitter();
    files.forEach(function(file) {
        fs.readFile(file, 'utf8', (err, content) => {
            if(err)
              return emitter.emit('error', err);
            emmiter.emit('fileread', file);
            let match;
            if(match = content.match(regex))
              match.forEach( elem => emitter.emit('found', file, elem));
        });
    });
    return emitter;
}

// 函数使用示例
findPattern(['fileA.txt','fileB.json'], /hello \w/g)
    .on('fileread', file => console.log(`${file} was read`))
    .on('found', (file, match) => console.log(`Matched ${match} in file ${file}`)
    .on('error', err => console.log(`Error emitted: ${err.message}`))

```

我想这段代码应该无需任何文档就可以很容易看懂，首先我们在findPattern这个函数的实现上，思路就是，好我现在要做一堆事情，通常，这些事情应当是比较耗时的，在Nodejs里面会用异步来实现的。比如这里的readFile。另一方面，这些事情可能后续需求会需要变更，或者这个函数需要可扩展，比如说这里，findPattern本身不对找到的数据进行处理，反正我找到数据就使用emit发送出去，交给监听者去处理。我们发现处理数据的方式被交给了使用者。**其实这正是观察者模式的一大优越之处**。

想想在不使用观察者模式之前我们实现同样功能的代码可能会是：
```js
if(match = content.match(regex))
    match.forEach( elem => console.log(`Matched ${elem} in file ${file}`));
```
类似上面这样，把对数据的处理硬编码在了函数当中，如果findPattern在整个程序中只被像上面那样的使用示例被使用一次时，那自然是可以这样写的，如果不止一次，那我相信大家都会意识到使用观察者的模式更好。更好地解耦、消除模板代码、当需求变更时改动最少等等这些，我相信是所有设计模式的共同目标，这一点在我们这个简单的示例当中也得以体现。

另外需要注意几点：

1. 链式调用，我们可以发现在findPattern中，无论是`return emitter.emit('error', err);`还是`return emitter;`都返回了EventEmitter实例，这是为了方便链式调用。

2. 必须是异步逻辑，关于这一点，我想如果在findPattern的实现里，将`fs.readFile`替换为`fs.readFileSync`那么我们的调用示例将会失败，原因是，emit事件这个动作，发生在了我们为事件添加监听器之前了

3. 异常处理，当异常发生的时候，我们应当使用像在findPattern的实现里那样，将错误当作一个事件emit出来，以供在后面处理。如果直接在错误发生的地方抛出错误，那将会导致错误消失在事件循环里。所以对于任何EventEmitter实例都为它注册一个error事件监听器是一种最佳实践。

## 继承式实践
```js
const EventEmitter = require('events').EventEmitter;
const fs = require('fs');

class FindPattern extends EventEmitter {
    constructor (regex) {
        super();
        this.regex = regex;
        this.files = [];
    }

    addFile (file) {
        this.files.push(file);
        return this;
    }

    find () {
        this.files.forEach( file => {
            fs.readFile(file, 'utf-8', (err, content) => {
                if(err)
                    return this.emit('error', err);
                this.emit('fileread', file);
                let match = null;
                if(match = content.match(this.regex)) {
                    match.forEach(elem => this.emit('found', file, elem));
                }
            })
        })
        return this;
    }
}

const findPatternObject = new FindPattern(/hello \w+/);
findPatternObject
    .addFile('fileA.txt')
    .addFile('fileB.json')
    .find()
    .on('fileread', file => console.log(`${file} was read`))
    .on('found', (file, match) => console.log(`Matched ${match} in file ${file}`)
    .on('error', err => console.log(`Error emitted: ${err.message}`))
```

这段代码和上面的代码产生的效果是一致的，但使用的方式确实有比较大的差异的，说实话我自己本身也分辨不出二者优劣及使用场景。但是继承的方式在Nodejs的生态里呗广泛的时候。比如说`Server`和`Stream`现在你再回头去看看你熟悉的createServer()创建出来的对象，它身上的诸如listen()、close()什么的这些方法。应该会有所意会他其中所蕴含的观察者设计模式

