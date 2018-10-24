# SAT-solver与数独问题

*这篇文章诞生于赖永炫老师的人工智能导论课下，关于本文的SAT-solver实现的具体算法，以及将数独问题转化为SAT问题CNF文件中的具体算法，这两个算法可能是该课程的精华，不过我都没有具体深入地去理解和研究。这篇文章就讲浅显表明不需要思考的东西，毕竟我就这副不求甚解的脸啊*

## 概述
NP完全问题是一类目前还没有找到在多项式时间内求解的问题。我们以一个被称为SAT的NP完全问题。尝试用多项式时间求解其近似解，完成一个叫做SAT-solver的求解器。当我们遇到其他NP完全问题，尝试将该NP完全问题转化为等价的SAT问题求解，再将SAT-sovler求解结果转化为原问题的解。

## SAT问题
SAT(Boolean Satisfiability Problem)问题，简单来说就是用来判断一组给定的布尔函数，是否可以找到一组变量赋值使其为真。

> a ∧ ¬b

当 a = true 而 b = false 时，上面的式子为true

而对于

> a ∧ ¬a

不存在使其为true的变量赋值

因此式子a ∧ ¬b 是satisfiable，而式子a ∧ ¬a是unsatisfiable

SAT问题是第一个被证明为NP完全问题的，因此，这也就意味着许多的NP完全问题，比如说电路可满足性问题(Circuit Satisfiability Problem)、四色问题(Four Color Theorem)都可以转化为SAT问题来解决。

## SAT问题求解

在讲SAT-solver之前，我们先了解业界处理SAT问题标准的输入格式CNF File Format（Dimacs format）

### CNF File Format（Dimacs format）

在讲这个格式内容之前我们先说一下什么是CNF

所谓CNF(conjunctive normal form)，中文翻译就是**合取范式**，我想学过离散数学的同学对这个概念都不陌生。对于任一布尔表达式，我们可以使用德摩根律和分配律将其转化为合取范式。

