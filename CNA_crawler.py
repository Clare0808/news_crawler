import requests
from bs4 import BeautifulSoup
import json
import time
import pandas as pd

def get_news_list(category, page):
    source_url = "https://www.cna.com.tw/cna2018api/api/WNewsList"

    data = {
        "action": "0",
        "category": category, 
        "pagesize": "100", 
        "pageidx": page
    }

    resp = requests.post(
        source_url, 
        headers=HEADERS,
        json=data, 
        verify=False
    )
    news_list = resp.json()["ResultData"]["Items"]

    return news_list

def get_news_content(url):
    html_ele = requests.get(
        url, 
        headers=HEADERS, 
        verify=False
    ).text

    soup = BeautifulSoup(html_ele, "html.parser")

    script_label = soup.find("script", type="application/ld+json")

    return script_label

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
    "Content-Type" : "application/json",
    "Origin" : "https://www.cna.com.tw",
    "Referer" : "https://www.cna.com.tw/list/aie.aspx"
}

CATEGORY = {
    "產經": "aie",
    "國際": "aopl",
    "生活": "ahel",
    "證券": "asc",
    "社會": "asoc",
}

clean_data_list = []

max_page = 10

for category in CATEGORY :
    curr_page = 1

    while curr_page <= max_page :    
        news_list = get_news_list(CATEGORY[category], curr_page)

        for news in news_list :
            data = {}

            data["Source"] = "中央社"
            data["Category"] = news["ClassName"]
            data["SubCategory"] = None
            data["Url"] = news["PageUrl"]
            data["Header"] = news["HeadLine"]
            data["CreateTime"] = news["CreateTime"]
            data["Content"] = ""

            script_label = get_news_content(news["PageUrl"])

            if script_label :
                news_json = json.loads(script_label.text)[0]

                if news_json.get("articleBody") :
                    data["Content"] = news_json["articleBody"]

            clean_data_list.append(data)

            time.sleep(1)

        curr_page += 1

df = pd.DataFrame(clean_data_list, columns=["Source", "Category", "SubCategory", "Url", "Header", "CreateTime", "Content"])
df.to_csv("./result/CNA_news.csv", index=False, encoding="utf-8", mode="w", header=True)
