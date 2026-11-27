"""新聞資料清洗：讀 result/*.csv，輸出 cleaned/。

用法：python clean.py
輸出：
  cleaned/news_clean.csv   清洗後、四家合併的新聞
  cleaned/rejected.csv     被剔除的新聞與原因
  cleaned/clean_report.md  每家來源的處理統計
原始 result/*.csv 不會被修改。
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "result"
OUT_DIR = ROOT / "cleaned"

SOURCES = {
    "CNA": "中央社",
    "CTEE": "工商時報",
    "EDN": "經濟日報",
    "Wealth": "財訊",
}

# 工商時報 API 只回傳前 200 字摘要
CTEE_SUMMARY_LEN = 200
# 清洗後少於這個字數就視為無效內容
MIN_CONTENT_LEN = 20

# 每家來源的雜訊規則：(規則名稱, 正規表示式)
# 依序套用，命中的規則名稱會記到 Flags 欄位，方便回頭查
RULES = {
    "CNA": [
        # 開頭圖說：緊接在電頭前、以圖片來源結尾的那段文字，例如
        # 「圖為…。（中央社檔案照片）」「…道路上。（共同社）」「…研討會。中央社記者X攝 115年11月21日」
        ("cna_photo_caption", r"^.{0,300}?(（[^）]{1,40}）|(攝|傳真)\s*\d{3}年\d{1,2}月\d{1,2}日)(?=（中央社)"),
        # 電頭：「（中央社記者X台北21日電）」「（中央社紐約20日綜合外電報導）」
        ("cna_dateline", r"^（中央社[^）]{0,60}）"),
        # 結尾編輯與民國日期碼：「（編輯：張均懋）1151121」
        ("cna_editor_tail", r"（編輯：[^）]{1,20}）\s*\d{7}\s*$"),
        ("cna_date_code", r"\d{7}\s*$"),
    ],
    "CTEE": [
        ("ctee_dateline", r"^【時報[^】]{0,60}】"),
        ("ctee_moneydj_head", r"^MoneyDJ新聞\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\S{0,10}\s*發佈"),
        ("ctee_moneydj_tail", r"\.{3}詳全文（本文由\s*MoneyDJ新聞\s*授權轉載）\s*$"),
    ],
    "EDN": [
        ("edn_word_count", r"^本文共\d+字\s*"),
        ("edn_copyright", r"【未經[^】]{0,20}許可，不得轉載[^】]{0,20}】\s*$"),
        # 獨立成行的圖說：「…。圖／凱基銀行提供」
        ("edn_photo_caption", r"(?m)^[^\n]{0,150}圖／[^\n。]{1,30}$"),
    ],
    "Wealth": [
        ("wealth_read_more", r"延伸閱讀：\s*$"),
        ("wealth_statement", r"【嚴正聲明】.*?切勿上當受騙！"),
        ("wealth_disclaimer", r"※?本網站及作者所提供資訊僅供參考，投資人應自行承擔投資風險及投資結果。"),
        ("wealth_reprint", r"※?（?本文由「[^」]*」授權(轉載|刊載)[^）\n]{0,20}）?"),
        ("wealth_orig_title", r"（雜誌原始標題為：[^）]*）"),
        ("wealth_no_reprint", r"（本文不開放合作媒體轉載）\s*$"),
    ],
}


def normalize_whitespace(text: str) -> str:
    """統一換行、去掉全形空白與多餘空行，段落之間保留一個換行。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("　", " ").replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


def clean_content(text, source_code: str):
    """回傳 (清洗後內文, 命中的規則名稱 list)。"""
    if not isinstance(text, str):
        return "", []
    text = normalize_whitespace(text)
    hits = []
    # 尾巴規則可能互相包住（例如免責聲明後面才是「延伸閱讀：」），重複套用到不再變動
    changed = True
    while changed:
        changed = False
        for name, pattern in RULES.get(source_code, []):
            new_text = re.sub(pattern, "", text, flags=re.S).strip()
            if new_text != text:
                text = new_text
                changed = True
                if name not in hits:
                    hits.append(name)
    return normalize_whitespace(text), hits


