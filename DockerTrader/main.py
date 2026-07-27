import os
import time
import ccxt
import psycopg2
from dotenv import load_dotenv
from notifier import send_line_message

load_dotenv('config.env')

api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

db_host = os.getenv('DB_HOST', 'postgres')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'secretpassword')
db_name = os.getenv('DB_NAME', 'tradertracker')

# 初始化資料庫
def init_db():
    try:
        conn = psycopg2.connect(
            host=db_host, port=db_port, user=db_user, password=db_password, database=db_name
        )
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_prices (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMPTZ NOT NULL,
                symbol VARCHAR(20) NOT NULL,
                price NUMERIC NOT NULL
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("PostgreSQL 資料庫與表格初始化完成！")
    except Exception as e:
        print(f"資料庫初始化失敗: {e}")

init_db()

# 啟動時發送 LINE 通知
send_line_message(" DockerTrader 系統已成功啟動並進入階段三（風控與即時通知模式）！")

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'},
})
exchange.set_sandbox_mode(True)

print("DockerTrader 數據與風控服務運行中...")

error_count = 0

while True:
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        price = ticker['last']
        print(f"[{now_time}] 抓取 BTC/USDT 報價: {price}")

        # 寫入資料庫
        conn = psycopg2.connect(
            host=db_host, port=db_port, user=db_user, password=db_password, database=db_name
        )
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO market_prices (timestamp, symbol, price) VALUES (%s, %s, %s)",
            (now_time, 'BTC/USDT', price)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # 成功執行，重置錯誤計數
        error_count = 0

    except Exception as e:
        error_count += 1
        error_msg = f" [風控警告] 抓取報價發生異常: {e} (連續錯誤次數: {error_count})"
        print(error_msg)

        # 當連續錯誤超過 3 次，透過 LINE 發送緊急警報
        if error_count >= 3:
            send_line_message(error_msg)

    time.sleep(60)