"""
Description:
    京都工芸繊維大学の当日の休講通知をXにポストするスクリプト

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
"""

import argparse
import datetime
import os
import sys

import dotenv

from browser import init_driver, post_cancellation_list_in_bullet_points
from database import Cancellation, create_database, get_cancellation_list_by_date


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=str, default=".env")
    parser.add_argument("--remote", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--cookie", type=str, default="cookies.pkl")
    parser.add_argument("--database", type=str, default="cancellations.db")
    return parser.parse_args()


if __name__ == "__main__":
    print("Start posttoday.py", file=sys.stderr)

    args = parse_args()

    # 環境変数の読み込み
    dotenv.load_dotenv(args.env)
    x_username = os.getenv("X_USERNAME")
    x_password = os.getenv("X_PASSWORD")

    if None in (x_username, x_password):
        print("", file=sys.stderr)
        sys.exit(1)

    # WebDriverの初期化
    driver = init_driver(args.remote, args.headless)

    # データベースの初期化
    session = create_database(args.database)

    # 今日の休講情報を取得
    today = datetime.date.today().strftime("%Y/%-m/%-d")
    cancellation_list = get_cancellation_list_by_date(session, today)

    # Xにポスト
    post_cancellation_list_in_bullet_points(
        driver,
        x_username,
        x_password,
        args.cookie,
        "【本日の休講情報】",
        cancellation_list,
    )

    # 終了
    driver.quit()

    print("End posttoday.py", file=sys.stderr)