def clean_header(text) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r"\s+", " ", text.replace("　", " ")).strip()


def parse_time(series: pd.Series, source_code: str) -> pd.Series:
    """統一成台北時間 ISO 8601（+08:00）。

    中央社、工商時報、經濟日報給的是沒標時區的台北時間；財訊給的是 UTC（結尾 Z）。
    """
    if source_code == "Wealth":
        parsed = pd.to_datetime(series, utc=True, errors="coerce").dt.tz_convert("Asia/Taipei")
    else:
        parsed = pd.to_datetime(series, format="mixed", errors="coerce").dt.tz_localize("Asia/Taipei")
    return parsed.map(lambda t: t.isoformat() if pd.notna(t) else "")


def ctee_article_key(url: str) -> str:
    """工商時報同一篇文章掛在不同分類時，網址只差最後的分類碼：
    /news/20261117700093-430301 與 /news/20261117700093-430303 是同一篇。"""
    m = re.search(r"/news/(\d+)-\d+", url or "")
    return m.group(1) if m else url


def dedup_key(text: str) -> str:
    """比對重複用：去掉空白與標點，只留文字和數字。"""
    return re.sub(r"[\W_]+", "", text or "")


def load_source(code: str) -> pd.DataFrame:
    df = pd.read_csv(RESULT_DIR / f"{code}_news.csv", dtype=str)
    df["SourceCode"] = code
    df["Source"] = SOURCES[code]  # 修正財訊爬蟲寫成「財經」的問題
    df["RawContentLen"] = df["Content"].fillna("").str.len()
    return df


def clean_source(df: pd.DataFrame, code: str) -> pd.DataFrame:
    df = df.copy()
    df["Header"] = df["Header"].map(clean_header)
    results = df["Content"].map(lambda t: clean_content(t, code))
    df["Content"] = results.map(lambda r: r[0])
    df["Flags"] = results.map(lambda r: r[1])
    df["PublishedAt"] = parse_time(df["CreateTime"], code)
    df["ContentLen"] = df["Content"].str.len()

    df["IsTruncated"] = False
    if code == "CTEE":
        df["IsTruncated"] = (df["RawContentLen"] == CTEE_SUMMARY_LEN) | df["Flags"].map(
            lambda f: "ctee_moneydj_tail" in f
        )
        # 紙本報紙的文章時間固定是 03:00:00，不是實際發布時間
        df["TimeIsPlaceholder"] = df["CreateTime"].fillna("").str.endswith("T03:00:00")
    else:
        df["TimeIsPlaceholder"] = False
    return df


def split_rejected(df: pd.DataFrame):
    reasons = pd.Series("", index=df.index)
    reasons[df["ContentLen"] < MIN_CONTENT_LEN] = f"內文少於 {MIN_CONTENT_LEN} 字"
    reasons[(df["PublishedAt"] == "") & (reasons == "")] = "發布時間無法解析"
    rejected = df[reasons != ""].assign(RejectReason=reasons[reasons != ""])
    return df[reasons == ""], rejected


def drop_duplicates_within_source(df: pd.DataFrame):
    """同一家來源內的重複：工商時報同篇多分類合併，其他用標題加內文比對。"""
    df = df.copy()
    if (df["SourceCode"] == "CTEE").all():
        df["_key"] = df["Url"].map(ctee_article_key)
    else:
        df["_key"] = df["Header"].map(dedup_key) + "|" + df["Content"].map(dedup_key)

    # 保留第一筆，其他分類併進 Category（用「、」分隔）
    categories = df.groupby("_key", sort=False)["Category"].agg(
        lambda c: "、".join(dict.fromkeys(x for x in c if isinstance(x, str)))
    )
    dup_mask = df["_key"].duplicated(keep="first")
    dropped = df[dup_mask].assign(RejectReason="同來源重複")
    kept = df[~dup_mask].copy()
    kept["Category"] = kept["_key"].map(categories)
    return kept.drop(columns="_key"), dropped.drop(columns="_key")


