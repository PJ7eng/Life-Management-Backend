# 使用 Python 3.8 作為基礎鏡像
FROM python:3.8-slim

# 設置工作目錄
WORKDIR /app

# 複製 requirements.txt
COPY requirements.txt ./

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製項目文件
COPY . .

# 暴露端口（FastAPI 默認使用 8000）
EXPOSE 8000

# 運行 FastAPI 應用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]