# 高性能多模式字符串Aho-Corasick搜索

## 一个生动的例子

做业务的时候可能有时候会遇到类似以下屏蔽敏感词的需求
```js
const blackwords = ['卧槽', '尼玛', '滚粗', '...'] // 假设有几十万个敏感词
const user_comment = '你滚粗好吗?我去尼玛的'
const nicer_comment = purify(user_comment) // nicer_comment = 你**好吗？我去**的
```

一种比较容易想到的思路可能是

```js
// purify version 1
function purify(comment) {
    for(let blackword of blackwords) {
        const regex = new RegExp(blackword, 'g')
        comment = comment.replace(regex, '**')
    }
    return comment
}
```

这种实现的思路在blackwords非常少时没有任何问题。但是当blackwords非常多时（大搞文字狱），遍历一遍可能将非常耗时。
其他相似的需求当中，例如想从用户的输入中隐藏国家/地区，由于国家/地区差不多也就两百多个，所以基本上性能没有太大问题。然而当遇到诸如想从用户的输入中提取某一泛领域的词，例如想从用户输入中提取医学领域的词，包括所有疾病名字、药品名字等。这个词典可能有几十万个这样的量级。这时候遍历这个词典列表将非常耗时。

对于这种词典较庞大时的多模式字符串匹配的需求，有一种算法叫做Aho-Corasick非常流行，也经常被称为AC自动机。我们先看一下使用这个算法来实现purify

```js
// purify version 2
const AhoCorasick = require('ahocorasick');

const ac = new AhoCorasick(blackwords);

function purify(comment) { // comment = '你滚粗好吗?我去尼玛的'
    const acresults = ac.search(comment); // acresults = [ [ 2, [ '滚粗' ] ], [ 9, [ '尼玛' ] ] ] 2和9表示endIndex即匹配到该词的最后一个字符的索引位置
    const hits = acresults.reduce((acc,cur) => acc.concat(cur[1]),[]) // hits = ['滚粗','尼玛']
    const regexp = new RegExp(`${hits.join('|')}`, 'g') // regexp= /滚粗|尼玛/g
    const nicer = comment.replace(regexp, '**') //nicer = '你**好吗?我去**的'
    return nicer
}
```
步骤如下：
1. 首先由我们的词典生成一个AC自动机结构（更详细的步骤是先将我们的词典生成一个叫Trie树的结构，再由Trie树生成一个AC自动机的结构，这点后面会细说）
2. 之后我们用ac.search来匹配所有的字符串中是否包含了词典中的内容，如果有包含，那在该字符串中的索引是哪里等等。
3. 最后利用上一步信息将我们的原始输入替换为和谐后的输入

利用词典构建完一遍AC自动机后，后续每次的ac.search的时间复杂度将与词典的规模m无关，而只与待搜索的字符串长度n有关，时间复杂度为O(n)，当词典的规模m很大时这种算法的收益就更可观。

然而什么是Trie树，什么是AC自动机呢？ac.search是如何做到“高效”的？

## Trie树

Trie树，又叫字典树、前缀树(Prefix Tree)等，以词典['cod','code','cook','five','file','fat']构建一棵Trie树如下：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/aho-corasick/trie.png)
*橙色结点表示一个词的完结*

这种结构很经常用于搜索输入提示，应该看结构很容易能体会，与用户已输入的部分文字前缀匹配即可推断后续可能的输入。

## AC自动机

AC自动机差不多就是在Trie树的基础上，为**每一个**结点生成一个`Fail指针`,我们看一下以下由词典['abd','abdk', 'abchijn', 'chnit', 'ijabdf', 'ijaij']构建的AC自动树

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/aho-corasick/ac.png)

*红圈表示一个词的完结，虚线表示Fail指针的指向，部分结点无虚线则表示该节点的Fail指针指向根节点*

**某个节点的Fail指针的含义是：由根结点到该结点所组成的字符序列的所有后缀 和 整个目标字符串集合（也就是整个Trie树）中的所有前缀 两者中最长公共的部分**

针对上面关于Fail指针的含义，举几个例子说明一下：

- 'ijabdf'这串的d结点

对于d结点，他的由根结点到该结点所组成的字符序列为'ijabd'，这个序列的所有后缀有d、bd、abd、jabd这四个，在词典['abd','abdk', 'abchijn', 'chnit', 'ijabdf', 'ijaij']里的所有前缀所能找到的最长公共部分就是abd，因此这个d结点的`Fail指针`指向abdk的'd'节点

- 'abchijn'这串的h结点（Fail指针不一定是词典中词的最后一个结点）

