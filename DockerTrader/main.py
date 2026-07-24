import os
import time
import ccxt
import psycopg2
from dotenv import load_dotenv

load_dotenv('config.env')

# 讀取環境變數
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'secretpassword')
db_name = os.getenv('DB_NAME', 'tradertracker')

# 初始化 PostgreSQL 連線並建立表格
def init_db():
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

init_db()

# 初始化交易所
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'future'},
})
exchange.set_sandbox_mode(True)

print("DockerTrader 資料收集服務啟動...")

while True:
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        price = ticker['last']
        print(f"[{now_time}] 抓取 BTC/USDT 報價: {price}，準備寫入資料庫...")

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

    except Exception as e:
        print(f"發生錯誤: {e}")

    # 每 60 秒搜集一次
    time.sleep(60)