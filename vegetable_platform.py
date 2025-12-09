import streamlit as st
import sqlite3
import pandas as pd
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta, datetime
import calendar 
import qrcode
from io import BytesIO
import base64

# --- 0. 網址設定 (已修正) ---
# 這是您部署後的網址，手機掃描 QR Code 會連到這裡
BASE_URL = "https://6dncbvkaysqdeasn6qrtfv.streamlit.app/" 

# --- 1. 網頁全域設定 ---
st.set_page_config(
    page_title="原鄉蔬菜箱數位平台",
    page_icon="🥦", # 已移除 Emoji
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS 美化與關鍵修復 ---
st.markdown("""
    <style>
    /* 調整頂部留白 */
    .block-container { padding-top: 3.5rem; padding-bottom: 5rem; }
    
    /* 卡片式設計 */
    .metric-card {
        background-color: white; border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center;
    }
    
    /* 農民端轉盤結果卡片 */
    .result-card {
        background-color: #e8f5e9; border: 3px solid #2e7d32;
        border-radius: 15px; padding: 20px; text-align: center;
        margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: pop-in 0.5s ease-out;
        color: #1b5e20 !important; 
    }
    .result-card h2, .result-card h1, .result-card p, .result-card div, .result-card span { color: #1b5e20 !important; }
    @keyframes pop-in { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
    
    /* CSS 轉盤 (動畫用) */
    .css-wheel {
        /* [調整] 轉盤大小：若修改這裡，下方的 top 定位也需要配合調整 (通常是高度的一半) */
        width: 350px; 
        height: 350px; 
        border-radius: 50%; 
        margin: 0 auto;
        border: 8px solid white; 
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        background: conic-gradient(#FF9AA2 0deg 72deg, #FFB7B2 72deg 144deg, #FFDAC1 144deg 216deg, #E2F0CB 216deg 288deg, #B5EAD7 288deg 360deg);
        animation: spin-infinite 0.2s linear infinite;
    }
    @keyframes spin-infinite { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* 天氣卡片 */
    .weather-card {
        background: linear-gradient(135deg, #6dd5ed 0%, #2193b0 100%);
        color: white; padding: 15px; border-radius: 12px; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 100%;
    }
    .weather-title { font-size: 0.9rem; opacity: 0.9; }
    .weather-temp { font-size: 1.8rem; font-weight: bold; }
    
    /* 預估箱數卡片 */
    .box-est-card {
        background: linear-gradient(135deg, #81c784 0%, #43a047 100%);
        color: white; padding: 15px; border-radius: 12px; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 100%;
    }
    
    /* --- [關鍵修改] 轉盤按鈕置中 --- */

    /* 步驟1: 隱藏標記本身 */
    div[data-testid="stMarkdownContainer"] p span#spin-btn-marker {
        display: none;
    }

    /* 步驟2: 定位父容器 */
    div[data-testid="stVerticalBlock"]:has(#spin-btn-marker) {
        position: relative !important;
        display: flex;
        flex-direction: column;
        align-items: center; 
    }

    /* 步驟3: 強制定位按鈕 (GO! 按鈕) */
    div[data-testid="stVerticalBlock"]:has(#spin-btn-marker) .stButton > button {
        position: absolute !important;
        
        /* [調整] 定位高度：如果你改了轉盤大小，這裡要設為轉盤高度的一半 (例如 350/2 = 175) */
        /* 如果你習慣用負值定位 (例如 top: -205px)，也可以改這裡，但正值定位在父容器內比較穩定 */
        top: -206px !important;  
        left: 50% !important;   
        transform: translate(-50%, -50%) !important; /* 這行確保按鈕的中心點對準座標，不用改 */
        z-index: 999 !important; 
        
        /* [調整] 按鈕大小：修改這兩個數值 (必須相同) 來改變半徑 */
        /* 例如：想要半徑 60px，就把這裡改成 120px */
        width: 100px !important;
        height: 100px !important;
        
        border-radius: 50% !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        font-family: 'Arial', sans-serif !important;
        background: radial-gradient(circle at 30% 30%, #ff8a65 0%, #d84315 100%) !important;
        color: white !important;
        border: 5px solid white !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
        transition: transform 0.1s, box-shadow 0.2s !important;
    }

    div[data-testid="stVerticalBlock"]:has(#spin-btn-marker) .stButton > button:active {
        transform: translate(-50%, -50%) scale(0.95) !important;
        background: #bf360c !important;
    }
    
    div[data-testid="stVerticalBlock"]:has(#spin-btn-marker) .stButton > button:hover {
        box-shadow: 0 0 20px rgba(255, 138, 101, 0.6) !important;
        border-color: #fff3e0 !important;
    }

    .modebar { display: none !important; }
    
    /* 自定義側邊欄樣式 */
    [data-testid="stSidebar"] { background-color: #f8f9fa; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { 
        color: #333333 !important; 
    }
    [data-testid="stSidebar"] button p, [data-testid="stSidebar"] button span { color: unset !important; }
    
    /* 庫存狀態標籤 */
    .stock-ready { color: #2e7d32; font-weight: bold; background: #e8f5e9; padding: 2px 8px; border-radius: 4px; }
    .stock-future { color: #f57f17; font-weight: bold; background: #fffde7; padding: 2px 8px; border-radius: 4px; }
    
    /* 表格標題列樣式 */
    .table-header { font-weight: bold; background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    
    /* 訂單列樣式 */
    .order-row { padding: 10px 0; border-bottom: 1px solid #eee; align-items: center; }
    .order-row-active { background-color: #f0f8ff; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 資料庫與設定 ---
DB_FILE = 'vegetable_system_v8.db' 

# 【核心設定】各類別的「單份」標準重量 (單位: 公克 g)
WEIGHT_CONFIG = {
    "短期葉菜": 250,    
    "中長期葉菜": 500, 
    "根莖類": 500,      
    "瓜果類": 500,      
    "豆科": 500        
}

# 蔬菜箱配方
BOX_CONFIG = {
    "標準蔬菜箱": {
        "短期葉菜": 2, 
        "中長期葉菜": 1,
        "根莖類": 1, 
        "瓜果類": 1, 
        "豆科": 1
    }
}

PLAN_OPTIONS = {
    "單次訂購": "one_time",
    "每月配送一次": "monthly",
    "每月配送兩次": "bi_monthly"
}

PLAN_LABELS = {v: k for k, v in PLAN_OPTIONS.items()}
# 反向對照表
PLAN_CODES = {k: v for k, v in PLAN_OPTIONS.items()}

def format_weight(grams):
    """將公克轉為適合閱讀的單位"""
    if grams >= 1000:
        return f"{grams/1000:.1f} kg"
    return f"{grams} g"

def get_week_label(date_val):
    """將日期轉換為週次標籤 (YYYY-Wxx (MM/DD~MM/DD))"""
    if pd.isna(date_val): return "Unknown"
    if isinstance(date_val, str):
        try:
            date_val = pd.to_datetime(date_val).date()
        except:
            return "Unknown"
    if isinstance(date_val, datetime):
        date_val = date_val.date()
        
    start = date_val - timedelta(days=date_val.weekday())
    end = start + timedelta(days=6)
    # ISO week number
    week_num = date_val.isocalendar()[1]
    return f"{start.year}-W{week_num:02d} ({start.strftime('%m/%d')}~{end.strftime('%m/%d')})"

def get_first_shipping_date(reg_date, tribe):
    """
    計算首次合規出貨日 (物流邏輯核心)
    羅娜: 週三 (weekday=2)
    雙龍: 週四 (weekday=3)
    邏輯: 若註冊日 <= 出貨日 -> 本週出貨; 否則 -> 下週出貨
    """
    target_weekday = 2 if "羅娜" in tribe else 3
    reg_weekday = reg_date.weekday()
    
    # 計算本週的該出貨日
    this_week_ship = reg_date + timedelta(days=(target_weekday - reg_weekday))
    
    if reg_date <= this_week_ship:
        return this_week_ship
    else:
        return this_week_ship + timedelta(days=7)

def get_conn():
    # 增加 timeout 避免 database is locked
    return sqlite3.connect(DB_FILE, timeout=10)

# --- 新增輔助函式：產生 QR Code Base64 字串 ---
def get_qr_code_base64(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# --- 新增輔助函式：更新下次出貨日 ---
def update_next_delivery(sub_id, next_date):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("UPDATE subscriptions SET next_delivery_date = ? WHERE id = ?", (next_date, sub_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"更新失敗: {e}")
        return False
    finally:
        conn.close()

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        # 新增 feedback 表格
        tables = [
            "planting_logs", "orders", "allocations", "crops", "farmers", 
            "customers", "subscriptions", "subscription_preferences", "subscription_skips",
            "feedback"
        ]
        for t in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {t}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT, category TEXT, growth_days INTEGER, harvest_window INTEGER, 
                unit_yield_g REAL, 
                tray_size INTEGER DEFAULT 128,
                quota_shuanglong INTEGER DEFAULT 0, quota_luona INTEGER DEFAULT 0
            )
        """)
        cursor.execute("CREATE TABLE IF NOT EXISTS farmers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, tribe_location TEXT, phone TEXT)")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planting_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, farmer_id INTEGER, crops_id INTEGER, 
                plant_date DATE, estimated_harvest_date DATE, 
                quantity_planted_g INTEGER, 
                remaining_qty_g INTEGER,
                status TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, address TEXT, 
                default_tribe_location TEXT, created_at DATE DEFAULT CURRENT_DATE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, plan_name TEXT, 
                frequency TEXT, start_date DATE, status TEXT DEFAULT 'active',
                next_delivery_date DATE
            )
        """)
        cursor.execute("CREATE TABLE IF NOT EXISTS subscription_preferences (id INTEGER PRIMARY KEY AUTOINCREMENT, subscription_id INTEGER, pref_type TEXT, item_name TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS subscription_skips (id INTEGER PRIMARY KEY AUTOINCREMENT, subscription_id INTEGER, skip_date DATE)")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT, subscription_id INTEGER, customer_id INTEGER, 
                customer_name TEXT, tribe_location TEXT, delivery_date DATE, box_type TEXT, 
                status TEXT, matched_log_id TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, planting_log_id INTEGER, 
                crop_name TEXT, weight_allocated_g INTEGER, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 新增回饋表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_id INTEGER,
                rating INTEGER,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # --- 注入種子數據 ---
        vegetables_data = [
            ('紅蘿蔔', '根莖類', 60, 14, 250, 72), ('白蘿蔔', '根莖類', 50, 14, 800, 72), ('甜菜根', '根莖類', 50, 14, 300, 72),
            ('粉豆', '豆科', 50, 30, 500, 72), ('四季豆', '豆科', 50, 30, 400, 72), ('長豆', '豆科', 50, 30, 500, 72), 
            ('甜豌豆', '豆科', 60, 45, 300, 72), ('大夾豌豆', '豆科', 60, 45, 300, 72),
            ('大黃瓜', '瓜果類', 50, 25, 800, 24), ('小黃瓜', '瓜果類', 50, 25, 600, 24), ('南瓜', '瓜果類', 80, 30, 2000, 24), 
            ('絲瓜', '瓜果類', 80, 45, 1500, 24), ('苦瓜', '瓜果類', 80, 30, 600, 24), ('茄子', '瓜果類', 80, 30, 1000, 24), 
            ('青椒', '瓜果類', 80, 30, 600, 24), ('甜玉米', '瓜果類', 60, 10, 400, 72), ('秋葵', '瓜果類', 30, 45, 500, 24),
            ('高麗菜', '中長期葉菜', 60, 14, 1500, 50), ('大白菜', '中長期葉菜', 50, 14, 1200, 50), ('皇宮菜', '中長期葉菜', 30, 60, 400, 72), 
            ('地瓜葉', '中長期葉菜', 60, 90, 500, 72), ('芹菜', '中長期葉菜', 60, 14, 200, 128), ('芥菜', '中長期葉菜', 45, 10, 600, 72), 
            ('青蔥', '中長期葉菜', 60, 30, 150, 128), ('蒜苗', '中長期葉菜', 50, 14, 150, 128), ('青花椰', '中長期葉菜', 80, 14, 500, 50),
            ('小白菜', '短期葉菜', 35, 5, 120, 128), ('青江菜', '短期葉菜', 35, 5, 100, 128), ('空心菜', '短期葉菜', 30, 10, 150, 128), 
            ('小松菜', '短期葉菜', 35, 5, 120, 128), ('黑葉白菜', '短期葉菜', 35, 5, 120, 128), ('塔菇菜', '短期葉菜', 40, 7, 120, 128), 
            ('格藍菜', '短期葉菜', 40, 7, 150, 128), ('福山萵苣', '短期葉菜', 40, 7, 150, 128), ('羅曼', '短期葉菜', 40, 7, 150, 128)
        ]
        cursor.executemany("INSERT INTO crops (name, category, growth_days, harvest_window, unit_yield_g, tray_size) VALUES (?, ?, ?, ?, ?, ?)", vegetables_data)
        
        cursor.execute("INSERT INTO farmers (name, tribe_location, phone) VALUES ('王大伯', '雙龍部落', '0912-333-444'), ('李阿姨', '羅娜部落', '0922-555-666'), ('高大哥', '雙龍部落', '0933-777-888')")
        cursor.execute("INSERT INTO customers (name, phone, address, default_tribe_location) VALUES ('陳小姐', '0911-000-111', '台中市西屯區', '雙龍部落')")
        cursor.execute("INSERT INTO customers (name, phone, address, default_tribe_location) VALUES ('林先生', '0922-111-222', '南投縣信義鄉', '羅娜部落')")
        
        today = date.today()
        
        # 陳小姐 (雙龍，週四)
        target_weekday = 3 # Thu
        days_diff = (target_weekday - today.weekday() + 7) % 7
        start_d_1 = today + timedelta(days=days_diff)
        next_d_1 = start_d_1 + timedelta(days=28) # 下個月
        
        # 林先生 (羅娜，週三)
        target_weekday = 2 # Wed
        days_diff = (target_weekday - today.weekday() + 7) % 7
        start_d_2 = today + timedelta(days=days_diff)
        next_d_2 = start_d_2 + timedelta(days=14) # 兩週後

        # 預設 next_delivery_date 為空 (None)，等待後續操作填入
        cursor.execute("INSERT INTO subscriptions (customer_id, plan_name, frequency, start_date, status, next_delivery_date) VALUES (1, '標準蔬菜箱', 'monthly', ?, 'active', NULL)", (start_d_1,))
        cursor.execute("INSERT INTO subscriptions (customer_id, plan_name, frequency, start_date, status, next_delivery_date) VALUES (2, '標準蔬菜箱', 'bi_monthly', ?, 'active', NULL)", (start_d_2,))
        cursor.execute("INSERT INTO subscription_preferences (subscription_id, pref_type, item_name) VALUES (1, 'dislike', '苦瓜')")

        cursor.execute("SELECT id FROM crops ORDER BY RANDOM() LIMIT 8")
        for (cid,) in cursor.fetchall(): cursor.execute("UPDATE crops SET quota_shuanglong = 1 WHERE id = ?", (cid,))
        cursor.execute("SELECT id FROM crops ORDER BY RANDOM() LIMIT 9")
        for (cid,) in cursor.fetchall(): cursor.execute("UPDATE crops SET quota_luona = 1 WHERE id = ?", (cid,))
        
        conn.commit()
    except Exception as e:
        st.error(f"資料庫初始化失敗: {e}")
    finally:
        conn.close()

def clear_history():
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM planting_logs")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='planting_logs'")
        cursor.execute("DELETE FROM allocations") 
        cursor.execute("DELETE FROM orders") 
        cursor.execute("DELETE FROM feedback")
        cursor.execute("UPDATE crops SET quota_shuanglong = 0, quota_luona = 0")
        cursor.execute("SELECT id FROM crops ORDER BY RANDOM() LIMIT 8")
        for (cid,) in cursor.fetchall(): cursor.execute("UPDATE crops SET quota_shuanglong = 1 WHERE id = ?", (cid,))
        cursor.execute("SELECT id FROM crops ORDER BY RANDOM() LIMIT 9")
        for (cid,) in cursor.fetchall(): cursor.execute("UPDATE crops SET quota_luona = 1 WHERE id = ?", (cid,))
        conn.commit()
    except Exception as e:
        st.error(f"清空資料失敗: {e}")
    finally:
        conn.close()

def get_df(query, params=None):
    conn = get_conn()
    try: return pd.read_sql(query, conn, params=params)
    except: return pd.DataFrame()
    finally: conn.close()

def calculate_supply_forecast(weeks=4):
    conn = get_conn()
    today = date.today()
    end_date = today + timedelta(weeks=weeks)
    
    sql = """
        SELECT c.category, pl.estimated_harvest_date, pl.remaining_qty_g, f.tribe_location
        FROM planting_logs pl
        JOIN crops c ON pl.crops_id = c.id
        JOIN farmers f ON pl.farmer_id = f.id
        WHERE pl.status = '生長中' AND pl.remaining_qty_g > 0
    """
    try:
        df = pd.read_sql(sql, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    
    if df.empty: return pd.DataFrame()
    
    try:
        df['estimated_harvest_date'] = pd.to_datetime(df['estimated_harvest_date']).dt.date
        df = df[(df['estimated_harvest_date'] >= today) & (df['estimated_harvest_date'] <= end_date)]
        df['week_start'] = df['estimated_harvest_date'].apply(lambda x: x - timedelta(days=x.weekday()))
        df['remaining_qty_kg'] = df['remaining_qty_g'] / 1000.0
        supply_agg = df.groupby(['week_start', 'category'])['remaining_qty_kg'].sum().reset_index()
        return supply_agg
    except:
        return pd.DataFrame()

def calculate_demand_forecast(weeks=4):
    conn = get_conn()
    today = date.today()
    end_date = today + timedelta(weeks=weeks)
    
    try:
        subs = pd.read_sql("""
            SELECT s.id, s.plan_name, s.frequency, s.start_date, c.default_tribe_location
            FROM subscriptions s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.status = 'active'
        """, conn)
        skips = pd.read_sql("SELECT subscription_id, skip_date FROM subscription_skips", conn)
    except:
        conn.close()
        return pd.DataFrame()

    if not skips.empty:
        skips['skip_date'] = pd.to_datetime(skips['skip_date']).dt.date
    
    conn.close()
    
    demand_rows = []
    if subs.empty: return pd.DataFrame()

    for _, sub in subs.iterrows():
        plan = BOX_CONFIG.get(sub['plan_name'], BOX_CONFIG["標準蔬菜箱"])
        try:
            start_date = pd.to_datetime(sub['start_date']).date()
            # 計算首次合規出貨日作為排程基準
            first_ship = get_first_shipping_date(start_date, sub['default_tribe_location'])
        except: continue

        if sub['frequency'] == 'one_time':
            freq_days = 9999 
        elif sub['frequency'] == 'monthly':
            freq_days = 28 
        elif sub['frequency'] == 'bi_monthly':
            freq_days = 14 
        else:
            freq_days = 7

        current_d = first_ship # 從首次合規日開始推算
        
        while current_d <= end_date:
            if current_d >= today: # 只預測未來的
                is_skipped = False
                if not skips.empty:
                    is_skipped = not skips[(skips['subscription_id'] == sub['id']) & (skips['skip_date'] == current_d)].empty
                
                if not is_skipped:
                    week_start = current_d - timedelta(days=current_d.weekday())
                    for cat, packs in plan.items():
                        unit_weight = WEIGHT_CONFIG.get(cat, 500)
                        total_weight_g = packs * unit_weight
                        
                        demand_rows.append({
                            'week_start': week_start,
                            'category': cat,
                            'required_qty_kg': total_weight_g / 1000.0,
                            'tribe_location': sub['default_tribe_location']
                        })
            current_d += timedelta(days=freq_days)
            
    if not demand_rows: return pd.DataFrame()
    demand_df = pd.DataFrame(demand_rows)
    demand_agg = demand_df.groupby(['week_start', 'category'])['required_qty_kg'].sum().reset_index()
    return demand_agg

def calculate_possible_boxes(tribe):
    conn = get_conn()
    today = date.today()
    
    sql = """
        SELECT c.category, SUM(pl.remaining_qty_g) as total_g
        FROM planting_logs pl
        JOIN crops c ON pl.crops_id = c.id
        JOIN farmers f ON pl.farmer_id = f.id
        WHERE pl.remaining_qty_g > 0 
        AND pl.estimated_harvest_date <= ?
    """
    params = [today]
    if "全部" not in tribe:
        sql += " AND f.tribe_location = ?"
        params.append(tribe)
    
    sql += " GROUP BY c.category"
    
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    
    if df.empty: return 0
    
    plan = BOX_CONFIG["標準蔬菜箱"]
    limits = []
    
    for cat, packs in plan.items():
        unit_weight = WEIGHT_CONFIG.get(cat, 500)
        req_g_per_box = packs * unit_weight 
        
        stock_row = df[df['category'] == cat]
        stock_g = stock_row['total_g'].values[0] if not stock_row.empty else 0
        
        possible_boxes = int(stock_g / req_g_per_box) if req_g_per_box > 0 else 0
        limits.append(possible_boxes)
    
    return min(limits) if limits else 0

def get_monthly_status(year, month):
    conn = get_conn()
    _, num_days = calendar.monthrange(year, month)
    month_start = date(year, month, 1)
    month_end = date(year, month, num_days)
    
    subs = pd.read_sql("""
        SELECT s.id, s.customer_id, c.name as 客戶, s.plan_name as 方案, s.frequency as 頻率, s.start_date, c.default_tribe_location
        FROM subscriptions s 
        JOIN customers c ON s.customer_id = c.id
        WHERE s.status = 'active'
    """, conn)
    
    if subs.empty:
        conn.close()
        return pd.DataFrame()
    
    orders = pd.read_sql("""
        SELECT subscription_id, COUNT(*) as actual_count
        FROM orders
        WHERE delivery_date >= ? AND delivery_date <= ?
        GROUP BY subscription_id
    """, conn, params=(month_start, month_end))
    
    conn.close()
    
    result_rows = []
    for _, sub in subs.iterrows():
        freq = sub['頻率']
        reg_date = pd.to_datetime(sub['start_date']).date()
        
        # 計算首次出貨日
        first_ship = get_first_shipping_date(reg_date, sub['default_tribe_location'])
        
        expected_count = 0
        if first_ship <= month_end:
            if freq == 'one_time':
                # 單次：若首次出貨日在本月
                if month_start <= first_ship <= month_end:
                    expected_count = 1
            else:
                freq_days = 28 if freq == 'monthly' else (14 if freq == 'bi_monthly' else 7) 
                
                curr = first_ship
                while curr <= month_end:
                    if curr >= month_start:
                        expected_count += 1
                    curr += timedelta(days=freq_days)
        
        order_match = orders[orders['subscription_id'] == sub['id']]
        actual_count = order_match['actual_count'].values[0] if not order_match.empty else 0
        
        if actual_count >= expected_count and expected_count > 0:
            status = "🟢已完成"
        elif actual_count < expected_count:
            status = "🟡進行中" 
        elif expected_count == 0 and actual_count > 0:
            status = "🔴超發"
        else:
            status = "⚪無排程" 
            
        result_rows.append({
            "客戶": sub['客戶'],
            "方案": sub['方案'],
            "頻率": PLAN_LABELS.get(sub['頻率'], sub['頻率']),
            "本月應出(箱)": expected_count,
            "已建立訂單": actual_count,
            "狀態": status
        })
        
    return pd.DataFrame(result_rows)

def generate_orders_for_week(target_date=None):
    if target_date is None: target_date = date.today()
    week_start = target_date - timedelta(days=target_date.weekday())
    
    count = 0 # 初始化 count
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT s.id, s.customer_id, c.name, c.default_tribe_location, s.plan_name, s.frequency, s.start_date
            FROM subscriptions s JOIN customers c ON s.customer_id = c.id WHERE s.status = 'active'
        """)
        subs = cursor.fetchall()
        
        for sub in subs:
            sub_id, cust_id, cust_name, tribe, plan, freq, reg_date_str = sub
            try: 
                reg_date = datetime.strptime(reg_date_str, '%Y-%m-%d').date()
            except: continue
            
            # 1. 算出這位客戶的「理論首次出貨日」 (基準點)
            first_ship = get_first_shipping_date(reg_date, tribe)
            
            # 2. 推算「本週」是否為出貨日
            delivery_date = None
            
            if freq == 'one_time':
                # 單次：只有當「本週」包含「首次出貨日」時才產生
                ship_week_start = first_ship - timedelta(days=first_ship.weekday())
                if week_start == ship_week_start:
                    delivery_date = first_ship
            else:
                # 週期性：檢查 (本週出貨日 - 首次出貨日) 是否為 freq_days 的倍數
                freq_days = 28 if freq == 'monthly' else (14 if freq == 'bi_monthly' else 7)
                
                # 找出本週的物流日 (羅娜週三, 雙龍週四)
                target_weekday = 2 if "羅娜" in tribe else 3
                this_week_ship = week_start + timedelta(days=target_weekday)
                
                if this_week_ship >= first_ship:
                    days_diff = (this_week_ship - first_ship).days
                    if days_diff % freq_days == 0:
                        delivery_date = this_week_ship
            
            if delivery_date:
                cursor.execute("SELECT id FROM orders WHERE subscription_id = ? AND delivery_date = ?", (sub_id, delivery_date))
                if not cursor.fetchone():
                    cursor.execute("SELECT id FROM subscription_skips WHERE subscription_id = ? AND skip_date = ?", (sub_id, delivery_date))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO orders (subscription_id, customer_id, customer_name, tribe_location, delivery_date, box_type, status)
                            VALUES (?, ?, ?, ?, ?, ?, '待媒合')
                        """, (sub_id, cust_id, cust_name, tribe, delivery_date, plan))
                        count += 1
        conn.commit()
    except Exception as e:
        st.error(f"產生訂單失敗: {e}")
    finally:
        conn.close()
    return count

def generate_mock_orders(count=5):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        names = ["王小明", "李小華", "陳大文", "張美麗", "吳志豪"]
        tribes = ["雙龍部落", "羅娜部落"]
        for _ in range(count):
            name = random.choice(names)
            tribe = random.choice(tribes)
            d_date = date.today() + timedelta(days=random.randint(1, 14))
            cursor.execute("INSERT INTO orders (customer_name, tribe_location, delivery_date, box_type, status) VALUES (?, ?, ?, '標準蔬菜箱', '待媒合')", (name, tribe, d_date))
        conn.commit()
    except Exception as e:
        st.error(f"模擬訂單失敗: {e}")
    finally:
        conn.close()

def generate_random_customers(count):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        last_names = ["陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊", "許", "鄭", "謝", "郭"]
        first_names = ["大為", "小美", "志豪", "雅婷", "怡君", "宗翰", "家豪", "淑芬", "俊宏", "美玲", "冠宇", "佩珊"]
        cities = ["台北市", "新北市", "台中市", "高雄市", "台南市", "桃園市"]
        districts = ["中區", "東區", "西區", "南區", "北區", "信義區", "大安區"]
        
        today = date.today()
        
        for _ in range(count):
            name = random.choice(last_names) + random.choice(first_names)
            phone = f"09{random.randint(10, 99)}-{random.randint(100, 999)}-{random.randint(100, 999)}"
            address = f"{random.choice(cities)}{random.choice(districts)}"
            tribe = random.choice(["雙龍部落", "羅娜部落"])
            
            # Insert Customer
            cursor.execute("INSERT INTO customers (name, phone, address, default_tribe_location) VALUES (?, ?, ?, ?)", (name, phone, address, tribe))
            cust_id = cursor.lastrowid
            
            # Insert Subscription
            freq_key = random.choice(list(PLAN_OPTIONS.keys()))
            freq_code = PLAN_OPTIONS[freq_key]
            
            # 決定起始日：必須是未來，且 羅娜=週三(2), 雙龍=週四(3)
            target_weekday = 2 if "羅娜" in tribe else 3
            
            # 邏輯：有70%機率是「趕得上最近一次」，30%機率是「錯過這次，下次再開始」
            # 計算最近的一次 Target Day
            days_until_target = (target_weekday - today.weekday() + 7) % 7
            if days_until_target == 0: # 剛好今天，假設已截單，排下週
                days_until_target = 7
                
            next_valid_delivery = today + timedelta(days=days_until_target)
            
            if random.random() > 0.7:
                # 30% 機率晚一週開始 (模擬較晚註冊)
                start_d = next_valid_delivery + timedelta(days=7)
            else:
                # 70% 機率最近一次開始
                start_d = next_valid_delivery
            
            # 預設 next_delivery_date 為空 (None)
            cursor.execute("INSERT INTO subscriptions (customer_id, plan_name, frequency, start_date, next_delivery_date) VALUES (?, ?, ?, ?, NULL)", (cust_id, "標準蔬菜箱", freq_code, start_d))
            sub_id = cursor.lastrowid
            
            if random.random() > 0.7: 
                cursor.execute("SELECT name FROM crops ORDER BY RANDOM() LIMIT 1")
                res = cursor.fetchone()
                if res:
                     cursor.execute("INSERT INTO subscription_preferences (subscription_id, pref_type, item_name) VALUES (?, 'dislike', ?)", (sub_id, res[0]))

        conn.commit()
    except Exception as e:
        st.error(f"批次新增失敗: {e}")
    finally:
        conn.close()

def add_mock_inventory(num_boxes_target=10): 
    conn = get_conn()
    cursor = conn.cursor()
    try:
        crops = pd.read_sql("SELECT * FROM crops", conn)
        farmers = pd.read_sql("SELECT * FROM farmers", conn)
        
        if crops.empty or farmers.empty:
            st.error("⚠️請先初始化資料庫 (Init DB)")
            return

        plan = BOX_CONFIG["標準蔬菜箱"]
        added_count = 0

        for category, packs_per_box in plan.items():
            cat_crops = crops[crops['category'] == category]
            if cat_crops.empty: continue

            selected_crops = cat_crops.sample(min(len(cat_crops), 2))
            
            for _, crop in selected_crops.iterrows():
                unit_weight = WEIGHT_CONFIG.get(category, 500)
                target_g = num_boxes_target * packs_per_box * unit_weight
                target_g = int(target_g * 1.5)
                
                farmer = farmers.sample(1).iloc[0]
                
                est_date = date.today()
                plant_date = est_date - timedelta(days=int(crop['growth_days']))
                
                cursor.execute("""
                    INSERT INTO planting_logs (farmer_id, crops_id, plant_date, estimated_harvest_date, quantity_planted_g, remaining_qty_g, status)
                    VALUES (?, ?, ?, ?, ?, ?, '已採收')
                """, (int(farmer['id']), int(crop['id']), plant_date, est_date, target_g, target_g))
                added_count += 1
            
        conn.commit()
        st.toast(f"已生成足夠配對 {num_boxes_target} 箱的現貨庫存！ (共 {added_count} 筆)")
    except Exception as e:
        st.error(f"新增庫存失敗: {e}")
    finally:
        conn.close()

def add_future_mock_inventory(num_boxes_target=10):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        crops = pd.read_sql("SELECT * FROM crops", conn)
        farmers = pd.read_sql("SELECT * FROM farmers", conn)
        
        if crops.empty or farmers.empty:
            st.error("請先初始化資料庫")
            return

        plan = BOX_CONFIG["標準蔬菜箱"]
        added_count = 0
        
        # 目標是「下週 (7天後)」
        target_date = date.today() + timedelta(days=7)

        for category, packs_per_box in plan.items():
            cat_crops = crops[crops['category'] == category]
            if cat_crops.empty: continue

            selected_crops = cat_crops.sample(min(len(cat_crops), 2))
            
            for _, crop in selected_crops.iterrows():
                unit_weight = WEIGHT_CONFIG.get(category, 500)
                target_g = num_boxes_target * packs_per_box * unit_weight
                target_g = int(target_g * 1.5)
                
                farmer = farmers.sample(1).iloc[0]
                
                # 預計採收日 = Today + 7
                plant_date = target_date - timedelta(days=int(crop['growth_days']))
                
                cursor.execute("""
                    INSERT INTO planting_logs (farmer_id, crops_id, plant_date, estimated_harvest_date, quantity_planted_g, remaining_qty_g, status)
                    VALUES (?, ?, ?, ?, ?, ?, '生長中')
                """, (int(farmer['id']), int(crop['id']), plant_date, target_date, target_g, target_g))
                added_count += 1
            
        conn.commit()
        st.toast(f"已生成下週 (7天後) 的預計產能庫存！ (共 {added_count} 筆)")
    except Exception as e:
        st.error(f"新增期貨失敗: {e}")
    finally:
        conn.close()

def execute_global_matching():
    conn = get_conn()
    cursor = conn.cursor()
    matched_count = 0
    
    cursor.execute("SELECT DISTINCT tribe_location FROM farmers")
    all_tribes = [row[0] for row in cursor.fetchall()]
    
    def get_shipping_priority(tribe_name):
        if "羅娜" in tribe_name: return 1 # 週三出貨 (優先)
        if "雙龍" in tribe_name: return 2 # 週四出貨
        return 3 # 其他
    
    all_tribes.sort(key=get_shipping_priority)
    
    try:
        cursor.execute("SELECT id, box_type, subscription_id, tribe_location, delivery_date FROM orders WHERE status = '待媒合'")
        pending_orders = cursor.fetchall()
        
        for order_id, box_type, sub_id, preferred_tribe, original_date_str in pending_orders:
            dislikes = []
            if sub_id:
                cursor.execute("SELECT item_name FROM subscription_preferences WHERE subscription_id = ? AND pref_type = 'dislike'", (sub_id,))
                dislikes = [r[0] for r in cursor.fetchall()]
            
            plan = BOX_CONFIG.get(box_type, BOX_CONFIG["標準蔬菜箱"])
            search_sequence = [preferred_tribe] + [t for t in all_tribes if t != preferred_tribe]
            
            fulfilled_tribe = None
            final_allocations = []
            
            for tribe in search_sequence:
                if not tribe: continue
                
                temp_allocations = []
                is_tribe_stock_enough = True
                
                for category, packs in plan.items():
                    unit_weight = WEIGHT_CONFIG.get(category, 500)
                    needed_qty_g = packs * unit_weight
                    
                    if needed_qty_g <= 0: continue
                    
                    # 撈取符合「訂單日期」條件的現貨 (日期敏感配貨)
                    # 只有 estimated_harvest_date <= delivery_date 才可以出貨
                    sql = f"""
                        SELECT pl.id, pl.remaining_qty_g, c.name 
                        FROM planting_logs pl 
                        JOIN crops c ON pl.crops_id = c.id 
                        JOIN farmers f ON pl.farmer_id = f.id 
                        WHERE c.category = ? 
                        AND f.tribe_location = ? 
                        AND pl.remaining_qty_g > 0 
                        AND pl.estimated_harvest_date <= ? 
                        ORDER BY pl.estimated_harvest_date ASC
                    """
                    # 將原字串轉為日期物件
                    order_date_obj = pd.to_datetime(original_date_str).date()
                    cursor.execute(sql, (category, tribe, order_date_obj))
                    available_logs = cursor.fetchall()
                    
                    qty_collected = 0
                    for log_id, current_stock, crop_name in available_logs:
                        if crop_name in dislikes: continue
                        if qty_collected >= needed_qty_g: break
                        
                        take_amount = min(needed_qty_g - qty_collected, current_stock)
                        temp_allocations.append({'log_id': log_id, 'amount': take_amount, 'name': crop_name})
                        qty_collected += take_amount
                    
                    if qty_collected < needed_qty_g:
                        is_tribe_stock_enough = False
                        break
                
                if is_tribe_stock_enough:
                    fulfilled_tribe = tribe
                    final_allocations = temp_allocations
                    break
            
            if fulfilled_tribe and final_allocations:
                # 計算新的出貨日 (根據實際出貨地重新校正)
                original_date = pd.to_datetime(original_date_str).date()
                week_start = original_date - timedelta(days=original_date.weekday())
                
                if "羅娜" in fulfilled_tribe:
                    new_delivery_date = week_start + timedelta(days=2) # Wed
                elif "雙龍" in fulfilled_tribe:
                    new_delivery_date = week_start + timedelta(days=3) # Thu
                else:
                    new_delivery_date = original_date

                for alloc in final_allocations:
                    cursor.execute("UPDATE planting_logs SET remaining_qty_g = remaining_qty_g - ? WHERE id = ?", (alloc['amount'], alloc['log_id']))
                    cursor.execute("INSERT INTO allocations (order_id, planting_log_id, crop_name, weight_allocated_g) VALUES (?, ?, ?, ?)", (order_id, alloc['log_id'], alloc['name'], alloc['amount']))
                
                cursor.execute("UPDATE orders SET status = '已配貨', tribe_location = ?, delivery_date = ? WHERE id = ?", (fulfilled_tribe, new_delivery_date, order_id))
                matched_count += 1
        conn.commit()
    except Exception as e:
        st.error(f"媒合執行失敗: {e}")
    finally:
        conn.close()
    return matched_count

def save_planting(farmer_id, crop_id, growth_days, unit_yield_g, tribe):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        quota_col = "quota_shuanglong" if "雙龍" in tribe else "quota_luona"
        cursor.execute(f"SELECT {quota_col}, tray_size FROM crops WHERE id = ?", (crop_id,))
        res = cursor.fetchone()
        if not res or res[0] < 1:
            conn.close()
            return None, None
        
        tray_size = res[1] if res[1] else 128
        cursor.execute(f"UPDATE crops SET {quota_col} = {quota_col} - 1 WHERE id = ?", (crop_id,))
        
        plant_date = date.today()
        est_date = plant_date + timedelta(days=int(growth_days))
        qty_g = int(float(unit_yield_g) * tray_size)
        
        cursor.execute("""INSERT INTO planting_logs (farmer_id, crops_id, plant_date, estimated_harvest_date, quantity_planted_g, remaining_qty_g, status) VALUES (?, ?, ?, ?, ?, ?, ?)""", (farmer_id, crop_id, plant_date, est_date, qty_g, qty_g, '生長中'))
        conn.commit()
        return est_date, qty_g
    except Exception as e:
        st.error(f"存檔失敗: {e}")
        return None, None
    finally:
        conn.close()

def add_customer(name, phone, address, tribe):
    conn = get_conn()
    c = conn.cursor()
    cust_id = None
    try:
        c.execute("INSERT INTO customers (name, phone, address, default_tribe_location) VALUES (?, ?, ?, ?)", (name, phone, address, tribe))
        cust_id = c.lastrowid
        conn.commit()
    except Exception as e:
        st.error(f"新增客戶失敗: {e}")
    finally:
        conn.close()
    return cust_id

def add_subscription(cust_id, plan, freq, start):
    conn = get_conn()
    c = conn.cursor()
    sub_id = None
    try:
        # 預設 next_delivery_date 為空
        c.execute("INSERT INTO subscriptions (customer_id, plan_name, frequency, start_date, next_delivery_date) VALUES (?, ?, ?, ?, NULL)", (cust_id, plan, freq, start))
        sub_id = c.lastrowid
        conn.commit()
    except Exception as e:
        st.error(f"新增訂閱失敗: {e}")
    finally:
        conn.close()
    return sub_id

def add_preference(sub_id, item_name, pref_type='dislike'):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO subscription_preferences (subscription_id, pref_type, item_name) VALUES (?, ?, ?)", (sub_id, pref_type, item_name))
        conn.commit()
    finally:
        conn.close()

def delete_farmer(farmer_id):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM farmers WHERE id = ?", (farmer_id,))
        cursor.execute("DELETE FROM planting_logs WHERE farmer_id = ?", (farmer_id,))
        conn.commit()
    finally:
        conn.close()

def add_new_farmer(name, tribe, phone):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO farmers (name, tribe_location, phone) VALUES (?, ?, ?)", (name, tribe, phone))
        conn.commit()
    finally:
        conn.close()

def get_all_inventory():
    """安全獲取庫存數據"""
    sql = """
    SELECT f.name as 農民, f.tribe_location as 部落, c.name as 作物, c.category as 類別,
           pl.plant_date as 種植日, pl.estimated_harvest_date as 預計採收日,
           pl.quantity_planted_g, pl.remaining_qty_g, pl.status as 狀態
    FROM planting_logs pl
    JOIN farmers f ON pl.farmer_id = f.id
    JOIN crops c ON pl.crops_id = c.id
    WHERE pl.remaining_qty_g > 0
    ORDER BY pl.estimated_harvest_date ASC
    """
    df = get_df(sql)
    if df.empty:
        return pd.DataFrame(columns=['農民', '部落', '作物', '類別', '種植日', '預計採收日', 'quantity_planted_g', 'remaining_qty_g', '狀態'])
    return df

def get_weather_mock(tribe):
    # 移除 icon
    weathers = [
        {"desc": "☀️晴朗", "temp": "24°C", "rain": "0%", "icon": "☀️"},
        {"desc": "☁️多雲", "temp": "21°C", "rain": "10%", "icon": "☁️"},
        {"desc": "🌧️小雨", "temp": "18°C", "rain": "60%", "icon": "🌧️"},
        {"desc": "⛈️雷雨", "temp": "16°C", "rain": "90%", "icon": "⛈️"}
    ]
    seed = sum(ord(c) for c in tribe) + date.today().day
    random.seed(seed)
    return random.choice(weathers)

# --- 4. 消費者專屬頁面邏輯 ---
def render_consumer_portal(sub_id):
    """
    渲染手機版消費者介面 (隱藏側邊欄，專注於回饋與預約)
    """
    # 強制隱藏側邊欄 CSS
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .consumer-card {
            background-color: white; border-radius: 12px; padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.08); margin-bottom: 20px;
        }
        .header-title { color: #2e7d32; font-weight: 800; font-size: 1.5rem; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

    # 獲取客戶資料
    sub_data = get_df(f"""
        SELECT s.id, c.name, s.next_delivery_date, s.frequency 
        FROM subscriptions s JOIN customers c ON s.customer_id = c.id 
        WHERE s.id = {sub_id}
    """)
    
    if sub_data.empty:
        st.error("找不到合約資料，請確認連結是否正確。")
        return

    cust_name = sub_data.iloc[0]['name']
    next_date = sub_data.iloc[0]['next_delivery_date']
    
    # Header
    st.markdown(f"<div class='header-title'>必班居抓根 - 客戶專區</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>哈囉，<b>{cust_name}</b>！感謝您支持部落小農。</p>", unsafe_allow_html=True)
    
    # 整合後的表單卡片
    st.markdown("<div class='consumer-card'>", unsafe_allow_html=True)
    st.subheader("預約與回饋")
    st.caption("請確認下次配送時間，並給予我們評價。")
    
    current_next = pd.to_datetime(next_date).date() if next_date else date.today() + timedelta(days=7)
    
    with st.form("consumer_combined_form"):
        st.markdown("### 1. 預約下次配送")
        st.caption("方便農民安排採收")
        new_date = st.date_input("期望配送日期", value=current_next, min_value=date.today())
        
        st.markdown("---")
        st.markdown("### 2. 滿意度回饋")
        st.caption("您的鼓勵是我們最大的動力")
        
        # 使用 st.feedback 實現星星評分 (0-4 代表 1-5 星)
        rating_selected = st.feedback("stars")
        
        comment = st.text_area("給農民的話 (選填)", placeholder="蔬菜很新鮮，謝謝！")
        
        # 整合送出按鈕
        submitted = st.form_submit_button("確認預約並送出回饋", type="primary", use_container_width=True)
        
        if submitted:
            conn = get_conn()
            c = conn.cursor()
            try:
                # 1. 更新預約日期
                c.execute("UPDATE subscriptions SET next_delivery_date = ? WHERE id = ?", (new_date, sub_id))
                
                # 2. 插入回饋 (若有填寫)
                # st.feedback 回傳 0-4，需轉換為 1-5。若未填寫則為 None
                final_rating = (rating_selected + 1) if rating_selected is not None else None
                
                if final_rating is not None or comment:
                    c.execute("INSERT INTO feedback (subscription_id, rating, comment) VALUES (?, ?, ?)", 
                              (sub_id, final_rating, comment))
                
                conn.commit()
                st.success(f"已成功預約 {new_date} 出貨，並收到您的回饋！")
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"發生錯誤: {e}")
            finally:
                conn.close()

    st.markdown("</div>", unsafe_allow_html=True)

# --- 5. 主程式入口邏輯 ---
# 檢查 URL 參數，決定進入後台還是消費者前台
query_params = st.query_params

# 如果 URL 包含 role=consumer 且有 sub_id，則進入消費者模式
if "role" in query_params and query_params["role"] == "consumer" and "sub_id" in query_params:
    try:
        sub_id_param = int(query_params["sub_id"])
        render_consumer_portal(sub_id_param)
    except:
        st.error("連結參數錯誤")
    
    # 停止執行後續的 Sidebar 與 Admin 程式碼
    st.stop()

# ================= 以下為原本的 Admin / Farmer 後台邏輯 =================

# --- 6. 側邊欄 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2909/2909808.png", width=80)
    st.title("原鄉蔬菜箱")
    st.caption("智慧供應鏈管理平台")
    st.markdown("---")
    menu = st.radio("功能選單", ["農民種植端", "戰情總覽 (Dashboard)", "訂單與媒合 (OMS)", "系統設定"], index=0)
    st.markdown("---")
    st.markdown("### 快速工具")
    if st.button("修復資料庫 (Init DB)", use_container_width=True):
        init_db()
        st.success("資料庫重置完成！(已加入回饋表)")
        time.sleep(1)
        st.rerun()
    if st.button("清空演示數據 (Reset)", type="primary", use_container_width=True):
        st.session_state['show_reset_overlay'] = True
        st.rerun()
    if st.button("快速新增庫存 (10箱現貨)", use_container_width=True):
        add_mock_inventory()
        time.sleep(1)
        st.rerun()
    if st.button("模擬新增下週產能 (期貨)", use_container_width=True):
        add_future_mock_inventory()
        time.sleep(1)
        st.rerun()

if st.session_state.get('show_reset_overlay', False):
    st.markdown("""<style>[data-testid="stSidebar"] { display: none; } .stApp {background-color: rgba(0,0,0,0.85)!important;}</style>""", unsafe_allow_html=True)
    col_x, col_center, col_y = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""<div style='background:white;padding:40px;border-radius:15px;text-align:center;border-top:10px solid #d32f2f;margin-top:100px;'><h2 style='color:#d32f2f;'>確認清空？</h2><p style='color:#555;'>將刪除所有<b>種植紀錄</b>與<b>訂單資料</b>。<br>(客戶與農民資料將保留，苗種盤數將重置)</p></div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("確認刪除", type="primary", use_container_width=True):
                clear_history()
                st.session_state['show_reset_overlay'] = False
                st.rerun()
        with c2:
            if st.button("取消", use_container_width=True):
                st.session_state['show_reset_overlay'] = False
                st.rerun()
    st.stop()

# --- 7. 頁面邏輯 (Admin) ---

# === 頁面 1: 農民種植端 ===
if menu == "農民種植端":
    col_spacer1, col_mobile, col_spacer2 = st.columns([1, 2, 1])
    with col_mobile:
        st.markdown("## 🌱必班居抓根")
        st.caption("農民智慧種植助手")
        farmers = get_df("SELECT * FROM farmers")
        if farmers.empty:
            st.error("請先點擊左側「修復資料庫」")
            st.stop()
        tribes = farmers['tribe_location'].unique()
        sel_tribe = st.selectbox("選擇部落", tribes)
        sel_farmers = farmers[farmers['tribe_location'] == sel_tribe]
        if not sel_farmers.empty:
            f_dict = {r['name']: r['id'] for i, r in sel_farmers.iterrows()}
            f_name = st.selectbox("選擇您的名字", list(f_dict.keys()))
            f_id = f_dict[f_name]
            
            st.divider()
            tab1, tab2 = st.tabs(["領取苗種 (抽籤)", "我的紀錄"])
            
            with tab1:
                available_crops = get_df(f"SELECT * FROM crops WHERE {'quota_shuanglong' if '雙龍' in sel_tribe else 'quota_luona'} > 0")
                if available_crops.empty:
                    st.error(f"{sel_tribe} 本週所有苗盤已分配完畢！")
                else:
                    st.info(f"本週 {sel_tribe} 尚有 **{len(available_crops)}** 種苗可供領取。")
                    col_l, col_wheel, col_r = st.columns([1, 2, 1])
                    with col_wheel:
                        chart_area = st.empty()
                        if 'spinning' not in st.session_state: st.session_state.spinning = False
                        
                        if not st.session_state.spinning:
                            # [關鍵修改] 靜止狀態：顯示 Plotly 圓餅圖
                            fig = px.pie(available_crops, values=[1]*len(available_crops), names='name', hole=0.45, color_discrete_sequence=px.colors.qualitative.Pastel)
                            fig.update_traces(textinfo='label', textposition='inside', showlegend=False)
                            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=350)
                            chart_area.plotly_chart(fig, use_container_width=True, key="wheel_idle")
                            
                            # [關鍵修改] 插入隱藏標記，CSS 會根據這個標記抓到下方的按鈕並將其「絕對定位」到轉盤中間
                            st.markdown('<span id="spin-btn-marker"></span>', unsafe_allow_html=True)
                            
                            # 按鈕 (Streamlit 原生按鈕，透過 CSS 移到中間)
                            if st.button("GO!", key="spin_btn"): 
                                st.session_state.spinning = True
                                st.rerun()
                                
                        else:
                            # 轉動狀態：顯示 CSS 動畫轉盤 (不顯示按鈕)
                            chart_area.markdown("""<div style="display:flex;justify-content:center;height:350px;align-items:center;"><div class="css-wheel"></div></div>""", unsafe_allow_html=True)
                            time.sleep(2.0)
                            final_crop = available_crops.sample(1).iloc[0]
                            est_date, qty_g = save_planting(f_id, int(final_crop['id']), final_crop['growth_days'], final_crop['unit_yield_g'], sel_tribe)
                            if est_date:
                                tray_s = final_crop.get('tray_size', 128)
                                st.session_state.spinning = False
                                chart_area.empty() 
                                st.markdown(f"""
                                    <div class='result-card'>
                                        <h1>{final_crop['name']}</h1>
                                        <p>{final_crop['category']} | 獲得: <b>1 盤苗 ({int(tray_s)}株)</b></p>
                                        <hr style='border-top: 1px dashed #1b5e20;'>
                                        <div>預計產量: <strong>{format_weight(qty_g)}</strong><br>(採收: {est_date})</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                time.sleep(3)
                                st.rerun()
            
            with tab2:
                logs = get_df(f"""SELECT c.name as 作物, pl.estimated_harvest_date as 預計採收, pl.remaining_qty_g FROM planting_logs pl JOIN crops c ON pl.crops_id = c.id WHERE pl.farmer_id = {f_id} ORDER BY pl.id DESC""")
                if not logs.empty:
                    # 顯示時將 g 轉為 kg 方便閱讀
                    logs['目前庫存'] = logs['remaining_qty_g'].apply(format_weight)
                    st.dataframe(logs[['作物', '預計採收', '目前庫存']], width="stretch")
                else: st.info("尚無紀錄")

