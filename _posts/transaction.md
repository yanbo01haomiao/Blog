# 数据库事务及sequelize.transaction实践

## 简要

一项事务可以理解是当你想把一个流程当作一个整体，整个流程要嘛发生要嘛不发生，不容许只进行到一半。一个经典的例子是银行转账，当进行【王健林转账给我1个亿】这项流程或者说就是一项事务的时候。分为两个步骤来实现

1. 从王健林的账户里扣除1个亿
2. 给我的账户里增加1个亿

这两个步骤应该视为一个整体，要么就是执行成功(commit)，要么就是执行失败(rollback)回滚到事务尚未开始前的状态。也就是不允许只扣了王健林1亿，却不给我的账户增加1亿这种情况的发生。

[了解更多参考维基百科Database transaction](https://en.wikipedia.org/wiki/Database_transaction)

## 业务逻辑对事务的需求

考虑网上书店场景，用户支付了订单，调用了payBill接口，payBill逻辑实现的伪代码如下：

```js
// pay_service.js
async payBill(params) {
    try {
        await bill_model.update({
            payStaus: 1
        }, {
            where: { 
                billId: params.billId 
            }
        }) //step1: 修改订单状态
        await book_inventory_model.update({
            inventory: Sequelize.literal(`inventory - ${params.numCount}`)
        }, { 
            where: {
                bookId: { [Op.in]: params.bookIds }
            }
        }) //step2: 库存更新
        await user_account_model.update({
            balance: Sequelize.literal(`balance - ${params.totalPay}`)
        }, {
            where: {
                userId: params.userId
            }
        })//step3: 更新客户钱包余额
        
        return {code: 200, msg: '支付成功'}
    }
    catch(err) {
        return {code: 500, msg: '服务器出错'}
    }
}
```

可以看到一个支付的逻辑，我们需要去更新多个表。考虑如下情况

当执行payBill里的逻辑时，首先进行step1: 更新订单表的该订单状态为1【已支付】。 执行成功

接着进行step2：更新商品库存表里的该订单下购买的书籍库存量。 这时假设出现了代码抛错、网络断连、服务器崩溃、数据库连接不上等等原因导致step2执行失败

此时代码逻辑会跳到 catch 返回给前端【服务器出错】

然而此时涉及到一个问题，由于订单表里该订单的支付状态已经被修改为1【已支付】。但库存表里的库存没减少，step3 用户的余额也没扣除。

这造成了严重的逻辑错误。这也就是事务的适用场景。【修改订单状态】【库存更新】【用户钱包余额更新】这三件事应该被视为一个整体事务，要么就完整地执行完成，要么就一个步骤也不执行。绝不容许只执行到一半。

## 利用sequelize.transaction来实现事务

```js
// pay_service.js
async payBill(params) {
    let t = await sequelize.transaction();
    try {
        await bill_model.update({
            payStaus: 1
        }, {
            where: { 
                billId: params.billId 
            }
            transaction: t
        }) //step1: 修改订单状态
        await book_inventory_model.update({
            inventory: Sequelize.literal(`inventory - ${params.numCount}`)
        }, { 
            where: {
                bookId: { [Op.in]: params.bookIds }
            }
            transaction: t 
        }) //step2: 库存更新
        await user_account_model.update({
            balance: Sequelize.literal(`balance - ${params.totalPay}`)
        }, {
            where: {
                userId: params.userId
            }
            transaction: t 
        }) //step3: 更新客户钱包余额
        
        await t.commit()
        return {code: 200, msg: '支付成功'}
    }
    catch(err) {
        await t.rollback()
        return {code: 500, msg: '服务器出错'}
    }
}
```

这样我们就可以保证这三个step被当作一个整体来看待。三个step都顺利执行就commit，其中哪个step抛错就rollback回滚到第一个step执行之前的状态。

更多关于sequelize.transaction的用法可以查看[sequelizejs docs - Transactions](http://docs.sequelizejs.com/manual/tutorial/transactions.html#)