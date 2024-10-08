"""
Description:
    京都工芸繊維大学の当日・翌日の休講通知をXにポストするスクリプト

Options:
    --env <path>: str = ".env"
        環境変数のファイルパス
    --remote <url>: str | None = None
        SeleniumのリモートホストURL
    --headless: bool = False
        ヘッドレスモードで実行するかどうか
    --cookie <path>: str = "cookies.pkl"
        クッキーファイルのパス
    --database <path>: str = "cancellations.db"
        データベースファイルのパス
    --when <date>: str = "today"
        休講情報を取得する日付
        - today: 本日
        - tomorrow: 明日
"""

import argparse
import datetime
import os
import sys
from logging import getLogger

import dotenv

from browser import init_driver, post_cancellation_list_in_bullet_points
from database import Cancellation, create_database, select_cancellation_list_by_date
from debug import get_logger


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=str, default=".env")
    parser.add_argument("--remote", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--cookie", type=str, default="cookies.pkl")
    parser.add_argument("--database", type=str, default="cancellations.db")
    parser.add_argument("--when", type=str, default="today")
    return parser.parse_args()


if __name__ == "__main__":
    # ロガーの設定
    logger = get_logger(__file__)
    logger.debug("Start")

    args = parse_args()

    # 環境変数の読み込み
    dotenv.load_dotenv(args.env)
    x_username = os.getenv("X_USERNAME")
    x_password = os.getenv("X_PASSWORD")

    if None in (x_username, x_password):
        logger.error("Environment variables are not set")
        sys.exit(1)

    # WebDriverの初期化
    driver = init_driver(args.remote, args.headless)

    # データベースの初期化
    session = create_database(args.database)

    if args.when == "today":
        # 今日の休講情報を取得
        today = datetime.date.today().strftime("%Y/%-m/%-d")
        cancellation_list = select_cancellation_list_by_date(session, today)
        title = f"🌄【今日({today})の休講情報】"
    elif args.when == "tomorrow":
        # 明日の休講情報を取得
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        tomorrow = tomorrow.strftime("%Y/%-m/%-d")
        cancellation_list = select_cancellation_list_by_date(session, tomorrow)
        title = f"🌃【明日({tomorrow})の休講情報】"
    else:
        logger.error("Invalid argument: --when")
        sys.exit(1)

    # Xにポスト
    post_cancellation_list_in_bullet_points(
        driver,
        x_username,
        x_password,
        args.cookie,
        title,
        cancellation_list,
    )

    # 終了
    driver.quit()

    logger.debug("End")
