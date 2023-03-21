"""
slackAPI
"""
import os
import time
import json
import logging
import datetime
import requests

from urllib3.util import Retry
from requests.adapters import HTTPAdapter


def setup_log(execfile):
    # ログ設定
    # ファイル、コンソール両方に出す
    ## 共通の設定
    log_level = "DEBUG"
    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S.%03d"#ミリ秒まで表示
    )

    ## ハンドラの設定
    ### file
    BASEPATH = os.path.dirname(execfile)
    EXECFILENAME = os.path.basename(execfile)
    filename = f"{BASEPATH}/logs/{EXECFILENAME}_{datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}.log"
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)

    ### コンソール
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(log_format)

    logging.basicConfig(level=log_level, handlers=[file_handler, stream_handler])

# このスクリプトの設定情報
format_json = {"indent": 2, "ensure_ascii": False}

class Request():
    """APIリクエスト処理"""
    def __init__(self):
        # 入力に関する属性
        # apiリクエストのパラメタ
        self.url = None  # リクエストURL(外から与えられる)
        self.token = None  # token

        # sessionパラメタ
        self.interval = 5  # リトライ間隔の秒数
        self.timeout = 300
        self.session = requests.Session()
        self.retries = Retry(
            total = 5,  # リトライ回数
            backoff_factor = self.interval,  # ?
            status_forcelist = [500, 502, 503, 504]
        )
        # 出力
        # http共通
        self.http_status = None  # httpレスポンスのステータス
        # slackAPI共通
        self.next_cursor = None
        self.raw = None  # レスポンスの返り値そのまま
        self.ok = None  # apiの返り値のok属性の値

        # セッション生成
        self.session.mount("https://", HTTPAdapter(max_retries=self.retries))

    def get(self):
        """apiを叩き、失敗したらリトライする"""
        header = {"Authorization": "Bearer " + self.token}
        try:
            time.sleep(self.interval)
            response = self.session.request(
                "GET", self.url, timeout=self.timeout, headers=header)
            self.http_status = response.status_code
        except requests.exceptions.ReadTimeout:
            logging.critical(f"Request Timeout. {self.url}")
            print("timeout")
            # TODO: 失敗したらログに出して次に行きたい

        # レスポンスがあったら
        self.raw = response.json()
        self.ok = self.raw.get("ok", "")#正常ならTrueが入る
        if self.raw.get("response_metadata") is None:
            # apiの仕様では必ずあるはずだが、空のチャンネルを取得するときになくてエラーになったので追加した
            self.next_cursor = ""
        else:
            self.next_cursor = self.raw.get("response_metadata").get('next_cursor', "")
        return response

class Common():
    """SlackAPI共通"""
    def __init__(self):
        self.data = []  # 取得されたchannelの全情報
        # self.ids = []  # idのみ
        self.token = None
        self.baseurl = None #APIのURL
        self.param = {
                "limit": 1000 #1回に取得する要素数
                }
        self.request_interval = 10 #リクエスト間隔のデフォルトは10秒
        self.target = None #rawのなかから取得する要素の名前

    def get(self):
        """APIを繰り返し叩いてすべてのデータを取得する"""
        is_end = False  # 取得がすべて終わったフラグ
        next_cursor_id = ""
        while not is_end:
            request = Request()
            request.token = self.token
            request.interval = self.request_interval  # 2秒間隔

            # param生成
            request_params = "&".join([f"{key}={val}" for key, val in self.param.items()])
            if next_cursor_id != "":
                request_params += "&" + f"cursor={next_cursor_id}"

            # リクエスト
            request.url = f"{self.baseurl}?{request_params}"
            request.get()

            # 必要なデータを取り出す
            if request.ok == True:
                self.data.extend(request.raw[self.target])

            # 終了判定と次のリクエストの準備
            if request.next_cursor == "":
                is_end = True
            else:
                next_cursor_id = request.next_cursor

        return self.data

    def get_ids(self):
        """idリストを返す"""
        return [element["id"] for element in self.data]

    def save(self, filepath):
        """data属性の中身をjson形式のファイルで保存する"""
        with open(filepath, mode="w", encoding="utf-8") as file:
            json.dump(self.data, file, **format_json)


class Channels(Common):
    """channelに関するデータ取得をする"""
    def __init__(self):
        super().__init__()
        self.baseurl = "https://slack.com/api/conversations.list"
        self.request_interval = 10
        self.target = "channels"


class Members(Common):
    """memberリストを取得する"""
    def __init__(self):
        super().__init__()
        self.baseurl = "https://slack.com/api/users.list"
        self.request_interval = 2 #リクエスト間隔2秒
        self.target = "members"


class Messages(Common):
    """チャンネル内のメッセージをすべて取得する"""
    def __init__(self, channel_id):
        super().__init__()
        self.channel_id = channel_id
        self.baseurl = "https://slack.com/api/conversations.history"
        self.request_interval = 2 #リクエスト間隔2秒
        self.target = "messages"
        self.param["channel"] = self.channel_id

    def get_timestamps(self):
        """messageのidとなるtsを返す"""
        return [message["ts"] for message in self.data]

    # 以下別のクラスの取得を楽にするためのメソッド
    def get_has_reply_timestamps(self):
        """replyのあるtsを返す"""
        return [message["ts"] for message in self.data if message.get("reply_count",0) > 0]

    def get_include_replies(self):
        """スレッド内のメッセージも含めて取得する"""
        #最初にメッセージをすべて取得
        self.get()
        # メッセージ内のリプライあるところだけを再取得
        for timestamp in self.get_has_reply_timestamps():
            sleads = Sleads(self.channel_id, timestamp)
            sleads.token = self.token
            sleads.get()
            self.data.extend(sleads.data[1:])#先頭は取得済みなので飛ばす

        return self.data

class Sleads(Messages):
    """スレッドを取得する"""
    def __init__(self, channel_id, ts):
        super().__init__(channel_id)
        # id
        self.timestamp = ts
        # api
        self.baseurl = "https://slack.com/api/conversations.replies"
        self.request_interval = 2 #リクエスト間隔2秒
        self.param["ts"] = self.timestamp
