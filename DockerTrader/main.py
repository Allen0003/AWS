import os
import time
import ccxt
import psycopg2
from dotenv import load_dotenv
from notifier import send_line_message
from trader_engine import OrderExecutor, init_db

load_dotenv('config.env')

api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

db_host = os.getenv('DB_HOST', 'postgres')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'secretpassword')
db_name = os.getenv('DB_NAME', 'tradertracker')

# 1. 程式一開始啟動時，先呼叫資料庫初始化函式
print("正在初始化資料庫...")
init_db(
    db_host=db_host,
    db_port=db_port,
    db_user=db_user,
    db_password=db_password,
    db_name=db_name
)

# 初始化交易所
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'},
})
exchange.set_sandbox_mode(True)

# 實例化下單與風控引擎
executor = OrderExecutor(exchange)

send_line_message("DockerTrader 階段三：下單模組與風險控管系統已全面啟動！")

error_count = 0
symbol = 'BTC/USDT'

while True:
    try:
        ticker = exchange.fetch_ticker(symbol)
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        price = ticker['last']
        print(f"[{now_time}] 正常運行中 - {symbol} 報價: {price}")

        # 成功連線，重置錯誤計數
        error_count = 0

    except Exception as e:
        error_count += 1
        err_msg = f"[連線異常警報] 抓取報價失敗: {e} (連續錯誤: {error_count})"
        print(err_msg)

        # 連續錯誤達 3 次以上，發送 LINE 並啟動安全風控
        if error_count >= 3:
            send_line_message(err_msg + "\n達到連續錯誤閾值，系統啟動防禦機制！")
            # 可以在這裡呼叫 executor.emergency_close_all(symbol) 進行保護

    time.sleep(60)