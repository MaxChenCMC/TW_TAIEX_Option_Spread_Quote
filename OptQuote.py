import os, time, requests
import pandas as pd
from datetime import datetime

k = input('目前價平在哪個履約價？')
mkt = input('要查一般盤(1)還是盤後盤(2)？')
premium = int(input('價平雙賣想收幾點權利金？'))  
check = []  # 在while之外才不會被洗掉
while True:   
    if mkt == '1':
        df = pd.DataFrame(pd.read_html('https://info512.taifex.com.tw/Future/OptQuote_Norl.aspx')[11])
    elif mkt == '2':
        res = requests.get('https://info512ah.taifex.com.tw/Future/OptQuote_Norl.aspx', headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Cookie':
            '_ga=GA1.3.298186347.1568167755; ASP.NET_SessionId=vnwtxvgnzlxyvwwjqoe2x0ot; BIGipServerPOOL_INFO512AH_TCP_80=1427509420.20480.0000'}).text            
        df = pd.DataFrame((pd.read_html(res))[11])
        
    for i in range(1,len(df)):
        if str(df.iloc[i][6]) == k :
            strike = i
            
    # 期交所回覆完再清空    
    os.system("cls")
    
    print('更新於：',datetime.now().strftime("%A,%H:%M:%S\n")) # 大寫A是Wednesday，小寫a是 Wed
    
    strike = strike - 2  # 價內 2檔
    print('履約價：',df.iloc[strike][6])
    sc, bc, sp, bp = float(df.iloc[strike][0]), float(df.iloc[strike+1][1]), float(df.iloc[strike][7]), float(df.iloc[strike-1][8])
    print('價平雙賣總收權利金',round((sc+sp-bc-bp),2) ,'，SC減BC權利金', round((sc - bc), 2) ,'，SP減BP權利金', round((sp - bp ), 2)) 
    if (sc+sp-bc-bp) >= premium:
        print(f'\n★ 權利金 >= {premium} 建議掛價委買'), print('= '*32)
        check.append(str(datetime.now().strftime("%H:%M:%S") + " 履約價在 " + str(df.iloc[strike][6])))
    else:
        print('= '*32)

    strike += 1 # 價內 1檔
    print('履約價：',df.iloc[strike][6])
    sc, bc, sp, bp = float(df.iloc[strike][0]), float(df.iloc[strike+1][1]), float(df.iloc[strike][7]), float(df.iloc[strike-1][8])
    print('價平雙賣總收權利金',round((sc+sp-bc-bp),2) ,'，SC減BC權利金', round((sc - bc), 2) ,'，SP減BP權利金', round((sp - bp ), 2))
    if (sc+sp-bc-bp) >= premium:
        print(f'\n★ 權利金 >= {premium} 建議掛價委買'), print('= '*32)
        check.append(str(datetime.now().strftime("%H:%M:%S") + " 履約價在 " + str(df.iloc[strike][6])))
    else:
        print('= '*32)

    strike += 1 # 價平
    print('履約價：',df.iloc[strike][6])
    sc, bc, sp, bp = float(df.iloc[strike][0]), float(df.iloc[strike+1][1]), float(df.iloc[strike][7]), float(df.iloc[strike-1][8])
    print('價平雙賣總收權利金',round((sc+sp-bc-bp),2) ,'，SC減BC權利金', round((sc - bc), 2) ,'，SP減BP權利金', round((sp - bp ), 2)) 
    if (sc+sp-bc-bp) >= premium:
        print(f'\n★ 權利金 >= {premium} 建議掛價委買'), print('= '*32)
        check.append(str(datetime.now().strftime("%H:%M:%S") + " 履約價在 " + str(df.iloc[strike][6])))
    else:
        print('= '*32)

    strike += 1  # 價外 1檔
    print('履約價：',df.iloc[strike][6])
    sc, bc, sp, bp = float(df.iloc[strike][0]), float(df.iloc[strike+1][1]), float(df.iloc[strike][7]), float(df.iloc[strike-1][8])
    print('價平雙賣總收權利金',round((sc+sp-bc-bp),2) ,'，SC減BC權利金', round((sc - bc), 2) ,'，SP減BP權利金', round((sp - bp ), 2)) 
    if (sc+sp-bc-bp) >= premium:
        print(f'\n★ 權利金 >= {premium} 建議掛價委買'), print('= '*32)
        check.append(str(datetime.now().strftime("%H:%M:%S") + " 履約價在 " + str(df.iloc[strike][6])))
    else:
        print('= '*32)

    strike += 1  # 價外 2檔
    print('履約價：',df.iloc[strike][6])
    sc, bc, sp, bp = float(df.iloc[strike][0]), float(df.iloc[strike+1][1]), float(df.iloc[strike][7]), float(df.iloc[strike-1][8])
    print('價平雙賣總收權利金',round((sc+sp-bc-bp),2) ,'，SC減BC權利金', round((sc - bc), 2) ,'，SP減BP權利金', round((sp - bp ), 2)) 
    if (sc+sp-bc-bp) >= premium:
        print(f'\n★ 權利金 >= {premium} 建議掛價委買'), print('= '*32)
        check.append(str(datetime.now().strftime("%H:%M:%S") + " 履約價在 " + str(df.iloc[strike][6])))
    else:
        print('= '*32)

    print(check)    
    time.sleep(5)