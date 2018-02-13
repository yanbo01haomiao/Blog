---
title: (动态规划)矩阵连乘
date: 2018-01-27 23:14:52
tags:
    - 动态规划
categories:
    - 算法
    - js经典算法实现
---

自己实现的js动态规划矩阵连乘

<!--more-->

```js
//矩阵连乘问题

//helper
function creat2dArray(rows,columns){
    let resultArr=new Array(rows)
    for(let i=0;i<rows;i++){
        resultArr[i]=new Array(columns)
    }
    return resultArr
}


//矩阵如果想要能过相乘，他的长宽必须符合一定的条件
//矩阵A1xA2 则矩阵A1的宽必须为矩阵A2的长

//我们的TestCase
//  A=50×10，B=10×40，C=40×30，D=30×5
//answer A(B(CD))	10500


//我们用p数组来记录边长，4个矩阵有5个长
var p = [50,10,40,30,5]

//这一个数组用来存储最优值
//例如min2d[i][j]用来表示从第i矩阵到第j个矩阵需要经过的计算次数的最小值
//原问题可等价于求min2d[1][n]
var min2d;

//这个数组用来存储分割点
//mark[i][j]=k用来表示最优分割点
//mark[1][n]=4 则表示矩阵计算最后一步为(A1A2A3A4)(A5A6)
var mark;

function martixMultiply(pArr){
    let Mnum = pArr.length-1
    //数组从1开始用
    min2d=creat2dArray(Mnum+1,Mnum+1)
    mark=creat2dArray(Mnum+1,Mnum+1)
    //从第i个矩阵到第i个矩阵无需计算
    for(let i=1;i<=Mnum;i++){
        min2d[i][i]=0
    }
    //l表示连乘矩阵的数量，从两个矩阵相乘算上去，直到算到所有矩阵连乘
    //自底向上去求计算次数最小的最优值
    for(let l=1;l<Mnum;l++){
        // l表示间隔 Mnum个矩阵最多有Mnum-1个间隔
        //如果l是1，则需要计算12|23|34|45|56   5个值
        //如果l是2，则需要计算123|234|345|456  4个值
        for(let r=1;r<=Mnum-l;r++){
            //假设现在在计算A1A2A3A4连城  此时l=3
            //那么当然已知min2d[1][3]|和min2d[2][4]
            //则要比较A1(A2A3A4)和(A1A2A3)A4 小的那个为min2d[1][4]的值
            //A1(A2A3A4)  的值 = min2d[2][4]+p[0]p[1]p[4]
            //(A1A2A3)A4  的值 = min2d[1][3]+p[0]p[3]p[4]
            let leftValue = min2d[r+1][r+l]+p[r-1]*p[r]*p[r+l]
            let rightValue = min2d[r][r+l-1]+p[r-1]*p[r+l-1]*p[r+l]
            if(leftValue <rightValue){
               min2d[r][r+l]=leftValue
               mark[r][r+l]=r
            }
            else{
               min2d[r][r+l]=rightValue
               mark[r][r+l]=r+l-1
            }

        }

    }
    return mark
}
//根据上一部计算结果mark来显示结果
function traceBack(i,j,markArr){
    if(i==j) return
    var k= markArr[i][j]
    //假设A1A2A3A4
    //markArr(1,4)=2
    //则(A1A2)(A3A4)
    arguments.callee(i,k,markArr)
    arguments.callee(k+1,j,markArr)
    console.log("计算"+"A"+i+","+k+"和"+"A"+(k+1)+","+j);
}
martixMultiply(p)
console.log("最小计算次数为:"+min2d[1][4]+"\n")
console.log(min2d)
console.log(mark)
traceBack(1,4,mark)
```