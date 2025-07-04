# 安裝前檢查
# python --version
# pip --version
# 如果需要更新 pip：pip install --upgrade pip

# 安裝說明
# 1. 創建虛擬環境（推薦）：
#    python -m venv venv
# 在 Linux 上使用: source venv/bin/activate  
# 在 Windows 上使用: venv\Scripts\activate

# 2. 安裝依賴項：
#    pip install -r requirements.txt

# 3. 初始化數據庫
#    python init_db.py

# 4. 運行後端服務
#    uvicorn main:app --host 0.0.0.0 --port 8000
