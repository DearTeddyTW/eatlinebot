from __future__ import unicode_literals
from asyncio import events
# from asyncio.windows_events import NULL
from cgitb import text
from datetime import date
from email import message
from sqlite3 import Time
from time import time
from urllib.parse import parse_qs
from click import ParamType
import pymysql, os
from typing import Text
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import datetime
import configparser
import re
import random

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')
test = config.get('db', 'dbhost')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 學你說話
@handler.add(MessageEvent, message=TextMessage)
def pretty_echo(event):
    name_id = event.source.user_id
    try:
        profile = line_bot_api.get_profile(name_id).display_name
    except LineBotApiError as e:
        profile = "noman"
    if event.message.text == "七年級開團機器人":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="【開團相關】\n    七年級開團 七年級開團教學\n【加團相關】\n    七年級加團 七年級加團教學\n    七年級加團詳細\n【退團相關】\n    七年級退團\n【候補相關】\n    七年級候補\n【修改相關】 \n    七年級修改")
        )
    if "七年級開團" in event.message.text:
        if "教學" in event.message.text:
            a = "輸入 開團 發起者 人數 店家網址或集合地點 價位 日期 時間 內建人員 備註說明\n底下為範例\n開團 ken 89 https://Google.com 700+10% 2022-05-11 17:30:00 ken,kim "
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
        else:
            try:
                profile = line_bot_api.get_profile(name_id).display_name
            except LineBotApiError as e:
                profile = "noman"
            line = event.message.text
            #正則用空白分開所有東西
            searchObj = re.split(r'[ ]', line)
            name_id = event.source.user_id
            sponsor = searchObj[1]
            people = searchObj[2]
            website = searchObj[3]
            price = searchObj[4]
            date = searchObj[5]
            Time = searchObj[6]
            participant = searchObj[7]
            if len(searchObj) <= 8:
                note = ""
            else:
                note = searchObj[8]
            create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db = pymysql.connect(host=config.get('db', 'dbhost'),user=config.get('db', 'dbuser'),password=config.get('db', 'dbpass'),database=config.get('db', 'dbname'))
            cursor = db.cursor()
            sql = "INSERT INTO eat(name_id, sponsor, people, website, price, date, time, participant, backup, note, create_time) VALUES ('"+ name_id +"', '"+ sponsor +"', '"+ people +"', '"+ website +"', '"+ price +"', '"+ date +"', '"+ Time +"', '"+ str(participant) +"', '', '"+ str(note) +"', '"+ str(create_time) +"')"
            try:
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()
            db.close()
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="開團成功囉"))

    if "七年級加團" in event.message.text:
        db = pymysql.connect(host=config.get('db', 'dbhost'),user=config.get('db', 'dbuser'),password=config.get('db', 'dbpass'),database=config.get('db', 'dbname'))
        cursor = db.cursor()
        party = ""
        participant = ""
        if "教學" in event.message.text:
            a = "輸入 【加團】可以列出所有活動\n輸入 【加團詳細 編號】可以看該活動詳細說明\n輸入 【加團 編號】可以報名該活動\n"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=a))
            pass
        elif event.message.text == "七年級加團":
            try:
                sql =  "select * from eat"
                cursor.execute(sql)
                results = cursor.fetchall()
                for each in results:
                    sql = "DELETE FROM eat where num=" + str(each[0])
                    #如果日期小於現在日期自動刪掉活動
                    if each[6] < datetime.date.today():
                        try:
                            cursor.execute(sql)
                            db.commit()
                        except:
                            db.rollback()
                    #拆分日期2022-5-11
                    searchObj_date = re.split(r'[-]', str(each[6]))
                    #拆分時間18:30:00
                    searchObj_time = re.split(r'[:]', str(each[7]))
                    #用拆分結果拼湊5月11日 18:30 不要顯示年跟秒
                    fin_date = searchObj_date[1] + "月" + searchObj_date[2] + "日" + searchObj_time[0] + ":" + searchObj_time[1]
                    party += '編號: '+ str(each[0]) + ' 發起人: '+ str(each[2]) + ' 人數: '+ str(each[3]) + ' 地點: '+ str(each[4]) + ' 價錢: '+ str(each[5]) + ' 日期:'+ fin_date+'\n'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=party))
            except:
                print("failed")
                pass
        elif "七年級加團詳細" in event.message.text:
            try:
                line = event.message.text
                searchObj = re.split(r'[ ]', line)
                sql =  "select * from eat where num = " + searchObj[1]
                cursor.execute(sql)
                results = cursor.fetchall()
                for each in results:
                    searchObj_date = re.split(r'[-]', str(each[6]))
                    searchObj_time = re.split(r'[:]', str(each[7]))
                    fin_date = searchObj_date[1] + "月" + searchObj_date[2] + "日" + searchObj_time[0] + ":" + searchObj_time[1]
                    party += '編號: '+ str(each[0]) + '\n'+ '發起人: '+ str(each[2]) + ' 人數: '+ str(each[3]) + '\n' + '地點: '+ str(each[4]) + '\n'+'價錢: '+ str(each[5])+ '\n' +'日期: '+ fin_date+ '\n' + '參與者:'+ str(each[8])+ '\n' + '候補:'+ str(each[9])+ '\n' + '備註:'+ str(each[10]) +'\n'
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text=party))
            except:
                print("failed")
                pass
        else:
            line = event.message.text
            searchObj = re.split(r'[ ]', line)
            sql =  "select people,participant from eat where num = " + searchObj[1]
            cursor.execute(sql)
            results = cursor.fetchall()
            #選到參團者
            searchObj_participant = re.split(r'[,]', results[0][1])
            #報名者已在名單 顯示已經報名過
            if profile in searchObj_participant:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="已經報名過囉"))
            #如果參團者小於總人數 報名成功
            elif len(searchObj_participant) < results[0][0]:
                    for i in range(0,len(searchObj_participant)):
                        participant += searchObj_participant[i]+","
                    participant += profile
                    sql = "UPDATE eat SET participant = '" + participant + "' where num = " + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                    except:
                        db.rollback()
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text="恭喜成功加入"))
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="人數已滿，若要候補，請輸入【候補 編號】"))
                print(results[0][1])
        db.close()
    if "七年級候補" in event.message.text:
        db = pymysql.connect(host=config.get('db', 'dbhost'),user=config.get('db', 'dbuser'),password=config.get('db', 'dbpass'),database=config.get('db', 'dbname'))
        cursor = db.cursor()
        backup = ""
        line = event.message.text
        searchObj = re.split(r'[ ]', line)
        if len(searchObj) == 1:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="輸入 【候補 編號】可以報名候補該活動"))
        #幫自己報名候補
        elif len(searchObj) == 2:
            sql =  "select num,backup from eat where num = " + searchObj[1]
            cursor.execute(sql)
            results = cursor.fetchall()
            searchObj_backup = re.split(r'[,]', results[0][1])
            #如果候補名單是空值 添加自己到名單
            if searchObj_backup[0] == "":
                backup += profile
            elif profile in searchObj_backup:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="已經在名單中囉"))
            else:
                for i in range(0,len(searchObj_backup)):
                    backup += searchObj_backup[i]+","
                backup += profile
            sql = "UPDATE eat SET backup = '" + backup + "' where num = " + searchObj[1]
            try:
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()
            db.close()
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="恭喜成功候補"))
            print(backup)
        else:
            pass
    if "七年級退團" in event.message.text:
        db = pymysql.connect(host=config.get('db', 'dbhost'),user=config.get('db', 'dbuser'),password=config.get('db', 'dbpass'),database=config.get('db', 'dbname'))
        cursor = db.cursor()
        backup = ""
        participant = ""
        line = event.message.text
        searchObj = re.split(r'[ ]', line)

        if len(searchObj) == 1:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="幫自己退團，請輸入【退團 編號】\n幫別人退團請輸入【退團 編號 人名】"))
            pass
        #幫自己退團
        elif len(searchObj) == 2:
            sql =  "select num,participant,backup from eat where num = " + searchObj[1]
            cursor.execute(sql)
            results = cursor.fetchall()
            searchObj_participant = re.split(r'[,]', results[0][1])
            searchObj_backup = re.split(r'[,]', results[0][2])
            for each in searchObj_participant:
                #參與者 不等於自己的重建名單
                if each != profile:
                    participant += each + ","
            #最後將候補第一位補上
            participant += searchObj_backup[0]
            #重建候補名單
            for i in range(1,(len(searchObj_backup)-1)):
                backup += searchObj_backup[i] + ","
            backup += searchObj_backup[len(searchObj_backup)-1]
            print(participant,backup)
            sql = "UPDATE eat SET backup = '" + backup + "', participant = '" + participant + "' where num = " + searchObj[1]
            try:
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()
            db.close()
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="退團成功囉"))
        elif len(searchObj) == 3:
            sql =  "select num,sponsor,participant,backup from eat where num = " + searchObj[1]
            cursor.execute(sql)
            results = cursor.fetchall()
            searchObj_sponsor = re.split(r'[,]', results[0][1])
            searchObj_participant = re.split(r'[,]', results[0][2])
            searchObj_backup = re.split(r'[,]', results[0][3])
            #限定開團者才能幫退團
            if searchObj_sponsor[0] == profile:
                if searchObj[2] not in searchObj_participant:
                    pass
                else:
                    for each in searchObj_participant:
                        if each != searchObj[2]:
                            participant += each + ","
                    participant += searchObj_backup[0]
                    if searchObj_backup[0] == "":
                        backup = ""
                    elif len(searchObj_backup) ==1:
                        backup = ""
                    else:
                        for i in range(1,(len(searchObj_backup)-1)):
                            backup += searchObj_backup[i] + ","
                        backup += searchObj_backup[len(searchObj_backup)-1]
                        print(participant, backup)
                    sql = "UPDATE eat SET backup = '" + backup + "', participant = '" + participant + "' where num = " + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                    except:
                        db.rollback()
                    db.close()
                pass
            else:
                line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你不是團主喔"))
        else:
            pass
        pass
    if "七年級修改" in event.message.text:
        db = pymysql.connect(host=config.get('db', 'dbhost'),user=config.get('db', 'dbuser'),password=config.get('db', 'dbpass'),database=config.get('db', 'dbname'))
        cursor = db.cursor()
        line = event.message.text
        name_id = event.source.user_id
        searchObj = re.split(r'[ ]', line)  
        sql = "select num,name_id from eat where num = " + searchObj[1]
        cursor.execute(sql)
        results = cursor.fetchall()
        searchObj_name_id = re.split(r'[,]', results[0][1])
        if len(searchObj) < 4:   
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="請輸入編號跟要修改的欄位底下範例\n七年級修改 12 日期 內容"))
            pass
        elif name_id != searchObj_name_id[0]:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text="你不是團主哦"))
        else:
            match searchObj[2]:
                case "人數":
                    sql = "UPDATE eat SET people='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
                case "地點":
                    sql = "UPDATE eat SET website='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
                case "價錢":
                    sql = "UPDATE eat SET price='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
                case "日期":
                    sql = "UPDATE eat SET date='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
                case "時間":
                    sql = "UPDATE eat SET time='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
                case "參團者":
                    sql = "UPDATE eat SET participant='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
                case "候補者":
                    sql = "UPDATE eat SET backup='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
                case "備註":
                    sql = "UPDATE eat SET note='" + searchObj[3] + "' WHERE num=" + searchObj[1]
                    try:
                        cursor.execute(sql)
                        db.commit()
                        line_bot_api.reply_message(event.reply_token,TextSendMessage(text="修改成功"))
                    except:
                        db.rollback()
            db.close()
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=""))
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)