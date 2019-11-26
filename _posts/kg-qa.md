# 一种基于知识图谱技术的简单智能问答系统实现

这篇文章看了中科院软件所刘焕勇老师的一个[小项目的源码](https://github.com/liuhuanyong/QASystemOnMedicalKG)后写出来的，可以看作是对该份源码的一些解读。该源码实现了医学领域的一个小型问答系统。但是该实现思路并不限于医学领域，只是以此为例。

## 可以达成的效果

### Q: 为什么有的人会失眠？

A: 失眠可能的成因有：躯体疾病和服用药物可以影响睡眠，如消化不良，头痛，背痛，关节炎，心脏病，糖尿病，哮鼻窦炎，溃疡病，或服用某些影响中枢神经的药物。
由于生活方式引起睡眠问题也很常见，如饮用咖啡或茶叶，晚间饮酒，睡前进食或晚饭较晚造成满腹食物尚未消化，大烟，睡前剧烈的体力活动，睡前过度的精神活动，夜班工作，白天小睡，上床时间不规律，起床时间不规律。
可能的原因有压力很大，过度忧虑，紧张或焦虑，悲伤或抑郁，生气，容易出现睡眠问题。
吵闹的睡眠环境，睡眠环境过于明亮，污染，过度拥挤。

### Q: 失眠有哪些并发症？

A: 失眠的症状包括：心肾不交；神经性耳鸣；咽鼓管异常开放症；偏执狂；十二指肠胃反流及胆汁反流性胃炎；腋臭黑斑；巨细胞动脉炎；Stargardt病；抑郁症；腔隙性脑梗死；甲状腺功能亢进伴发的精神障碍；紧张性头痛；胃下垂；虚；迷路震荡；口腔结核性溃疡；痰饮；游走性结节性脂膜炎；小儿脑震荡

### Q: 失眠的人不要吃啥？

A: 失眠忌食的食物包括有：油条；河蚌；猪油（板油）；淡菜(鲜)

## 知识图谱

从实际应用的角度可以将知识图谱理解为**多关系图**，多关系图一般包含多种类型的节点和多种类型的边。下图是一般的图结构与多关系图的区别。

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/kg-qa/mutilple-graph.png)

再看一个真实的医学领域知识图谱（橙色是疾病类型的结点,蓝色是食物类型的结点，高血压和小麦粥的关系是“recommand_eat”，绿色是检查类型的结点，膀胱镜和重复尿道的关系是“need_check”，以此可以真实体现多种类型节点和多种类型的边）

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/kg-qa/real-medical-kg.png)

## 开源项目QASystemOnMedicalKG的实现思路

1. 构建知识图谱

爬取寻医问药网数据，清洗整理数据后存入neo4j图数据库，例如以下截图，建立疾病类型的【失眠】节点，食物类型的【河蚌】【油条】等节点，建立两种节点的关系【no_eat】

[寻医问药网—疾病百科-失眠-忌吃食物](http://jib.xywy.com/il_sii/food/6866.htm)

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/kg-qa/xywy-shimian.png)

*该项目的知识图谱包含7类规模为4.4万的知识实体，11类规模约30万实体关系*

2. 用户问题NER和意图识别

- 输入输出
```python
user_query = "失眠的人不要吃啥？"
result = question_classifer(user_query) # question_classifer相当于做了意图识别和NER
# 得到的结果如下
result = { args: {'失眠':['disease','symptom']}, question_type: ['disease_not_food']} # 问题想问 疾病忌口
```

### question_classifer究竟是怎么实现的？

分为实体识别（NER）和意图识别两步

#### 实体识别NER

- 构建字典

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/kg-qa/dict.png)

收集7种医疗类型词条，用一个list将这7种类型的词条存在一起，类似如下数据结构

```python
medical_region_words = ['茶鸡蛋','白果鸡汤','上清丸','肢端肥大症','失眠'...]
```

- 构建AC自动机
```python
# 判断一个字符串“失眠的人不要吃啥？”里是否有一个字符串数组['茶鸡蛋','白果鸡汤','上清丸','肢端肥大症','失眠'...]中的字符，如果采用常规的遍历数组再在字符串中正则匹配的思路，当数组很大时效率将非常差，因此需要使用AC自动机
import ahocorasick
AC= ahocorasick.Automaton()
for index, word in enumerate(medical_region_words):
    AC.add_word(word, (index, word))
AC.make_automaton()
```

- 得到问句里面包含的医学领域词
```python
user_query = "失眠的人不要吃啥？"
result = AC.iter(user_query) # [(8,(4,'失眠'))]  (end_index, value)
```
*如果问句里面匹配到了 '失眠' '失眠抑郁' 两个医学领域词，我们默认取长词 ‘失眠抑郁’，因为我们默认更长的词是更精确地代表用户的需求，例如用户询问‘反流性食管炎怎么治疗？’时，'食管炎'和'反流性食管炎'都能匹配到医学领域词，然而显然，NER将疾病识别为'反流性食管炎'更精确代表用户的想法*

- 获取医学领域词的类别

