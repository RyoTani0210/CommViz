"""
実行ファイル
"""
import json
import preprocessing
import pickle


workspasename = "sample"
messages = preprocessing.Messages()

#channel_idリスト作成
channels_json =json.load(open(f"data/{workspasename}/channels.json", encoding="utf8"))
channel_ids = [channel["id"] for channel in channels_json]

#channelごとにread
for channel_id in channel_ids:
    messages_json = json.load(open(f"data/{workspasename}/{channel_id}.json", encoding="utf8"))
    messages.append(messages_json, channel_id=channel_id)#集約

#1ファイルにして出力
with open(f"data/{workspasename}/messages.df.pkl", "wb") as f:
    pickle.dump(messages.to_dataframe(), f)
