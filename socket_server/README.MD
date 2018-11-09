# 新版 Socket 服务器文档

标签（空格分隔）： api

---

**连接地址：ws://mido.fibar.cn/**

总体流程：

进入房间->点歌->上麦询问->演唱->下麦->休息->上麦询问...

房间状态改变、成员进出房间、排麦更新时服务器会主动推送消息给客户端

### 消息体解读：

```
{
    "status":0, # 消息状态， 0 代表成功
    "body":{
        "count":1, # 房间成员数量
        "status":"4", # 房间状态
        "room":"R123", # 房间 id
        "cover": "xxx", # 房间封面
        "room_name": "xxx", # 房间名称
        "current_time":1527574165, # 当前时间戳
        "start_time":"1527574164", # 此状态开始时间
        "author":"",  # 歌曲作者 （仅演唱状态时不为空）
        "name":"", # 歌曲名称  （仅演唱状态时不为空）
        "nick":"", # 麦上人昵称
        "end_time":"1527660564", # 此状态结束时间
        "members":[ # 房间成员列表
            {
                "nick":"15608059720", # 昵称
                "fullname":"15608059720", # fullname
                "avatar":"15608059720" # 头像地址
            }
        ],
        "sid":"0", # 歌曲 id （仅演唱状态时不为空）
        "duration":"86400", # 此状态持续时长 （演唱时为歌曲时长）
        "fullname":"", # 麦上人 fullname （仅演唱状态时不为空）
        "songs":[ # 麦序
            {
                "nick":"皮皮",  # 排麦人昵称
                "fullname":"13888888888", # 排麦人 fullname
                "author":"dany", # 歌曲作者
                "name":"dany", # 歌曲名称
                "sid":"1", # 歌曲 id
                "lrc": "xxx", # 歌词地址
                "link": "xxx" # 歌曲地址
            }
        ]
    },
    "message":"success", # 状态信息
    "timestamp":"1527574165.09" # 消息发送时间戳
}
```



|房间 status 码|含义|
| --------------  | :---: |
|1|演唱中|
|2|上麦询问中|
|3|间隔休息中|
|4|空闲|


# 用户
## **进入房间**
```
action: join
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据



### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```

## **获取房间状态**

ps: 房间主动推送信息格式与此一致

```
action: status
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据



### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```

## **同意上麦**

```
action: ask
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* ack(_Required_|integer)- 是否上麦 1 上 0 不上
* body(_Optional_|object)-可选数据

### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```


## **切歌**

```
action: cut
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据

### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```


## **广播消息**

```
action: boardcast
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据

### **Return**
成功
```
{
    "status":0,
    "body":{
        "count":1,
        "status":"4",
        "room":"R123",
        "current_time":1527574165,
        "start_time":"1527574164",
        "author":"",
        "name":"",
        "nick":"",
        "end_time":"1527660564",
        "members":[
            {
                "nick":"15608059720",
                "fullname":"15608059720",
                "avatar":"15608059720"
            }
        ],
        "sid":"0",
        "duration":"86400",
        "fullname":"",
        "songs":[

        ]
    },
    "message":"success",
    "timestamp":"1527574165.09"
}
```
失败
```
```

## **排麦**

```
action: sing
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* body(_Optional_|object)-可选数据
* sid(_Required_|string)- 歌曲 id
* duration(_Required_|string)-歌曲 时长 （秒）

### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"success",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"不能重复排麦",
    "timestamp":"1527915707.61"
}
```

## **取消排麦**

```
action: del
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id

### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"取消排麦成功",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"不能重复排麦",
    "timestamp":"1527915707.61"
}
```


## **心跳包**

```
action: heart
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id

### **Return**
成功
```
{
    "status":0,
    "body":{
        "heart":"success"
    },
    "message":"success",
    "type":1,
    "timestamp":"1528381016.1"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```

## **发送聊天**

```
action: chat
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* content(_Required_|string)-聊天消息


### **Return**
成功
```
{
    "status":0,
    "body":{
        "content":"test",
        "nick":"皮皮",
        "fullname":"13888888888",
        "action":"chat",
        "room":"R123"
    },
    "message":"success",
    "type":2,
    "timestamp":"1528381126.71"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```

## **获取聊天历史**

```
action: history
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id


### **Return**
成功
```
{
    "status":0,
    "body":[
        {
            "content":"test",
            "nick":"15608059720",
            "room":"R123",
            "action":"chat",
            "timestamp":1528449835.640356,
            "fullname":"15608059720"
        },
        {
            "content":"test",
            "nick":"15608059720",
            "room":"R123",
            "action":"chat",
            "timestamp":1528449829.496153,
            "fullname":"15608059720"
        },
        {
            "content":"test",
            "nick":"15608059720",
            "room":"R123",
            "action":"chat",
            "timestamp":1528449829.11485,
            "fullname":"15608059720"
        },
        {
            "content":"test",
            "nick":"15608059720",
            "room":"R123",
            "action":"chat",
            "timestamp":1528449828.6196,
            "fullname":"15608059720"
        },
        {
            "content":"test",
            "nick":"15608059720",
            "room":"R123",
            "action":"chat",
            "timestamp":1528449828.198985,
            "fullname":"15608059720"
        },
        {
            "content":"test",
            "nick":"15608059720",
            "room":"R123",
            "action":"chat",
            "timestamp":1528449827.558498,
            "fullname":"15608059720"
        }
    ],
    "message":"success",
    "type":2,
    "timestamp":"1528449863.58"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```

## **发送设备信息**

```
action: device
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* device(_Required_|string)- 设备类型 （麦克风、摄像头）
* value(_Required_|string)- 开关 0 关 1 开



### **Return**
成功
```
{
    "status":0,
    "body":{
        "device":"video",
        "fullname":"15608059720",
        "room":"R123",
        "value":0
    },
    "message":"success",
    "type":2,
    "timestamp":"1528384592.1"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```


## **点歌**

```
action: listen
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* sid(_Required_|string)-歌曲 id
* duration(_Required_|string)-歌曲时长



### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"success",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"不能重复排麦",
    "timestamp":"1527915707.61"
}
```


## **删除歌曲**

```
action: del_music
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id



### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"success",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```


## **切歌曲**

```
action: cut_music
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id



### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"success",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```


## **切视频**

```
action: cut_video
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id



### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"success",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```



## **点视频**

```
action: watch
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* vid(_Required_|integer)-视频 id



### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"success",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```

## **拖动进度**

```
action: set_duration
```
### **Parameters**
* action(_Required_|string)-行为
* fullname(_Required_|string)- 用户 fullname
* token(_Required_|string)- 用户 token
* room(_Required_|string)-房间 id
* current(_Required_|integer)-拖动到的进度（例如duration=100s的视频，current=60s，就拖动到 60s 处）

**其他客户端同步进度使用房间信息的 end_time - current_time 得到当前进度**
**播放完成时调用此接口改变房间状态，current=duration 即可**


### **Return**
成功
```
{
    "status":0,
    "body":{

    },
    "message":"success",
    "timestamp":"1527915490.31"
}
```
失败
```
{
    "status":-1,
    "body":{

    },
    "message":"",
    "timestamp":"1527915707.61"
}
```