上一步从用户的问句中提取了"失眠"这个词，这一步将"失眠"这个词，分别从check.txt、deny.txt、disease.txt、drug.txt、等那八个词典中去找，发现disease.txt和symptom.txt中都有这个词。
因此得到`args: {'失眠':['disease','symptom']}`

#### 意图识别

- 建立疑问词词典

```python
symptom_qwds = ['症状', '表征', '现象', '症候', '表现']
cause_qwds = ['原因','成因', '为什么', '怎么会', '怎样才', '咋样才', '怎样会', '如何会', '为啥', '为何', '如何才会', '怎么才会', '会导致', '会造成']
acompany_qwds = ['并发症', '并发', '一起发生', '一并发生', '一起出现', '一并出现', '一同发生', '一同出现', '伴随发生', '伴随', '共现']
food_qwds = ['饮食', '饮用', '吃', '食', '伙食', '膳食', '喝', '菜' ,'忌口', '补品', '保健品', '食谱', '菜谱', '食用', '食物','补品']
drug_qwds = ['药', '药品', '用药', '胶囊', '口服液', '炎片']
prevent_qwds = ['预防', '防范', '抵制', '抵御', '防止','躲避','逃避','避开','免得','逃开','避开','避掉','躲开','躲掉','绕开','怎样才能不', '怎么才能不', '咋样才能不','咋才能不', '如何才能不','怎样才不', '怎么才不', '咋样才不','咋才不', '如何才不','怎样才可以不', '怎么才可以不', '咋样才可以不', '咋才可以不', '如何可以不','怎样才可不', '怎么才可不', '咋样才可不', '咋才可不', '如何可不']
lasttime_qwds = ['周期', '多久', '多长时间', '多少时间', '几天', '几年', '多少天', '多少小时', '几个小时', '多少年']
cureway_qwds = ['怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治', '医治方式', '疗法', '咋治', '怎么办', '咋办', '咋治']
cureprob_qwds = ['多大概率能治好', '多大几率能治好', '治好希望大么', '几率', '几成', '比例', '可能性', '能治', '可治', '可以治', '可以医']
easyget_qwds = ['易感人群', '容易感染', '易发人群', '什么人', '哪些人', '感染', '染上', '得上']
check_qwds = ['检查', '检查项目', '查出', '检查', '测出', '试出']
belong_qwds = ['属于什么科', '属于', '什么科', '科室']
cure_qwds = ['治疗什么', '治啥', '治疗啥', '医治啥', '治愈啥', '主治啥', '主治什么', '有什么用', '有何用', '用处', '用途', '有什么好处', '有什么益处', '有何益处', '用来', '用来做啥', '用来作甚', '需要', '要']
```

- 结合医学领域词类型和问句中的疑问词判断意图

上一步NER得到问句中的医学领域词是`args: {'失眠':['disease','symptom']}`，类型是`['disease','symptom']`

问句： "失眠的人不要吃啥？" 包含的`吃`是 `food_qwds` 即食品疑问词，同时里面含有`不`字是`deny_words`

结合二者得到用户的意图是`question_type: ['disease_not_food']`,即询问疾病忌口,至此本阶段完成

3. 从知识图谱中获取相关数据

上一步，我们已经从用户的问句`"失眠的人不要吃啥？"`得到了以下格式的数据`{ args: {'失眠':['disease','symptom']}, question_type: ['disease_not_food']}`。

利用上面信息可以拼接图数据库查询语句

```SQL
MATCH (m:Disease)-[r:no_eat]->(n:Food) where m.name = '失眠' return m, r, n
```
结果如下：

![](https://raw.githubusercontent.com/caistrong/Blog/master/_posts/kg-qa/noteat_graph_shimian.png)


我们这里回答的内容只需要节点的名字
```SQL
MATCH (m:Disease)-[r:no_eat]->(n:Food) where m.name = '失眠' return m.name, r.name, n.name
```
m.name|r.name|n.name
-|-|-
失眠|忌吃|河蚌
失眠|忌吃|猪油（板油）
失眠|忌吃|油条
失眠|忌吃|淡菜(鲜)

4. 回答生成

程序通过针对不同的问题类型，定制相应的回答模板，将知识图谱中抽取的数据套进模板生成相应的回答。

```python
def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'disease_symptom':
            desc = [i['n.name'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}的症状包括：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit])) # self.num_limit = 20

        elif question_type == 'disease_cause':
            desc = [i['m.cause'] for i in answers]
            subject = answers[0]['m.name']
            final_answer = '{0}可能的成因有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        elif question_type == 'disease_not_food': # 我们的例子关注这个！
            desc = [i['n.name'] for i in answers] # ['河蚌','猪油（板油）','油条','淡菜(鲜)']
            subject = answers[0]['m.name'] # 失眠
            final_answer = '{0}忌食的食物包括有：{1}'.format(subject, '；'.join(list(set(desc))[:self.num_limit]))
        # ......
```

最终生成回答
```
失眠忌食的食物包括有：油条；河蚌；猪油（板油）；淡菜(鲜)
```

