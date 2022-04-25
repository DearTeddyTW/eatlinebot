# eatlinebot

因為line群組的記事本要手動刪除，而且如果開記事本的人退群組了，那篇記事本就沒人可以刪掉了
所以想說寫一個機器人用在群組開團使用，主要有底下指令

【開團相關】
    七年級開團 七年級開團教學
【加團相關】
    七年級加團 七年級加團教學 七年級加團詳細
【退團相關】
    七年級退團
【候補相關】
    七年級候補
【修改相關】 
    七年級修改
    
開團教學 會顯示範例，因為要照著格式寫才會被機器人寫到sql中
輸入 開團 發起者 人數 店家網址或集合地點 價位 日期 時間 內建人員 備註說明
底下為範例
開團 ken 89 https://Google.com 700+10% 2022-05-11 17:30:00 ken,kim

七年級加團 會將所有存在的團都列出來，但不會列參團人、候補人跟備註，全列出來的話會佔太多版面，然後會針對已經過期的團自動刪除
七年級加團詳細 就會把單一團的訊息都列出來

退團 分為自己退出 跟團主幫忙退出
自己退出顧名思義 要有報名該活動，臨時有事不能參加 就可以退掉，候補的會自己補上
或是也可以請團主幫你取消

候補報名就會被列入候補名單，只要有人取消，候補的就會自動補上

修改只有開團者可以修改自己開的團
--------------------------------------底下主要紀錄這次遇到的問題------------------------------------------------
最主要的應該都是從sql抓取數值出來後的資料型態，最麻煩的就是參團者跟候補者
抓出來以後都是tuple型態，沒辦法對成員做修改
所以用正則將其分開，因為寫入資料庫的格式都是用,分開 kim,ken,king
所以re.split(r'[,]', list)就可以將其名單拆開後，在用判斷式跟迴圈去重組

然後linebot要一次發多則消息也有限制，網路上有看到說用push，但一個月只有500則，後續收費好像也很高，所以不考慮
後面查到用陣列的形式．但一次最多也只能發5則，我們群組的團可能大部分都會超過，所以最後直接for迴圈把所有團的資料串在一起，做一則消息一次發送