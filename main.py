import concurrent.futures
import yfinance as yf
import requests
import os


def threaded_filter(func, items, max_workers=20):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, item) for item in items]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                results.append(res)
    return results


def high_volume(symbol:str)-> list | None:
    symbol = symbol.strip().upper()+".NS"
    try:
        info = yf.Ticker(symbol).info
        volume = info.get("volume",0)
        ave_volume = info.get("averageDailyVolume10Day",0)
        price = info.get("regularMarketPrice",0)

        if price > 100 and price < 5000 and volume > 2*ave_volume:
            return list((symbol, price, round(volume/ave_volume,2)))
        else:
            return None
    except:
        return None

def send_message(msg):  
    try:
        url = os.getenv("URL")
        if isinstance(url, str) and url:
            response = requests.post(url=url, data=msg)
            response.raise_for_status()
            return ("success", msg)
        else:
            return ("error", msg)
    except requests.RequestException as e:
        return ("error", str(e))

stock_list=["ABB","ABCAPITAL","ADANIENSOL",
  "ADANIENT","ADANIGREEN","ADANIPORTS","ALKEM",
  "AMBER","AMBUJACEM","ANGELONE","APLAPOLLO",
  "APOLLOHOSP","ASHOKLEY","ASIANPAINT","ASTRAL",
  "AUBANK","AUROPHARMA","AXISBANK","BAJAJ-AUTO",
  "BAJAJFINSV","BAJFINANCE","BANDHANBNK","BANKBARODA",
  "BANKINDIA","BDL","BEL","BHARATFORG","BHARTIARTL",
  "BHEL","BIOCON","BLUESTARCO","BOSCHLTD","BPCL",
  "BRITANNIA","BSE","CAMS","CANBK","CDSL",
  "CGPOWER","CHOLAFIN","CIPLA","COALINDIA","COFORGE",
  "COLPAL","CONCOR","CROMPTON","CUMMINSIND","CYIENT",
  "DABUR","DALBHARAT","DELHIVERY","DIVISLAB","DIXON",
  "DLF","DMART","DRREDDY","EICHERMOT","ETERNAL",
  "EXIDEIND","FEDERALBNK","FORTIS","GAIL","GLENMARK",
  "GMRAIRPORT","GODREJCP","GODREJPROP","GRASIM","HAL",
  "HAVELLS","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE",
  "HEROMOTOCO","HFCL","HINDALCO","HINDPETRO","HINDUNILVR",
  "HINDZINC","HUDCO","ICICIBANK","ICICIGI","ICICIPRULI",
  "IDEA","IDFCFIRSTB","IEX","IGL","IIFL",
  "INDHOTEL","INDIANB","INDIGO","INDUSINDBK","INDUSTOWER",
  "INFY","INOXWIND","IOC","IRCTC","IREDA",
  "IRFC","ITC","JINDALSTEL","JIOFIN","JSWENERGY",
  "JSWSTEEL","JUBLFOOD","KALYANKJIL","KAYNES","KEI",
  "KFINTECH","KOTAKBANK","KPITTECH","LAURUSLABS","LICHSGFIN",
  "LICI","LODHA","LT","LTF","LTIM",
  "LUPIN","M&M","MANAPPURAM","MANKIND","MARICO",
  "MARUTI","MAXHEALTH","MAZDOCK","MCX","MFSL",
  "MOTHERSON","MPHASIS","MUTHOOTFIN","NATIONALUM","NAUKRI",
  "NBCC","NCC","NESTLEIND","NHPC","NMDC",
  "NTPC","NUVAMA","NYKAA","OBEROIRLTY","OFSS",
  "OIL","ONGC","PAGEIND","PATANJALI","PAYTM",
  "PERSISTENT","PETRONET","PFC","PGEL","PHOENIXLTD",
  "PIDILITIND","PIIND","PNB","PNBHOUSING","POLICYBZR",
  "POLYCAB","POWERGRID","PPLPHARMA","PRESTIGE","RBLBANK",
  "RECLTD","RELIANCE","RVNL","SAIL","SAMMAANCAP",
  "SBICARD","SBILIFE","SBIN","SHREECEM","SHRIRAMFIN",
  "SIEMENS","SOLARINDS","SONACOMS","SRF","SUNPHARMA",
  "SUPREMEIND","SUZLON","SYNGENE","TATACHEM","TATACONSUM",
  "TATAELXSI","TATAMOTORS","TATAPOWER","TATASTEEL","TATATECH",
  "TCS","TECHM","TIINDIA","TITAGARH","TITAN",
  "TORNTPHARM","TORNTPOWER","TRENT","TVSMOTOR","ULTRACEMCO",
  "UNIONBANK","UNITDSPR","UNOMINDA","UPL","VBL",
  "VEDL","VOLTAS","WIPRO","YESBANK","ZYDUSLIFE"
]

results = threaded_filter(high_volume, stock_list)
if results:
    sortedList = sorted(results, key=lambda x: x[2], reverse=True)
    msg = "\n".join([f"{item[0]}: {item[1]} - ({item[2]}x)" for item in sortedList])
else:
    msg = "No results"

send = send_message(msg)
print(send[0])
print(send[1])