def mark_cross_source_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """不同來源刊出同一篇稿（多半是中央社供稿）：不刪，只標同一個 DupGroup。"""
    df = df.copy()
    key = df["Content"].map(dedup_key)
    counts = key.map(key.value_counts())
    group_ids = {k: f"G{i:04d}" for i, k in enumerate(key[counts > 1].unique(), 1)}
    df["DupGroup"] = key.map(group_ids).fillna("")
    return df


OUTPUT_COLUMNS = [
    "Id", "Source", "SourceCode", "Category", "SubCategory", "Url", "Header",
    "PublishedAt", "TimeIsPlaceholder", "Content", "ContentLen", "IsTruncated",
    "DupGroup", "Flags",
]


def run() -> dict:
    OUT_DIR.mkdir(exist_ok=True)
    kept_parts, rejected_parts, stats = [], [], []

    for code in SOURCES:
        raw = load_source(code)
        cleaned = clean_source(raw, code)
        valid, rejected = split_rejected(cleaned)
        deduped, dups = drop_duplicates_within_source(valid)
        kept_parts.append(deduped)
        rejected_parts += [rejected, dups]
        stats.append({
            "來源": SOURCES[code],
            "原始筆數": len(raw),
            "內容無效剔除": len(rejected),
            "同來源重複剔除": len(dups),
            "保留": len(deduped),
            "內文被截斷": int(deduped["IsTruncated"].sum()),
            "時間為紙本預設值": int(deduped["TimeIsPlaceholder"].sum()),
            "清掉雜訊的篇數": int((deduped["Flags"].str.len() > 0).sum()),
        })

    news = mark_cross_source_duplicates(pd.concat(kept_parts, ignore_index=True))
    news = news.sort_values(["PublishedAt", "SourceCode"], ascending=[False, True])
    news["Id"] = news["SourceCode"] + "-" + news["Url"].map(
        lambda u: re.sub(r"\W+", "", u.rsplit("/", 1)[-1].replace(".aspx", ""))
    )
    news["Flags"] = news["Flags"].map(";".join)
    news[OUTPUT_COLUMNS].to_csv(OUT_DIR / "news_clean.csv", index=False, encoding="utf-8-sig")

    rejected = pd.concat(rejected_parts, ignore_index=True)
    rejected["Flags"] = rejected["Flags"].map(";".join)
    rejected[["Source", "Url", "Header", "CreateTime", "RawContentLen", "RejectReason"]].to_csv(
        OUT_DIR / "rejected.csv", index=False, encoding="utf-8-sig"
    )

    stats_df = pd.DataFrame(stats)
    cross = news[news["DupGroup"] != ""]
    rule_counts = news["Flags"].str.split(";").explode().loc[lambda s: s != ""].value_counts()
    report = [
        "# 清洗報告",
        "",
        "由 `python clean.py` 產生，不要手動修改。",
        "",
        stats_df.to_markdown(index=False),
        "",
        f"合計保留 {len(news)} 篇。不同來源刊出同一篇稿的有 {cross['DupGroup'].nunique()} 組、"
        f"{len(cross)} 篇，保留並標在 `DupGroup` 欄位。",
        "",
        "## 各規則命中篇數",
        "",
        rule_counts.rename_axis("規則").rename("篇數").to_frame().to_markdown(),
        "",
    ]
    (OUT_DIR / "clean_report.md").write_text("\n".join(report), encoding="utf-8")
    return {"news": news, "rejected": rejected, "stats": stats_df}


if __name__ == "__main__":
    out = run()
    print(out["stats"].to_string(index=False))
    print(f"\n輸出：{OUT_DIR}")
