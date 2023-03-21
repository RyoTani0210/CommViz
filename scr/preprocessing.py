"""
取得したデータを可視化のためのデータにするモジュール


出力データに合わせてつくる?
入力データのパースをするクラス
パースしたデータを集約・加工して求める表をつくる


"""
import re
import pandas as pd


class Messages:
    """
    メッセージや返信を集約した

    """
    def __init__(self):
        #チャンネル単位
        self.data = {
            "channel_id": [],
            #メッセージ単位
            "client_msg_id": [],
            "message_type": [],
            "timestamp": [],
            #人関係
            "send_user_id": [],#送信した人のID
            "recieved_user_id": [],#受信した人のID
            "team": [],#teamのID
            "text": [],#本文
            #reply関係
            "reply_count": [],
            "reply_users_count": [],
            "reply_users": [],
            "latest_reply_timestamp": [],
            "thread_timestamp": [],#おそらくメッセージのtimestampと一致するが念のため
        }


    def append(self, messages, channel_id=str()):
        """
        channelsに指定されたIDのチャンネルのデータを読み込んで表形式に整理して出力する
        """
        for message in messages:
            self.data["channel_id"].append(channel_id)
            self.data["client_msg_id"].append(message.get("client_msg_id", None))
            self.data["message_type"].append(message.get("type", None))
            self.data["timestamp"].append(to_datetime(message.get("ts", None)))
            self.data["text"].append(message.get("text", None))
            #人関係
            self.data["send_user_id"].append(message.get("user", None))
            mentioned_members = collect_mensioned_members(message.get("text", []))
            self.data["recieved_user_id"].append(set(mentioned_members))
            self.data["team"].append(message.get("team", None))

            #reply関係
            self.data["reply_count"].append(message.get("reply_count", None))
            self.data["reply_users_count"].append(message.get("reply_users_count", None))
            self.data["reply_users"].append(set(message.get("reply_users", [])))
            self.data["latest_reply_timestamp"].append(to_datetime(message.get("latest_reply", None)))
            self.data["thread_timestamp"].append(to_datetime(message.get("thread_ts", None)))
    def to_dataframe(self):
        """dataをデータフレームとして出力する"""
        return pd.DataFrame(self.data)


def collect_mensioned_members(text):
    """
    textから、<@~>の~にあるメンバーのIDを抽出する
    """
    return re.findall(r"<@([0-9A-Z]+?)>", text)

def to_datetime(number):
    """
    unix時刻(秒)をpandasのdatetime64(utc)に変換する
    """
    return pd.to_datetime(number, unit="s")

class Relations:
    """関係行列"""
    def __init__(self):
        self.data = {
            "channel_id":[],
            "timestamp":[],
            "from":[],
            "to":[]
        }
