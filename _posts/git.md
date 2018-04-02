# Git最终话

我接触git有一段时间了，实话说这应该不算太难的东西，不过在实习之前，对于git的使用，我基本上也就只有 `git add .`,`git commit -m 'msg'`、`git push`三连。对于自己开发的个人项目，并且把github当作云盘来用的话，这其实也差不多了。不过随着开始与人合作开发，对于git的要求就会开始深入，今天抽出点时间看了[<Pro Git 中文版2nd>](https://git-scm.com/book/zh/v2/)。希望能一举解决大部分git使用的问题，并作下此记录。

## git config
关于git的配置可以使用以下命令查看
```
git config --list
```
包括但不限于user.email、user.name、remote.origin.url等等信息都可以在此看到，具体配置的方法这里不赘述

## 仓库三种状态
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/git/git3.png)
> Git 仓库目录是 Git 用来保存项目的元数据和对象数据库的地方。 这是 Git 中最重要的部分，从其它计算机克隆仓库时，拷贝的就是这里的数据。（整个版本历史数据库）

> 工作目录是对项目的某个版本独立提取出来的内容。 这些从 Git 仓库的压缩数据库中提取出来的文件，放在磁盘上供你使用或修改。（你能看到的代码文件夹）

> 暂存区域是一个文件，保存了下次将提交的文件列表信息，一般在 Git 仓库目录中。 有时候也被称作`‘索引’'，不过一般说法还是叫暂存区域。（会在下次commit时提交到Git Repo的改动清单）

## 文件四种状态
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/git/git4.png)


使用以下命令查看文件状态（Unmodified的文件不显示，处于其余三种状态的文件都会显示）
```
git status
```

文件从工作目录到暂存区的`git add`以及从暂存区到Git 仓库的`git commit`我们都比较熟悉了。

>`git add` 是个多功能命令：可以用它开始跟踪新文件，或者把已跟踪的文件放到暂存区，还能用于合并时把有冲突的文件标记为已解决状态等。将这个命令理解为“添加内容到下一次提交中”而不是“将一个文件添加到项目中”要更加合适。

> 有时候我们提交完了才发现漏掉了几个文件没有添加，或者提交信息写错了。 此时，可以运行带有 --amend 选项的提交命令尝试重新提交：`git commit --amend`这个命令会将暂存区中的文件提交。 如果自上次提交以来你还未做任何修改（例如，在上次提交后马上执行了此命令），那么快照会保持不变，而你所修改的只是提交信息。

### git checkout
如果你在工作目录下修改了代码，但是现在突然想放弃你所做的修改，使用以下命令**(不可逆)**。
```
git checkout -- README.md
```
如果README.md现在已经在暂存区里，就会用暂存区的版本覆盖工作目录。如果不在暂存区，则会用git repo的最近一次commit覆盖工作目录

### git reset
`git reset`和上面的`git checkout`很容易混乱：
如果我们`git add`了一些文件到了暂存区域，现在我们想撤销`git add`操作，把文件从暂存区移除
```
git reset README.md
```
README.md 这个文件就会回到Untracked状态.
不带参数的`git reset`会从暂存区移除所有文件

除了撤销`git add`操作以外，`git reset`还能撤销`git commit`操作
```
git reset --soft HEAD~N
```
执行上述操作会撤销最后N次 commit 产生的效果并且保留 working directory 你所改动的内容。
```
git reset --hard HEAD~N
```
执行上述操作会撤销最后N次 commit 产生的效果并且**覆盖** working directory 你所改动的内容

至于也有点类似的`git rm`这个命令我没怎么用过，先略过。

### git log/git diff/git tag
`git log`可以查看commit提交历史，知道一下有-p、--graph、--stat...等选项来花式展示提交历史。这个命令就略过
`git diff`可以对比暂存区和工作目录、或者对比两次commit等等，不过现在一般有图形化工具可以使用，比如用vscode自带的工具来对比啥的。这个命令也略过
`git tag`似乎可以对commit打上标签。一般会用来打v1.2这样的版本标签。这个具体的也略过
## 远程仓库
在上面所有部分中我们都没有涉及远程仓库。远程仓库实际上可以看作是另一台计算机（git服务器）上存在着该git项目的另一个本地仓库。

### git remote
使用以下命令可以查看你已经配置的远程仓库服务器
```
git remote -v
```
添加远程仓库的命令如下
```
git remote add origin https://github.com/caistrong/Blog.git
```
origin可以换成任意你喜欢的名字

### git push/git pull
这两个命令是大家比较熟悉的命令，可以简要地说不管是git push还是git pull都是把本地的分支代码（例如master），因为我们使用了`git commit`为本地的master分支新增了许多commit。现在本地的代码已经新于远程的origin仓库的master分支代码，使用`git push origin master`可以把我们本地新的代码同步到远程origin仓库。另外，如果有人在我们push之前，push了代码到远程的origin仓库，我们的push就会被rejected。我们需要先`git pull`把远程别人的更新先同步到本地仓库。这时候有可能产生conflict，需要解决之后再push
**无论是git push还是git pull操作的都是git 仓库，不是暂存区也不是工作目录**

### git fetch
我以前几乎从来不使用`git fetch`命令，因为我不明白他是什么意思。对于`git pull`与`git fetch`的区别也只有别人告诉我的`git pull` = `git fetch` + `git merge`。这句话并没错，但是知道≠理解。我尝试解释一下`git fetch`的含义（先假设只有origin/master、master两个分支）

> 不管你使用`git clone`还是`git init` + `git remote add`。你的git 仓库都会和一个远程仓库(假设是origin)建立起连接，使用`git config --list`可以找到远程仓库的url。当你初次与远程仓库建立连接时（`git clone`或`git remote add`），你的本地仓库会存有一份此刻远程仓库所有分支的commits历史副本。你可以使用`git checkout origin/master`来检出到相应的远程分支。也就是本地仓库除了存有本地分支代码外，还存有远程所有分支代码的副本，不过本地的这些远程分支代码副本不是和远程仓库实时同步的。当有人push他们的新代码到远程仓库时，我们本地这些远程分支代码副本就会过期，此时我们使用git fetch就能更新远程分支代码的本地副本。而`git pull`则等同于`git fetch`更新远程分支副本之后，`git merge origin/master`将远程分支的更改合并到本地分支。就是把新的origin/master合并到本地master分支来。

## 分支
[<Pro Git>3.1Git分支](https://git-scm.com/book/zh/v2/Git-%E5%88%86%E6%94%AF-%E5%88%86%E6%94%AF%E7%AE%80%E4%BB%8B)
上面的Pro Git的一系列关于分支的文章既完整又形象地讲解了Git分支，还有工作流相关的知识。我只提取一个基本的流程进行记录。



我们有个新的git项目，第一次提交是C0，我们在master分支上开发，然后多次`git commit`来到C2，这时，我们项目想开发一个关于iss53的新功能，我们在C2的时候使用
```
git branch iss53
git checkout iss53
```
(相当于↓)
```
git checkout -b iss53
```
此刻iss53和master以及HEAD三个**指针**都是指向C2这个commit，然后我们开始开发iss53，假设我们又添加了代码，提交了新的commit C3。这时突然发现master分支上面又bug，需要紧急修复。所以我们使用
```
git checkout master
```
切回master分支，并修改了bug，然后提交了新的commit C4。
之后我们又切回iss53继续我们的新特性开发，这时又提交了commit C5，新特性开发完毕!
此刻我们的提交历史如下：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/git/gitbranch1.png)

最后我们又要切回master分支，完成最后的merge操作，将新特性合并到master分支来
```
git checkout master
git merge iss53
```
效果如下：
![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/git/gitbranch2.png)

合并的时候可能会产生冲突，像`git pull`遇到的冲突，实际上也是来源于merge这个操作。如果两个分支更改了同一行就会触发冲突。（git 完全就是靠行号来判断是否修改了同一行）。我们需要手动解决冲突，即手动确定保留哪个分支的代码。

完成合并之后还可以使用
```
git branch -d iss53
```
来删除一些不用了的分支

