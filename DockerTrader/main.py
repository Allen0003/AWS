import os
import time
import ccxt
import psycopg2
from dotenv import load_dotenv
from notifier import send_line_message
from trader_engine import OrderExecutor, init_db

# 載入 config.env
load_dotenv('config.env')

# 讀取 API 金鑰
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

# 從 config.env 讀取資料庫設定
db_host = os.getenv('DB_HOST', 'postgres')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'secretpassword')
db_name = os.getenv('DB_NAME', 'tradertracker')

# 1. 程式一開始啟動時，先初始化資料庫
print("正在初始化資料庫...")
init_db(
    db_host=db_host,
    db_port=db_port,
    db_user=db_user,
    db_password=db_password,
    db_name=db_name
)


print(f"DEBUG - 讀到的 API Key 長度: {len(api_key) if api_key else 0}")
print(f"DEBUG - 讀到的 API Key 開頭: {api_key[:5]}...")


print(f"DEBUG - 讀到的 secret_key 長度: {len(secret_key) if api_key else 0}")
print(f"DEBUG - 讀到的 secret_key 開頭: {secret_key[:5]}...")


# 初始化交易所 (已移除被幣安廢棄的 set_sandbox_mode)
# 初始化交易所
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'},
})

# 強制將期貨與現貨網址指向幣安最新的 Demo 模擬環境
exchange.urls['api'] = {
    'public': 'https://demo-api.binance.com/api/v3',
    'private': 'https://demo-api.binance.com/api/v3',
    'v1': 'https://demo-api.binance.com/api/v1',
    'fapiPublic': 'https://demo-api.binance.com/fapi/v1',
    'fapiPrivate': 'https://demo-api.binance.com/fapi/v1',
    'fapiPublicV2': 'https://demo-api.binance.com/fapi/v2',
    'fapiPrivateV2': 'https://demo-api.binance.com/fapi/v2',
    'fapiPublicV3': 'https://demo-api.binance.com/fapi/v3',
    'fapiPrivateV3': 'https://demo-api.binance.com/fapi/v3',
    'fapiData': 'https://demo-api.binance.com/futures/data',
}


print(f"DEBUG - 交易所網址設定: {exchange.urls['api']}")


# 實例化下單與風控引擎
executor = OrderExecutor(exchange)

send_line_message("DockerTrader 階段三：下單模組與風險控管系統已全面啟動！")

error_count = 0
symbol = 'BTC/USDT'
has_tested_order = False  # 用來示範啟動後執行一次測試下單

while True:
    try:
        ticker = exchange.fetch_ticker(symbol)
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        price = ticker['last']
        print(f"[{now_time}] 正常運行中 - {symbol} 報價: {price}")

        # 寫入資料庫
        conn = psycopg2.connect(
            host=db_host, port=db_port, user=db_user, password=db_password, database=db_name
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO market_prices (timestamp, symbol, price) VALUES (%s, %s, %s)",
            (now_time, symbol, price)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # 階段三實戰功能：系統啟動後，示範發送一筆小額限價單來測試下單模組
        if not has_tested_order:
            print("正在進行階段三下單功能測試...")
            test_limit_price = round(price * 0.9, 2)
            executor.create_limit_order(symbol=symbol, side='buy', amount=0.001, price=test_limit_price)
            has_tested_order = True

        # 成功連線，重置錯誤計數
        error_count = 0

    except Exception as e:
        error_count += 1
        err_msg = f"[連線異常警報] 抓取報價失敗: {e} (連續錯誤: {error_count})"
        print(err_msg)

        # 連續錯誤達 3 次以上，發送 LINE 並啟動安全風控（自動平倉）
        if error_count >= 3:
            send_line_message(err_msg + "\n達到連續錯誤閾值，系統啟動防禦機制！")
            executor.emergency_close_all(symbol)

    time.sleep(60)