# 信息安全技术-网络入侵技术原理

本文是一些常见的网络入侵技术的原理调研,包含下列内容

1. 端口扫描技术
2. 操作系统探测技术
3. 漏洞分析技术
4. 基于字典的口令破解技术
5. 缓冲区溢出攻击
6. 注入类型的攻击
7. 木马
8. 蠕虫病毒
9. 拒绝服务攻击
10. 钓鱼类型的攻击
11. 网络嗅探技术
12. 跨站攻击技术

## 端口扫描技术

- 原理

服务器上所开放的端口就是潜在的通信通道，也就是一个入侵通道，对目标计算机进行端口扫描，能得到许多有用的信息，进行端口扫描的方法很多，可以是手工进行扫描、也可以用端口扫描软件进行。扫描器通过选用远程TCP/IP不同的端口的服务，并记录目标给予的回答，通过这种方法可以搜集到很多关于目标主机的各种有用的信息，例如远程系统是否支持匿名登陆、是否存在可写的FTP目录、是否开放TELNET服务和HTTPD服务等。

扫描器能揭示一个网络的脆弱点。本身并不直接攻击网络漏洞，仅仅是发现目标机的弱点。漏洞扫描器探查远程服务器上可能存在的具有安全隐患的文件是否存在，它的socket建立过程和上面的端口扫描器是相同的，所不同的是漏洞扫描器通常使用80端口，然后对这个端口发送一个GET文件的请求，服务器接收到请求会返回文件内容，如果文件不存在则返回一个错误提示，通过接收返回内容可以判断文件是否存在。发送和接收数据需要使用函数send()和recv()，另外对流中存在的字符串进行判断需要使用函数strstr()，这除了需要具备socket函数库的知识以外，还需要一些有关string函数库的知识。

