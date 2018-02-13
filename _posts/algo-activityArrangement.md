---
title: (贪心算法)活动安排问题
date: 2018-01-27 23:25:35
tags:
    - 贪心算法
categories:
    - 算法
    - js经典算法实现
---

自己写得关于js贪心算法活动安排问题的实现

<!--more-->

```js
// 贪心算法 - 活动安排问题
// compareFunction()
function compareEndTime(a,b){
    if(a.endTime<b.endTime){
        return -1
    }
    if(a.endTime>b.endTime){
        return 1
    }
    return 0
}

// 贪心算法有两个基本要素
// 　 1.贪心选择性质
// 　  假设E是所有活动
// 　  那么A包含于E，且A是该活动安排问题的一个最优解
// 　  假设A的第一个活动是k
// 　  假设k = 1，那么A就是以贪心选择开始的最优解
// 　 假设k ≠ 1，那么设B = {A-{k}}∪{1} 即把A的第一个选择k去掉换成是1
// 　 在这个情况下 B 的数量等于 A-1+1
// 　 则B也是该问题的一个最优解
// 2.最优子结构性质
//    假设首先将1加进A中，即活动1是最优解的第一个活动
//    那么问题就变成了求E中所有与活动1相容的最大子集合
//    假设A是原问题最优解，那么A' = A - {1}就是新的问题
//    E' = {i∈E，si>f1} 即求剩下活动中的最大相容子集的最优解
//    反证法
//    假设A'不是这个新问题的最优解，这个新问题存在一个最优解B'且B'活动数大于A’
//    那么B'+{1} = B （B的活动数大于A） 的这个解也会是原问题 E 的最优解
//    自相矛盾
class Activity {
    constructor(start,end){
        this.startTime = start
        this.endTime = end
    }
}

var activities = new Array(12)

activities[5]=new Activity(1,4)
activities[11]=new Activity(3,5)
activities[4]=new Activity(0,6)
activities[3]=new Activity(5,7)
activities[1]=new Activity(3,8)
activities[9]=new Activity(5,9)
activities[7]=new Activity(6,10)
activities[8]=new Activity(8,11)
activities[6]=new Activity(8,12)
activities[10]=new Activity(2,13)
activities[2]=new Activity(12,14)

//这些活动已经按结束时间的非递减序排列好

function greedySelect(activityArr){
    var resultArr = []
    var currentEnd = 0
    activityArr.sort(compareEndTime).forEach(element => {
        if(element.startTime>currentEnd){
            resultArr.push(element)
            currentEnd = element.endTime
        }
    });
    return resultArr
}

console.log(greedySelect(activities))

```