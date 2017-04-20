# HouseParty API

标签（空格分隔）： api

---

**host: http://house.fibar.cn**

**api_version: v1**

# 概要

 2. API请求格式：host + "api" + api_version + 请求地址。
 3. API返回格式：`json:{"status":1,"body":{}}`status返回操作结果码,body包含返回信息，如果无返回信息，body为空。
 4. status结果码对照表： 
 
|status结果码|状态|
| --------------  | :---: |
|0|未知错误|
|1|成功|
|2|权限不足|
|3|帐号不存在|
|4|数据错误|
|5|密码错误|
|6|已存在|
|7|不存在|
|8|已过期|
|10|验证码为空|
|11|验证码错误| 


# API安全

为保证接口调用安全，所有接口都需要：`timestamp`与`sign`两个参数，用来验证接口请求的合法性。其中： 


 1. `timestamp`是类型为数字的10位的时间戳，代表发生请求时的时间。
 2. `sign` 是类型为字符串的32位验证字符串，具体生成方式为`MD5(timestamp + secret)`，其中`secret` 从系统申请后分配。请保证`secret` 的安全性，如果不慎泄露请及时更换。
 3. 验证合法性请均使用`get`方式构造参数请求，即在所有请求地址后构造类似`?timestamp=xx&sign=xx`的参数

# 文档

# 用户
## **获取注册验证码**
```
POST /verify
```
### **Parameters**
* phone(_Required_|string)-手机号

### **Return**
成功
```
{
  "body": {},
  "status": 1,
  "msg": "success"
}
```
失败
```
{
  "body": {},
  "status": 4,
  "msg": "请求短信时间间隔过短"
}

{
  "body": {},
  "status": 4,
  "msg": "请输入11位手机号"
}

{
  "body": {},
  "status": 4,
  "msg": "请输入手机号"
}
```

## **验证注册验证码**
```
GET /verify
```
### **Parameters**
* phone(_Required_|string)-手机号
* code(_Required_|string)-验证码

### **Return**
成功
```
{
  "body": {},
  "status": 1,
  "msg": "success"
}
```
失败
```
{
  "body": {},
  "status": 4,
  "msg": "数据缺失"
}

{
  "body": {},
  "status": 10,
  "msg": "请获取验证码"
}

{
  "body": {},
  "status": 11,
  "msg": "验证码不正确"
}

```

## **用户注册**
```
POST /register
```
### **Parameters**
* phone(_Required_|string)-手机号
* fullname(_Required_|string)-全名
* password(_Required_|string)-密码
* nick(_Required_|string)-昵称
### **Return**
成功
```
{
  "body": {
    "nick": "2333",
    "token": "pBgtwFXgCuN0GnsPOnbfe9paDfbyK2qM1vjoYhHdIloRem7icEZzkltarLx8WwvV",
    "create_time": 1460382192,
    "id": 7,
    "phone": "18212666355"
  },
  "status": 1,
  "msg": "success"
}
```
失败
```
{
  "body": {},
  "status": 4,
  "msg": "帐号已存在"
}
```

## **用户登陆**
```
POST /login
```
### **Parameters**
* phone(_Required_|string)-手机号
* password(_Required_|string)-密码
### **Return**
```
{
  "body": {
    "phone": "15608059720",
    "nick": "zhn",
    "token": "skvMC8SBYrfgobpj4DAx9iqlttQ0IvnxUHzFNuz3Zmkl5PJadsWRw7arK6OLXTew",
    "create_time": "2016-04-09 12:24:12",
    "id": 1
  },
  "status": 1,
  "msg": "success"
}
```

##  **用户忘记密码**
```
POST /reset
```
## **Parameters**
* phone(_Required_|string)-电话号码
* verify(_Required_|string)-验证码
* new_password(_Required_|string)-新密码
### **Return**
成功
```
{
  "body": {
    "phone": "15608059720",
    "nick": "zhn",
    "token": "CViXsWaku7hi6gJOgHxNlTcZDlxtQcIRneqbUmLk2rEYpzeraPfohv1A9KuSwyft",
    "create_time": "2016-04-09 12:24:12",
    "avatar": "http://www.fibar.cn/",
    "id": 1
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "帐号不存在"
}
```


## **用户登出**
```
GET /logout
```
### **Parameters**
* token(_Required_|string)-用户识别码
### **Return**
```
{"status":1,"body":{}, "msg": "success"}
```

