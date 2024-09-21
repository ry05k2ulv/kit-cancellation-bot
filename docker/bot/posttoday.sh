#!/bin/bash

/usr/local/bin/python /app/src/posttoday.py \
    --env /app/.env \
    --remote "http://chrome:4444/wd/hub" \
    --headless \
    --cookie /app/cache/cookies.pkl \
    --database /app/cache/database.db \
    --when $1
