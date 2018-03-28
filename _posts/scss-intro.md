# SCSS初探

因项目需要学习SCSS，本文主要是学习语法，没啥干货。主要参照[Sass参考手册](http://sass.bootcss.com/docs/sass-reference/)

## 启动
安装
```bash
npm install sass-loader node-sass webpack --save-dev
```
配置loader
```js
// webpack.config.js
module.exports = {
  ...
  module: {
    rules: [{
      test: /\.scss$/,
      use: [{
          loader: "style-loader" // 将 JS 字符串生成为 style 节点
      }, {
          loader: "css-loader" // 将 CSS 转化成 CommonJS 模块
      }, {
          loader: "sass-loader" // 将 Sass 编译成 CSS
      }]
    }]
  }
};
```
[webpack sass-loader更多配置](https://doc.webpack-china.org/loaders/sass-loader/)

## 嵌套规则
```scss
#main p {
    color: #00ff00;
    width: 97%;
    
    .redbox {
        background-color: #ff0000;
        color: #000000;
    }
}
```
### 引用父选择符：&
> Sometimes it's useful to use a nested rule's parent selector in other ways than the default.

```scss
a {
  font-weight: bold;
  text-decoration: none;
  &:hover { text-decoration: underline; }
  body.firefox & { font-weight: normal; }
}
```

注：默认的嵌套规则下
```scss
a {
    hover {text-decoration:underline}
}
```
会被编译为
```scss
a hover {text-decoration:underline}
```
这不是我们想要的，因此&这个符号就是父元素的占位符，我们可以用此代替默认嵌套规则
### 嵌套属性
```scss
.funky {
    // 编译器层面与嵌套selector区别的关键点应该在 ":" 
    font: {
        family: fantasy;
        size: 30em;
        weight: bold;
    }
}
```
## SassScript
引入SassScript是为了让SCSS拥有诸如变量、算术、和函数之类的CSS没有的功能

### 变量：$
```scss
$primary-blue: #118BFB;
$fontSize: 14px;
```
```scss
.mt-btn {
    background-color: $primary-blue
    font-size: $fontSize
}
```
变量具有哪些数据类型可以到Sass参考手册里面看

## 运算：+ - * / %
重点关注下 "/"
```scss
p {
  font: 10px/8px;             // 纯 CSS，不是除法运算
  $width: 1000px;
  width: $width/2;            // 使用了变量，是除法运算
  width: round(1.5)/2;        // 使用了函数，是除法运算
  height: (500px/2);          // 使用了圆括号，是除法运算
  margin-left: 5px + 8px/2px; // 使用了加（+）号，是除法运算
}
```
结果
```scss
p {
  font: 10px/8px;
  width: 500px;
  height: 250px;
  margin-left: 9px; }
```
除了数字外，像颜色、字符串的值也可以计算

## @规则和指令
### @import
```scss
// 默认情况下，它会寻找 Sass 文件并直接引入
@import "utilities"; // 等同加了scss扩展名
@import "variable.scss";
```
### @media
媒体查询和CSS用法差不多，唯一的新能力是它可以被嵌套，如下
```scss
.sidebar {
  width: 300px;
  @media screen and (orientation: landscape) {
    width: 500px;
  }
}
```
### @extend
适用场景在于我们以往需要下面这种方式使用的情况（注意class）
```html
<div class="error seriousError">
  Oh no! You've been hacked!
</div>
```
用了@extend
```scss
.error {
  border: 1px #f00;
  background-color: #fdd;
}
.seriousError {
  @extend .error; //被定义在.error里的样式也将被应用于.seriousError
  border-width: 3px;
}
```
编译后
```scss
.error, .seriousError {
  border: 1px #f00;
  background-color: #fdd;
}

.seriousError {
  border-width: 3px;
}
```
### @mixin
一个典型的用例
```scss
@mixin large-text {
  font: {
    family: Arial;
    size: 20px;
    weight: bold;
  }
  color: #ff0000;
}
```
@mixin可以看作是一个类似"变量"的东西，存的是一串css规则。与@extend的不同之处在于@extend是按照css selector来作为"变量名"。这一点贴近"mixin"这个术语的含义（混入）
结合下面的@include使用
### @include
```scss
.page-title {
    @include large-text;
    padding: 4px;
    margin-top: 10px;
}
```
编译为
```scss
.page-title {
  font-family: Arial;
  font-size: 20px;
  font-weight: bold;
  color: #ff0000;
  padding: 4px;
  margin-top: 10px; }
```

## More
除了上面以外，SCSS还有很多高级特性。不过目前掌握这些应该已经够用了。
这篇文章里面SCSS和Sass混用，二者的区别在于，SCSS是兼容CSS的（单纯地把以前写的CSS文件后缀名直接改成.scss也能运行良好）。语法规则也比较CSS-like。简单说就这样了