---
title: HTML-form表单
date: 2018-02-01 00:19:14
tags:
    - html
    - form
categories:
    - HTML
---
html中很多标签，比如img,audio,video,svg等一些多媒体标签。以及稍微较为表格table等等我都跳过没有介绍。但是form表单我却觉得实在是不得不介绍。在任何web程序中表单都是很重要的一部分。
<!--more-->
## 代码相关
```html
<!-- 假设这个页面在cai.com下 -->
<form action="/my-handling-form-page" method="post"> 
  <div>
    <label for="name">Name:</label>
    <!-- 通过他们各自的for 属性和 id 属性，<label> 标签与 <input> 正确相关联。 -->
    <input type="text" id="name" name="user_name" value="input type=text 默认文本放在value属性里"/>
  <div>
  <div>
    <label for="mail">E-mail:</label>
    <input type="email" id="mail" name="user_email" />
    <!-- type="email"这个值是HTML5规范加进去的 -->
  </div>
  <div>
    <label for="msg">Message:</label>
    <textarea id="msg" name="user_message">textarea默认文本插在标签之间</textarea>
  </div>
  <div class="button">
    <button type="submit">Send your message</button>
    <!-- HTML5之前提交按钮是<input type="sumbit"> -->
  </div>
</form>
```

## 表单数据提交
浏览器的原生 `<form>` 表单，如果不设置 enctype 属性，那么最终就会以 application/x-www-form-urlencoded 方式提交数据。
如果是GET方法提交表单，那么会发送一个http请求,他的header如下
```
GET /my-handling-form-page?user_name=xxx&user_emali=xx@xx.com&user_message=xxx HTTP/1.1
Host: cai.com
```
*使用GET的话，只能通过uri的queryString形式，这会遇到长度的问题，各个浏览器或server可能对长度支持的不同，所以到要提交的数据如果太长并不适合使用GET提交。*

如果是POST方法提交表单，将发送一个HTTP请求，其中包含的数据如下
```
POST /my-handling-form-page HTTP/1.1
Host: cai.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 123

user_name=xxx&user_emali=xx@xx.com&user_message=xxx
```
这时候数据user_name=xxx&user_emali=xx@xx.com&user_message=xxx不是在HTTP的URL里而是在HTTP的request body里了

[这个文档提供了一些使用JavaScript来提交表单的方式(模拟原生表单以x-www-form-urlencoded)](https://developer.mozilla.org/zh-CN/docs/Learn/HTML/Forms/Sending_forms_through_JavaScript)
#### 构造优秀的表单
MDN总结了一份原生表单部件。我们可以在这里选用合适的部件来构筑表单
[MDN 原生表单部件](https://developer.mozilla.org/zh-CN/docs/Learn/HTML/Forms/The_native_form_widgets)

有一些诸如
1. 有一组单选按钮的话最好嵌套在filedset标签之中
2. label元素和input元素正确的关联有诸多益处，比如点击label文本可以勾选`<input type='checkbox'>`
3. autofocus可以帮助input元素自动获得焦点
...
等等知识可以来帮助我们构建更优秀易用的表单

### 表单数据检验
[MDN 表单数据检验](https://developer.mozilla.org/zh-CN/docs/Learn/HTML/Forms/Data_form_validation)
```html
<!-- 省略了部分与主题无关代码 -->
    <style>
      input:invalid {
        border: 2px dashed red;
      }
      input:valid {
        border: 2px solid black;
      }
    </style>
    <form>
        <label for="choose">Would you prefer a banana or cherry?</label>
        <input id="choose" name="i_like" required>
        <button>Submit</button>
    </form>
```
当chooser这个input有输入时边框是实线黑色，没有输入时边框则是点线红色
**input的验证约束有**
- required属性
- pattern属性(正则表达式)
```html
<input id="choose" name="i_like" required pattern="banana|cherry">
```
- minlength,maxlength属性
```html
<input id="choose" name="i_like" required minlength="6" maxlength="6">
```
- type属性
```html
<input type="email" id="t2" name="email"> 
<!-- 只能输入Email格式 -->
```

#### 参考链接
[MDN 表单指南](https://developer.mozilla.org/zh-CN/docs/Learn/HTML/Forms)
[MDN 发送表单数据](https://developer.mozilla.org/zh-CN/docs/Learn/HTML/Forms/Sending_and_retrieving_form_data)
[四种常见POST提交数据的方式](https://imququ.com/post/four-ways-to-post-data-in-http.html)