对于h结点，他的由根结点到该结点所组成的字符序列为'abch'，这个序列的所有后缀有h、ch、bch这三个，在词典['abd','abdk', 'abchijn', 'chnit', 'ijabdf', 'ijaij']里的所有前缀所能找到的最长公共部分就是chnit中的ch，因此这个h结点的`Fail指针`指向chnit中的'h'结点

- 'abdk'这串的d结点（Fail指针是根结点的情况）

对于d结点，他的由根结点到该结点所组成的字符序列为'abd'，这个序列的所有后缀有d、bd这两个，在词典['abd','abdk', 'abchijn', 'chnit', 'ijabdf', 'ijaij']里的所有前缀找不到任何公共部分（没有以d或者bd开头的词），因此这个d结点的`Fail指针`指向null结点

到这里关于`Fail`指针的含义相信大家也了解了，整个AC自动机的数据结构大概大家也有底了，至于算法层面怎么由一个词典列表构建AC自动机这样的数据结构，大家可以在网上找到非常多的文章这里不多说了。

## AC自动机多模式匹配运行原理

上面我们构建了由词典['abd','abdk', 'abchijn', 'chnit', 'ijabdf', 'ijaij']构成的一个AC自动机

下面我们假设要在一个字符串“abchnijabdfk”中去找到词典中的词。这个需求与我们在开篇提到的屏蔽敏感词的需求基本是一致的。

以下给出这个过程的**伪代码**
```js
function search(str) {
    let result = []
    let curNode = rootNode 
    let char = firstCharOf(str)
    let needGetNextChar = false
    while(1){
        if(needGetNextChar){
            char = getNextChar(str); // 每次得到str的下一个字符，第一次是拿到的是
        }
        if(!char) break; // str里的字符全部拿完后跳出循环
        if(curNode.childNodes.include(char)){ //当前结点的子结点中有个结点是char记为nextNode
            if(curNode.isEnd === true || curNode.failPointerNode.isEnd === true){
                // 当前结点是一个单词结束or当前结点fail指向的结点是一个单词的结束
                result.push([getIndex(), getWord()])
            }
            curNode = nextNode
            needGetNextChar = true
        } else {
            if(curNode.failPointerNode === null) {
                curNode = rootNode
                needGetNextChar = true
            }else {
                curNode = failPointerNode
                needGetNextChar = false
            }
        }
    }
}
```

这个过程的文字版描述

1. 表示当前结点的指针指向AC自动机的根结点，即curNode = rootNode
2. 从文本串中读取（下）一个字符 char
3. 判断当前结点的所有孩子结点中有无与该字符char匹配的结点
- 若孩子结点中有nextNode是字符char:
    - 判断那个curNode或者curNode的failPointerNode是单词的结束，是的话记录下这个单词和索引
    - 将curNode移向nextNode,然后执行第2步
- 若孩子结点中无字符char:
    - 执行第4步
4. 判断curNode的failPointerNode是否是null
- 若failPointerNode是null, 执行步骤1
- 若failPointerNode不是null，将curNode置为failPointerNode，执行步骤3

选择**伪代码**或者**文字描述**的一种方式，对上面构建的AC自动机走一下"abchnijabdfk"这个字符串，整个流程如下图

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/aho-corasick/ac-walk.png)

走完这遍流程我们可能就很清楚地感受到了，AC自动机在多模式字符串匹配时只需要O(n)的复杂度了

## 彩蛋

上面我们实现了`purify version 2`，如果将其中purify改造为如下的版本

```js
// purify version 3
function purify(comment) { // comment = '你滚粗好吗?我去尼玛的'
    const regexp = new RegExp(`${blackwords.join('|')}`, 'g') // regexp= /卧槽|尼玛|滚粗|.../g
    const nicer = comment.replace(regexp, '**') //nicer = '你**好吗?我去**的'
    return nicer
}
```
亲测这个版本的代码也可以实现需求，然而这个版本的时间复杂度如何，完全依赖于[replace](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/String/replace)这个函数，底层引擎V8是如何实现。我没有看过源码，但是我倾向于猜测V8引擎已经利用过AC自动机对其性能经过优化。因为其实从逻辑上来讲，这不是一件太难的事情。大概用下面的方式即可实现
```js
String.prototype.replace = (regexp, '**') => {
    if(regexp.source.split('|').length > 10000){
        // 当需要正则匹配的词典数目非常多时，应该使用AC自动机来加速这个匹配过程
        ahocorasick()
    } else {
        // 正常遍历即可
    }
}
```
所以写出`purify version 2`这种代码的同学，有可能正印证了“聪明反被聪明误”那句话？哈哈哈
不过具体`purify version 2`和`purify version 3`两个版本的代码，在比较大的词典集下哪种方式效率更高，我并没有验证，感兴趣的同学可以用benchmark试一下。