## **心跳包**
```
GET /heart
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Return**
成功
```
{
  "body": {
    "phone": "15608059720",
    "nick": "RaPoSpectre",
    "modify_time": 1468997830,
    "online": true,
    "friends": [
      {
        "participants": [
          {
            "phone": "15608059721",
            "nick": "snoopy",
            "notify": {
              "message": "向你打招呼",
              "modify_time": 1468920124
            },
            "online": true,
            "id": 5,
            "modify_time": 1468983178
          }
        ],
        "room": "cc11"
      },
      {
        "participants": [
          {
            "phone": "15608059722",
            "nick": "PP",
            "notify": {
              "message": "成为朋友",
              "modify_time": 1468916085
            },
            "online": true,
            "id": 6,
            "modify_time": 1468985743
          }
        ],
        "room": "c33"
      },
      {
        "participants": [
          {
            "phone": "15608059730",
            "nick": "mitty",
            "notify": {
              "message": "",
              "modify_time": 1468986670
            },
            "online": false,
            "id": 7,
            "modify_time": 1468990586
          }
        ],
        "room": "free"
      }
    ],
    "id": 4
    "deletes": [
      {
        "id": 1,
        "deleter": {
          "room": null,
          "phone": "15608059733",
          "nick": "11113333",
          "room_id": null,
          "modify_time": 1469005615,
          "online": false,
          "id": 2
        },
        "modify_time": 1469087761
      }
    ]
  },
  "status": 1,
  "msg": "success"
}
```

## **发送好友请求**
```
POST /friend
```
### **Parameters**
* token(_Required_|string)-用户令牌
* phone(_Required_|string)-好友电话号码
### **Return**
成功
```
{
  "body": {},
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **处理好友请求**
```
GET /friend/<phone>
```
### **Parameters**
* token(_Required_|string)-用户令牌
* agree(_Required_|integer)-是否同意 1 同意 0 拒绝
### **Return**
成功
```
{
  "body": {},
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **删除好友**
```
DELETE /friend/<phone>
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Return**
成功
```
{
  "body": {},
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **获取好友请求列表**
```
GET /requests
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Return**
成功
```
{
  "body": {
    "friendrequest_list": [
      {
        "id": 8,
        "requester": {
          "nick": "RaPoSpectre",
          "id": 4,
          "avatar": "/s/image/avatar.png",
          "phone": "15608059720"
        }
      }
    ],
    "page_obj": {},
    "is_paginated": false
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **匹配通讯录**
```
POST /match
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Request**
```
[{"phone": "15608059721", "remark": "test"}, {"phone": "15608059722"}, {"phone": "15608059730", "remark": "test"}, {"phone": "15608052720", "remark": "test"}, {"phone": "15608054320", "remark": "test"}]
```
### **Return**

friend 字段类型表：

|结果码|含义|
| --------------  | :---: |
|1|互为好友|
|2|已经向好友发送请求|
|3|好友向你发送好友请求|
|4|好友在用|
|5|好友没在用|
成功
```
{
  "body": {
    "address_book": [
      {
        "remark": "test",
        "phone": "15608059721",
        "nick": "snoopy",
        "fullname": "建奇 张",
        "id": 5,
        "friend": 1
      },
      {
        "remark": "",
        "phone": "15608059722",
        "nick": "PP",
        "fullname": "建奇 张",
        "id": 6,
        "friend": 1
      },
      {
        "remark": "test",
        "phone": "15608059730",
        "nick": "mitty",
        "fullname": "asdf",
        "id": 7,
        "friend": 1
      },
      {
        "remark": "test",
        "phone": "15608052720",
        "nick": "",
        "fullname": "",
        "id": null,
        "friend": 5
      },
      {
        "remark": "test",
        "phone": "15608054320",
        "nick": "",
        "fullname": "",
        "id": null,
        "friend": 5
      }
    ]
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **向好友打招呼**
```
GET /hook/<phone>
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Return**
(10s 内重复打招呼会返回 6 限制打招呼次数)
成功
```
{
  "body": {},
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 6,
  "msg": "已向好友打过招呼"
}
```

## **进入聊天室**
```
GET /room/<room_id>
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Return**
```
{
  "body": {
    "room_id": "R33"
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **确认删除消息**
```
GET /confirm/<d_id>
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Return**
```
{
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **获取好友列表**
```
GET /friends
```
### **Parameters**
* token(_Required_|string)-用户令牌
### **Return**
```
{
  "body": {
    "page_obj": {},
    "is_paginated": false,
    "partyuser_list": [
      {
        "nick": "PP",
        "fullname": "建奇 张",
        "id": 6,
        "phone": "15608059722"
      },
      {
        "nick": "snoopy",
        "fullname": "建奇 张",
        "id": 5,
        "phone": "15608059721"
      },
      {
        "nick": "mitty",
        "fullname": "asdf",
        "id": 7,
        "phone": "15608059730"
      }
    ]
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```


## **搜索**
```
GET /search
```
### **Parameters**
* token(_Required_|string)-用户令牌
* query(_Required_|string)-搜索字符串
### **Return**

friend 字段类型表：

|结果码|含义|
| --------------  | :---: |
|0|不是好友|
|1|互为好友|
|2|已经向好友发送请求|
|3|好友向你发送好友请求|

```
{
  "body": {
    "phone": "15608059730",
    "nick": "mitty",
    "create_time": 1468916238,
    "fullname": "asdf",
    "id": 7,
    "friend": 1
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "搜索用户不存在"
}
```

## **修改个人信息**
```
POST /info
```
### **Parameters**
* token(_Required_|string)-用户令牌
* nick(_Required_|string)-用户昵称
* fullname(_Required_|string)-用户姓名
### **Return**
```
{
  "body": {
    "nick": "tstrr",
    "fullname": "123",
    "id": 4,
    "phone": "15608059720"
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 7,
  "msg": "用户不存在"
}
```

## **修改头像**
```
POST /avatar?token={token}
```
### **Parameters**
* avatar(_Required_|file)-图片
### **Return**
```
{
  "body": {
    "phone": "15608059720",
    "nick": "RaPoSpectre",
    "create_time": 1469004454,
    "avatar": "/s/image/upload/149266818996v2-dfbc73a036407c674277f1005d072d6f_l.jpg",
    "fullname": "建奇 张",
    "id": 1
  },
  "status": 1,
  "msg": "success"
}
```
其他
```
{
  "body": {},
  "status": 4,
  "msg": "数据缺失"
}
```