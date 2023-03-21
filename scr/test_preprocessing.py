import preprocessing
import pytest
import pandas as pd







@pytest.mark.parametrize(("text", "expected"),[
        ("<@ABC0123>あいうえお", ["ABC0123"]),#普通
        ("<@ABC0123><@XYZ098>あいうえお", ["ABC0123", "XYZ098"]),#複数
        ("あいうえお", []),#なし
        ("あいう<@ABC0123>えお", ["ABC0123"]),#先頭以外にある
        ("<ABC0123>あいうえお", []),#mentionではないパターン
        ("<あいう@ABC0123>あいう", []),#mentionではないパターン
        ("<@ABC0あ123>あいうえお", []),#メンションではないパターン
        ("<@ABC0n123>あいうえお", []),#メンションではないパターン
        ("あい\n<@ABC0123>うえお", ["ABC0123"]),#改行の直後
        ("あい<@ABC0123>\nうえお", ["ABC0123"]),#すぐ後に改行
        ("<@P7CEEQMB>9E+:+*HYmb'2Qqx0k<mDB*xhu&Kwae(xt{BW~%7\t*JmyPPGYcT>P#+dEt{0Hb!\u000b3i77aei/W[N<dY\\%?*3AKgI&ZjHI-}i!D^m\r\\A{!zA..u:",["P7CEEQMB"])
])
def test_collect_mentioned_members(text, expected):
    result = preprocessing.collect_mensioned_members(text)
    print(result)
    assert result == expected


@pytest.mark.parametrize(("unixtime", "expected"), [
#期待値はcasioの高精度計算サイトを使った　https://keisan.casio.jp/exec/system/1526004418
        (1560000000.123456, pd.to_datetime("2019-06-08T13:20:00.123456", format="%Y-%m-%dT%H:%M:%S.%f")),
        (1894722857, pd.to_datetime("2030-01-15T15:54:17.000000", format="%Y-%m-%dT%H:%M:%S.%f")),
        (1421337257, pd.to_datetime("2015-01-15T15:54:17.000000", format="%Y-%m-%dT%H:%M:%S.%f")),
        (None, None)
])
def test_to_datetime(unixtime, expected):
    result = preprocessing.to_datetime(unixtime)
    assert result == expected