离散数学和理论计算机科学的中心(Dimacs)规定了CNF文件的输入格式，这个组织还规定了像图数据的输入格式[DIMACS_graph_format](http://lcs.ios.ac.cn/~caisw/Resource/about_DIMACS_graph_format.txt)之类的其他数据结构输入格式.

我们看一下以下这个cnf file
```cnf
c This is a comment
c This is another comment
p cnf 6 3
1 -2 3 0
2 4 5 0
4 6 0
```
与该cnf file对应的合取范式为
> (A v ¬B v C) ^ (B v D v E) ^ (D V F)
我们来看看这是怎么对应上的

首先c开头的两行是注释,忽略

> p cnf 6 3

p开头这行是一个关于问题的定义,现在这里是p cnf 6 3

其中6表示有6个变量,这里分别是A B C D E F在这之后分别对应于1 2 3 4 5 6这些数字

而3表示有3个clause,clause指的是合取范式里面的每一个子项,例如上面的式子有(A v ¬B v C)和(B v D v E)和(D V F)这三个子项

p开头这行之后,就剩3行数据,这三行数据分别表示的是每个子项的具体内容
1 -2 3 0代表的就是 (A v ¬B v C). 
*非用负号来表示,0表示每个clause的结束*

*上次我看图的数据时这里是p edge 3 5,表示有3个结点,5条边,之后就有5行数据表示这5条边分别连接的是哪两个结点.*

### 开源的CNF-SAT solver

关于SAT问题,网上有很多开源的求解器,我们只要提供上面一个CNF file format就可以得到求解结果

[MiniSat(JavaScript Version)](https://jgalenson.github.io/research.js/demos/minisat.html)是一个比较流行的SAT solver,我们进入这个在线的网站,试看看将上面的那个示例CNF file作为输入,验证一下求解结果.
```cnf
CPU time: 0.257s
SAT 1 -2 -3 -4 5 6
```
其中得到的结果为
A=true  B=false C=false D=false E=true F=true
代入那个问题合取范式(CNF)里面
> (A v ¬B v C) ^ (B v D v E) ^ (D V F)
得到整个CNF的结果为true,答案符合预期

如果对SAT-solver是怎么实现的很感兴趣可以参考[一个含有源码实现的SAT-solver demo](https://github.com/caistrong/Blog/blob/master/demos/sat-solver/main.js)

## 其他NP完全问题转化为SAT问题

我们先简单看将电路可满足性问题转化为SAT问题的大致思路，之后再以数独游戏的例子详细讲解。

### Tseytin Transformation

[Tseytin Transformation](https://en.wikipedia.org/wiki/Tseytin_transformation)就是将电路可满足性问题转化为CNF-SAT问题的转化方法。

对于电路可满足性问题，比如说一个与门，我们可以将其转化为一个合取范式(CNF)
![](./andgate.png)
可以看出，只有当A、B都为true时，C才为true能满足整个CNF为true。当A、B其中任一为false或者都为false时，C必须为false才能使得整个CNF为true。这满足与门的定义。

于是我们将电路可满足性问题成功转化为了CNF-SAT问题。

### 用SAT-solver求解数独问题

先看看最后的成果，上面是问题，0代表空着的未填的空格，下面是运行结果，填好的数独。
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/sat/result.png)

我们看看是怎么一步一步地得到这个结果的。其中涉及的代码都在[该文件夹下](https://github.com/caistrong/Blog/blob/master/demos/sudoku-sat/)

1. 给出数独问题的源文件，0代表空着代填的空格
*//problem文件*
```
200080300
060070084
030500209
000105408
000000000
402706000
301007040
720040060
004010003
```

2. 使用[sud2sat.py](https://github.com/caistrong/Blog/blob/master/demos/sudoku-sat/sud2sat.py)程序将该数独问题转化为等价的SAT问题

```bash
python sud2sat.py problem -minisat -extended=false
```
将会得到符合CNF File Format（Dimacs format）的output文件

```
p cnf 729 8859
2 0
44 0
57 0
96 0
124 0
152 0
157 0
174 0
194 0
218 0
243 0
271 0
...
```
其中变量个数有729个，表示的方式类似与S(x,y,z).例如S(4,5,8)表示第4行第5列填的数字是8，所以总共有9x9x9 = 729.至于clause的数字8859怎么算出来，是和数独的题目，以及数独游戏的几个规则限制决定的.我也没看太懂，如果对此感兴趣，可以参考[Sudoku as a SAT Problem](https://github.com/caistrong/Blog/blob/master/demos/sudoku-sat/Sudoku%20as%20a%20SAT%20Problem)这篇论文。

3. 使用SAT-solver求解该等价的SAT问题

我们这里依然使用上面用过的开源在线SAT-solver[MiniSat(JavaScript Version)](https://jgalenson.github.io/research.js/demos/minisat.html).
将output文件复制粘贴过去，solve之后得到结果存在solution_sat文件下

```
SAT -1 2 -3 -4 -5 -6 -7 -8 -9 -10 -11 -12 13 -14 -15 -16 -17 -18 -19 -20 -21 -22 23 -24 -25 -26 -27 -28 -29 -30 -31 -32 -33 -34 -35 36 -37 -38 -39 -40 -41 -42 -43 44 -45 46 -47 -48 -49 -50 -51 -52 -53 -54 -55 -56 57 -58 -59 -60 -61 -62 -63 -64 -65 -66 -67 -68 -69 70 -71 ...
```
这就是等价的SAT问题求解的答案

4. 使用[sat2sud.py](https://github.com/caistrong/Blog/blob/master/demos/sudoku-sat/sat2sud.py)将等价SAT问题的答案还原回原数独游戏的答案

```bash
python sat2sud.py solution_sat -minisat
```
最后在终端得到了我们上述得到的结果
```
2 4 5 | 9 8 1 | 3 7 6
1 6 9 | 2 7 3 | 5 8 4
8 3 7 | 5 6 4 | 2 1 9
- - - - - - - - - - -
9 7 6 | 1 2 5 | 4 3 8
5 1 3 | 4 9 8 | 6 2 7
4 8 2 | 7 3 6 | 9 5 1
- - - - - - - - - - -
3 9 1 | 6 5 7 | 8 4 2
7 2 8 | 3 4 9 | 1 6 5
6 5 4 | 8 1 2 | 7 9 3
```