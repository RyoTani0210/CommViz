import slackAPI


# testworkspaseのtoken
token ="xoxp-3720489068866-3722895609988-4327524841843-7b1130cc02835ea57dd11b3c8ef7211a"


#log設定
slackAPI.setup_log(__file__)

# request のテスト
## 準備
s = slackAPI.Request()
s.token  = token
s.url = "https://slack.com/api/conversations.list"
## 実施
s.get()
## 検証
assert s.http_status == 200 #正常なレスポンス
assert s.raw != None #空でないこと



# channelクラス
# 準備
channels = slackAPI.Channels()
channels.token = token

# テスト
channels.get()
channels.save("data/testworkspase/test_channels.json")

#検証
assert len(channels.data) > 0

#memberクラス
members = slackAPI.Members()
members.token = token
members.get()
members.save("data/testworkspase/test_members.json")

#メッセージ
for channel_id in channels.get_ids():
    messages = slackAPI.Messages(channel_id)
    messages.token = token
    messages.get_include_replies()
    messages.save(f"data/testworkspase/{channel_id}.json")


