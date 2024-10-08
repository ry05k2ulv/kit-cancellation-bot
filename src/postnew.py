"""
Description:
    京都工芸繊維大学の休講通知をXにポストするスクリプト

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
import os
import sys

import dotenv
from sqlalchemy.orm.session import Session

from browser import (
    fetch_cancellation_list,
    init_driver,
    post_cancellation_list_individually,
)
from database import (
    create_database,
    insert_cancellation_list_if_not_exist,
    select_cancellation_list_by_posted,
    update_cancellation_list_posted,
)
from debug import get_logger


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=str, default=".env")
    parser.add_argument("--remote", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--cookie", type=str, default="cookies.pkl")
    parser.add_argument("--database", type=str, default="cancellations.db")
    return parser.parse_args()


if __name__ == "__main__":
    # ロガーの設定
    logger = get_logger(__file__)
    logger.debug("Start")

    args = parse_args()

    # 環境変数の読み込み
    dotenv.load_dotenv(args.env)
    kit_username = os.getenv("KIT_USERNAME")
    kit_password = os.getenv("KIT_PASSWORD")
    x_username = os.getenv("X_USERNAME")
    x_password = os.getenv("X_PASSWORD")

    if None in (kit_username, kit_password, x_username, x_password):
        logger.error("Environment variables are not set")
        sys.exit(1)

    # WebDriverの初期化
    driver = init_driver(args.remote, args.headless)

    # データベースの初期化
    session = create_database(args.database)

    # 京都工芸繊維大学の休講情報を取得
    cancellation_list = fetch_cancellation_list(driver, kit_username, kit_password)

    # データベースに休講情報を挿入
    insert_cancellation_list_if_not_exist(session, cancellation_list)

    # 未ポストの休講情報を取得
    new_list = select_cancellation_list_by_posted(session, False)

    # Xにポスト
    if new_list:
        post_cancellation_list_individually(
            driver,
            x_username,
            x_password,
            args.cookie,
            "【新着の休講情報】",
            new_list,
        )

    # ポスト済みに更新
    update_cancellation_list_posted(session, new_list, True)

    # 終了
    driver.quit()

    logger.debug("End")
