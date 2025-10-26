# 使用輕量級 Python 版本
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製所有檔案進容器
COPY . .

# 安裝依賴套件
RUN pip install --no-cache-dir -r requirements.txt

# 設定環境變數（Render 預設會提供 PORT）
ENV PORT=10000
EXPOSE 10000

# 啟動程式
CMD ["python", "bot.py"]
