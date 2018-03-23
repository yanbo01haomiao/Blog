# Unicode和utf-8与字符编码

字符编码常常是很多莫名其妙的坑的来源。对字符编码有一点了解应该也算是程序员的基本功。

我们都知道。在计算机的世界中，一切数据都是由高低电平分别代表1和0来存储的。所以我们的图片视频当然还有字符可以转化为0和1表示。比如这些试图用0和1进行艺术创作的人类[既然文件是以二进制方式存放在硬盘，那我能否通过二进制编码在自己的电脑上编出一部电影？](https://www.zhihu.com/question/27468258)

所以现在我们知道，我们计算机的一切存储，不管是内存闪存硬盘，上面所谓的数据，都只是一些1011100101010这样的东西，现在假设我们现在有一小块存储，上面存了一段数据（这段数据是高低电平的0和1，不是数字的0和1）

> 01101000 01100101 0110110 01101100 01101111 

此时此刻，这段数据可以有多种含义。我们可以用utf-8来解码，用jpeg、mp4来解码。

如果我们不指定解码规则直接读取这段数据(会以16进制显示)
```js
let fs = require("fs");
// 读取原始二进制内容
let buffer = fs.readFileSync("hello.txt"); 
console.log(buffer);
//<Buffer 68 65 6c 6c 6f>
```

我们也可以使用以下代码来用utf-8解码这串数据
```js
let fs = require("fs");
let text = fs.readFileSync("hello.txt", "utf-8"); 
console.log(text);
//hello
```

## 这里我们引出unicode和utf-8的区别

> unicode是字符集，也就是为每一个**字符（char）**分配一个码点(codepoint)
> utf-8是编解码规则，将码点(codepoint)转化为字节序列的规则，包括编码和解码

我们看看utf-8的编解码规则（左到右为编码，右到左为解码） 

Unicode符号范围 码点(hex) |        UTF-8编码方式（bin）
--------------------------|-------------------------------------
U+ 0000-U+ 007F | 0xxxxxxx
U+ 0080-U+ 07FF | 110xxxxx 10xxxxxx
U+ 0800-U+ FFFF | 1110xxxx 10xxxxxx 10xxxxxx
U+1 0000-U+10 FFFF | 11110xxx 10xxxxxx 10xxxxxx 10xxxxxx

所以现在我们看到上面那串数据，我们认为是它用utf-8进行编码的，所以我们对其用utf-8进行解码（vscode的reopen with encoding -> utf-8）。

utf-8是一种可变长度的编码。这时候我们上面的那串数据根据上表的编解码规则，都是由0开头的(符合0000 0000 ~ 0000 007F这个范围)。所以他的一个字节（8bit）代表一个字符（char）。所以0110 1000就对应1101000这个bin，转化为codepoint表示就是U+ 0068。[unicode codepoint to char](http://unicode.scarfboy.com/)查出其对应的字符就是'h'。按照这个规则一一解码，我们可以发现上面这串数据的以utf-8的格式就是'hello'

另一方面，编码的过程。

假设我们用vscode打开一个新的文件，并输入hello这五个字符，然后选择save with encoding -> utf-8。这样之后，我们的这个文件的数据其实就是以01101000 01100101 0110110 01101100 01101111 存储在计算机硬盘之中，下次我们想要查看这个数据的时候直接reopen with encoding -> utf-8。就可以看到这个字符串了。

到现在为止。一切都没有问题。甚至是，我们打开一个文件，输入一串英文字符串，使用gbk编码。但是之后打开的时候使用utf-8解码。也没有问题。问题就在于，我们如果写入中文，甚至是emoji然后用utf-8编码保存之后，下次打开使用gbk解码。这就出现问题了，也就是我们常说的**乱码**。

除了utf-8以外还有utf-16,utf-32等等编码而他们使用的字符集都是unicode。

我们大部分时候使用utf-8这种编码方式，现在差不多可以说utf-8已经是事实上的标准了。不过他仍然有一些缺陷，比如说对于utf-8，一个中文需要用3个字节表示

**U+4e00 - U+9fff** 这段的码点是属于中文的，所以比如我们在JavaScript中可以使用`/[\u4e00-\u9fff]/`这个RegExp来检测输入的字符是不是中文。例如
```js
/[\u4e00-\u9fff]/.test("我")  //true
/[\u4e00-\u9fff]/.test("I")  //false
```
从上面的unicode<->utf-8表格可以看到，中文需要3个字节。（utf-16和gbk编码规则中文都只需要2字节，所以有时候为了节省硬盘/流量。在中文世界里我们会使用gbk或utf-16来编码）

## 关于JavaScript字符串编码

在ES6之前，JavaScript的字符串以16位字符编码(UCS-2)为基础，每个16位序列(16bit)都是一个码元(code unit)。所以JavaScript的字符串的所有属性和方法都基于16位的码元，比如length属性与charAt()方法。这在之前不存在任何问题，因为对于UTF-16（UCS-2是16位固定编码，UTF-16是16或32位可变长度编码），像汉字和英文字符都是用16位表示都是一个码元。所以
```js
'我'.length  // 1
'I'.length   // 1
//length属性比较学术的说法就是这个字符串有几个码元
```

然而Unicode的明确目标是给世界上的每一个字符提供一个全局唯一的标识符（即上文所说码点code points），而16位的字符长度限制无法满足这一要求。所以UTF-16引入了代理对，通俗点说就是16位不够就用32位，所以后面的扩展字符会用2个code unit来表示一个code point。比如说emoji所对应的code point就需要4个字节也就是32位来表示。也就需要2个码元（code unit）

所以对于JavaScript
```js
'😄'.length  // 2
'😄'.charAt(0) //"?"
'😄'.charCodeAt(0) // 55357
```
ES5的这些基于UCS-2的固定编码的属性和方法都失效了

ES6 为全面支持 UTF-16 而新增了codePointAt() 方法。codePointAt()方法对于基本字符集来说和charCodeAt()一样，对于扩展字符集
```js
'😄'.codePointAt(0) //128561
```

#### 参考资料
[字符串与正则表达式](https://sagittarius-rev.gitbooks.io/understanding-ecmascript-6-zh-ver/content/chapter_2.html)
[文字编码的那些事](https://zhuanlan.zhihu.com/p/30950632)
[Unicode 和 UTF-8 有何区别？](https://www.zhihu.com/question/23374078)