---
title: (递归分治)二分查找
date: 2018-01-27 22:03:43
tags:
    - 查找
categories:
    - 算法
    - js经典算法实现
---

自己实现的js二分查找算法
<!--more-->

```js
var arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

function binarySearch(target, arr, start, end) {
    if (!target || !(arr instanceof Array)) return;

    var start = typeof start !== "number" ? 0 : start
    var end = typeof end !== "number" ? arr.length - 1 : end
    // var start = start || 0
    // var end = end || arr.length-1
    //这样的写法会报错，比如查找1，需要start,end都为0，如果end为0时 则会end又变成arr.length-1
    if (start > end) return -1

    var mid = Math.floor((end + start) / 2)
    if (target == arr[mid]) return mid

    if (target > arr[mid])  return arguments.callee(target, arr, mid + 1, end)
    else  return arguments.callee(target, arr, start, mid - 1)
}

//不存在
console.log(binarySearch(100, arr))

//存在
arr.forEach((item) => {
    console.log(binarySearch(item, arr))
})
```