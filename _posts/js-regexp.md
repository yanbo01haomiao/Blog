# JavaScript正则表达式

正则表达式非常非常有用，但是我一直以来都不太会写。今天就系统地学习一下。

## 正则表达式字面量

表达式字面量语法 
```js
//  /pattern/flags
const regex = /^[a-zA-Z]+[0-9]*\W?_$/gi
// 其中 
// ^[a-zA-Z]+[0-9]*\W?_$ 是pattern
// gi是flags
// 上面的字面量语法等价于
const regex = new RegExp(/^[a-zA-Z]+[0-9]*\W?_$/, "gi");
const regex = new RegExp("^[a-zA-Z]+[0-9]*\\W?_$", "gi");
// 其实就像字符串我们不常用new String，数组我们不常用new Array一样，正则表达式大部分时候我们也是用字面量语法来表达
```
## exec的信息
```js
var myRe = /d(b+)d/g;
var myArray = myRe.exec("cdbbdbsbz");
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-regexp/info.png)

对象| 属性或索引 | 描述 | 在例子中对应的值
----|-----------|-----|----------------
myArray | 值 | 匹配到的字符串和所有被记住的子字符串 | ["dbbd","bb"]
myArray |index| 在输入的字符串中匹配到的以0为开始的索引值 | 1
myArray |input| 初始字符串 | "cdbbdbdbz"
myArray |[0]| 整个模式匹配到的字符串（不是匹配后记住的哪个子字符串） | "dbbd"
myArray |[1]| 匹配后记住的子字符串| "bb"
myRe | 值 | 整个正则字面量 | /d(b+)d/g
myRe | lastIndex|下一个匹配的索引值。(这个属性只有在使用g参数时可用)|5
myRe | source | 模式文本。在正则表达式创建时更新，不执行。| "d(b+)d"

## 使用正则表达式的方法
使用正则表达式的方法常用的有两部分，一部分是RegExp的exec和test，另一部分是String的match、replace、search和split。

*下表来自MDN*

方法|描述
----|----
exec| 一个在字符串中执行查找匹配的RegExp方法，它返回一个数组（未匹配到则返回null）。
test|一个在字符串中测试是否匹配的RegExp方法，它返回true或false。
match|一个在字符串中执行查找匹配的String方法，它返回一个数组或者在未匹配到时返回null。
search|一个在字符串中测试匹配的String方法，它返回匹配到的位置索引，或者在失败时返回-1。
replace|一个在字符串中执行查找匹配的String方法，并且使用替换字符串替换掉匹配到的子字符串。
split|一个使用正则表达式或者一个固定字符串分隔一个字符串，并将分隔后的子字符串存储到数组中的String方法。

我们以/cai/这个pattern来看，这是一个很简单的pattern，只能精准匹配cai这个字符串
- exec
```js
/cai/.exec('caistrong')
/cai/.exec('caostrong')
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-regexp/exec.png)
- test
```js
/cai/.test('caistrong') // true
/cai/.test('caostrong') // falses
```

- match
```js
'caistrong'.match(/cai/)
'caistrong'.match(/cao/)
'caostrong'.match(/cai/)
```
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-regexp/match.png)
- search
```js
'caistrong'.search(/cai/) // 0
'caistrong'.search(/str/) // 3
'caistrong'.search(/cao/) // -1
```

- replace
```js
'caistrong'.replace(/cai/, 'CAI') // CAIstrong
'caistrong'.replace(/cao/, 'CAI') // caistrong
'caistrong caiweak'.replace(/cai/, 'CAI') // CAIstrong caiweak
'caistrong caiweak'.replace(/cai/g, 'CAI') // CAIstrong CAIweak
// 其实这里的第一个参数也不一定要是RegExp，也可以是String
'caistrong caiweak'.replace('cai', 'CAI') //CAIstrong caiweak
```

- split
```js
'caistrong'.split(/i/) // ["ca", "strong"]
// 同理这里的RegExp也能换成String，不过RegExp要比String功能丰富得多
'caistrong'.split('i') // ["ca", "strong"]
```

