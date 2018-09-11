# coding: utf-8
import requests,json
auth_key = 'AAAARFFjVHE:APA91bGt9MWWmoiVwploJQn0xqqRJI-nw2jro1h8tBSYXWe0CGNrfLEd_T0-oMHZjLP-zwWB8sJRnQ2z4IQbQp1etlK1sozL4tvwAvXDNZ5LkLaP8rRjw9cv4KgXNEJ4kMGIiyJiue2X'
def friend_greet(room_id,nick,fullname_rece):
    msg = "{0}邀请你加入房间".format(nick)
    headers = {'Content-Type': 'application/json', 'Authorization': 'key='+auth_key}
    url = r'https://fcm.googleapis.com/fcm/send'
    data = {"notification": {
        "body": msg},
        "to": fullname_rece,
        "data": {"room_id": room_id}}
    try:
       a = requests.post(url=url, headers=headers, data=json.dumps(data))
       return "firebase send success"
    except Exception as e:
        print e
        return "firebase send failure"



