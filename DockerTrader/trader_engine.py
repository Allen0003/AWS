import ccxt
from notifier import send_line_message
import psycopg2

class RiskManager:
    def __init__(self, max_position_usdt=100.0, max_loss_limit=50.0):
        self.max_position_usdt = max_position_usdt  # 總資金部位上限 (USDT)
        self.max_loss_limit = max_loss_limit        # 單筆或累計最大虧損限制

    def check_position_limit(self, current_position_value: float) -> bool:
        """檢查是否超過總資金部位上限"""
        if current_position_value > self.max_position_usdt:
            send_line_message(f"[風控攔截] 當前部位價值 {current_position_value} USDT 已超過上限 ({self.max_position_usdt} USDT)，禁止開新倉！")
            return False
        return True


class OrderExecutor:
    def __init__(self, exchange_instance: ccxt.Exchange):
        self.exchange = exchange_instance
        self.risk_manager = RiskManager()

    def create_market_order(self, symbol: str, side: str, amount: float):
        """實作市價單 (Market Order)"""
        try:
            # 取得當前價格估算部位大小
            ticker = self.exchange.fetch_ticker(symbol)
            est_value = ticker['last'] * amount

            # 執行風控檢查
            if side == 'buy' and not self.risk_manager.check_position_limit(est_value):
                return None

            print(f"正在發送市價單: {side} {amount} {symbol}...")
            order = self.exchange.create_order(symbol, 'market', side, amount)

            msg = f"[市價單成交回报]\n交易對: {symbol}\n方向: {side.upper()}\n數量: {amount}\n成交ID: {order.get('id')}"
            print(msg)
            send_line_message(msg)
            return order
        except Exception as e:
            err_msg = f" [下單錯誤] 市價單發送失敗 ({symbol}): {e}"
            print(err_msg)
            send_line_message(err_msg)
            return None

    def create_limit_order(self, symbol: str, side: str, amount: float, price: float):
        """實作限價單 (Limit Order)"""
        try:
            print(f"正在發送限價單: {side} {amount} {symbol} @ {price}...")
            order = self.exchange.create_order(symbol, 'limit', side, amount, price)

            msg = f"[限價單掛單回报]\n交易對: {symbol}\n方向: {side.upper()}\n數量: {amount}\n價格: {price}\n掛單ID: {order.get('id')}"
            print(msg)
            send_line_message(msg)
            return order
        except Exception as e:
            err_msg = f"[下單錯誤] 限價單發送失敗 ({symbol}): {e}"
            print(err_msg)
            send_line_message(err_msg)
            return None

    def emergency_close_all(self, symbol: str):
        """API 連線中斷或觸發重大風險時的自動平倉/緊急處置機制"""
        try:
            send_line_message(f"[緊急風控] 觸發自動平倉機制，正在強制關閉 {symbol} 所有部位...")
            # 查詢當前持倉部位
            positions = self.exchange.fetch_positions([symbol])
            for p in positions:
                contracts = float(p.get('contracts', 0))
                if contracts > 0:
                    side = 'sell' if p['side'] == 'long' else 'buy'
                    self.exchange.create_order(symbol, 'market', side, contracts)
                    send_line_message(f"⚠[已強制平倉] {symbol} 數量: {contracts}")
        except Exception as e:
            send_line_message(f"[緊急平倉失敗] 無法自動平倉: {e}")


def init_db(db_host, db_port, db_user, db_password, db_name):
    """
    初始化資料庫與建立資料表
    """
    try:
        # 使用傳進來的變數進行連線
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # 建立資料表
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
