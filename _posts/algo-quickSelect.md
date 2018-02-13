---
title: (递归分治)线性时间选择
date: 2018-01-27 22:09:57
tags:
    - 查找
categories:
    - 算法
    - js经典算法实现
---

自己实现的js快速选择算法

<!--more-->

```js
var a = [34, 203, 3, 746, 200];

function swap(arr,a,b){
    if(a==b) return //提高效率
    var tmp = arr[a]
    arr[a]=arr[b]
    arr[b]=tmp 
}
//寻找数组中第k小的数
//quickSelect查找arr从start到end中第k小的数
function quickSelect(arr,k,start,end){
    if(!arr instanceof Array || !k) return
    //如果没有解
    // if(end-start<=1) return arr[start]

    var left = typeof start != "number"?0:start,
        right = typeof end !="number"?arr.length-1:end
    
    var pivotIndex = right, 
        pivot = arr[pivotIndex],
        partitionIndex = left
    // swap(arr,pivotIndex,right)
    for(let i = left;i<right;i++){
        if(arr[i]<pivot){
            swap(arr,i,partitionIndex)
            partitionIndex++
        }
    }
    swap(arr,partitionIndex,right)

    //这个时候left的值就是pivot是第几小

    if(k-1==partitionIndex) return arr[partitionIndex]

    if(k-1>partitionIndex){
        arguments.callee(arr,k,partitionIndex+1,right)
    }else{
        arguments.callee(arr,k,left,partitionIndex-1)
    }

}

var v =quickSelect(a,2) 
console.log(v)

```