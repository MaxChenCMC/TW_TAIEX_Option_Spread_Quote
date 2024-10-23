import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import requests
import os
import time
import pandas as pd
from datetime import datetime, timedelta
from threading import Thread
import queue

'''
要在title顯示last close與chg 才直觀
'''
# Create a queue for thread communication
# Separated data collection and plotting into different threads
data_queue = queue.Queue()


def strike_range_code(DispEName: str, mkt_type: str, contract_id: str, ExpireMonth: str) -> pd.DataFrame:
    '''
    RegularSession：https://mis.taifex.com.tw/futures/RegularSession/EquityIndices/Options/
    AfterHoursSession：https://mis.taifex.com.tw/futures/AfterHoursSession/EquityIndices/Options/
    F12查network裡的「getQuoteDetail」跟「getQuoteListOption」
    日盤與夜盤取最新成交價的"Request URL"都一樣，payload也一樣，只差在MarketType是0或1
    先產±1個履約價的Call與Put 共6個 DispEName
    '''
    try:
        # change per week contract
        if mkt_type == "0":
            arg1, arg2, arg3 = 'K', "F", "Q"
        elif mkt_type == "1":
            arg1, arg2, arg3 = 'K', "M", "R"

        res = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteDetail",
                            json={"SymbolID": [
                                "TXF-S", f"TXF{arg1}4-{arg2}", f"TXO-{arg3}"]}
                            ).json()["RtData"]['QuoteList'][1]
        QRTime = datetime.strptime(res["CTime"], '%H%M%S').strftime('%H:%M:%S')
        last_close = float(res['CLastPrice'])
        close_to_strike = int(last_close / 50) * 50
        stike_range_code = []
        for k in [(close_to_strike + i * 50) for i in range(-1, 2)]:
            stike_range_code.append(f'{DispEName + str(k)}C')
            stike_range_code.append(f'{DispEName + str(k)}P')

        quote_table = requests.post("https://mis.taifex.com.tw/futures/api/getQuoteListOption",
                                    json={"MarketType": mkt_type,
                                          "CID": contract_id,
                                          "ExpireMonth": ExpireMonth,
                                          "SymbolType": "O", "KindID": "1", "RowSize": "全部", "PageNo": "", "SortColumn": "", "AscDesc": "A"},
                                    ).json()["RtData"]['QuoteList']

        _temp = []
        for i in range(len(quote_table)):
            if quote_table[i]['DispEName'] in stike_range_code:
                _temp.append([
                    QRTime,
                    quote_table[i]['DispEName'][-6:-1],
                    (float(quote_table[i]['CBestAskPrice']) +
                     float(quote_table[i]['CBestBidPrice'])) / 2,
                    float(quote_table[i]['CBestAskPrice']) -
                    float(quote_table[i]['CBestBidPrice'])
                ])

        _df = pd.DataFrame(
            _temp, columns=['time', 'strike', 'mid_price', 'spread'])
        _df['strike'] = _df['strike'].astype(str)
        _df['mid_price'] = pd.to_numeric(_df['mid_price'])
        _df['spread'] = pd.to_numeric(_df['spread'])
        grouped_df = _df.groupby(['time', 'strike']).agg({
            'mid_price': 'sum',
            'spread': 'sum'
        }).reset_index()

        return grouped_df.sort_values(['time', 'strike'])

    except Exception as e:
        print(f"Data collection error: {e}")
        return None


def append_to_csv(df, filename):
    if df is not None:
        file_exists = os.path.isfile(filename)
        if file_exists:
            df.to_csv(filename, mode='a', header=False, index=False)
        else:
            df.to_csv(filename, mode='w', header=True, index=False)


def data_collection_thread():
    while True:
        try:
            df = strike_range_code("TX5W5104;", "0", "TXO", "202410W5")
            if df is not None:
                append_to_csv(df, 'premium.csv')
                data_queue.put(True)  # Signal that new data is available
            time.sleep(30)  # 爬的頻率
        except Exception as e:
            print(f"Data collection thread error: {e}")
            time.sleep(30)


def update_plot(frame):
    try:
        if os.path.exists('premium.csv'):
            data = pd.read_csv('premium.csv')
            data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S')

            plt.gca().clear()

            for strike in data['strike'].unique():
                strike_data = data[data['strike'] == strike]
                plt.plot(strike_data['time'], strike_data['mid_price'],
                         marker='o', label=f'Strike {strike}')

            plt.title('Call Put Premium')
            plt.legend(loc='upper right')
            plt.ylabel('mid_price')
            plt.grid(True)
            plt.xticks(rotation=45)

            if len(data) > 150:
                plt.xlim(data['time'].iloc[-150:].iloc[0],
                         data['time'].iloc[-1])

            plt.gcf().autofmt_xdate()
            plt.tight_layout()

    except Exception as e:
        print(f"Plot update error: {e}")


def main():
    # Start the data collection thread
    collection_thread = Thread(target=data_collection_thread, daemon=True)
    collection_thread.start()

    # Create and show the plot
    fig = plt.figure(figsize=(12, 6))
    # Update every 5 seconds
    ani = FuncAnimation(fig, update_plot, interval=15_000)
    plt.show()


if __name__ == "__main__":
    main()
