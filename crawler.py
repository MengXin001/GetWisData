import datetime
import time
import numpy as np
import requests
import re
import json
import urllib

ultid = []

def get_html(url):
    res = requests.get(url)
    res.encoding = 'utf-8'
    html = res.text
    return html

def DXKtask():
    request = requests.get("DXKAPI").json()
    if request['IsError'] == False:
        url = "DXKAPI" + request['Data'][29]['ListFn']
        fn = request['Data'][29]['ListFn']
        urllib.request.urlretrieve(url, "./Radar/DXK/" + fn)
        print('Successfully Downloaded ' + fn)
    else:
        print('Failed To Get DXK')
    return 1

def XKZtask():
    pictime =  (datetime.datetime.now()-datetime.timedelta(minutes=10)).strftime('%Y%m%d%H%M')
    url = "GDXKAPI"
    fn = 'GD_XKZ_'+ pictime +'CR.png'
    urllib.request.urlretrieve(url, "./Radar/XKZ/" + fn)
    print('Successfully Downloaded ' + fn)
    return 1
        
def Warningtask(Roi):#101280601
    Key = "f87b8bdefcc9427894c24fc0179d0039"
    request = requests.get("https://devapi.qweather.com/v7/warning/now", params={"location":Roi,"key":Key}).json()
    #{'code': '200', 'updateTime': '2022-08-20T20:54+08:00', 'fxLink': 'http://hfx.link/3j15', 'warning': [{'id': '10128110620220820203400474811192', 'sender': '台山市气象台', 'pubTime': '2022-08-20T20:34+08:00', 'title': '台山市气象台发布暴雨黄色预警[III级/较重]', 'startTime': '2022-08-20T20:30+08:00', 'endTime': '2022-08-21T20:30+08:00', 'status': 'active', 'level': '黄 色', 'severity': 'Moderate', 'severityColor': 'Yellow', 'type': '1003', 'typeName': '暴雨', 'urgency': '', 'certainty': '', 'text': '【台山暴雨黄色 预警】过去3小时我市南部已出现强降雨，预计未来6小时全市大部地区降水持续，台山市气象台8月20日20时30分发布暴雨黄色预警信号，请注意防御。', 'related': ''}, {'id': '10128110620220820120300073109232', 'sender': '台山市气象台', 'pubTime': '2022-08-20T12:03+08:00', 'title': '台山市气象台发布雷雨大风黄色预警[III级/较重]', 'startTime': '2022-08-20T12:00+08:00', 'endTime': '2022-08-21T12:00+08:00', 'status': 'active', 'level': '黄色', 'severity': 'Moderate', 'severityColor': 'Yellow', 'type': '1020', 'typeName': '雷雨大风', 'urgency': '', 'certainty': '', 'text': '【台山雷雨大风黄色预警】目前冲蒌和斗山已出现7级阵风，预计未来6小时我市雷雨持续，局部雨势较大并伴有7到8级短时大风，台山市气象台8月20日12时发布雷雨大风黄色预警信号，请注意防御。', 'related': ''}], 'refer': {'sources': ['12379'], 'license': ['no commercial use']}}
    if request['code'] == '200':
        if request['warning'] == []:
            warningtext = '该地区暂无预警'
            return None, None, None, None, warningtext
        else:
            text = request['warning'][0]['text']
            title = request['warning'][0]['title']
            typeName = request['warning'][0]['typeName']
            startTime = request['warning'][0]['startTime']
            id = request['warning'][0]['id']
            warningtext = '[' + startTime +'] ' + title + text
            return text, title, startTime, id, warningtext
    else:
        print('Configuration Or Network Error!')
        return 1

def Polling():
    while True:
        global ultid
        text, title, startTime, id, warningtext = Warningtask("101280601")
        if "降水" in warningtext:
            if id != ultid:
                print(startTime + title)
                ultid = id
            DXKtask()
        else:
            print(datetime.datetime.now().strftime('%Y%m%d%H%M ') + warningtext)
        time.sleep(300)
Polling()
