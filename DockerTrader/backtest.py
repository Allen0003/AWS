import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv('config.env')

# 讀取資料庫連線資訊（直接對應 docker-compose 的設定）
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD', 'secretpassword')
db_name = os.getenv('DB_NAME', 'tradertracker')

print("正在從 PostgreSQL 讀取歷史報價資料...")

# 1. 連線並把資料讀進 Pandas DataFrame
conn = psycopg2.connect(
    host=db_host, port=db_port, user=db_user, password=db_password, database=db_name
)
query = "SELECT timestamp, price FROM market_prices WHERE symbol = 'BTC/USDT' ORDER BY timestamp ASC;"
df = pd.read_sql(query, conn)
conn.close()

if len(df) < 30:
    print(f"目前資料量只有 {len(df)} 筆，建議讓資料庫再收集多一點（至少 30~50 筆以上）再來跑回測比較準確喔！")
else:
    print(f"成功載入 {len(df)} 筆歷史數據，開始進行回測分析...")

    # 2. 資料前處理
    df['price'] = df['price'].astype(float)

    # 3. 設定雙均線參數 (假設我們的資料是一分鐘一筆，短期用 5 根，長期用 20 根)
    short_window = 5
    long_window = 20

    df['short_ma'] = df['price'].rolling(window=short_window).mean()
    df['long_ma'] = df['price'].rolling(window=long_window).mean()

    # 4. 產生交易訊號 (1 = 多單/買進, -1 = 空單/賣出, 0 = 觀望)
    df['signal'] = 0
    df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1
    df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1

    # 5. 計算策略報酬率
    df['market_return'] = df['price'].pct_change() # 市場本身漲跌幅
    df['strategy_return'] = df['market_return'] * df['signal'].shift(1) # 策略報酬

    # 6. 計算累積績效
    df['cum_market_return'] = (1 + df['market_return'].fillna(0)).cumprod() - 1
    df['cum_strategy_return'] = (1 + df['strategy_return'].fillna(0)).cumprod() - 1

    print("\n========== 回測結果摘要 ==========")
    print(f"回測起始時間: {df['timestamp'].iloc[0]}")
    print(f"回測結束時間: {df['timestamp'].iloc[-1]}")
    print(f"市場同期累積漲跌幅: {df['cum_market_return'].iloc[-1]*100:.2f}%")
    print(f"雙均線策略累積報酬率: {df['cum_strategy_return'].iloc[-1]*100:.2f}%")
    print("==================================")