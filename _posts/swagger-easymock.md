# 前后端分离工具实践(swagger和easy-mock)

在前后端分离的大背景下，关于前后端如何并行开发、接口文档的编写等等就带来了一些问题。

以我很有限的工作经验而言，大部分团队里面的前后端合作，接口文档或者是口头、或者是简单地编写一些word文档、markdown文档，同时更新到公司内部的wiki等方式，或者像阿里的RAP，使用开源的swagger生成文档。至于并行开发，也就是后端接口还没写好时前端怎么拿到模拟数据，则有的是在代码里写一些mock data，有的则是前后端沟通好数据格式之后，用mock.js这个包自己写一个mock server，而有的用到了大搜车的开源项目easy-mock。

我想以上各种各样的方式其实不分优劣，像swagger、easy-mock这样看起来高大上的解决方案其实也不一定是最合适的，有时候口头文档或者代码里随便造一点假数据这种看起来比较low的方式也不是不行。特别是那种只有一两个接口，前后端还坐一起或者自己本身是全栈哈哈，反正接口文档的管理还没出现太大麻烦的时候，去搞swagger和easy-mock这种比较"重"的工具纯粹吃力不讨好。技术大部分时候都不分高下，而主要还是在于场景是否合适。

## 由代码注释生成文档

这里推荐两个包，一个是apidoc，另一个是swagger-jsdoc.两者大同小异

### apidoc

一般在服务端代码里的在Router层（也可能是Controller层）里的接口上方，按照一定的规则[参照APIDOC](http://apidocjs.com/#example-basic)编写注释，如下的例子：

```js
/**
 * @api {get} /api/books/ 获取书籍信息接口
 * @apiName getbook 获取书籍
 * @apiGroup book
 *
 * @apiParam {Number} bookId 书籍Id
 * 
 * @apiSuccess {Number} code 状态码
 * @apiSuccess {String} message 消息
 * @apiSuccess {Object} data 数据
 *
 * @apiSuccessExample {json} 成功
 *     {
 *       "code": 0,
 *       "message": "success",
 *       "data": {
 *          "id": 100,
 *          "title": "Nodejs Design Pattern",
 *          "author": "xiaocongcai@tencent.com"
 *       }
 *     }
 *
 * @apiSuccessExample {json} 失败
 *     {
 *       "code": 1,
 *       "message": "can not find book"
 *     }
 */
router.get('/api/book', controller.getBookById);
```

然后使用命令行工具`apidoc -i src/router -o apidoc`之类的生成静态的apidoc网页，结果如下：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/swagger-easymock/apidoc.png)

### swagger-jsdoc

差不多也是在Router层的接口上面写好注释代码，如下：
```js
// swagger-jsdoc的注释代码

/**
 * @swagger
 * definitions:
 *   Book:
 *     type: object
 *     required:
 *       - title
 *     properties:
 *       title:
 *         type: string
 *       description:
 *         type: string
 */

/**
 * @swagger
 * /api/books:
 *    get:
 *      description: Returns all books
 *      produces:
 *        - application/json
 *      responses:
 *        200:
 *          description: An array of books
 *          schema:
 *            type: "array"
 *            items:
 *              $ref: '#/definitions/Book' 
 */
router.get('books', controller.getAllBooks);
```

同时下面是一个根据注释代码自动生成json数据格式的文档的代码，如下：
```js
// swagger-jsdoc.js     npm run swagger所执行的代码
const swaggerJSDoc = require('swagger-jsdoc')
const fs = require('fs')
const path = require('path')

const options = {
    definition: {
        info: {
            title: 'BookStore API',
            version: '1.0.0'
        },
    },
    apis: [
        path.join(__dirname, '../src/router/book_router.js')
    ]
}

const swaggerJsonPath = path.join(__dirname, '../dist/public/doc/swagger.json')
const swaggerSpec = swaggerJSDoc(options)

fs.writeFile(swaggerJsonPath, JSON.stringify(swaggerSpec), (err) => {
    if(err) throw err;
    console.log('swagger jsdocs generated!!')
})
```
```json
// package.json
{
  "scripts": {
    "swagger": "node bin/swagger-doc.js"
  }
}
```
然后我们写好接口后，或者每次更新了接口，就重新`npm run swagger`更新swagger.json这个文件，可以去swagger-ui下载html版的swagger可视化文档，然后将这个swagger.json数据导入，就可以像上面的apidoc一样生成类似的可视化文档，如下：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/swagger-easymock/swaggerdoc.png)

### 小结

无论是apidoc还是swagger-jsdoc。这两个工具概括起来的功能就是 **能根据代码注释自动生成好看的文档** 而已，所以我想大家自然知道什么时候需要他，我补充一些这个工具显而易见的好处：
1. 我们可以通过在代码中写一点注释，无侵入地生成好看的文档，省去我们使用markdown或者word排版文档的时间，简便易用。
2. 当我们修改了接口之后，可以顺便就在代码注释里把文档更新了，然后一行命令重新生成文档，代码和文档不分离，较容易保持同步。

## 为前端搭建Mock Server

我了解到的大概有三种方式，由轻到重的分别是，mock.js、swagger-tools、easy-mock。

### mock.js

