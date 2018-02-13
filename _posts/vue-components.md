---
title: Vue-组件通信
date: 2018-02-07 18:38:28
tags:
    - MVVM
    - vue
categories:
    - Vue
---

组件实例的作用域是孤立的。这意味着不能 (也不应该) 在子组件的模板内直接引用父组件的数据。同时父组件也无法直接引用子组件的数据。

<!--more-->

在 Vue 中，父子组件的关系可以总结为 prop 向下传递，事件向上传递。父组件通过 prop 给子组件下发数据，子组件通过事件给父组件发送消息。先来张直观的图。
<img src="passemit.png" width="100%" >

## Pass Props

首先子组件要显式地用[proprs选项](https://cn.vuejs.org/v2/api/#props)声明它预期的数据：

```js
Vue.component('child', {
    // 声明 props
    props: ['message'],
    // 就像 data 一样，prop 也可以在模板中使用
    // 同样也可以在 vm 实例中通过 this.message 来使用
    template: '<span>{{ message }}</span>'
})
```
然后我们在父组件里就可以传入子组件想要的这个props数据
静态传入
```html
<child message="hello!"></child>
```
动态绑定
```html
<div>
    <inout v-model="parentMsg">
    <br>
    <child :message="parentMsg">
</div>
```
如果你想把一个对象的所有属性作为 prop 进行传递，可以使用不带任何参数的 v-bind。例如，已知一个 todo 对象：
```js
todo: {
  text: 'Learn Vue',
  isComplete: false
}
```
然后
```html
<todo-item v-bind="todo"></todo-item>
```
等价于
```html
<todo-item
  v-bind:text="todo.text"
  v-bind:is-complete="todo.isComplete"
></todo-item>
```

*初学者常犯的一个错误是使用字面量语法传递数值：<comp some-prop="1"></comp><!-- 传递了一个字符串 "1" -->*

**Prop 是单向绑定的：当父组件的属性变化时，将传导给子组件，但是反过来不会。这是为了防止子组件无意间修改了父组件的状态，来避免应用的数据流变得难以理解**

**每次父组件更新时，子组件的所有 prop 都会更新为最新值。这意味着你不应该在子组件内部改变 prop 。如果你这么做了，Vue 会在控制台给出警告。**

但是有时候我们确实很容易忍不住想在子组件去修改 prop 中数据
1. Prop 作为初始值传入后，子组件想把它当作局部数据来用；
2. Prop 作为原始数据传入，由子组件处理成其它数据输出。

对这两种情况，正确的应对方式是:
定义一个局部变量，并用 prop 的值初始化它：
```js
props: ['initialCounter'],
data: function () {
  return { counter: this.initialCounter }
}
```
定义一个计算属性，处理 prop 的值并返回：
```js
props: ['size'],
computed: {
  normalizedSize: function () {
    return this.size.trim().toLowerCase()
  }
}
```

### 非 Prop 特性
所谓非 prop 特性，就是指它可以直接传入组件，而不需要定义相应的 prop。

有时候你也可以不在子组件声明props,而是不管他有什么props,直接从父组件传入一个特性，这个特性会被自动添加到子组件的根元素上。

*我自己遇到过的情况，比如在使用第三方ui框架muse-ui的时候，他给的button控件`<mu-button></mu-buttom>`有一个默认的样式，不过我不太喜欢他的样式所以想添加自己的样式，ui框架的设计者在有的组件上会提供诸如'activeClass'之类的props我们可以传递数据进去，但是有些控件他没有提供，我们就可以直接为他添加非prop特性(直接在自定义组件上添加class特性`<mu-button class="mybtnstyle"></mu-buttom>`)来在框架控件的基础上自定义样式*

**当对待class和style,来自父组件添加的属性，会和组件自身模板的class属性进行merge而其他多数则会覆盖组件本身设定的值**

## Emit Event

父组件可以在使用子组件的地方直接用 v-on 来监听子组件触发的事件

一个例子

```html
<div id="counter-event-example">
    <p>{{ total }}</p>
    <button-counter v-on:increment="incrementTotal"></button-counter>
    <button-counter v-on:increment="incrementTotal"></button-counter>
</div>
```

```js
Vue.component('button-counter', {
    template: '<button v-on:click="incrementCounter">{{ counter }}</button>',
    data: function () {
        return {
            counter: 0
        }
    },
    methods: {
        incrementCounter: function () {
            this.counter += 1
            this.$emit('increment')
        }
    },
})
new Vue({
    el: '#counter-event-example',
    data: {
        total: 0
    },
    methods: {
        incrementTotal: function () {
            this.total += 1
        }
    }
})
```

**子组件唯一与父组件的接口就是this.$emit('increment') 除此以外组件是完全独立的。因为父组件有可能会监听这个事件，所以才暴露这个接口，当子组件调用了该函数的时候通知父组件。**

有时候，你可能想在某个组件的根元素上监听一个原生事件。可以使用 v-on 的修饰符 .native。例如：
```html
<my-component v-on:click.native="doTheThing"></my-component>
```
*所谓原生事件应该是相对于自定义事件而言，像刚刚我们的"increment"就很明显是一个自定义事件*

*这个有点没懂，是因为往子组件中传入的每一个v-on:后面的值都会被当作是子组件中的自定义事件(不加native的话，会被当作我们自定义了一个名为click的事件？)，需要在子组件this.$emit('click')才能触发，原本的点击该元素这个操作不会触发？因此想要监听原生事件反而需要加上.native修饰符*

*还有一个.sync修饰符查看vue官方文档*

### v-model的原理

```html
<input v-model="something">
```
不过是以下示例的语法糖：
```html
<input
  v-bind:value="something"
  v-on:input="something = $event.target.value">
```

所以在组件中使用v-model，它相当于下面的简写：
```html
<custom-input
  v-bind:value="something"
  v-on:input="something = arguments[0]">
</custom-input>
```
vue2.2新增以下写法
```html
<my-checkbox v-model="foo" value="some value"></my-checkbox>
```
```js
Vue.component('my-checkbox', {
  model: {
    prop: 'checked',
    event: 'change'
    // 如果不做配置的话，prop默认是value,event默认是input
  },
  props: {
    checked: Boolean,
    //注意你仍然需要显式声明 checked 这个 prop。
    value: String
    // 这样就允许拿 `value` 这个 prop 做其它事了
  },
  // ...
})
```

### 非父子组件的通信
有时候，非父子关系的两个组件之间也需要通信。在简单的场景下，可以使用一个空的 Vue 实例作为事件总线：
```js
var bus = new Vue()
```
```js
// 触发组件 A 中的事件
bus.$emit('id-selected', 1)
```
```js
// 在组件 B 创建的钩子中监听事件
bus.$on('id-selected', function (id) {
  // ...
})
```

再复杂的情况请考虑[vuex](https://vuex.vuejs.org/zh-cn/)

#### 参考资料

[vue 官方文档](https://cn.vuejs.org/v2/guide/components.html)