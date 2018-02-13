---
title: (动态规划)0-1背包问题
date: 2018-01-27 23:17:17
tags:
    - 动态规划
categories:
    - 算法
    - js经典算法实现
---

自己实现的js动态规划算法01背包问题

<!--more-->

```js
//0-1背包问题
//http://www.hawstein.com/posts/dp-knapsack.html

//helper
function creat2dArray(rows,columns){
    let resultArr=new Array(rows)
    for(let i=0;i<rows;i++){
        resultArr[i]=new Array(columns)
    }
    return resultArr
}

//n个宝石（先假设n=3）
// 宝石i     0    1    2
// 重量w(i)  5    4    3
// 价值v(i)  20   10   12

//背包的容量为C（假设C=10）
//选择装进背包的宝石使得（V最大）

//问题的解 x[i]=0表示宝石i不装，=1表示装进去

//定义状态  solution[a][b]
// 表示前a装到剩余体积为b的背包里能达到的最大价值
//问题 即为 solution[n][C]

//状态转移(最优子结构)
//例 当求解solution[3][10]
//其实在考虑2号宝石要不要装不装入的问题
//要装入的话 = solution[2][10-w[2]]+v[2]
//不装入 = solution[2][10]
//比较大小 选择大的那一部分

//去特殊化
//在能装入的前提下 if b> w[a-1]
//solution[a][b] = solution[a-1][10-w[a-1]]+v[a-1] :solution[a-1][b]? 
//    solution[a-1][10-w[a-1]]+v[a-1] :solution[a-1][b]
function knapsack(weightArr,valueArr,c){
    if(!weightArr instanceof Array ||
       !valueArr instanceof Array) return
    if(!c) return
    if(weightArr.length != valueArr.length ) return

    let n = weightArr.length //宝石数量
    
    var solutionArr = creat2dArray(n+1,c+1)

    for(let i=0;i<=n;i++){
        for(let j=0;j<=c;j++){
            solutionArr[i][j] = i==0? 0:solutionArr[i-1][j];
            //这一步把所有solution都初始为不能装的情况
            //即求solution[2][10] = solution[0][10]
            //此时solution[0][10] = 0
            if(i>0 && j>=weightArr[i-1]){
                solutionArr[i][j] = solutionArr[i][j]>solutionArr[i-1][ j-weightArr[i-1] ]+valueArr[i-1]?
                        solutionArr[i][j]:solutionArr[i-1][ j-weightArr[i-1] ]+valueArr[i-1];
            } 
        }
    }

    console.log(solutionArr[n][c])

    var xArr = new Array(n)
    var tmpc = c
    for(let i=n;i>0;i--){
        //初始是false表示不放
        xArr[i-1]=false
        if(solutionArr[i][tmpc]>solutionArr[i-1][tmpc]){
            xArr[i-1]=true
            tmpc = tmpc-weightArr[i-1]
        }
    }
    console.log(xArr)
}

var w = [5,4,3]
var v = [20,10,12]

knapsack(w,v,10)
```