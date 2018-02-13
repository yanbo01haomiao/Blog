---
title: (贪心算法)活动安排问题
date: 2018-01-27 23:28:08
tags:
    - 贪心算法
categories:
    - 算法
    - js经典算法实现
---

自己写得js背包问题的贪心算法实现

<!--more-->

```js
//背包问题 的贪心选择算法
//
//0-1背包问题每个物品只有放和不放两种选择（可用动态规划方法求解）
//背包问题则可以放入一部分（可用贪心选择求解）

class Diamond {
    constructor(name,weight,value){
        this.name = name
        this.weight = weight
        this.value = value
    }
}

var diamonds=new Array(3)
diamonds[0]=new Diamond("碎-红宝石",5,20)
diamonds[1]=new Diamond("碎-蓝宝石",4,10)
diamonds[2]=new Diamond("碎-绿宝石",3,12)

function knapsackGreedy(diamondArr,c){
    if(!diamondArr instanceof Array) return
    if(!c) return

    let n = diamondArr.length

    diamondArr.forEach((element,index,array) => {
        Object.defineProperty(element,'valuePerWeight',{value:element.value/element.weight})
    });

    let sortedArr = diamondArr.sort((a,b)=>{
        if(a.valuePerWeight>b.valuePerWeight) return -1
        if(a.valuePerWeight<b.valuePerWeight) return 1
        return 0
    })

    let tempc = c,
        sumValue = 0,
        i=0
    while(tempc){
        if(tempc>sortedArr[i].weight){
            console.log("拿走了"+sortedArr[i].name)
            sumValue+=sortedArr[i].value
            tempc-=sortedArr[i].weight
        }else{
            console.log("拿走了"+tempc/sortedArr[i].weight+sortedArr[i].name)
            sumValue+=(sortedArr[i].valuePerWeight)*tempc
            tempc = 0
        }
        i++
    }
    
    console.log("总价值"+sumValue)
    
}

knapsackGreedy(diamonds,10)
```