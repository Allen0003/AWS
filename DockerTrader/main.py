import os
import time
ccxt = __import__('ccxt')
from dotenv import load_dotenv


load_dotenv(dotenv_path='config.env')


api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

# 初始化交易所
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'},
})

# 開啟測試網模式
exchange.set_sandbox_mode(True)

print("DockerTrader 啟動成功，開始抓取報價...")

while True:
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S' )}] BTC/USDT 報價: {ticker['last']}")
    except Exception as e:
        print(f"發生錯誤: {e}")
    time.sleep(5)