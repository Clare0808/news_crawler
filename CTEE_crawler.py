from curl_cffi import requests
import pandas as pd
import time
import orjson

COMPANY_URL = "https://www.ctee.com.tw"

CATEGORY = {
    "半導體" : "semi",
    "科技動態" : "tech",
    "綜合產業" : "i-prime",
    "生技醫療" : "bio",
    "金融話題" : "f-highlights",
    "外匯市場" : "forex",
    "金融科技" : "fintech",
    "銀行動態" : "bank",
    "金融人物" : "f-people",
    "全球政經" : "w-highlights",
    "全球市場" : "w-market",
    "議題觀點" : "w-view",
    "國際產業" : "w-industry",
    "重大訊息" : "mops"
}

max_page = 10

clean_data_list = []

for category in CATEGORY :
    curr_page = 1

    while curr_page <= max_page :
        api = f"https://www.ctee.com.tw/api/category/{CATEGORY[category]}/{curr_page}"

        # 使用 impersonate 模擬真實瀏覽器的 TLS 指紋
        try:
            resp = requests.get(api, impersonate="chrome", timeout=20)

        except requests.exceptions.RequestException as e:
            print(f"{category} 第 {curr_page} 頁請求失敗：{e}")

            curr_page += 1

            time.sleep(1)
            
            continue

        if resp :
            try:
                row_data = resp.json()

            except orjson.JSONDecodeError:
                print(f"{category} 第 {curr_page} 頁非 JSON：HTTP {resp.status_code}，內容開頭：{resp.text[:100]!r}")
                
                curr_page += 1
                
                time.sleep(1)
                
                continue

            print(f"{category} : {resp.status_code}")

            for news in row_data :
                data = {}

                data["Source"] = "工商時報"
                data["Category"] = news["pCategoryName"]
                data["SubCategory"] = None
                data["Url"] = COMPANY_URL + news["hyperLink"]
                data["Header"] = news["title"]
                data["CreateTime"] = news["publishDatetime"]
                data["Content"] = news["content"]

                clean_data_list.append(data)

        curr_page += 1

        time.sleep(1)

df = pd.DataFrame(clean_data_list, columns=["Source", "Category", "SubCategory", "Url", "Header", "CreateTime", "Content"])
df.to_csv("./result/CTEE_news.csv", index=False, encoding="utf-8", mode="w", header=True)
