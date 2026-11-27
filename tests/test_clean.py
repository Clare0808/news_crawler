import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from clean import (  # noqa: E402
    clean_content,
    clean_header,
    ctee_article_key,
    drop_duplicates_within_source,
    parse_time,
)


def test_cna_caption_dateline_and_tail_removed():
    raw = "圖為基隆港貨櫃場一景。（中央社檔案照片）（中央社記者曾筠庭台北21日電）經濟部今天表示，出口有望破兆。（編輯：張均懋）1151121"
    text, hits = clean_content(raw, "CNA")
    assert text == "經濟部今天表示，出口有望破兆。"
    assert {"cna_photo_caption", "cna_dateline", "cna_editor_tail"} <= set(hits)


def test_cna_caption_with_foreign_credit_and_photographer():
    assert clean_content("民眾行走在積雪道路上。（共同社）（中央社東京21日綜合外電報導）山形縣下雪。", "CNA")[0] == "山形縣下雪。"
    raw = "研討會在台北舉辦。中央社記者陳至中台北攝 115年11月21日（中央社記者陳至中台北21日電）研討會今天登場。"
    assert clean_content(raw, "CNA")[0] == "研討會今天登場。"
    raw = "甘澍宮發生大火。（民眾提供）中央社記者鄭維真傳真 115年11月21日（中央社記者鄭維真彰化21日電）甘澍宮今天凌晨發生大火。"
    assert clean_content(raw, "CNA")[0] == "甘澍宮今天凌晨發生大火。"


def test_cna_caption_with_inner_parentheses():
    raw = "川普（中）20日返回白宮。（美聯社）（中央社華盛頓20日綜合外電報導）川普今天召開記者會。"
    assert clean_content(raw, "CNA")[0] == "川普今天召開記者會。"


def test_cna_without_caption_keeps_body():
    raw = "（中央社台北20日電）新台幣今天收盤收32.936元。1151120"
    assert clean_content(raw, "CNA")[0] == "新台幣今天收盤收32.936元。"


def test_wealth_nested_tails_removed():
    raw = "內文。（雜誌原始標題為：某標題）※本網站及作者所提供資訊僅供參考，投資人應自行承擔投資風險及投資結果。延伸閱讀："
    assert clean_content(raw, "Wealth")[0] == "內文。"
    assert clean_content("內文。（本文由「」授權轉載）   延伸閱讀：", "Wealth")[0] == "內文。"
    assert clean_content("延伸閱讀：", "Wealth")[0] == ""


def test_edn_word_count_copyright_and_caption_line():
    raw = "本文共81字\r\n第一段。\r\n銀行贊助演唱會。圖／凱基銀行提供\r\n第二段。\r\n【未經MIC許可，不得轉載與作其他用途使用】"
    assert clean_content(raw, "EDN")[0] == "第一段。\n第二段。"


def test_ctee_fullwidth_space_and_moneydj():
    assert clean_content("第一段。\r\n　第二段。", "CTEE")[0] == "第一段。\n第二段。"
    raw = "MoneyDJ新聞 2026-11-21 03:01:29 數位內容中心 發佈Broadcom下跌...詳全文（本文由 MoneyDJ新聞 授權轉載）"
    text, hits = clean_content(raw, "CTEE")
    assert text == "Broadcom下跌"
    assert "ctee_moneydj_tail" in hits


def test_rules_do_not_touch_other_sources():
    raw = "內文。延伸閱讀："
    assert clean_content(raw, "CNA")[0] == raw


def test_missing_content():
    assert clean_content(float("nan"), "CNA") == ("", [])


def test_header_whitespace():
    assert clean_header("  台積電　法說會\n 登場 ") == "台積電 法說會 登場"


def test_parse_time_timezones():
    local = parse_time(pd.Series(["2026/11/21 16:50", "2026-11-18T16:34:30", "2026-09-15 22:43"]), "CNA")
    assert local.tolist() == [
        "2026-11-21T16:50:00+08:00",
        "2026-11-18T16:34:30+08:00",
        "2026-09-15T22:43:00+08:00",
    ]
    utc = parse_time(pd.Series(["2026-11-04T03:01:40.000Z"]), "Wealth")
    assert utc.tolist() == ["2026-11-04T11:01:40+08:00"]
    assert parse_time(pd.Series(["不是時間"]), "CNA").tolist() == [""]


def test_ctee_same_article_in_two_categories_merged():
    assert ctee_article_key("https://www.ctee.com.tw/news/20261117700093-430301") == "20261117700093"
    df = pd.DataFrame({
        "SourceCode": ["CTEE", "CTEE", "CTEE"],
        "Url": [
            "https://www.ctee.com.tw/news/20261117700093-430301",
            "https://www.ctee.com.tw/news/20261117700093-430303",
            "https://www.ctee.com.tw/news/20261117700094-430301",
        ],
        "Category": ["金融", "產業", "金融"],
        "Header": ["A", "A", "B"],
        "Content": ["x", "x", "y"],
    })
    kept, dropped = drop_duplicates_within_source(df)
    assert len(kept) == 2 and len(dropped) == 1
    assert kept.iloc[0]["Category"] == "金融、產業"
