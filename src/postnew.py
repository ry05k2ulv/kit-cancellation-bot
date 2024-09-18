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

from browser import fetch_cancellation_list, init_driver, post_cancellation_list
from database import Cancellation, create_database


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", type=str, default=".env")
    parser.add_argument("--remote", type=str, default=None)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--cookie", type=str, default="cookies.pkl")
    parser.add_argument("--database", type=str, default="cancellations.db")
    return parser.parse_args()


def pick_up_new_cancellation_list(
    session: Session,
    cancellation_list: list[dict[str, str]],
) -> list[dict[str, str]]:
    new_list = []
    for c in cancellation_list:
        exist = session.query(Cancellation).filter_by(**c).first()
        if not exist:
            new_list.append(c)
            new_cancellation = Cancellation(**c)
            session.add(new_cancellation)

    session.commit()
    return new_list


if __name__ == "__main__":
    print("Start postnew.py", file=sys.stderr)

    args = parse_args()

    # 環境変数の読み込み
    dotenv.load_dotenv(args.env)
    kit_username = os.getenv("KIT_USERNAME")
    kit_password = os.getenv("KIT_PASSWORD")
    x_username = os.getenv("X_USERNAME")
    x_password = os.getenv("X_PASSWORD")

    if None in (kit_username, kit_password, x_username, x_password):
        print("", file=sys.stderr)
        sys.exit(1)

    # WebDriverの初期化
    driver = init_driver(args.remote, args.headless)

    # データベースの初期化
    session = create_database(args.database)

    # 京都工芸繊維大学の休講情報を取得
    cancellation_list = fetch_cancellation_list(driver, kit_username, kit_password)

    # 新しい休講情報を取得
    new_list = pick_up_new_cancellation_list(session, cancellation_list)

    # Xにポスト
    if new_list:
        post_cancellation_list(
            driver,
            x_username,
            x_password,
            args.cookie,
            "【新着の休講情報】",
            new_list,
        )

    # 終了
    driver.quit()
    print("End postnew.py", file=sys.stderr)