## pattern
关于pattern这部分我觉得是正则最核心也是最困难的部分，对于一个具体的需求而言，他所需要的pattern是什么，一般而言写了正确的pattern基本也就完成需求了。对于pattern而言，像上面那个/cai/中的这种精准简单匹配字符串非常直观，但是也没什么通用性，实际使用中往往可以直接被'cai'字符串替代，比较难的是如何使用一些特殊字符来表达一些更加通用的 **模式** ，这也是正则表达的所长。

*下表来自MDN的特殊字符表（我花费了很多时间整理加工，并将比较常用的字符做了灰底的展示）*

字符|含义
----|----
`\` | 转义，表示\后面的下一个字符将被特殊对待，具体怎么特殊视具体情况而定，/\d/表示匹配一个数字而不是字符'd'，/a\*/表示匹配'a*'而不是0或多个a（/a*/）
`^` | 匹配输入的开始，/^c/.test('cai')是true，而/^c/.test('xcai cai')是false，而/^c/m.test(\`xcai\ncai\`)是true
`$` | 匹配输入的结束，/g$/.test('caistrong')是true，而/g$/.test('strong cai')是false，同上g$/m.test(\`strong\ncai\`)是true
`*` | 匹配前一个表达式0次或多次，等价于{0,}，例如/cai*/匹配'caostring'和'caiiistring'前部
`+` | 匹配前一个表示式1次或多次，等价于{1,}，例如/cai+/匹配'caistrong'和'caiiistrong'的前部，但不匹配'caostrong'
`?` | 匹配前一个表达式0次或者1次，等价于{0,1}，例如/ca?i?/匹配'cstrong'，'castrong'和'cistrong'和'caistrong'
`.` | 匹配除换行符之外的任何单个字符。例如/ca./匹配'caostrong','caistrong'不匹配'ca'
`(x)` | 匹配x并且记住匹配项，括号被称为捕获括号。/(foo) (bar) \1 \1 \2/.test('foo bar foo foo bar')是true，\1有点像变量的意思。'bar foo'.replace(/(bar) (foo)/, '$2 $1')结果是'foo bar'，$2和$1也是用来替代匹配捕获到的字符串，这特别是在我们未知匹配到的内容时特别有用
`(?:x)` | 非捕获括号，使得你能够定义为与正则表达式运算符一起使用的子表达式。示例表达式/(?:foo){1,2}/如果表达式是/foo{1,2}/，则{1,2}将只对'foo'的最后一个字符'o'生效。
x(?=y) | 匹配'x'仅仅当'x'后面跟着'y'，这种叫做正向肯定查找。例如/cai(?=strong|weak)/，匹配'cai'仅仅当它后面跟着'strong或者weak'例如'caistrong','caiweak'，而'caiother'不匹配
x(?!y) | 匹配'x'仅仅当后面跟着不是'y'，这个叫正向否定查找。
`x|y` | 匹配'x'或者'y'，/cai|cao/匹配'caistrong'和'caostrong'
`{n}` | n是一个正整数，匹配前面一个字符 **刚好**发生了n次，/ca{2}i/匹配'caaistrong'不匹配'caistrong'
`{n,m}` | n和m都是整数，匹配前面的字符至少n次，最多m次。其中m可以省略。/ca{2,}/匹配'caaistrong'、'caaaaistrong'不匹配'caistrong'
`[xyz]` | 一个字符集合，匹配方括号中的任意字符，包括转义字符，可以使用短横杠-来指定一个范围，而点.和星号*这样的特殊符号在一个字符集中没有特殊意义。不必进行转译，但转义也起作用。例如/[a-z.]+/和/[\w.]+/都匹配'test.i.ng'中的的所有字符
`[^xyz]` | 一个反向字符集，匹配任何没有包含在方括号的字符,[^a-c]匹配'chop'中的h，上面的那个取反就是
[\b] | 匹配退格符backspace（U+0008）
\b | 匹配一个词边界，边界的内容长度是0，/\bs/匹配'cai strong'中的s但不匹配'caistrong'中的s。
\B | 匹配非单词的边界，/\B../匹配"noonday"中的'oo', 而/y\B../匹配"possibly yesterday"中的'yes'
\cX | 当X是处于A到Z之间的字符时，匹配字符串中的一个控制符
`\d` | 匹配一个数字，等价于[0-9],匹配"B2 is the suite number."中的'2'
\D | 匹配一个非字符，等价于[^0-9]
\f | 匹配一个换页符 (U+000C)。
\n | 匹配一个换行符 (U+000A)。
\r | 匹配一个回车符 (U+000D)。
`\s` | 匹配一个空白字符，包括空格、制表符、换页符和换行符，等价于[ \f\n\r\t\v\u00a0\u1680\u180e\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]。例如, /\s\w*/ 匹配"foo bar."中的' bar'。
\S | 匹配非空白字符，上面取反就是。例如， /\S\w*/ 匹配"foo bar."中的'foo'
\t | 匹配一个水平制表符 (U+0009)。
\v | 匹配一个垂直制表符 (U+000B)。
`\w` | 匹配一个单字字符（字母、数字或者下划线）。等价于[A-Za-z0-9_]。例如,/\w/ 匹配 "apple," 中的 'a'，"$5.28,"中的 '5' 和 "3D." 中的 '3'。
\W | 匹配一个非单字字符。等价于[^A-Za-z0-9_]。例如, /\W/ 或者 /[^A-Za-z0-9_]/ 匹配 "50%." 中的 '%'。
\n |在正则表达式中，它返回最后的第n个子捕获匹配的子字符串(捕获的数目以左括号计数)。比如 /apple(,)\sorange\1/ 匹配"apple, orange, cherry, peach."中的'apple, orange,' 。
\0 | 匹配 NULL (U+0000) 字符， 不要在这后面跟其它小数，因为\0是一个八进制转义序列。
\xhh | 与代码 hh 匹配字符（两个十六进制数字）
\uhhhh | 与代码 hhhh 匹配字符（四个十六进制数字）。
\u{hhhh} | (仅当设置了u标志时) 使用Unicode值hhhh匹配字符 (十六进制数字).

上面的表格其实是JavaScript Regular Expression的精华所在，但是想完全掌握并且灵活使用其实是需要经过训练实践的。比如我们有一个场景：
使用`/Chapter (\d+)\.\d*/`这个模式来匹配某个输入，例如字符串"Open Chapter 4.3, paragraph 6"。这个时候，根据上面的表格Chapter 4.3是会被匹配的。我们看/Chapter (\d+)\.\d*/.exec("Open Chapter 4.3, paragraph 6")的运行结果
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/js-regexp/chapter.png)
我们可以从运行结果中提取几乎我们想要的所有信息。其中因为加了捕获括号，所以我们拿到了4这个值，这往往很重要。

## flags

学习正则表达式的标志flags，我们首先也来看一下表格，flags可选的标志比较少

标志 | 描述
-----|-----
g | 全局搜索。
i | 不区分大小写搜索。
m | 多行搜索。
y | 执行“粘性”搜索,匹配从目标字符串的当前位置开始，可以使用y标志。

以g为例看一下标志的作用
```js
var patternG = /\w+\s/g
var pattern = /\w+\s/
var str = "fee fi fo fum"
str.match(patternG) // ["fee ", "fi ", "fo "]
str.match(pattern) // ["fee ", index: 0, input: "fee fi fo fum", groups: undefined]
patternG.exec(str) // ["fee ", index: 0, input: "fee fi fo fum", groups: undefined]
patternG.exec(str) // ["fi ", index: 4, input: "fee fi fo fum", groups: undefined]
patternG.exec(str) // ["fo ", index: 7, input: "fee fi fo fum", groups: undefined]
patternG.exec(str) // null
pattern.exec(str) // ["fee ", index: 0, input: "fee fi fo fum", groups: undefined]
pattern.exec(str) // ["fee ", index: 0, input: "fee fi fo fum", groups: undefined]
```
很明显，加了g就会全局搜索，会找到所有匹配模式的值，而不加g就永远只会找到匹配模式的第一个值。其余的标志作用这里就不细说了，以后有用到再慢慢体会。