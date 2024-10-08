FROM python:3.12.0-slim

# タイムゾーンを日本時間に設定
ENV TZ=Asia/Tokyo
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN echo "Asia/Tokyo" > /etc/timezone

# パッケージのインストール
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# cronのインストール
RUN apt-get update && \
    apt-get install -y cron && \
    apt-get install -y sqlite3 && \
    rm -rf /var/lib/apt/lists/*


# python-jobをcronに登録し，cronを起動
ENTRYPOINT [ "sh", "-c", " \
    echo 'Bot Starting' && \
    chmod 0644 /etc/cron.d/python-job && \
    crontab /etc/cron.d/python-job && \
    touch /var/log/cron.log && \
    cron && \
    echo 'Cron Started' && \
    tail -f /var/log/cron.log" ]

