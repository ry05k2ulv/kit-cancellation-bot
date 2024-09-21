import os
import pickle as pkl

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from database import Cancellation

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15"
IMPLICIT_WAIT = 20

KIT_CANCELLATION_URL = "https://portal.student.kit.ac.jp/ead/?c=lecture_cancellation"
KIT_USERNAME_ID = "username"
KIT_PASSWORD_ID = "password"
KIT_SUBMIT_XPATH = '//button[@type="submit"]'
KIT_TBODY_XPATH = '//*[@id="cancel_info_data_tbl"]/tbody'

X_LOGIN_URL = "https://x.com/i/flow/login"
X_POST_URL = "https://twitter.com/intent/tweet?text={text}&hashtags={hashtags}"
X_HOME_URL = "https://x.com/home"
X_TEXT_XPATH = '//input[@name="text"]'
X_PASSWORD_XPATH = '//input[@name="password"]'
X_POST_XPATH = '//button[@data-testid="tweetButton"]'


def init_driver(
    remote_url: str | None,
    headless: bool,
) -> WebDriver:
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument(f"user-agent={USER_AGENT}")
        options.add_argument("--disable-gpu")
        options.add_argument("--hide-scrollbars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if remote_url:
        driver = webdriver.Remote(command_executor=remote_url, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.implicitly_wait(IMPLICIT_WAIT)
    return driver


def fetch_cancellation_list(
    driver: WebDriver,
    username: str,
    password: str,
) -> list[Cancellation]:
    # ログイン
    driver.get(KIT_CANCELLATION_URL)
    driver.find_element(By.ID, KIT_USERNAME_ID).send_keys(username)
    driver.find_element(By.ID, KIT_PASSWORD_ID).send_keys(password)
    driver.find_element(By.XPATH, KIT_SUBMIT_XPATH).click()

    # 休講情報を取得
    tbody = driver.find_element(By.XPATH, KIT_TBODY_XPATH)
    list = []
    for tr in tbody.find_elements(By.TAG_NAME, "tr")[1:]:
        td_list = tr.find_elements(By.TAG_NAME, "td")
        list.append(
            Cancellation(
                program=td_list[1].text,
                course=td_list[2].text,
                instructor=td_list[3].text,
                date=td_list[4].text,
                day_of_week=td_list[5].text,
                period=td_list[6].text,
                remarks=td_list[7].text,
                published_at=td_list[8].text,
            )
        )
    return list


def login_x(
    driver: WebDriver,
    username: str,
    password: str,
    cookie_filename: str,
):
    # クッキーファイルが存在する場合は読み込む
    if os.path.exists(cookie_filename):
        driver.get(X_HOME_URL)
        cookies = pkl.load(open(cookie_filename, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.get(X_HOME_URL)

    # クッキーファイルが存在しない場合はログインする
    else:
        driver.get(X_LOGIN_URL)
        elem = driver.find_element(By.XPATH, X_TEXT_XPATH)
        elem.send_keys(username)
        elem.send_keys(Keys.RETURN)

        elem = driver.find_element(By.XPATH, X_PASSWORD_XPATH)
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)

    # ログイン後の画面が表示されるまで待つ
    WebDriverWait(driver, 16).until(EC.url_contains(X_HOME_URL))

    # クッキーを保存
    cookies = driver.get_cookies()
    pkl.dump(cookies, open(cookie_filename, "wb"))


def post_cancellation_list_individually(
    driver: WebDriver,
    username: str,
    password: str,
    cookie_filename: str,
    title: str,
    cancellation_list: list[Cancellation],
):
    # ログイン
    login_x(driver, username, password, cookie_filename)

    # 休講情報をポスト
    for c in cancellation_list:
        text = f"{title}%0a分類%E3%80%80：{c.program}%0a講義名：{c.course}%0a日付%E3%80%80：{c.date}({c.day_of_week}) {c.period}限%0a"
        url = X_POST_URL.format(text=text, hashtags="KIT休講情報")
        driver.get(url)
        elem = driver.find_element(By.XPATH, X_POST_XPATH)
        elem.click()

        WebDriverWait(driver, 16).until(EC.url_changes(url))


def post_cancellation_list_in_bullet_points(
    driver: WebDriver,
    username: str,
    password: str,
    cookie_filename: str,
    title: str,
    cancellation_list: list[Cancellation],
):
    # ログイン
    login_x(driver, username, password, cookie_filename)

    # 休講情報をポスト
    if cancellation_list:
        page_size = 5
        num_pages = len(cancellation_list) // page_size + (
            len(cancellation_list) % page_size > 0
        )
        for i in range(0, len(cancellation_list), page_size):
            text = f"{title} {i // page_size + 1}/{num_pages}%0a"
            for c in cancellation_list[i : i + page_size]:
                text += f"・{c.program} {c.period}限 {c.course}%0a"
            url = X_POST_URL.format(text=text, hashtags="KIT休講情報")
            driver.get(url)
            elem = driver.find_element(By.XPATH, X_POST_XPATH)
            elem.click()

            WebDriverWait(driver, 16).until(EC.url_changes(url))

    else:
        text = f"{title}%0a休講情報はありません%0a"
        url = X_POST_URL.format(text=text, hashtags="KIT休講情報")
        driver.get(url)
        elem = driver.find_element(By.XPATH, X_POST_XPATH)
        elem.click()

        WebDriverWait(driver, 16).until(EC.url_changes(url))