其中[Nmap](https://nmap.org/)软件就提供了端口扫描的功能

- 以下介绍两种常见的端口扫描技术：
1. TCP SYN扫描

TCP SYN扫描是Nmap默认的也是最受欢迎的扫描方式。其中SYN就是TCP连接建立时三次握手的第一次握手。扫描程序向目标机器发送一个SYN数据包，这时候如果目标机的该端口处于侦听状态，则会返回一个SYN&ACK数据包，如果目标端口没有处于侦听态，则返回一个RST，扫描程序根据返回的数据包来判断端口的状态。最后扫描程序发送一个RST信号来关闭连接过程。TCP SYN扫描被认为是"半开放式"的扫描，原因是扫描程序无须建立一个完整的TCP连接。同时这种扫描方式一般也不会在目标机器上留下记录。缺点是一般需要有root权限才能建立自己的SYN数据包

2. TCP connect()扫描

当TCP SYN扫描不可用时，TCP connect()扫描就是默认的TCP扫描，当用户没有root权限发送原始报文，或者扫描IPv6网络时，这也是一种基本的扫描手段。Nmap通过创建connect() 系统调用要求操作系统和目标机以及端口建立连接，而不像其它扫描类型直接发送原始报文。 这是和Web浏览器，P2P客户端以及大多数其它网络应用程序用以建立连接一样的 高层系统调用。它是叫做Berkeley Sockets API编程接口的一部分。Nmap用该API获得每个连接尝试的状态信息，而不是读取响应的原始报文。

当SYN扫描可用时，它通常是更好的选择。因为Nmap对高层的 connect()调用比对原始报文控制更少， 所以前者效率较低。 该系统调用完全连接到开放的目标端口而不是像SYN扫描进行 半开放的复位。这不仅花更长时间，需要更多报文得到同样信息，目标机也更可能 记录下连接。IDS(入侵检测系统)可以捕获两者，但大部分机器没有这样的警报系统。 当Nmap连接，然后不发送数据又关闭连接， 许多普通UNIX系统上的服务会在syslog留下记录，有时候是一条加密的错误消息。 此时，有些真正可怜的服务会崩溃，虽然这不常发生。如果管理员在日志里看到来自同一系统的 一堆连接尝试，她应该知道她的系统被扫描了。


- 参考资料

[端口扫描技术详解CSDN](https://blog.csdn.net/notbaron/article/details/53193354)

[Nmap官方文档/端口扫描技术](https://nmap.org/man/zh/man-port-scanning-techniques.html)

## 操作系统探测技术

- 原理

操作系统探测也是网络安全扫描中的一个重要组成部分，它是网络攻防研究的重点内容之一。在很多探测工具中都使用了此项技术来获得某些服务的标识信息，操作系统探测技术的发展也非常迅速，出现了很多技术，其中最具代表性的是Nmap的基于协议栈指纹的扫描。

常用的网络协议是标准的，因而从理论上讲各个操作系统的协议栈应该是相同的。但是，在实际情况中，各种操作系统的协议栈的实现存在细微的差异。这些差异称作网络协议栈的指纹。由于每个操作系统对于网络部分的实现不尽相同，虽然在一些核心功能上都是一样的，但有些细节可以区分，这样就为识别操作系统提供了条件。TCP/IP规范并不是被严格地执行，每个不同的实现将会拥有它们自己的特性，这样就为成功探测带来了可能。规范可能被打乱，一些选择性的特性被使用，而其他的一些系统则可能没有使用。某些私自对IP协议的改进也可能被实现，这就成为了某些操作系统的特性。

根据TCP数据包的响应来进行探测，它是依靠不同操作系统对特定TCP的不同反应来区分的。它们产生一组TCP和UDP请求发送到远程目标主机的开放端口或者未开放端口。远程主机响应的有用信息就会被探测工具接收到，然后对其进行分析。对TCP协议族来说，这些差异通常表现在数据包头的标志字段中，如窗口、ACK序号、TTL等的不同取值。通过对这些差别进行归纳和总结，可以比较准确地识别出远程系统的类型。

- 一些较为具体的探测方式

1. IP报文的TTL（Time To Live）是数据包的存活时间，表示一个数据包在被丢弃之前可以通过多少跃点。不同操作系统的默认TTL值往往是不同的。

2. IP报文的DF位（Don't Fragment）表示不分段的标志，在IP协议中设定，不同操作系统对DF位有不同的处理方式，有些操作系统设置DF位，有些不设置DF位，还有一些操作系统在特定场合设置DF位，在其他场合不设置DF位。

3. TCP报文的Window Size表示TCP接收或者发送窗口大小(流量控制中的滑动窗口大小)，它决定了接收信息的机器在收到多少数据包后发送ACK包，一个特定操作系统的默认Window Size基本是常数。

4. ACK序号也可以用来判断，不同的操作系统处理ACK序号时是不同的。如果发送一个含有FIN，PSH，URG的数据包到一个关闭的TCP 端口，大多数操作系统会把回应ACK包的序号设置为发送的包的初始序号，而Windows 系统则会发送序号为初始序号加1的ACK包。

5. 发送一个只有FIN标志位的TCP数据包给一个打开的端口，Linux等系统不响应，有些系统，例如 MS Windows、CISCO、HP/UX等，发回一个RESET数据包。

6. 在SYN包的TCP头里设置一个未定义的TCP 标记，目标系统在响应时，有的会保持这个标记，有的不保持，还有一些系统在收到这样的包的时候会复位连接。

7. 还可以利用初始化序列号ISN来识别，不同的操作系统在选择TCP ISN时采用不同的方法。一些UNIX系统采用传统的64K递增方法，较新的Solaris,IRIX,FreeBSD,Digital UNIX,Cray等系统采用随机增量的方法，Linux 2.0、OpenVMS、AIX等系统采用真随机方法。Windows系统采用一种时间相关的模型。还有一些系统使用常数

8. 在做IP包的分段重组时，不同的操作系统处理方式不同。有些操作系统会用新IP段覆盖旧的IP段，而有些会用旧的IP段覆盖新的IP段。不同的操作系统有不同的默认MSS值，对不同的MSS值的回应也不同。

9. 根据ICMP报文响应分析，由于很多操作系统对于ICMP报文的响应不尽相同，这样就可以利用ICMP报文进行探测，可以发送正常的ICMP报文或者非正常的ICMP报文，观察目标主机的响应，分析相应的结果。

10. 在发送ICMP错误信息时，不同的操作系统有不同的行为。RFC 1812建议限制各种错误信息的发送率，有的操作系统做了限制，而有的没做。RFC 规定ICMP错误消息可以引用一部分引起错误的源消息。在处理端口不可达消息时，大多数操作系统送回IP请求头外加8 字节。Solaris 送回的稍多，Linux 更多。有些操作系统会把引起错误消息的头做一些改动再发回来。例如，FreeBSD、OpenBSD、ULTRIX、VAXen等会改变头的ID。**这种方法比较有用，甚至可以在目标主机没有打开任何监听端口的情况下就识别出Linux和Solaris。**

11. 对于ICMP端口不可达消息，返回包的服务类型(TOS)值有时也是有差别的。

- 实践

当我们的系统装有Nmap软件时，我们可以通过
```bash
sudo nmap -v -Pn -O 192.168.0.63
```
这样一行命令，来对目标机进行探测。我们可以运行结果看到类似如下的结果。
```bash
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.6
Uptime guess: 0.324 days (since Sun Apr 23 08:43:32 2017)
```
Nmap内部使用了我们上述的操作系统探测技术来得到上面的结果

- 参考资料

[操作系统探测技术](http://book.51cto.com/art/200907/134998.htm)
[用 NMAP 探测操作系统](https://linux.cn/article-8656-1.html)

## 漏洞分析技术

- 背景

软件漏洞分析是信息安全和软件质量保障的重要手段,分析工作的开展通常与软件生命周期紧密地结合在一起:(1)在设计阶段,进行软件架构的安全性分析,了解软件架构中存在的安全威胁,由此发现设计错误,以尽早消除安全隐患;(2)在开发阶段,进行源代码的安全性分析,了解代码自身存在的固有问题,由此发现编码缺陷,以弥补编码的不足;(3)在测试阶段,进行可执行代码的安全性分析,了解软件在实际运行中可能出现的安全问题,由此发现运行故障,以采取相应措施补救.

- 五类漏洞分析技术

软件漏洞分析划分为软件架构分析技术、代码静态分析技术、代码动态分析技术、动静结合的分析技术和漏洞定位技术等五类。

软件架构分析技术是对软件的架构设计进行分析，发现违反安全属性的设计错误后反馈给设计人员进行修改。代码静态分析技术和代码动态分析技术的分析对象是源代码或可执行代码，分析过程中需要辅以相应的分析规则，输出可能的安全漏洞;有时为了提高效率和准确度，需将两者结合使用;漏洞定位技术主要对是漏洞进行追踪定位等分析，由此确定漏洞的位置、可利用性等属性。上述各类技术构成了一个完整的体系，能够针对软件的不同形态完成漏洞的发现和分析工作。

- 参考资料

[软件漏洞分析技术进展](http://or.nsfc.gov.cn/bitstream/00001903-5/93867/1/1000004896719.pdf)

## 基于字典的口令破解技术

- 原理

基于字典的口令破解技术其实就是同构分析用户群体的心理结合人类的性格习惯，生产密码字典，然后通过不停地"试"的方式暴力破解。密码能否被破解的关键在于字典是否足够强大。

- hydra

hydra是著名黑客组织thc的一款开源的暴力密码破解工具，可以在线破解多种密码。

```bash
hydra -l root -P pass.txt ssh://192.168.15.131 -e nsr
```
其中pass.txt就是密码字典

- 参考资料

[黑客破解工具Hydra在线爆破密码](https://weibo.com/ttarticle/p/show?id=2309404130446836378480)

## 缓冲区溢出攻击

- 原理

顾名思义，缓冲区溢出的含义是为缓冲区提供了多于其存储容量的数据，就像往杯子里倒入了过量的水一样。通常情况下，缓冲区溢出的数据只会破坏程序数据，造成意外终止。但是如果有人精心构造溢出数据的内容，那么就有可能获得系统的控制权！如果说用户（也可能是黑客）提供了水——缓冲区溢出攻击的数据，那么系统提供了溢出的容器——缓冲区。

缓冲区在系统中的表现形式是多样的，高级语言定义的变量、数组、结构体等在运行时可以说都是保存在缓冲区内的，因此所谓缓冲区可以更抽象地理解为一段可读写的内存区域，缓冲区攻击的最终目的就是希望系统能执行这块可读写内存中已经被蓄意设定好的恶意代码。按照冯·诺依曼存储程序原理，**程序代码是作为二进制数据存储在内存的**，同样程序的数据也在内存中，因此直接从内存的二进制形式上是无法区分哪些是数据哪些是代码的，这也为缓冲区溢出攻击提供了可能。

- 一个简单例子

```cpp
void fun(unsigned char *data)
{
    unsigned char buffer[BUF_LEN];
    strcpy((char*)buffer,(char*)data);//溢出点
}
```
这个函数是一个典型的栈溢出代码。在使用不安全的strcpy库函数时，系统会盲目地将data的全部数据拷贝到buffer指向的内存区域。buffer的长度是有限的，一旦data的数据长度超过BUF_LEN，便会产生缓冲区溢出。

由于栈是低地址方向增长的，因此局部数组buffer的指针在缓冲区的下方。当把data的数据拷贝到buffer内时，超过缓冲区区域的高地址部分数据会“淹没”原本的其他栈帧数据，根据淹没数据的内容不同，可能会产生不同程度的风险。

如果在data本身的数据内就保存了一系列的指令的二进制代码，一旦栈溢出修改了函数的返回地址，并将该地址指向这段二进制代码的其实位置，那么就完成了基本的溢出攻击行为。

- 参考资料

[缓冲区溢出攻击](https://www.cnblogs.com/fanzhidongyzby/p/3250405.html)

## 注入类型的攻击

这里介绍SQL注入、XSS攻击两种注入类型攻击

### SQL注入

- 原理

首先从业务开发中的构造动态字符串说起，构造动态字符串是一种编程技术，它允许开发人员在运行过程中动态构造SQL语句。开发人员可以使用动态SQL来创建通用、灵活的应用。动态SQL语句是在执行过程中构造的，它根据不同的条件产生不同的SQL语句。当开发人员在运行过程中需要根据不同的查询标准来决定提取什么字段(如SELECT语句)，或者根据不同的条件来选择不同的查询表时，动态构造SQL语句会非常有用。

- 一个简单攻击例子

```php
$query = "SELECT * FROM users WHERE username = ".$_GET["name"];
```
这是一段很简单的服务器代码，其中$_GET["name"]是用户输入决定的一个变量。$query就是即将在数据库中执行的SQL语句，是我们准备注入攻击代码的目标语句。

有可能这行SQL代码出现在xmu.edu.cn/students这个接口中。

我们调用xmu.edu.cn/students?name=cai or wang

就会使得$query的SQL语句变为SELECT * FROM users WHERE username = cai or wang。这个SQL语句会被数据库执行

如果我们恶意注入一些攻击，删除数据库等等。将会造成更大的灾害。

### XSS

- 原理

XSS 全称“跨站脚本”，是注入攻击的一种。其特点是不对服务器端造成任何伤害，而是通过一些正常的站内交互途径，例如发布评论，提交含有 JavaScript 的内容文本。这时服务器端如果没有过滤或转义掉这些脚本，作为内容发布到了页面上，其他用户访问这个页面的时候就会运行这些脚本。

- 一个攻击例子

假设在一篇博客的评论下注入以下代码
```js
//用 <script type="text/javascript"></script> 包起来放在评论中
while (true) {
    alert("你关不掉我~");
}
```
以后访问该博客的其他用户就会不断弹出关不掉的弹出窗口

- 参考资料

[渗透攻防Web篇-SQL注入攻击初级](https://paper.seebug.org/15/)
[XSS和CSRF浅析](https://github.com/caistrong/Blog/issues/31)

防范注入类型攻击，不管是sql注入还是xss，关键在于 **不要信任用户输入**，要随时注意过滤用户输入。

## 木马

- 背景

木马病毒几乎是一个所有互联网用户都耳熟能详的名词，“木马” 程序是目前比较流行的病毒文件，与一般的病毒不同，它不会自我繁殖，也并不“刻意”地去感染其他文件，它通过将自身伪装吸引用户下载执行，向施种木马者提供打开被种者计算机的门户，使施种者可以任意毁坏、窃取被种者的文件，甚至远程操控被种者的计算机。一般而言，木马病毒会通过藏匿于正常的软件（互联网上各种盗版、破解版程序）中。

- 具体实现方式

我们知道在C/S架构中，Client端程序和Server端程序通过建立socket连接进行通信。一旦我们安装了Client端程序，并且赋予程序一定的权限，那么Client端就会和Server端程序进行通信，Server端程序可以获得部分对我们计算机的控制权。当C/S架构的软件是实用有效正版的软件时，我们授予软件对我们计算机的控制权能够满足我们的工作娱乐需求。这是正常的使用。从技术上而言，木马程序和提供正常服务的程序并没有不同。但是当我们安装了木马程序的Client并授予他一定的权限，他和木马程序的Server端进行的通信可能是对我们不利的。木马程序Server端的控制者甚至可以直接接管我们对计算机的控制。用于盗号、刷流量、释放其他病毒。

攻击者通常辅以诱惑性图标和名称来诱骗用户安装木马程序的Client端或者更甚者提供了具有正常功能的程序，但是随着该程序把木马代码也混入其中。例如前一阵子被爆料的黑客将“挖矿木马”植入了知名激活工具KMS，当用户下载安装此带毒工具后，挖矿木马也会入侵电脑，利用用户的电脑资源，为黑客“挖矿”赚钱。

- 参考资料

[木马，你好!](https://lellansin.wordpress.com/tutorials/hello_trojan/)

## 蠕虫病毒

- 原理

蠕虫病毒与一般的计算机病毒不同，它不采用将自身拷贝附加到其他程序中的方式来复制自己，所以在病毒中它也算是一个“另类”。蠕虫病毒的破坏性很强，部分蠕虫病毒不仅可以在因特网上兴风作浪，局域网也成了它们“施展身手”的舞台――蠕虫病毒可以潜伏在基于客户机/服务机模式的局域网的服务机上的软件内，当客户机访问服务机，并对有毒的软件实施下载后，病毒就神不知、鬼不觉地从服务机上“拷贝”到客户机上了。 

- 蠕虫病毒实现方式

```vb
Set objFs=CreateObject("Scripting.FileSystemObject") 
'创建一个文件系统对象 
objFs.CreateTextFile("C:\virus.txt", 1)
'通过文件系统对象的方法创建了一个TXT文件
```
如果我们把这两句话保存成为.vbs的VB脚本文件，点击就会在C盘中创建一个TXT文件了。倘若我们把第二句改为： 
```vb
objFs.GetFile(WScript.ScriptFullName).Copy("C:\virus.vbs")
```
就可以将自身复制到C盘virus.vbs这个文件。本句前面是打开这个脚本文件，WScript.ScriptFullName指明是这个程序本身，是一个完整的路径文件名。GetFile函数获得这个文件，Copy函数将这个文件复制到C盘根目录下virus.vbs这个文件。这么简单的两句就实现了自我复制的功能，已经具备病毒的基本特征――自我复制能力。

病毒需要传播，电子邮件病毒的传播无疑是通过电子邮件传播的。对于OutLook来说地址簿的功能相当不错，可是也给病毒的传播打开了方便之门。几乎所有通过OutLook传播的电子邮件病毒都是向地址簿中存储的电子邮件地址发送内同相同的脚本附件完成的。

要使病毒潜伏，对于“脚本”语言并不是很难的一件事，因为这种语言并不是面向对象的可视化编程，自然就不存在窗体，所以可以免去隐藏窗体的麻烦。从I love you病毒中，很容易看出蠕虫病毒在潜伏时的特点，它们多数是修改注册表等信息以判断各种条件及取消一些限制。

- 参考资料

[高手实例解析蠕虫病毒的原理](http://www.5dmail.net/html/2006-9-28/2006928135009.htm)

## 拒绝服务攻击

- 原理

拒绝服务攻击(Denial-of-Service Attack)亦称洪水攻击，是一种网络攻击手法，其目的在于使目标电脑的网络或系统资源耗尽，使服务暂时中断或停止，导致其正常用户无法访问。

分布式拒绝服务攻击(Distributed Denial-of-Service Attack)，是使用网络上两个或两个以上被攻陷的电脑作为 “僵尸” 向特定的目标发动 “拒绝服务” 式攻击。

受害主机在 DDoS 攻击下，明显特征就是大量的不明数据报文流向受害主机，受害主机的网络接入带宽被耗尽，或者受害主机的系统资源(存储资源和计算资源)被大量占用，甚至发生死机。前者可称为带宽消耗攻击，后者称为系统资源消耗攻击。两者可能单独发生，也可能同时发生。

- 一些具体的攻击方式

1. SYN FLOOD攻击

　　SYN FLOOD攻击是利用TCP协议的一些特性发动的，通过发送大量伪造的带有SYN标志位的TCP报文使目标服务器连接耗尽，达到拒绝服务的目的。要想理解SYN FLOOD的攻击原理必须要先了解TCP协议建立连接的机制。SYN FLOOD攻击就是在三次握手机制的基础上实现的。攻击者通过伪造IP报文，在IP报文的原地址字段随机填入伪造的IP地址，目的地址填入要攻击的服务器IP地址，TTL、Source Port等随机填入合理数据，TCP的目的端口填入目的服务器开放的端口，如80、8080等，SYN标志位置1。然后不停循环将伪造好的数据包发送到目的服务器。

2. ACK FLOOD攻击

　　ACK FLOOD攻击同样是利用TCP三次握手的缺陷实现的攻击，ACK FLOOD攻击利用的是三次握手的第二段，也就是TCP标志位SYN和ACK都置1，攻击主机伪造海量的虚假ACK包发送给目标主机，目标主机每收到一个带有ACK标志位的数据包时，都会去自己的TCP连接表中查看有没有与ACK的发送者建立连接，如果有则发送三次握手的第三段ACK+SEQ完成三次握手建立TCP连接；如果没有则发送ACK+RST断开连接。但是在这个过程中会消耗一定的CUP计算资源，如果瞬间收到海量的SYN+ACK数据包将会消耗大量的CPU资源使得正常的连接无法建立或者增加延迟，甚至造成服务器瘫痪、死机。

3. ...

- 参考资料

[拒绝服务攻击的常见类型](https://www.cnblogs.com/ssooking/p/7486227.html)

## 钓鱼类型的攻击

- 原理

网络钓鱼攻击（phishing与fishing发音相近）是最初通过发送消息或邮件，意图引诱计算机用户提供个人敏感信息如密码、生日、信用卡卡号以及社保账号的一种攻击方式。为实施此类网络诈骗，攻击者将自己伪装成某个网站的官方代表或与用户可能有业务往来的机构（如PayPal、亚马逊、联合包裹服务公司（UPS）和美国银行等）的代表。

- 具体策略

攻击者发送的通信内容的标题可能包含“iPad赠品”、“欺诈告警”或其他诱惑性内容。邮件可能包含公司的标志、电话号码及其他看似完全合法的内容。攻击者的另一惯用伎俩是使邮件看起来像是来自您的亲朋好友，让您以为他们要与你分享一些东西。

然而，当您点击了邮件中的链接，会被带到虚拟网站而非真实网站，让您在毫无戒备的情况下按照提示输入个人信息。攻击者会获取这些输入信息，然后立即使用或在黑市上买卖用于恶意目的，或既自用又出售。很多时候，用户计算机也会受到感染，然后将钓鱼邮件发送给通讯录上的联系人，助其肆意传播（恶意代码会控制受感染计算机的web浏览器，该攻击手段称为域欺骗。）

在传统钓鱼攻击中，这些诈骗者会发送数百万“鱼钩”，只需较少用户点击链接“上钩”。根据加拿大政府的统计，每日全球发送1.56亿封钓鱼邮件，而最终有8万用户点击邮件中的链接， 导致重大损失。Ponemon机构估计，通常拥有10000名员工的公司每年应对网络钓鱼攻击的花费就高达370万美元，而这种趋势没有减弱迹象，而是愈演愈烈。

- 参考资料

[网络钓鱼攻击定义及历史](http://blog.nsfocus.net/phishing-definition-history/)

## 网络嗅探技术

- 原理

嗅探器的英文写法是Sniff，可以理解为一个安装在计算机上的窃听设备它可以用来窃听计算机在网络上所产生的众多的信息。计算机网络嗅探器则可以窃听计算机程序在网络上发送和接收到的数据。可是，计算机直接所传送的数据，事实上是大量的二进制数据。因此, 一个网络窃听程序必须也使用特定的网络协议来分解嗅探到的数据，嗅探器也就必须能够识别出那个协议对应于这个数据片断，只有这样才能够进行正确的解码。很多的计算机网络采用的是“共享媒体"。 也就是说，你不必中断他的通讯，并且配置特别的线路，再安装嗅探器，你几乎可以在任何连接着的网络上直接窃听到你同一掩码范围内的计算机网络数据。我们称这种窃听方式为“基于混杂模式的嗅探”（promiscuous mode）

- 嗅探器如何工作

以太网的数据传输是基于“共享”原理的：所有的同一本地网范围内的计算机共同接收到相同的数据包。这意味着计算机直接的通讯都是透明可见的。

正是因为这样的原因，以太网卡都构造了硬件的“过滤器”这个过滤器将忽略掉一切和自己无关的网络信息。事实上是忽略掉了与自身MAC地址不符合的信息。

由于大量的计算机在以太网内“共享“数据流，所以必须有一个统一的办法用来区分传递给不同计算机的数据流的。这种问题不会发生在拨号用户身上，因为计算机会假定一切数据都由你发动给modem然后通过电话线传送出去。可是，当你发送数据到以太网上的时候，你必须弄清楚，哪台计算机是你发送数据的对象。的确，现在有大量的双向通讯程序出现了，看上去，他们好像只会在两台机器内交换信息，可是你要明白，以太网的信息是共享的，其他用户，其实一样接收到了你发送的数据，只不过是被过滤器给忽略掉了。

嗅探程序正是利用了这个特点，它主动的关闭了这个嗅探器，也就是前面提到的设置网卡“混杂模式”。因此，嗅探程序就能够接收到整个以太网内的网络数据了信息了

- 参考资料

[嗅探原理与反嗅探技术详解](http://netsecurity.51cto.com/art/200512/13152.htm)

## 跨站攻击技术

- 背景

CSRF 的全称是“跨站请求伪造”，而 XSS 的全称是“跨站脚本”。看起来有点相似，它们都是属于跨站攻击——不攻击服务器端而攻击正常访问网站的用户。CSRF 顾名思义，是伪造请求，冒充用户在站内的正常操作。其实XSS和CSRF并不是两种毫无关系完全对立的手段。XSS可以是实现CSRF诸多途径中的一条。

- 跨站脚本攻击示例

在一个有安全缺陷的博客系统中。将设博客后端web应用程序的开发者采用如下途径来设计删除博文的功能。
```html
//发送一个GET请求到'small-min.blog.com/delete?id=123'这个url
<a href="/delete?id=123">删除</a>
//后端收到这个GET请求后，验证这个请求带的cookie里面的session id是不是这个id为123博文的作者
//如果是的话，那就采取删除文章的操作
```
攻击者另外制作一个钓鱼网站（任意域名）里面有如下代码
```html
<a href='https://small-min.blog.com/delete?id=123'>开始测验</a>
```
这个时候假设博文的作者打开了钓鱼网站，并且点击了开始测验这个链接。浏览器就会发送一个GET请求给https://small-min.blog.com/delete?id=123 并且由于浏览器的运行机制。浏览器会一并把small-min.blog.com的cookie也带上去。服务端收到了这个请求，判断了cookie发现无误后就把这篇文章删除了。

- 参考资料

[XSS和CSRF浅析](https://github.com/caistrong/Blog/issues/31)