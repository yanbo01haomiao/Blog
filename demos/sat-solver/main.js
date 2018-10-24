const satSolver = require('./sat.js')
const fs = require('fs')
const readline = require('readline');

let pPattern = /p\s+cnf\s+(\d+)\s+(\d+)/
let clausePattern = /\s0$/

const rl = readline.createInterface({
    input: fs.createReadStream('./mytest.cnf')
    // input: fs.createReadStream('./uf20-91/uf20-02.cnf')
});

let satProblem = {
    varNum: 0,
    clauses: []
}

rl.on('line', (line) => {
    if(pPattern.test(line)) {
        // 读取变量的个数
        satProblem.varNum = parseInt(line.split(/\s+/)[2])
    }
    if(clausePattern.test(line)) {
        // 从cnf中读取每一个clause
        let clause = line.split(/\s+/).filter((item) => {
            return !Number.isNaN(parseInt(item))
            // 先将不是数字的过滤掉
        })
        .map((numStr)=>{
            return parseInt(numStr)
        }).slice(0,-1)
        satProblem.clauses.push(clause)
       
    }
}).on('close', ()=>{
    console.log(`问题有${satProblem.varNum}个变量`)
    console.log('clauses: ', satProblem.clauses)
    console.log('solutions: ', satSolver(satProblem.varNum, satProblem.clauses).slice(1))
})
