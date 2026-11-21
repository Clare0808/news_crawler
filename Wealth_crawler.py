import requests
import json
import pandas as pd

def get_news_list(id) :
    data = {
        "operationName" : "Category",
        "variables" : {
            "id" : id,
            "type" : None,
            "offset" : 0,
            "limit" : 100,
            "viewOrderType" : None
        },
        "query" : "query Category($id: ID!, $offset: Int, $limit: Int, $type: ArticleType, $viewOrderType: ArticleViewOrderType) {\n  category(id: $id) {\n    id\n    name\n    navItem {\n      id\n      group\n      __typename\n    }\n    articles(\n      offset: $offset\n      limit: $limit\n      type: $type\n      viewOrderType: $viewOrderType\n    ) {\n      ...ArticleBaseFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ArticleBaseFields on Article {\n  id\n  state\n  title\n  subtitle\n  cover\n  coverText\n  coverAlt\n  content\n  contents\n  type\n  vipOnly\n  views\n  video {\n    id\n    youtubeId\n    playlistId\n    __typename\n  }\n  authors {\n    id\n    name\n    state\n    fameColumn {\n      id\n      avatar\n      description\n      __typename\n    }\n    __typename\n  }\n  directors\n  organizers {\n    id\n    name\n    state\n    fameColumn {\n      id\n      avatar\n      description\n      __typename\n    }\n    __typename\n  }\n  hashtags {\n    id\n    name\n    __typename\n  }\n  categories {\n    id\n    name\n    __typename\n  }\n  releasedAt\n  createdAt\n  updatedAt\n  deletedAt\n  isHeadline\n  isPinned\n  isSponsored\n  __typename\n}\n"
    }
    
    resp = requests.post(
        URL, 
        json=data,
        verify=False
    ).text
    row_data_list = json.loads(resp)["data"]["category"]

    return row_data_list

URL = "https://www.wealth.com.tw/graphql"
ARTICLE_URL = "https://www.wealth.com.tw/articles/"

CATEGORY = {
    "地產": "800e2b3c-0352-4fba-aea2-01fff6b16015",
    "金融圈": "d1354fa3-82bf-42e6-84ad-9e36d7615892",
    "國際": "2c6379e9-7527-442b-880a-bb9552689e06",
    "健康醫療": "de408237-667e-4594-abd8-8106ba567324",
    "企業": "3187845b-57fb-4336-bc4b-4f30cbeb642c",
    "投資": "87259978-8ff6-465c-b552-c33f69f6432e",
    "政經": "352be1d4-7ce8-42b8-9a84-0f491f7927ea",
    "科技": "79c03f3f-d546-4551-a05f-c6d38e5579ca",
}

clean_data_list = []

for category in CATEGORY :
    row_data_list = get_news_list(CATEGORY[category])

    data = {}

    news_source = "財經"
    news_category = row_data_list["name"]

    news_articles = row_data_list["articles"]

    for news in news_articles :
        data = {}

        data["Source"] = news_source
        data["Category"] = news_category

        data["Url"] = ARTICLE_URL + news["id"]
        data["Header"] = news["title"]
        data["CreateTime"] = news["createdAt"]

        raw_content = json.loads(news["content"])
        
        clean_content = ""

        for raw in raw_content :
            curr_row = raw["children"]

            for curr in curr_row : 
                if "text" in curr :
                    clean_content += curr["text"]

        data["Content"] = clean_content

        clean_data_list.append(data)

df = pd.DataFrame(clean_data_list, columns=["Source", "Category", "SubCategory", "Url", "Header", "CreateTime", "Content"])
df.to_csv("./result/Wealth_news.csv", index=False, encoding="utf-8", mode="w", header=True)
