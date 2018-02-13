---
title: (递归分治)归并排序
date: 2018-01-27 22:08:18
tags:
    - 排序
categories:
    - 算法
    - js经典算法实现
---

自己实现的js归并排序算法

<!--more-->

```js
var a = [34, 203, 3, 746, 200, 984, 198, 764, 9];

function mergeSort(arr){
    if(! arr instanceof Array) return
    //这一句是关键
    //它意味着你必须把数组分到每个数组只有一个值
    //当arr.length<2就没办法再分成两份了
    if(arr.length<2) return arr

    let mid = Math.floor(arr.length/2)
    var leftArr = arr.slice(0,mid)
    var rightArr = arr.slice(mid)
    return merge(arguments.callee(leftArr),arguments.callee(rightArr))
}

//把两个已排好序的数组合成一个数组
function merge(left,right){
    //left和rigth是两个已经排好序的数组
    if(!left instanceof Array || !right instanceof Array) return

    var resultArr = []
    //当两边数组都还有数字
    while(left.length && right.length){
        //比较两边最小的一个元素
        if(left[0]<right[0]){
            resultArr.push(left.shift())
        }
        else{
            resultArr.push(right.shift())
        }
    }

    //到最后肯定是只有left剩或者只有right剩不能二者都剩
    while(left.length){
        resultArr.push(left.shift())
    }
    while(right.length){
        resultArr.push(right.shift())
    }

    return resultArr
}

console.log(mergeSort(a))
```