# === 頁面 2: 戰情總覽 (Dashboard) ===
elif menu == "戰情總覽 (Dashboard)":
    
    available_tribes = ["全部據點 (總覽)"]
    try:
        tribe_df = get_df("SELECT DISTINCT tribe_location FROM farmers")
        if not tribe_df.empty: available_tribes += tribe_df['tribe_location'].tolist()
    except: pass

    col_title, col_filter = st.columns([3, 1])
    with col_filter: selected_dashboard_tribe = st.selectbox("選擇物流中心 / 部落", available_tribes)
    
    # 建立分頁
    tab_overview, tab_inventory, tab_allocations = st.tabs(["供需戰情室", "本週庫存明細", "出貨扣帳明細"])

    with tab_overview:
        # 1. 頂部資訊卡片區 (天氣 + 預估箱數)
        if "全部" in selected_dashboard_tribe:
            # 總覽模式：顯示所有部落的天氣與箱數
            t_list = [t for t in available_tribes if "全部" not in t]
            
            cols = st.columns(4)
            
            for idx, t_name in enumerate(t_list):
                weather_col_idx = idx * 2
                box_col_idx = idx * 2 + 1
                
                if box_col_idx < 4: 
                    w = get_weather_mock(t_name)
                    boxes = calculate_possible_boxes(t_name)
                    
                    with cols[weather_col_idx]:
                        st.markdown(f"<div class='weather-card'><div class='weather-title'>{t_name}</div><div class='weather-temp'>{w['icon']} {w['temp']}</div><div style='font-size:0.8rem'>{w['desc']} | 降雨 {w['rain']}</div></div>", unsafe_allow_html=True)
                    
                    with cols[box_col_idx]:
                        st.markdown(f"""
                        <div class='box-est-card'>
                            <div class='weather-title'>{t_name}庫存</div>
                            <div class='weather-temp'>{boxes} 箱</div>
                            <div style='font-size:0.8rem'>現貨可組</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            # 單一據點模式 (保持原樣)
            w_cols = st.columns(4)
            w = get_weather_mock(selected_dashboard_tribe)
            boxes = calculate_possible_boxes(selected_dashboard_tribe)
            
            with w_cols[0]:
                st.markdown(f"<div class='weather-card'><div class='weather-title'>{selected_dashboard_tribe}</div><div class='weather-temp'>{w['icon']} {w['temp']}</div><div style='font-size:0.8rem'>{w['desc']} | 降雨 {w['rain']}</div></div>", unsafe_allow_html=True)
            
            with w_cols[1]:
                st.markdown(f"""
                <div class='box-est-card'>
                    <div class='weather-title'>預估可組裝箱數</div>
                    <div class='weather-temp'>{boxes} 箱</div>
                    <div style='font-size:0.8rem'>基於現貨庫存</div>
                </div>
                """, unsafe_allow_html=True)

        dashboard_title = f"{selected_dashboard_tribe.split(' ')[0]} - 供應鏈戰情室"
        
        df = get_all_inventory()
        
        if "全部" not in selected_dashboard_tribe and not df.empty:
            df = df[df['部落'] == selected_dashboard_tribe]
        
        today = date.today()
        next_week = today + timedelta(days=7)
        
        if not df.empty and '預計採收日' in df.columns:
            df['預計採收日'] = pd.to_datetime(df['預計採收日']).dt.date
            immediate_supply_g = df[(df['預計採收日'] >= today) & (df['預計採收日'] <= next_week)]['remaining_qty_g'].sum()
            total_potential_g = df['remaining_qty_g'].sum()
            active_farmers = df['農民'].nunique()
            urgent_harvest = df[(df['預計採收日'] >= today) & (df['預計採收日'] <= (today + timedelta(days=3)))]
        else:
            immediate_supply_g = 0; total_potential_g = 0; active_farmers = 0
            urgent_harvest = pd.DataFrame()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("本週預計採收", format_weight(immediate_supply_g), help="未來 7 天內成熟")
        k2.metric("未來總產能", format_weight(total_potential_g), help="田裡所有作物的總預估量")
        k3.metric("作物多樣性", f"{df['作物'].nunique() if not df.empty else 0} 種", help="目標: 7種以上")
        k4.metric("活躍農民", f"{active_farmers} 人")
        
        if not urgent_harvest.empty:
            st.warning(f"**⚠️緊急採收通知**：有 **{len(urgent_harvest)}** 筆作物需在 3 天內採收！")
            urgent_harvest['預估產量'] = urgent_harvest['remaining_qty_g'].apply(format_weight)
            st.dataframe(urgent_harvest[['預計採收日', '作物', '預估產量', '農民', '部落']], width="stretch", hide_index=True)
        
        st.divider()
        
        # 圖表 (以 kg 為單位繪製)
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("未來產能預測 (kg)")
            if not df.empty:
                df['qty_kg'] = df['remaining_qty_g'] / 1000.0
                fig = px.bar(df, x='預計採收日', y='qty_kg', color='作物', title="每日預計採收量明細", labels={'qty_kg': '產量 (kg)', '預計採收日': '日期'}, hover_data=['農民', '部落'])
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("尚無數據")
        with c2:
            st.subheader("作物類別佔比")
            if not df.empty:
                fig = px.pie(df, values='remaining_qty_g', names='類別', hole=0.4)
                fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("無數據")

        st.divider()
        st.subheader("未來 4 週供需預測 (kg)")
        supply_df = calculate_supply_forecast(4)
        demand_df = calculate_demand_forecast(4)
        
        if not supply_df.empty and not demand_df.empty:
            merged = pd.merge(demand_df, supply_df, on=['week_start', 'category'], how='outer', suffixes=('_demand', '_supply')).fillna(0)
            fig_sd = px.bar(merged, x='week_start', y=['required_qty_kg', 'remaining_qty_kg'], 
                            barmode='group', facet_col='category',
                            labels={'value': '重量 (kg)', 'week_start': '週次', 'variable': '類型'},
                            color_discrete_map={'required_qty_kg': '#FF6B6B', 'remaining_qty_kg': '#4ECDC4'},
                            title="紅=需求 | 綠=供給")
            st.plotly_chart(fig_sd, use_container_width=True)
        else:
            st.info("尚無足夠的種植或訂閱資料來進行預測。")

        st.subheader("詳細生產排程表")
        if not df.empty:
            df['預估產量'] = df['remaining_qty_g'].apply(format_weight)
            st.dataframe(df[['預計採收日', '作物', '類別', '預估產量', '農民', '部落', '狀態']].sort_values('預計採收日'), width="stretch", hide_index=True)

    with tab_inventory:
        st.subheader(f"{selected_dashboard_tribe} - 現有庫存清單")
        
        # 重新撈取資料，這次是為了詳細清單
        inv_df = get_all_inventory()
        if "全部" not in selected_dashboard_tribe and not inv_df.empty:
            inv_df = inv_df[inv_df['部落'] == selected_dashboard_tribe]
            
        if not inv_df.empty:
            inv_df['預計採收日'] = pd.to_datetime(inv_df['預計採收日']).dt.date
            
            # 分流：現貨 vs 期貨
            ready_df = inv_df[inv_df['預計採收日'] <= date.today()].copy()
            future_df = inv_df[inv_df['預計採收日'] > date.today()].copy()
            
            # 1. 現貨專區 (Ready)
            st.markdown("#### 🟢現貨專區 (Ready to Ship)")
            if not ready_df.empty:
                # 計算已媒合量
                ready_df['matched_qty_g'] = ready_df['quantity_planted_g'] - ready_df['remaining_qty_g']
                ready_df['qty_kg'] = ready_df['remaining_qty_g'] / 1000.0
                summary_ready = ready_df.groupby('類別')['qty_kg'].sum().reset_index()
                
                cols = st.columns(len(summary_ready))
                for i, row in summary_ready.iterrows():
                    with cols[i]:
                        st.markdown(f"<div class='stock-ready'>{row['類別']}: {row['qty_kg']:.1f} kg</div>", unsafe_allow_html=True)
                
                # 格式化欄位
                ready_df['初始產量'] = ready_df['quantity_planted_g'].apply(format_weight)
                ready_df['已媒合(扣除)'] = ready_df['matched_qty_g'].apply(format_weight)
                ready_df['目前庫存'] = ready_df['remaining_qty_g'].apply(format_weight)
                
                st.dataframe(ready_df[['作物', '類別', '預計採收日', '初始產量', '已媒合(扣除)', '目前庫存', '農民', '部落']], width="stretch", hide_index=True)
            else:
                st.info("目前無成熟現貨。")
            
            st.divider()
            
            # 2. 預計產能 (Future)
            st.markdown("#### 🟡預計產能 (Coming Soon)")
            if not future_df.empty:
                future_df['qty_kg'] = future_df['remaining_qty_g'] / 1000.0
                summary_future = future_df.groupby('類別')['qty_kg'].sum().reset_index()
                
                cols = st.columns(len(summary_future))
                for i, row in summary_future.iterrows():
                    with cols[i]:
                        st.markdown(f"<div class='stock-future'>{row['類別']}: {row['qty_kg']:.1f} kg</div>", unsafe_allow_html=True)
                
                future_df['預估量'] = future_df['remaining_qty_g'].apply(format_weight)
                st.dataframe(future_df[['作物', '類別', '預計採收日', '預估量', '農民', '部落']], width="stretch", hide_index=True)
            else:
                st.info("目前無待採收作物。")
        else:
            st.info("目前無任何種植紀錄。")

    with tab_allocations:
        st.subheader("出貨扣帳明細 (Allocations)")
        # Add week column and week filter
        sql = """
        SELECT 
            a.created_at as 媒合時間,
            o.delivery_date as 預計出貨日,
            o.customer_name as 客戶,
            a.crop_name as 作物,
            a.weight_allocated_g as 重量_g,
            f.name as 農民,
            f.tribe_location as 部落
        FROM allocations a
        JOIN orders o ON a.order_id = o.id
        JOIN planting_logs pl ON a.planting_log_id = pl.id
        JOIN farmers f ON pl.farmer_id = f.id
        ORDER BY a.created_at DESC
        """
        df_alloc = get_df(sql)
        
        if not df_alloc.empty:
            # Add Week Column
            df_alloc['dt'] = pd.to_datetime(df_alloc['媒合時間'])
            df_alloc['週次'] = df_alloc['dt'].apply(get_week_label)
            
            # Select Week
            weeks = sorted(df_alloc['週次'].unique(), reverse=True)
            selected_week = st.selectbox("選擇週次", weeks, key="alloc_week_filter")
            
            # Filter
            filtered_df = df_alloc[df_alloc['週次'] == selected_week].copy()
            
            # Display
            filtered_df['重量'] = filtered_df['重量_g'].apply(format_weight)
            st.dataframe(filtered_df[['媒合時間', '預計出貨日', '客戶', '作物', '重量', '農民', '部落']], width="stretch", hide_index=True)
        else:
            st.info("目前尚無扣帳紀錄。")

# === 頁面 3: 訂單與媒合 (OMS) ===
elif menu == "訂單與媒合 (OMS)":
    tab_orders, tab_subs, tab_history, tab_progress, tab_feedback = st.tabs(["出貨排程與媒合", "訂戶與合約管理", "已配貨訂單查詢", "履約進度監控", "客戶回饋"])
    
    with tab_orders:
        st.title("訂單處理中心")
        st.caption("支援全域跨部落自動調度")
        
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        with c1: st.info("系統會根據訂閱合約的「頻率」自動產生訂單。")
        with c2: 
            if st.button("產生本週訂閱單"):
                cnt = generate_orders_for_week(date.today())
                if cnt > 0: st.success(f"已生成 {cnt} 筆合約訂單！")
                else: st.warning("本週無新合約訂單需生成")
                time.sleep(1); st.rerun()
        with c3:
            if st.button("產生下週訂閱單 (測試)"):
                cnt = generate_orders_for_week(date.today() + timedelta(days=7))
                if cnt > 0: st.success(f"已生成 {cnt} 筆下週訂單！")
                else: st.warning("下週無新合約訂單需生成")
                time.sleep(1); st.rerun()
        with c4:
            if st.button("模擬匯入 5 筆假單"):
                generate_mock_orders()
                st.success("已匯入模擬單")
                st.rerun()
        
        # 查詢 pending orders，只選擇要顯示的欄位
        orders = get_df(f"SELECT id as 訂單編號, customer_name as 客戶, delivery_date as 出貨日, box_type as 方案, status as 狀態 FROM orders WHERE status = '待媒合'")
        if not orders.empty:
            st.write(f"待處理訂單：{len(orders)} 張 (全域調度)")
            # 這裡不會顯示 tribe_location，因為 SQL 沒有 select 它
            st.dataframe(orders, width="stretch")
            
            if st.button("啟動全域自動配貨 (Global Match)", type="primary", use_container_width=True):
                with st.status("正在分析全台部落庫存與調度..."):
                    matched = execute_global_matching()
                    time.sleep(0.5)
                if matched > 0:
                    st.success(f"配對完成！成功處理 {matched} 張訂單。")
                else:
                    st.error("配對失敗：無足夠的「現貨庫存」可供分配 (請確認庫存日期 <= 訂單出貨日)。")
                time.sleep(2); st.rerun()
        else:
            st.success("目前沒有待處理訂單。")
            
    with tab_subs:
        # 新增按鈕在標題列
        c_title, c_btn = st.columns([4, 1])
        with c_title:
            st.subheader("客戶資料庫 & 訂閱合約")
        with c_btn:
            if st.button("新增訂閱戶", use_container_width=True):
                st.session_state['show_add_customer'] = not st.session_state.get('show_add_customer', False)

        # 新增介面區塊 (展開)
        if st.session_state.get('show_add_customer', False):
            # 使用 columns 來限制表單寬度，使其看起來像之前側邊欄的大小 (約 1/3 頁面寬)
            c_form_layout, c_space = st.columns([1, 2]) 
            with c_form_layout:
                with st.container(border=True):
                    st.markdown("### 新增訂閱戶資料")
                    with st.form("new_sub_form"):
                        name = st.text_input("客戶姓名")
                        phone = st.text_input("電話")
                        addr = st.text_input("地址")
                        tribe = st.selectbox("偏好集貨地 (優先)", ["雙龍部落", "羅娜部落"])
                        
                        st.markdown("---")
                        # 方案固定為標準蔬菜箱
                        st.info("方案預設：標準蔬菜箱")
                        
                        # 頻率選單 (顯示中文)
                        freq_display = st.selectbox("配送頻率", list(PLAN_OPTIONS.keys()))
                        start_d = st.date_input("開始配送日", date.today())
                        
                        # 整合忌口選擇
                        st.markdown("#### 忌口設定 (選填)")
                        all_crops_df = get_df("SELECT DISTINCT name FROM crops")
                        crop_options = all_crops_df['name'].tolist() if not all_crops_df.empty else []
                        dislikes = st.multiselect("選擇不吃的品項", crop_options)
                        
                        c_sub1, c_sub2 = st.columns(2)
                        with c_sub1:
                            submitted = st.form_submit_button("建立客戶與合約", use_container_width=True)
                        
                        if submitted:
                            if name and phone:
                                cid = add_customer(name, phone, addr, tribe)
                                # 使用 PLAN_OPTIONS[freq_display] 取得代碼 (e.g., 'monthly')
                                sub_id = add_subscription(cid, "標準蔬菜箱", PLAN_OPTIONS[freq_display], start_d)
                                
                                # 儲存忌口
                                if sub_id and dislikes:
                                    for item in dislikes:
                                        add_preference(sub_id, item)
                                        
                                st.success(f"已建立 {name} 的資料！")
                                st.session_state['show_add_customer'] = False
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("姓名與電話為必填")
        
        # Add Bulk Generate Section
        with st.expander("快速批次產生測試訂戶", expanded=False):
             c_num, c_gen = st.columns([1, 2])
             qty = c_num.number_input("產生數量", min_value=1, max_value=50, value=5, step=1)
             if c_gen.button(f"隨機產生 {qty} 位訂戶", use_container_width=True):
                 generate_random_customers(qty)
                 st.success(f"已成功新增 {qty} 位測試訂戶！")
                 time.sleep(1)
                 st.rerun()
        
        # 列表介面 (可編輯)
        st.markdown("### 有效合約列表 (可編輯)")
        
        # Get data
        subs_df = get_df("""
            SELECT s.id, c.name, c.phone, c.address, s.plan_name, s.frequency, s.start_date, s.next_delivery_date
            FROM subscriptions s JOIN customers c ON s.customer_id = c.id
            WHERE s.status = 'active'
        """)

        if not subs_df.empty:
            # Transform to labels for display
            subs_df['frequency_label'] = subs_df['frequency'].map(PLAN_LABELS)
            
            # FIX: Ensure dates are objects for editing/display
            subs_df['next_delivery_date'] = pd.to_datetime(subs_df['next_delivery_date'], errors='coerce').dt.date
            subs_df['start_date'] = pd.to_datetime(subs_df['start_date'], errors='coerce').dt.date
            
            # Reorder columns for editor
            editor_df = subs_df[['id', 'name', 'phone', 'address', 'frequency_label', 'start_date', 'next_delivery_date']].copy()
            
            edited_df = st.data_editor(
                editor_df,
                column_config={
                    "id": st.column_config.NumberColumn("合約編號", disabled=True),
                    "name": st.column_config.TextColumn("客戶", disabled=True),
                    "phone": st.column_config.TextColumn("電話", disabled=True),
                    "address": st.column_config.TextColumn("地址", disabled=True),
                    "frequency_label": st.column_config.SelectboxColumn("配送頻率", options=list(PLAN_OPTIONS.keys()), required=True),
                    "start_date": st.column_config.DateColumn("首次訂閱日", format="YYYY-MM-DD", disabled=True),
                    "next_delivery_date": st.column_config.DateColumn("預計下次出貨日", format="YYYY-MM-DD"),
                },
                width="stretch",
                hide_index=True,
                key="subs_editor"
            )

            if st.button("儲存變更", type="primary"):
                conn = get_conn()
                c = conn.cursor()
                try:
                    for index, row in edited_df.iterrows():
                        sub_id = row['id']
                        freq_label = row['frequency_label']
                        next_date = row['next_delivery_date']
                        
                        # Fix: Convert NaT to None for SQL
                        if pd.isna(next_date):
                            next_date = None
                        
                        # Map label back to code
                        freq_code = PLAN_CODES.get(freq_label, freq_label)
                        
                        c.execute("UPDATE subscriptions SET frequency = ?, next_delivery_date = ? WHERE id = ?", (freq_code, next_date, sub_id))
                    conn.commit()
                    st.success("資料已更新！")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"更新失敗: {e}")
                finally:
                    conn.close()
        else:
            st.info("目前無有效合約")

    with tab_history:
        st.subheader("已配貨訂單與出貨單列印")
        
        # 1. 篩選工具列
        col_filter_1, col_filter_2 = st.columns(2)
        with col_filter_1:
            tribe_filter = st.selectbox("篩選出貨據點", ["全部據點", "雙龍部落", "羅娜部落"], key="hist_tribe_filter")
        
        # 2. 撈取訂單資料
        base_sql = """
            SELECT o.id, o.customer_name, o.box_type, o.delivery_date, o.tribe_location, o.status, 
                   o.subscription_id, c.phone, c.address, c.name as real_name
            FROM orders o
            JOIN subscriptions s ON o.subscription_id = s.id
            JOIN customers c ON s.customer_id = c.id
            WHERE o.status != '待媒合'
        """
        
        if tribe_filter != "全部據點":
            orders_df = get_df(f"{base_sql} AND o.tribe_location = '{tribe_filter}' ORDER BY o.delivery_date DESC")
        else:
            orders_df = get_df(f"{base_sql} ORDER BY o.delivery_date DESC")
            
        if not orders_df.empty:
            # 週次篩選
            orders_df['dt'] = pd.to_datetime(orders_df['delivery_date'])
            orders_df['週次'] = orders_df['dt'].apply(get_week_label)
            
            with col_filter_2:
                weeks = sorted(orders_df['週次'].unique(), reverse=True)
                sel_week = st.selectbox("選擇出貨週次", weeks, key="hist_week_filter")
            
            # 過濾顯示資料
            display_df = orders_df[orders_df['週次'] == sel_week].copy()
            
            if not display_df.empty:
                st.markdown("---")
                
                # --- 定義 CSS (出貨單樣式) ---
                standard_style = """
                <style>
                    body { font-family: 'Microsoft JhengHei', sans-serif; background-color: #555; margin: 0; padding: 20px; }
                    .page { background-color: white; padding: 40px; margin: 0 auto; max-width: 800px; margin-bottom: 20px; position: relative; box-sizing: border-box; }
                    .page-break { page-break-after: always; }
                    
                    table { width: 100%; border-collapse: collapse; border: 1px solid black; margin-bottom: 20px; font-size: 14px; }
                    th, td { border: 1px solid black; padding: 8px 10px; vertical-align: middle; }
                    
                    .field-label { background-color: #f0f0f0; font-weight: bold; text-align: center; width: 15%; white-space: nowrap; }
                    .field-value { width: 35%; }
                    .items-header { background-color: #f0f0f0; text-align: center; font-weight: bold; }
                    .text-center { text-align: center; }
                    .text-right { text-align: right; }
                    
                    .slip-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; border-bottom: 0px; }
                    h1 { text-align: center; letter-spacing: 10px; margin: 10px 0 30px 0; font-size: 28px; }

                    @media print { 
                        body { background-color: white; padding: 0; margin: 0; } 
                        .page { margin: 0; width: 100%; max-width: none; box-shadow: none; padding: 30px; border: none; }
                        .page-break { page-break-after: always; } 
                    }
                </style>
                """

                # 準備所有 ID 列表 (用於全選)
                all_ids = display_df['id'].tolist()
                
                # --- [頂部] 批量操作控制區 ---
                # 1. 計算目前選取狀態
                current_selected = []
                for oid in all_ids:
                    # 如果 key 存在且為 True，加入選取列表
                    if st.session_state.get(f"sel_{oid}", False):
                        current_selected.append(oid)
                
                # 2. 全選 Callback
                def toggle_select_all():
                    new_state = st.session_state.get('select_all_master', False)
                    for oid in all_ids:
                        st.session_state[f"sel_{oid}"] = new_state

                # 3. 顯示頂部工具列 (兩欄配置)
                # 使用 vertical_alignment="center" 確保 Checkbox 和按鈕對齊
                top_col1, top_col2 = st.columns([1, 3], vertical_alignment="center")
                
                with top_col1:
                    # 全選 Checkbox
                    st.checkbox("全選本頁訂單", key="select_all_master", on_change=toggle_select_all)
                
                with top_col2:
                    # 批量下載按鈕 (只在有選取時顯示)
                    if current_selected:
                        # 撈出被選取的資料
                        target_orders = display_df[display_df['id'].isin(current_selected)]
                        
                        # 生成批量 HTML
                        bulk_html_ready = f"""
                        <html>
                        <head><title>批量出貨單</title>{standard_style}</head><body>
                        """
                        for idx_b, (_, row_b) in enumerate(target_orders.iterrows()):
                            items_df_bulk = get_df(f"SELECT crop_name, weight_allocated_g FROM allocations WHERE order_id = {row_b['id']}")
                            # [關鍵修改] 使用真正的 App 連結
                            mock_url_bulk = f"{BASE_URL}?role=consumer&sub_id={row_b['subscription_id']}"
                            qr_img_bulk = get_qr_code_base64(mock_url_bulk)
                            
                            items_rows_bulk = ""
                            t_items = 0
                            for _, item_b in items_df_bulk.iterrows():
                                items_rows_bulk += f"""
                                <tr>
                                    <td class="text-center">{t_items + 1}</td>
                                    <td class="text-center">{item_b['crop_name']}</td>
                                    <td class="text-center">一級規</td>
                                    <td class="text-center">{format_weight(item_b['weight_allocated_g'])}</td>
                                    <td class="text-center">-</td>
                                    <td class="text-center">-</td>
                                </tr>"""
                                t_items += 1
                            for k in range(5 - t_items):
                                items_rows_bulk += '<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td></tr>'
                            
                            page_html = f"""
                            <div class="page">
                                <div class="slip-header">
                                    <div style="font-size: 12px; color: #666; align-self: flex-end;">單號：{str(row_b['id']).zfill(5)}</div>
                                    <div style="text-align: right;"><img src="data:image/png;base64,{qr_img_bulk}" width="80" height="80"><div style="font-size: 10px;">掃描預約下次到貨</div></div>
                                </div>
                                <h1>必班居抓根出貨單</h1>
                                <div class="text-right" style="font-size: 14px; margin-bottom: 5px;">列印日期: {date.today().strftime('%Y/%m/%d')}</div>
                                <table>
                                    <tr><td class="field-label">填寫人</td><td class="field-value">系統管理員</td><td class="field-label">出貨部門</td><td class="field-value">{row_b['tribe_location']}集貨站</td></tr>
                                    <tr><td class="field-label">客戶名稱</td><td class="field-value">{row_b['customer_name']}</td><td class="field-label">聯絡人</td><td class="field-value">{row_b['real_name']}</td></tr>
                                    <tr><td class="field-label">聯絡電話</td><td class="field-value">{row_b['phone']}</td><td class="field-label">出貨日期</td><td class="field-value">{row_b['delivery_date']}</td></tr>
                                    <tr><td class="field-label">地址</td><td colspan="3">{row_b['address']}</td></tr>
                                </table>
                                <table>
                                    <thead><tr><th class="items-header" style="width:10%">項次</th><th class="items-header" style="width:30%">品名</th><th class="items-header" style="width:15%">規格</th><th class="items-header" style="width:15%">數量/重量</th><th class="items-header" style="width:15%">單價</th><th class="items-header" style="width:15%">備註</th></tr></thead>
                                    <tbody>{items_rows_bulk}<tr><td colspan="3" class="text-right" style="font-weight:bold;">合計</td><td class="text-center">{t_items} 品項</td><td colspan="2" class="text-center">已結清</td></tr></tbody>
                                </table>
                                <table><tr><td class="field-label" style="width: 15%; height: 60px;">其他備註</td><td style="vertical-align: top;">請於收到貨後掃描右上角 QR Code 確認商品狀況，並預約下一次配送時間。</td></tr></table>
                            </div>
                            """
                            bulk_html_ready += page_html
                            if idx_b < len(target_orders) - 1:
                                bulk_html_ready += '<div class="page-break"></div>'
                        bulk_html_ready += "</body></html>"
                        
                        st.download_button(
                            label=f"批量下載 ({len(target_orders)}張)",
                            data=bulk_html_ready,
                            file_name="bulk_slips.html",
                            mime="text/html",
                            type="primary"
                        )
                    # 移除了 else 區塊

                # --- 列表標題列 ---
                st.markdown("") # Spacer
                # 加入 vertical_alignment="center" 確保標題列也對齊
                # 欄位調整：[選取, 單號, 客戶, 出貨日, 出貨地, 狀態, 操作, 出貨單]
                # 權重調整：[0.5, 0.8, 1.2, 1.2, 1.2, 0.8, 1.0, 1.3]
                h_sel, h1, h2, h3, h4, h5, h6, h7 = st.columns([0.5, 0.8, 1.2, 1.2, 1.2, 0.8, 1.0, 1.3], vertical_alignment="center")
                h_sel.write("選取")
                h1.write("單號")
                h2.write("客戶")
                h3.write("出貨日")
                h4.write("出貨地")
                h5.write("狀態")
                h6.write("操作")
                h7.write("出貨單")
                
                # --- 列表內容 (卡片式區塊) ---
                for _, row in display_df.iterrows():
                    # 使用 border=True 創造區塊感
                    with st.container(border=True):
                        # 關鍵修改：加入 vertical_alignment="center" 讓文字與按鈕垂直置中
                        # 對應上方標題的權重調整
                        c_sel, c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 0.8, 1.2, 1.2, 1.2, 0.8, 1.0, 1.3], vertical_alignment="center")
                        
                        # 初始化 key
                        if f"sel_{row['id']}" not in st.session_state:
                            st.session_state[f"sel_{row['id']}"] = False
                            
                        # 選取 Checkbox
                        c_sel.checkbox("", key=f"sel_{row['id']}", label_visibility="collapsed")
                        
                        # 資料顯示
                        c1.write(f"#{row['id']}")
                        c2.write(row['customer_name'])
                        c3.write(row['delivery_date'])
                        c4.write(row['tribe_location'])
                        c5.markdown(f":green[{row['status']}]")
                        
                        # 1. 明細按鈕 (現在在 c6 操作欄)
                        if c6.button("明細", key=f"btn_det_{row['id']}"):
                            st.session_state[f"show_det_{row['id']}"] = not st.session_state.get(f"show_det_{row['id']}", False)

                        # 2. 單張下載 (現在在 c7 出貨單欄) - 準備 HTML
                        items_df = get_df(f"SELECT crop_name, weight_allocated_g FROM allocations WHERE order_id = {row['id']}")
                        mock_url = f"https://mock-vege-system.com/portal?sub={row['subscription_id']}"
                        qr_img = get_qr_code_base64(mock_url)
                        
                        items_html_rows = ""
                        t_items = 0
                        for idx, item in items_df.iterrows():
                            items_html_rows += f"""<tr><td class="text-center">{idx + 1}</td><td class="text-center">{item['crop_name']}</td><td class="text-center">一級規</td><td class="text-center">{format_weight(item['weight_allocated_g'])}</td><td class="text-center">-</td><td class="text-center">-</td></tr>"""
                            t_items += 1
                        for i in range(5 - t_items):
                            items_html_rows += '<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td></tr>'

                        single_html = f"""
                        <html><head><title>出貨單 #{row['id']}</title>{standard_style}</head><body>
                        <div class="page">
                            <div class="slip-header"><div style="font-size: 12px; color: #666; align-self: flex-end;">單號：{str(row['id']).zfill(5)}</div><div style="text-align: right;"><img src="data:image/png;base64,{qr_img}" width="80" height="80"><div style="font-size: 10px;">掃描預約下次到貨</div></div></div>
                            <h1>必班居抓根出貨單</h1><div class="text-right" style="font-size: 14px; margin-bottom: 5px;">列印日期: {date.today().strftime('%Y/%m/%d')}</div>
                            <table><tr><td class="field-label">填寫人</td><td class="field-value">系統管理員</td><td class="field-label">出貨部門</td><td class="field-value">{row['tribe_location']}集貨站</td></tr><tr><td class="field-label">客戶名稱</td><td class="field-value">{row['customer_name']}</td><td class="field-label">聯絡人</td><td class="field-value">{row['real_name']}</td></tr><tr><td class="field-label">聯絡電話</td><td class="field-value">{row['phone']}</td><td class="field-label">出貨日期</td><td class="field-value">{row['delivery_date']}</td></tr><tr><td class="field-label">地址</td><td colspan="3">{row['address']}</td></tr></table>
                            <table><thead><tr><th class="items-header" style="width:10%">項次</th><th class="items-header" style="width:30%">品名</th><th class="items-header" style="width:15%">規格</th><th class="items-header" style="width:15%">數量/重量</th><th class="items-header" style="width:15%">單價</th><th class="items-header" style="width:15%">備註</th></tr></thead><tbody>{items_html_rows}<tr><td colspan="3" class="text-right" style="font-weight:bold;">合計</td><td class="text-center">{t_items} 品項</td><td colspan="2" class="text-center">已結清</td></tr></tbody></table>
                            <table><tr><td class="field-label" style="width: 15%; height: 60px;">其他備註</td><td style="vertical-align: top;">請於收到貨後掃描右上角 QR Code 確認商品狀況，並預約下一次配送時間。</td></tr></table>
                        </div></body></html>
                        """
                        
                        c7.download_button("下載", data=single_html, file_name=f"slip_{row['id']}.html", mime="text/html", key=f"btn_dl_{row['id']}")
                        
                    
                    # 展開的明細區塊 (位於卡片下方)
                    if st.session_state.get(f"show_det_{row['id']}", False):
                        with st.container():
                            # 增加一點縮排感
                            _, det_col = st.columns([0.5, 9.5])
                            with det_col:
                                st.info(f"訂單 #{row['id']} 內容物：")
                                d_items = items_df.copy()
                                d_items.columns = ['作物名稱', '配貨重量(g)']
                                d_items['配貨重量'] = d_items['配貨重量(g)'].apply(format_weight)
                                st.dataframe(d_items[['作物名稱', '配貨重量']], hide_index=True)

            else:
                st.warning("該週次無出貨紀錄")
        else:
            st.info("尚無已配貨的訂單")
            
    with tab_progress:
        # --- 新增：月度出貨進度監控區塊 (Moved here) ---
        st.subheader("履約進度監控")
        st.markdown("監控訂閱戶本月的履約狀況，確保不漏單、不超發。")
        
        # 選擇月份 (預設本月) - Using st.date_input
        c_date_picker, c_space_prog = st.columns([1, 2])
        with c_date_picker:
            selected_date_for_month = st.date_input("選擇查詢月份 (任意日期)", value=date.today())
            
        sel_year = selected_date_for_month.year
        sel_month = selected_date_for_month.month
        
        progress_df = get_monthly_status(sel_year, sel_month)
        
        if not progress_df.empty:
            st.dataframe(progress_df, width="stretch", hide_index=True)
        else:
            st.info("目前無活躍的訂閱合約。")
            
    # [新增] 回饋 Tab
    with tab_feedback:
        st.subheader("客戶回饋中心")
        st.caption("來自 QR Code 掃描後的真實聲音")
        
        feedback_sql = """
            SELECT f.created_at, c.name, f.rating, f.comment
            FROM feedback f
            JOIN subscriptions s ON f.subscription_id = s.id
            JOIN customers c ON s.customer_id = c.id
            ORDER BY f.created_at DESC
        """
        fb_df = get_df(feedback_sql)
        
        if not fb_df.empty:
            for _, row in fb_df.iterrows():
                with st.chat_message("user"):
                    stars = "★" * row['rating']
                    st.write(f"**{row['name']}** ({row['created_at']})")
                    st.markdown(f"評分: {stars}")
                    if row['comment']:
                        st.info(row['comment'])
                    else:
                        st.caption("無文字評論")
        else:
            st.info("尚無客戶回饋資料。")

# === 頁面 4: 系統設定 ===
elif menu == "系統設定":
    st.title("系統參數設定")
    with st.expander("苗種進貨管理", expanded=True):
        current_crops = get_df("SELECT id, name, category, quota_shuanglong, quota_luona, tray_size FROM crops")
        if not current_crops.empty:
            edited_crops = st.data_editor(
                current_crops,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True, width="small"),
                    "name": st.column_config.TextColumn("作物名稱", disabled=True),
                    "category": st.column_config.TextColumn("類別", disabled=True),
                    "tray_size": st.column_config.NumberColumn("每盤株數", min_value=1, max_value=200, step=1),
                    "quota_shuanglong": st.column_config.NumberColumn("雙龍剩餘盤數", min_value=0, step=1),
                    "quota_luona": st.column_config.NumberColumn("羅娜剩餘盤數", min_value=0, step=1)
                },
                disabled=["id", "name", "category"],
                width="stretch",
                hide_index=True,
                key="crops_editor"
            )
            if st.button("儲存盤數設定", type="primary"):
                conn = get_conn()
                cursor = conn.cursor()
                for index, row in edited_crops.iterrows():
                    cursor.execute("UPDATE crops SET quota_shuanglong = ?, quota_luona = ?, tray_size = ? WHERE id = ?", 
                                   (row['quota_shuanglong'], row['quota_luona'], row['tray_size'], row['id']))
                conn.commit()
                conn.close()
                st.success("設定已更新！")
                time.sleep(1); st.rerun()

    with st.expander("農民資料管理", expanded=True):
        tab_view, tab_add, tab_del = st.tabs(["檢視名單", "➕新增農民", "➖刪除農民"])
        with tab_view:
            farmers = get_df("SELECT * FROM farmers")
            st.dataframe(farmers, width="stretch")
        with tab_add:
            with st.form("add_farmer_form_main"):
                new_name = st.text_input("姓名"); new_tribe = st.selectbox("部落", ["雙龍部落", "羅娜部落"]); new_phone = st.text_input("電話")
                if st.form_submit_button("新增資料") and new_name:
                    add_new_farmer(new_name, new_tribe, new_phone); st.success(f"已新增：{new_name}"); time.sleep(1); st.rerun()
        with tab_del:
            all_farmers = get_df("SELECT * FROM farmers")
            if not all_farmers.empty:
                del_dict = {f"{r['name']} ({r['tribe_location']})": r['id'] for i, r in all_farmers.iterrows()}
                del_name = st.selectbox("選擇欲移除對象", list(del_dict.keys()), key="del_farmer_select_main")
                if st.button("確認刪除此農民", type="primary"):
                    delete_farmer(del_dict[del_name]); st.success(f"已移除"); time.sleep(1); st.rerun()
                    
    with st.expander("蔬菜箱配方設定 (BOM)"):
        st.json(BOX_CONFIG)
        st.write("**重量設定 (g/份):**", WEIGHT_CONFIG)