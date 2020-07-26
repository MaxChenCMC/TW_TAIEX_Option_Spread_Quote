'''報錯 往往是盤後盤的cookie碼未更新'''
import requests, time, os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

k = input('加權指數價平在哪個履約價?')
mkt = input('查日盤(輸入1)還是夜盤(輸入2)?')
timeout = input('日, 時, 分(以符號或空格分隔)')

web    = 'https://info512.taifex.com.tw/Future/OptQuote_Norl.aspx'   # 日盤
web_pm = 'https://info512ah.taifex.com.tw/Future/OptQuote_Norl.aspx' # 盤後盤
cookie = '_ga=GA1.3.504299376.1594277634; ASP.NET_SessionId=mqbnoz0nw125qhgv540swhdq; BIGipServerPOOL_INFO512AH_TCP_80=1444286636.20480.0000' # 報錯往往就是這邊沒更新

# 只為了取盤中or盤後盤報價的len，還沒到真的爬蟲
if mkt == '1':
    df = pd.DataFrame(pd.read_html(web)[11])
elif mkt == '2':
    df = pd.DataFrame((pd.read_html( requests.get(web_pm, headers = {'Cookie': cookie}).text))[11])

premiums = []

for i in range(1, len(df)):
    while df.iloc[i][6] == k:
        
        # 每次迴圈都要重爬網站，抓最新報價，不能沿用while之前的df變數
        if mkt == '1':
            df = pd.DataFrame(pd.read_html(web)[11])
        elif mkt == '2':
            df = pd.DataFrame((pd.read_html( requests.get(web_pm, headers = {'Cookie': cookie}).text))[11])

        loc = i-2
        k_100c = float(df.iloc[loc][0]) - float(df.iloc[loc+1][1]) 
        k_100p = float(df.iloc[loc][7]) - float(df.iloc[loc-1][8])

        loc = i-1
        k_50c = float(df.iloc[loc][0]) - float(df.iloc[loc+1][1]) 
        k_50p = float(df.iloc[loc][7]) - float(df.iloc[loc-1][8])

        # 價平的call買 - 價外的call賣
        kparc = float(df.iloc[i][0]) - float(df.iloc[i+1][1]) # call的價外是往下 +1
        # 價平的put買 - 價外的put賣
        kparp = float(df.iloc[i][7]) - float(df.iloc[i-1][8]) # put的價外是往上 -1

        loc = i+1
        k50c = float(df.iloc[loc][0]) - float(df.iloc[loc+1][1]) 
        k50p = float(df.iloc[loc][7]) - float(df.iloc[loc-1][8])

        loc = i+2
        k100c = float(df.iloc[loc][0]) - float(df.iloc[loc+1][1]) 
        k100p = float(df.iloc[loc][7]) - float(df.iloc[loc-1][8])

        ts = datetime.now().strftime('%H:%M:%S') # 時間戳記

        k_100 = k_100c + k_100p # 負100點的履約價雙賣權利金
        k_50 = k_50c + k_50p    # 負50點的履約價雙賣權利金
        kpar = kparc + kparp    # 價平雙賣權利金
        k50 = k50c + k50p       # 正50點的履約價雙賣權利金
        k100 = k100c + k100p    # 正100點的履約價雙賣權利金

                 # 時間|跌100的履約價|跌50的履約價|價平的p 價平的履約價 價平的c|漲50的履約價|漲100的履約價 
        premium = [ ts,    k_100,       k_50,     kparp,    kpar,    kparc,       k50,        k100 ]  
        premiums.append(premium)  # 許多tuples裝進單一list，轉成df時會針對每個tuple變一個row
        res = pd.DataFrame( premiums, columns = ['time', 
                                                 f'{int(k)-100}', f'{int(k)-50}', 
                                                 'sp-bp', f'par@{k}', 'sc-bc', 
                                                 f'{int(k)+50}', f'{int(k)+100}'])
        res.set_index(['time'], inplace=True)
        print(res)
        print('='*61)

        # 若超過h點m分就停，設收盤時間
        if time.localtime()[2:5] >= (int(timeout[:2]), int(timeout[3:5]), int(timeout[6:8])):
            break
        else:
            time.sleep(60) # 休息60秒才重爬一次報價
            os.system("cls")

df = res.drop(['sp-bp', 'sc-bc'], axis =1)
print(df, f'\n完成於{datetime.now().strftime("%H:%M:%S")}')
df.plot() # 要畫圖定格，否則視窗直接閃退結束
plt.show()