这是一个轻量级的js库，大概的功能就是能够根据你指定的一些规则生成一些模拟数据，规则参见官网[mock.js示例](http://mockjs.com/examples.html)。其中也提供了一些方法来让我们快速搭建Mock Server...与其说是轻量级，其实倒不如说是可定制化、自由度较高的工具，我想，如果团队的开发实力较强的话，应该根据mock.js定制化一个适合自己团队的Mock Server工具，这是关于Mock Server我觉得最舒服的解决方案，使用示例如下：

```js
// node server（koa）
var Mock = require('mockjs')

router.get('/api/books', function (ctx, next) {
    var data = Mock.mock({
        // 属性 data 的值是一个数组，其中含有 1 到 10 个元素
        'data|1-10': [{
            'title': '@title',
            'description': '@sentence'
        }]
    })
    ctx.body = data
});
```
同时Mock.js还提供了在前端拦截Ajax请求的API
```js
 Mock.mock(/\/api\/books$/, 'get', {
        'data|1-10': [{
            'title': '@title',
            'description': '@sentence'
        }]//所有ajax地址以/api/books结尾的都被拦截，并且返回数据
    })
$.ajax({
    url: 'bookstore.com/api/books',
    dataType: 'json'
}).done(function(data, status, jqXHR){
    $('<pre>').text(JSON.stringify(data, null, 4))
    .appendTo('body')
})
```

### swagger-tools

上面我们讲到，使用swagger-jsdoc生成了一个json数据格式版的接口文档（为了简便，以下直接称swagger.json文件）。这个swagger.json文件，是很多swagger生态中工具的入口，我们上面讲到，我们可以根据这个swagger.json然后使用swagger-ui这个库生成好看的离线的代码文档页面。同样swagger-tools里的工具也是以这个swagger.json作为入口的。他提供了很多中间件，可以来帮助我们搭建一个Mock Server。
```js
// 使用swagger-tools和connect引入各种中间件代码的示例
const app = require('connect')();
const http = require('http');
const swaggerTools = require('swagger-tools');

let serverPort = 3001;

let options = {
  useStubs: true // turn on stubs (mock mode)
};

// The Swagger document (require it, build it programmatically, fetch it from a URL, ...)
let swaggerDoc = require('./swagger.json');

// Initialize the Swagger middleware
swaggerTools.initializeMiddleware(swaggerDoc, function (middleware) {
  // Interpret Swagger resources and attach metadata to request - must be first in swagger-tools middleware chain
  app.use(middleware.swaggerMetadata());

  // Validate Swagger requests
  app.use(middleware.swaggerValidator());

  // Route validated requests to appropriate controller
  app.use(middleware.swaggerRouter(options));

  // Serve the Swagger documents and Swagger UI
  app.use(middleware.swaggerUi());

  // Start the server
  http.createServer(app).listen(serverPort, function () {
    console.log('Your server is listening on port %d (http://localhost:%d)', serverPort, serverPort);
  });
});
```
我们发现在这里我们自己起了一个node app，这个node app提供访问文档的在线接口`localhost:3001/docs`，同时你可以访问Mock Server的各种API接口，他会返回模拟的数据，这里也能在在线文档那里可视化地request这些接口。不过模拟的数据总是一些固定的死数据，没有mock.js库提供的模拟数据那么丰富的变化。

这里提供一种可行的解决方案，后端在自己的Restful API Server主程序中，将`npm run apidoc`生成的swagger.json放到/dist/public/文件夹下，暴露给Mock Server获取，Mock Server里面动态地从Server主程序中去拿到swagger.json然后再生成Mock Server以及能在线查看的文档等等。这样一来，以后当Restful API Server的某个接口有变动，则后端程序员只需要在更改完接口的逻辑之后，将接口注释也改了，然后`npm run apidoc`重新生成一份swagger.json文件，Mock Server那边完全不用改，前端上Mock Server时就能看到更新的文档了。

这种解决方案是我目前想到的最方便的方案之一，同时文档、Mock数据的功能提供也和主业务逻辑的代码分离开在两个node app里了，二者唯一的关联则是Mock Server发起网络去请求API Server的swagger.json文件。也是符合关注点分离的思想之一的解决方案，唯一的缺点在于，生成的假数据没有办法像mock.js那么优雅，但是我觉得前端其实更看重的是返回的数据结构，至于数据本身是什么，可能就是美观度的问题而已，另外，对于列表数据，我目前还没找到方法，让Mock Server返回多条数据...我想这是实用的时候的一个大硬伤..

### easy-mock

easy-mock是杭州大搜车团队的一个开源作品，他集成了mock.js，同时也支持直接导入swagger.json，我觉得他就是一个加入了mock.js用来造数据的集成版swagger-tools，当然这个集成得我觉得比较完美。建议大家可以到他的官网[easy-mock](https://www.easy-mock.com/)去体验一下。上手也十分容易，这里我就不过多介绍使用方法了。总而言之算是一个做得还挺尽善尽美的Mock Server的工具了。

然而！还是存在着一定问题，主要在于，公司的内部使用的文档数据，一般应该是不允许外泄的，而你直接在easy-mock上创建项目，或者导入swagger.json，这都是在外网上的操作，直接把自己项目的文档都流到外网上去了。这肯定不行。目前的解决方法可能只能从github上去clone下easy-mock这个项目，同时在公司的内网自己搭建easy-mock服务器，这种途径的话应该是比较可行的，美团内部也搭了一个这样的服务器，然后问题就是这个搭建的成本，虽然可能也不太大，但是也需要一定的工作量，这里我不太好评估，毕竟我也没试过。不过这是一个一劳永逸的方法，可以尝试在组里或者部门里做推广。当然这是一个可定制化比较弱的方案，但是他足够方便，相比我们自己使用mock.js封装省了不少事，我们自己使用mock.js封装到最后可能也是一个和easy-mock八九不离十的东西，另外我觉得他也比swagger-tools那套东西要好用一点。
