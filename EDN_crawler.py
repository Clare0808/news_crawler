from urllib.parse import urljoin
import re
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

COMPANY_URL = "https://money.udn.com"

CATEGORY = {
    "金融": {
        "金融脈動": "5613",
        "外匯市場": "5616",
        "銀行": "122376",
        "保險": "122377",
        "稅務法規": "6710"
    },
    "國際": {
        "國際焦點": "5599",
        "美股動態": "123398",
        "美國新聞": "10511",
        "外媒解析": "122381",
        "日經中文網": "120769",
    },
    "房市": {
        "房市話題": "5621",
        "不動產投資": "5930",
        "房市點線面": "12276"
    },
    "產業": {
        "產業熱點": "5612",
        "科技產業": "11162",
        "綜合產業": "10871"
    },
    "證券": {
        "市場焦點": "5607",
        "集中市場": "5710",
        "櫃買動態": "11074",
        "台股擂台": "123397",
        "證券達人": "8543"
    }
}

CODE = {
    "金融": "12017",
    "國際": "5588",
    "房市": "5593",
    "產業": "5591",
    "證券": "5590"
}

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Referer": "https://money.udn.com/money/cate/5591"
}

MAX_PAGE = 10

# 明確的付費牆提示
PAYWALL_PATTERNS = [
    r"此為付費文章",
    r"付費內容",
    r"會員限定",
    r"會員專屬",
    r"訂閱後即可閱讀",
    r"訂閱即可閱讀全文",
    r"解鎖全文",
    r"登入後即可閱讀全文",
    r"請先登入.*閱讀",
    r"購買此文章",
]

# 常見的非新聞正文
NOISE_PATTERNS = [
    r"^※?\s*歡迎用「轉貼」或「分享」的方式轉傳文章連結",
    r"^未經授權，請勿複製轉貼文章內容",
    r"^本文.*未經授權",
    r"^延伸閱讀",
    r"^相關新聞",
    r"^熱門新聞",
    r"^更多新聞",
    r"^推薦閱讀",
]

# 取得新聞列表
def get_news_block(url):
    resp = requests.get(
        url,
        headers=HEADERS,
        timeout=(5, 20)
    )

    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    news_block = soup.find_all(
        "div",
        class_="story__content"
    )

    return news_block

# 取得新聞全文
def get_news_content(url):
    resp = requests.get(
        url,
        headers=HEADERS,
        timeout=(5, 20)
    )

    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    article = soup.find("article")

    if article is None:
        return "", "找不到 article"

    paragraphs = article.find_all("p")

    content_list = []

    for p in paragraphs:

        text = p.get_text(" ", strip=True)

        if not text:
            continue

        # 排除版權、推薦新聞等雜訊
        if any(
            re.search(pattern, text, flags=re.IGNORECASE)
            for pattern in NOISE_PATTERNS
        ):
            continue

        content_list.append(text)

    news_content = "\n".join(content_list).strip()

    # 檢查付費牆
    matched_paywall = [
        pattern
        for pattern in PAYWALL_PATTERNS
        if re.search(
            pattern,
            news_content,
            flags=re.IGNORECASE
        )
    ]

    if matched_paywall:
        return "", "疑似付費牆：" + ", ".join(matched_paywall)

    # 避免將空白或極短的擷取結果寫入 CSV
    if len(news_content) < 50:
        return "", f"正文過短：{len(news_content)} 字"

    return news_content, None

clean_data_list = []

for category_name, subcategories in CATEGORY.items():
    for subcategory_name, category_id in subcategories.items():
        curr_page = 1

        while curr_page <= MAX_PAGE:
            curr_url = (
                f"https://money.udn.com/money/get_article/"
                f"{curr_page}/1001/{CODE[category_name]}/{category_id}"
                f"?_=1791614417837"
            )

            try:
                news_block = get_news_block(curr_url)

            except requests.RequestException as e:
                print(
                    f"取得 {category_name}/{subcategory_name} "
                    f"新聞列表失敗：{e}"
                )
                # 不把請求失敗當作正常完成
                raise

            if not news_block:
                print(f"{category_name}/{subcategory_name} 沒有更多新聞")
                break

            for news in news_block:
                a_ele = news.find("a")
                string_ele = news.find("h3", class_="story__headline")
                time_ele = news.find("time", class_="rank__time")

                if not a_ele or "href" not in a_ele.attrs:
                    continue

                if not string_ele or not time_ele:
                    continue

                article_url = urljoin(COMPANY_URL, a_ele["href"])

                data = {
                    "Source": "經濟日報",
                    "Category": category_name,
                    "SubCategory": subcategory_name,
                    "Url": article_url,
                    "Header": string_ele.get_text(strip=True),
                    "CreateTime": time_ele.get_text(strip=True)
                }

                try:
                    content, reason = get_news_content(data["Url"])

                    if reason:
                        print(
                            f"略過新聞：{data['Header']}\n"
                            f"原因：{reason}"
                        )
                        continue

                    data["Content"] = content
                    clean_data_list.append(data)
                    print(f"成功擷取：{data['Header']}")

                except requests.RequestException as e:
                    print(
                        f"新聞擷取失敗：{data['Url']}，"
                        f"原因：{e}"
                    )

                time.sleep(1)

            curr_page += 1

df = pd.DataFrame(clean_data_list, columns=["Source", "Category", "SubCategory", "Url", "Header", "CreateTime", "Content"])
df.to_csv("./result/EDN_news.csv", index=False, encoding="utf-8", mode="w", header=True)
