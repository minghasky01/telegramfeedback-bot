# 使用官方 Python 版本
FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 複製所有檔案到容器中
COPY . .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# Render 會提供 PORT 環境變數
ENV PORT=10000
EXPOSE 10000

# 啟動你的機器人
CMD ["python3", "bot.py"]
